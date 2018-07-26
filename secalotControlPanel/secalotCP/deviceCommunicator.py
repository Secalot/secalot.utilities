# Secalot utilities.
# Copyright (c) 2017 Matvey Mukha <matvey.mukha@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot, QMetaObject, Q_ARG, QUrl
import smartcard.System
import time

import secalotCP.otpControl as otpControl
import secalotCP.updateFirmware as updateFirmware
import secalotCP.totpService as totpService
import secalotCP.ethControl as ethControl
import secalotCP.sslControl as sslControl
from secalotCP.deviceFinder import DeviceFinder
from mnemonic import Mnemonic


class DeviceCommunicatorException(Exception):
    def __init__(self, reason):
        super().__init__()
        self.reason = reason


class EnglishMnemonic(Mnemonic):
    @classmethod
    def list_languages(cls):
        return ['english']


class DeviceCommunicatorImplementation(QObject):
    remoteScreenErrorOccurred = pyqtSignal(str, arguments=['errorMessage'])
    remoteScreenCommandSent = pyqtSignal(bytes, arguments=['response'])

    getOTPSettingsReady = pyqtSignal(str, str, arguments=['numberOfDigits', 'otpType'])
    setOTPSettingsReady = pyqtSignal()
    generatedOTPKeyReady = pyqtSignal(str, arguments=['key'])
    getDeviceInfoReady = pyqtSignal(str, str, str, str, str,
                                    arguments=['deviceID', 'serialNumber', 'fwVersion', 'fsVersion',
                                               'bootloaderVersion'])
    errorOccurred = pyqtSignal(str, arguments=['errorMessage'])
    firmwareUpdateInfo = pyqtSignal(str, arguments=['message'])
    firmwareUpdateReady = pyqtSignal()
    firmwareUpdateFailed = pyqtSignal(str, arguments=['errorMessage'])
    getFirmwareImageInfoReady = pyqtSignal(str, str, str, str,
                                           arguments=['deviceID', 'fwVersion', 'fsVersion', 'bootloaderVersion'])
    getEthereumWalletInfoReady = pyqtSignal(str, str, str, arguments=['appVersion', 'walletInitialized', 'pinVerified'])
    wipeoutEthereumWalletReady = pyqtSignal()
    restoreEthereumWalletReady = pyqtSignal()
    createEthereumWalletReady = pyqtSignal(str, arguments=['seed'])
    getSslPublicKeyFingerprintReady = pyqtSignal(str, arguments=['fingerprint'])
    getSslPublicKeyReady = pyqtSignal(str, arguments=['publicKey'])

    selectedReader = None
    selectedReaderType = None

    def __init__(self):
        super().__init__()

    @pyqtSlot(str, str)
    def readerSelected(self, reader, readerType):
        self.selectedReader = reader
        self.selectedReaderType = readerType
        time.sleep(0.2)

    @pyqtSlot()
    def readerDeselected(self):
        self.selectedReader = None
        self.selectedReaderType = None

    @pyqtSlot(bytes)
    def sendRemoteScreenCommand(self, command):
        connection = None
        try:
            connection = self.connectToDevice()
            response, sw1, sw2 = connection.transmit(list(command))
            response = response + [sw1] + [sw2]
            self.remoteScreenCommandSent.emit(bytes(response))
        except DeviceCommunicatorException as e:
            self.remoteScreenErrorOccurred.emit("Device not connected")
        except Exception as e:
            self.remoteScreenErrorOccurred.emit(self.tr("Failed to communicate with the device"))
        finally:
            self.disconnectFromDevice(connection)

    @pyqtSlot()
    def getOTPSettings(self):
        connection = None
        try:
            connection = self.connectToDevice()
            numberOfDigits, type = otpControl.getNumberOfDigitsAndType(connection)
            self.getOTPSettingsReady.emit(str(numberOfDigits), type)
        except DeviceCommunicatorException as e:
            self.errorOccurred.emit(e.reason)
        except otpControl.InvalidCardResponseError:
            self.errorOccurred.emit(self.tr("Communication failed."))
        except Exception as e:
            self.errorOccurred.emit(self.tr("An error occurred."))
        finally:
            self.disconnectFromDevice(connection)

    @pyqtSlot(str, str, str)
    def setOTPSettings(self, numberOfDigits, type, key):
        connection = None
        try:

            numberOfDigits = otpControl.number_of_digits(numberOfDigits)
            type = otpControl.otp_type(type)

            try:
                key = otpControl.otp_key(key)
            except Exception:
                raise DeviceCommunicatorException(self.tr("Invalid Key format. The key should be 10 to 32 bytes long."))

            connection = self.connectToDevice()

            otpControl.setKeyAndType(connection, key, type)
            otpControl.setNumberOfDigits(connection, numberOfDigits)

            self.setOTPSettingsReady.emit()
        except DeviceCommunicatorException as e:
            self.errorOccurred.emit(e.reason)
        except otpControl.InvalidCardResponseError:
            self.errorOccurred.emit(self.tr("Communication failed."))
        except Exception as e:
            self.errorOccurred.emit(self.tr("An error occurred."))
        finally:
            self.disconnectFromDevice(connection)

    @pyqtSlot(str, str)
    def generateOTPKey(self, keyFormat, keyLength):
        try:
            keyLength = int(keyLength)
            key = otpControl.generateKey(keyFormat, keyLength)
            self.generatedOTPKeyReady.emit(key)
        except Exception as e:
            self.errorOccurred.emit(self.tr("Generic error."))

    @pyqtSlot()
    def getDeviceInfo(self):
        connection = None
        try:
            connection = self.connectToDevice()
            deviceInfo = updateFirmware.getDeviceInfo(self.getSelectedReaderType(), connection)

            self.getDeviceInfoReady.emit(hex(deviceInfo.deviceID), hex(deviceInfo.serialNumber)[2:].zfill(8),
                                         hex(deviceInfo.firmwareVersion), hex(deviceInfo.fileSystemVersion),
                                         hex(deviceInfo.bootloaderVersion))
        except DeviceCommunicatorException as e:
            self.errorOccurred.emit(e.reason)
        except otpControl.InvalidCardResponseError:
            self.errorOccurred.emit(self.tr("Communication failed."))
        except Exception as e:
            self.errorOccurred.emit(self.tr("An error occurred."))
        finally:
            self.disconnectFromDevice(connection)

    @pyqtSlot(str, bool)
    def flashFirmware(self, fileName, cleanFileSystemRequested):
        connection = None

        try:
            self.firmwareUpdateInfo.emit(self.tr('Loading firmware...'))
            deviceType = self.getSelectedReaderType()
            fileName = QUrl(fileName).toLocalFile()
            file = open(fileName, "rb")

            try:
                imageInfo = updateFirmware.getUpdateImageInfo(file)
            except Exception:
                raise DeviceCommunicatorException(self.tr('Invalid image file format.'))

            fwApduList, blApduList = updateFirmware.updateImageToAPDUs(file, cleanFileSystemRequested)
            connection = self.connectToDevice()
            deviceInfo = updateFirmware.getDeviceInfo(deviceType, connection)
            updateFirmware.checkImageInfo(imageInfo, deviceInfo, cleanFileSystemRequested)

            if deviceType == 'bootloader':
                if deviceInfo.bootloaderVersion != imageInfo.bootloaderVersion:
                    self.firmwareUpdateInfo.emit(self.tr('Please replug your device.'))
                    updateFirmware.switchModes(deviceType, connection)
                    deviceType, connection = updateFirmware.findConnectedDevice()
                    self.firmwareUpdateInfo.emit(self.tr('Loading firmware...'))
                    updateFirmware.loadTheImage(connection, blApduList)
                    self.firmwareUpdateInfo.emit(self.tr('Please replug your device.'))
                    updateFirmware.switchModes(deviceType, connection)
                    deviceType, connection = updateFirmware.findConnectedDevice()
            else:
                if (
                            deviceInfo.bootloaderVersion != imageInfo.bootloaderVersion) or deviceInfo.bootloaderIsBootable == False:
                    self.firmwareUpdateInfo.emit(self.tr('Loading firmware...'))
                    updateFirmware.loadTheImage(connection, blApduList)
                self.firmwareUpdateInfo.emit(self.tr('Please replug your device.'))
                updateFirmware.switchModes(deviceType, connection)
                deviceType, connection = updateFirmware.findConnectedDevice()

            self.firmwareUpdateInfo.emit(self.tr('Loading firmware...'))
            updateFirmware.loadTheImage(connection, fwApduList)
            self.firmwareUpdateInfo.emit(self.tr('Please replug your device.'))
            updateFirmware.switchModes(deviceType, connection)
            self.firmwareUpdateReady.emit()

        except DeviceCommunicatorException as e:
            self.firmwareUpdateFailed.emit(e.reason)
        except updateFirmware.InvalidCardResponseError:
            self.firmwareUpdateFailed.emit(self.tr("Communication failed."))
        except updateFirmware.NotSuitableImageError as e:
            self.firmwareUpdateFailed.emit(self.notSuitableImageInfoCodeToString(e.reasonCode))
        except updateFirmware.InvalidUpdateImageError:
            self.firmwareUpdateFailed.emit(self.tr("Invalid image file format."))
        except Exception as e:
            self.firmwareUpdateFailed.emit(self.tr("An error occurred."))
        finally:
            self.disconnectFromDevice(connection)

    @pyqtSlot(str)
    def getFirmwareImageInfo(self, fileName):
        try:
            fileName = QUrl(fileName).toLocalFile()
            file = open(fileName, "rb")
            try:
                imageInfo = updateFirmware.getUpdateImageInfo(file)
            except Exception:
                raise DeviceCommunicatorException(self.tr("Invalid image file format."))
            self.getFirmwareImageInfoReady.emit(hex(imageInfo.deviceID), hex(imageInfo.firmwareVersion),
                                                hex(imageInfo.fileSystemVersion), hex(imageInfo.bootloaderVersion))
        except DeviceCommunicatorException as e:
            self.errorOccurred.emit(e.reason)
        except Exception as e:
            self.errorOccurred.emit(self.tr("Generic error."))

    @pyqtSlot()
    def getEthereumWalletInfo(self):
        connection = None
        try:
            connection = self.connectToDevice()

            appExists = True

            try:
                info = ethControl.getInfo(connection)
            except:
                appExists = False

            if appExists == False:
                self.getEthereumWalletInfoReady.emit('0.0', self.tr('unknown'), self.tr('unknown'))
            else:
                if info.walletInitialized == True:
                    initStatus = self.tr('initialized')
                else:
                    initStatus = self.tr('not initialized')

                if info.pinVerified == True:
                    pinStatus = self.tr('verified')
                else:
                    pinStatus = self.tr('unverified')

                self.getEthereumWalletInfoReady.emit(info.version, initStatus, pinStatus)

        except DeviceCommunicatorException as e:
            self.errorOccurred.emit(e.reason)
        except ethControl.InvalidCardResponseError:
            print(self.tr("Communication failed."))
        except Exception as e:
            self.errorOccurred.emit(self.tr("An error occurred."))
        finally:
            self.disconnectFromDevice(connection)

    @pyqtSlot()
    def wipeoutEthereumWallet(self):
        connection = None
        try:
            connection = self.connectToDevice()

            ethControl.wipeoutWallet(connection)

            self.wipeoutEthereumWalletReady.emit()

        except DeviceCommunicatorException as e:
            self.errorOccurred.emit(e.reason)
        except ethControl.InvalidCardResponseError:
            print(self.tr("Communication failed."))
        except Exception as e:
            self.errorOccurred.emit(self.tr("An error occurred."))
        finally:
            self.disconnectFromDevice(connection)

    @pyqtSlot(str, str, str)
    def restoreEthereumWallet(self, seed, newPin, repeatPin):
        connection = None
        try:
            connection = self.connectToDevice()

            if newPin != repeatPin:
                raise DeviceCommunicatorException(self.tr("PIN-codes do not match"))

            try:
                newPin = ethControl.pin(newPin)
            except Exception:
                raise DeviceCommunicatorException(self.tr("Pin length should be between 4 and 32 bytes"))

            try:
                seed = ethControl.seed(seed)
            except Exception:
                raise DeviceCommunicatorException(self.tr("Invalid seed format. \n"
                                                          " The seed should be either a Bip39 mnemonic \n"
                                                          "or a hex string of 32 to 64 bytes."))

            ethControl.initWallet(connection, seed, newPin)

            self.restoreEthereumWalletReady.emit()

        except DeviceCommunicatorException as e:
            self.errorOccurred.emit(e.reason)
        except ethControl.InvalidCardResponseError:
            print(self.tr("Communication failed."))
        except Exception as e:
            self.errorOccurred.emit(self.tr("An error occurred."))
        finally:
            self.disconnectFromDevice(connection)

    @pyqtSlot(str, str)
    def createEthereumWallet(self, newPin, repeatPin):
        connection = None
        try:
            connection = self.connectToDevice()

            if newPin != repeatPin:
                raise DeviceCommunicatorException(self.tr("PIN-codes do not match"))

            try:
                newPin = ethControl.pin(newPin)
            except Exception:
                raise DeviceCommunicatorException(self.tr("Pin length should be between 4 and 32 bytes"))

            mnemonic = EnglishMnemonic('english')

            entropy = ethControl.getRandom(connection, 16)
            entropy = bytearray(entropy)
            phrase = mnemonic.to_mnemonic(entropy)
            seed = mnemonic.to_seed(phrase)

            ethControl.initWallet(connection, seed, newPin)

            self.createEthereumWalletReady.emit(phrase)

        except DeviceCommunicatorException as e:
            self.errorOccurred.emit(e.reason)
        except ethControl.InvalidCardResponseError:
            print(self.tr("Communication failed."))
        except Exception as e:
            self.errorOccurred.emit(self.tr("An error occurred."))
        finally:
            self.disconnectFromDevice(connection)

    @pyqtSlot()
    def getSslPublicKeyFingerprint(self):
        connection = None
        try:
            connection = self.connectToDevice()

            try:
                sslControl.selectApp(connection)
            except sslControl.InvalidCardResponseError as e:
                return

            fingerprint = sslControl.getPublicKeyFingerprint(connection)

            self.getSslPublicKeyFingerprintReady.emit(fingerprint)

        except DeviceCommunicatorException as e:
            self.errorOccurred.emit(e.reason)
        except Exception as e:
            self.errorOccurred.emit(self.tr("An error occurred."))
        finally:
            self.disconnectFromDevice(connection)

    @pyqtSlot()
    def getSslPublicKey(self):
        connection = None
        try:
            connection = self.connectToDevice()
            publicKey = sslControl.getPublicKey(connection)

            self.getSslPublicKeyReady.emit(publicKey)

        except DeviceCommunicatorException as e:
            self.errorOccurred.emit(e.reason)
        except Exception as e:
            self.errorOccurred.emit(self.tr("An error occurred."))
        finally:
            self.disconnectFromDevice(connection)

    @pyqtSlot(str, str)
    def sendCurrentTimeToDevice(self, reader, readerType):
        connection = None
        if readerType == "firmware":
            try:
                time.sleep(0.2)
                connection = self.connectToDevice(reader)
                totpService.sendTime(connection)
            except Exception as e:
                pass
            finally:
                self.disconnectFromDevice(connection)

    @pyqtSlot()
    def sendCurrentTimeToAllConnectedDevices(self):
        connection = None
        try:
            connectedFirmwareReaders, connectedBootloaderReaders = DeviceFinder.getAllReaders()

            for reader in connectedFirmwareReaders:
                connection = self.connectToDevice(reader.name)
                totpService.sendTime(connection)
        except Exception as e:
            pass
        finally:
            self.disconnectFromDevice(connection)

    def notSuitableImageInfoCodeToString(self, reasonCode):
        errorMessages = [self.tr('This update is targeting a different device version.'),
                         self.tr('A downgrade can not be performed.'),
                         self.tr('A downgrade can not be performed.'),
                         self.tr('A downgrade can not be performed.'),
                         self.tr(
                             'This update can only be applied together with cleaning a file system.\nPlease tick the "Erase file system" checkbox.'),
                         self.tr(
                             'An update performed on this device was interrupted while cleaning a file system.\nPlease tick the "Erase file system" checkbox.'),
                         self.tr(
                             'Previous update was interrupted. Please continue with the exact same update image file.')]

        return errorMessages[reasonCode - 1]

    def connectToDevice(self, reader=None):

        if reader == None:
            selectedReader = self.getSelectedReaderName()
        else:
            selectedReader = reader

        connectedReaders = smartcard.System.readers()

        reader = next((reader for reader in connectedReaders if selectedReader in reader.name), None)

        if reader == None:
            raise DeviceCommunicatorException(self.tr("No reader selected."))

        connection = reader.createConnection()
        connection.connect()

        return connection

    def getSelectedReaderName(self):
        if self.selectedReader == None:
            raise DeviceCommunicatorException(self.tr("No reader selected."))

        return self.selectedReader

    def getSelectedReaderType(self):
        if self.selectedReaderType == None:
            raise DeviceCommunicatorException(self.tr("No reader selected."))

        return self.selectedReaderType

    def disconnectFromDevice(self, connection):
        try:
            if connection != None:
                connection.disconnect()
        except Exception:
            pass


class DeviceCommunicator(QObject):
    remoteScreenErrorOccurred = pyqtSignal(str, arguments=['errorMessage'])
    remoteScreenCommandSent = pyqtSignal(bytes, arguments=['response'])
    getOTPSettingsReady = pyqtSignal(str, str, arguments=['numberOfDigits', 'otpType'])
    setOTPSettingsReady = pyqtSignal()
    generatedOTPKeyReady = pyqtSignal(str, arguments=['key'])
    getDeviceInfoReady = pyqtSignal(str, str, str, str, str,
                                    arguments=['deviceID', 'serialNumber', 'fwVersion', 'fsVersion',
                                               'bootloaderVersion'])
    errorOccurred = pyqtSignal(str, arguments=['errorMessage'])
    firmwareUpdateInfo = pyqtSignal(str, arguments=['message'])
    firmwareUpdateReady = pyqtSignal()
    firmwareUpdateFailed = pyqtSignal(str, arguments=['errorMessage'])
    getFirmwareImageInfoReady = pyqtSignal(str, str, str, str,
                                           arguments=['deviceID', 'fwVersion', 'fsVersion', 'bootloaderVersion'])
    getEthereumWalletInfoReady = pyqtSignal(str, str, str, arguments=['appVersion', 'walletInitialized', 'pinVerified'])
    wipeoutEthereumWalletReady = pyqtSignal()
    restoreEthereumWalletReady = pyqtSignal()
    createEthereumWalletReady = pyqtSignal(str, arguments=['seed'])
    getSslPublicKeyFingerprintReady = pyqtSignal(str, arguments=['fingerprint'])
    getSslPublicKeyReady = pyqtSignal(str, arguments=['publicKey'])

    def __init__(self):
        super().__init__()
        self.implementation = DeviceCommunicatorImplementation()
        self.implementationThread = QThread()
        self.implementation.moveToThread(self.implementationThread)
        self.implementationThread.start()

        self.implementation.remoteScreenErrorOccurred.connect(self.remoteScreenErrorOccurred)
        self.implementation.remoteScreenCommandSent.connect(self.remoteScreenCommandSent)
        self.implementation.getOTPSettingsReady.connect(self.getOTPSettingsReady)
        self.implementation.setOTPSettingsReady.connect(self.setOTPSettingsReady)
        self.implementation.generatedOTPKeyReady.connect(self.generatedOTPKeyReady)
        self.implementation.getDeviceInfoReady.connect(self.getDeviceInfoReady)
        self.implementation.errorOccurred.connect(self.errorOccurred)
        self.implementation.firmwareUpdateInfo.connect(self.firmwareUpdateInfo)
        self.implementation.firmwareUpdateReady.connect(self.firmwareUpdateReady)
        self.implementation.firmwareUpdateFailed.connect(self.firmwareUpdateFailed)
        self.implementation.getFirmwareImageInfoReady.connect(self.getFirmwareImageInfoReady)
        self.implementation.getEthereumWalletInfoReady.connect(self.getEthereumWalletInfoReady)
        self.implementation.wipeoutEthereumWalletReady.connect(self.wipeoutEthereumWalletReady)
        self.implementation.restoreEthereumWalletReady.connect(self.restoreEthereumWalletReady)
        self.implementation.createEthereumWalletReady.connect(self.createEthereumWalletReady)
        self.implementation.getSslPublicKeyFingerprintReady.connect(self.getSslPublicKeyFingerprintReady)
        self.implementation.getSslPublicKeyReady.connect(self.getSslPublicKeyReady)

    def cleanup(self):
        self.implementationThread.quit()
        if self.implementationThread.wait(2000) == False:
            self.implementationThread.terminate()
            self.implementationThread.wait(2000)

    @pyqtSlot(str, str)
    def readerSelected(self, reader, readerType):
        QMetaObject.invokeMethod(self.implementation, "readerSelected", Qt.QueuedConnection, Q_ARG(str, reader),
                                 Q_ARG(str, readerType))

    @pyqtSlot()
    def readerDeselected(self):
        QMetaObject.invokeMethod(self.implementation, "readerDeselected", Qt.QueuedConnection)

    @pyqtSlot(bytes)
    def sendRemoteScreenCommand(self, command):
        QMetaObject.invokeMethod(self.implementation, "sendRemoteScreenCommand", Qt.QueuedConnection,
                                 Q_ARG(bytes, command))

    @pyqtSlot()
    def getOTPSettings(self):
        QMetaObject.invokeMethod(self.implementation, "getOTPSettings", Qt.QueuedConnection)

    @pyqtSlot(str, str, str)
    def setOTPSettings(self, numberOfDigits, type, key):
        QMetaObject.invokeMethod(self.implementation, "setOTPSettings", Qt.QueuedConnection, Q_ARG(str, numberOfDigits),
                                 Q_ARG(str, type), Q_ARG(str, key))

    @pyqtSlot(str, str)
    def generateOTPKey(self, keyFormat, keyLength):
        QMetaObject.invokeMethod(self.implementation, "generateOTPKey", Qt.QueuedConnection, Q_ARG(str, keyFormat),
                                 Q_ARG(str, keyLength))

    @pyqtSlot()
    def getDeviceInfo(self):
        QMetaObject.invokeMethod(self.implementation, "getDeviceInfo", Qt.QueuedConnection)

    @pyqtSlot(str, bool)
    def flashFirmware(self, fileName, cleanFileSystemRequested):
        QMetaObject.invokeMethod(self.implementation, "flashFirmware", Qt.QueuedConnection, Q_ARG(str, fileName),
                                 Q_ARG(bool, cleanFileSystemRequested))

    @pyqtSlot(str)
    def getFirmwareImageInfo(self, fileName):
        QMetaObject.invokeMethod(self.implementation, "getFirmwareImageInfo", Qt.QueuedConnection, Q_ARG(str, fileName))

    @pyqtSlot()
    def getEthereumWalletInfo(self):
        QMetaObject.invokeMethod(self.implementation, "getEthereumWalletInfo", Qt.QueuedConnection)

    @pyqtSlot()
    def wipeoutEthereumWallet(self):
        QMetaObject.invokeMethod(self.implementation, "wipeoutEthereumWallet", Qt.QueuedConnection)

    @pyqtSlot(str, str, str)
    def restoreEthereumWallet(self, seed, newPin, repeatPin):
        QMetaObject.invokeMethod(self.implementation, "restoreEthereumWallet", Qt.QueuedConnection, Q_ARG(str, seed),
                                 Q_ARG(str, newPin), Q_ARG(str, repeatPin))

    @pyqtSlot(str, str)
    def createEthereumWallet(self, newPin, repeatPin):
        QMetaObject.invokeMethod(self.implementation, "createEthereumWallet", Qt.QueuedConnection, Q_ARG(str, newPin),
                                 Q_ARG(str, repeatPin))

    @pyqtSlot()
    def getSslPublicKeyFingerprint(self):
        QMetaObject.invokeMethod(self.implementation, "getSslPublicKeyFingerprint", Qt.QueuedConnection)

    @pyqtSlot()
    def getSslPublicKey(self):
        QMetaObject.invokeMethod(self.implementation, "getSslPublicKey", Qt.QueuedConnection)

    @pyqtSlot(str, str)
    def sendCurrentTimeToDevice(self, reader, readerType):
        QMetaObject.invokeMethod(self.implementation, "sendCurrentTimeToDevice", Qt.QueuedConnection,
                                 Q_ARG(str, reader), Q_ARG(str, readerType))

    @pyqtSlot()
    def sendCurrentTimeToAllConnectedDevices(self):
        QMetaObject.invokeMethod(self.implementation, "sendCurrentTimeToAllConnectedDevices", Qt.QueuedConnection)
