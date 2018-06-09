import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
import QtQuick.Window 2.0

Item {

    Component.onCompleted: {
        qmlHelperUtils.getCurrentSettings()

        remoteScreenRoutines.isMobilePhoneBinded()
    }

    Connections {
        target: systemTray
        onOpenAppMenuItemClicked: {
            mainWindow.show()
            mainWindow.raise()
            mainWindow.requestActivate()
        }

        onExitMenuItemClicked: {
            Qt.quit()
        }
    }

    Connections {
        target: qmlHelperUtils

        onCurrentSettingsReady: {
            options.setCheckboxState(sendCurrentTimeToDevice)

            if(sendCurrentTimeToDevice === true) {
                deviceCommunicator.sendCurrentTimeToAllConnectedDevices()
                deviceFinder.deviceAdded.connect(deviceCommunicator.sendCurrentTimeToDevice)
            }
            else {
                deviceFinder.deviceAdded.disconnect(deviceCommunicator.sendCurrentTimeToDevice)
            }
        }
    }

    Connections {
        target: options

        onCheckBoxClicked: {
            qmlHelperUtils.setCurrentSettings(state)

            if(state === true) {
                deviceCommunicator.sendCurrentTimeToAllConnectedDevices()
                deviceFinder.deviceAdded.connect(deviceCommunicator.sendCurrentTimeToDevice)
            }
            else {
                deviceFinder.deviceAdded.disconnect(deviceCommunicator.sendCurrentTimeToDevice)
            }
        }
    }

    Connections {
        target: otpControl

        onSetOtpSettingsRequested: {
            deviceCommunicator.setOTPSettings(numberOfDigits, type, key)
        }

        onGenerateNewKeyRequested: {
            deviceCommunicator.generateOTPKey(keyFormat, keyLength)
        }
    }

    Connections {
        target: firmwareUpdate

        onUpdateRequested: {

            deviceFinder.stopMonitoring()
            deviceCommunicator.flashFirmware(fileName, cleanFileSystemRequested)
        }

        onFirmwareImageInfoRequested: {
            deviceCommunicator.getFirmwareImageInfo(fileName)
        }
    }

    Connections {
        target: ethereumWallet

        onWipeoutRequested: {

            deviceCommunicator.wipeoutEthereumWallet()
        }

        onRestoreRequested: {

            deviceCommunicator.restoreEthereumWallet(seed, newPin, repeatPin)
        }

        onCreateRequested: {

            deviceCommunicator.createEthereumWallet(newPin, repeatPin)
        }

    }

    Connections {
        target: remoteScreen

        onMobilePhoneBindingStarted: {

            remoteScreenRoutines.startMobilePhoneBinding()
        }

        onMobilePhoneBindingFinished: {

            remoteScreenRoutines.finishMobilePhoneBinding()
        }

        onMobilePhoneUnbind: {
            remoteScreenRoutines.unbindMobilePhone()
        }

    }

    Connections {
        target: deviceFinder

        onOneDeviceConnected: {

            mainWindow.deviceConnected(readerType)

            deviceCommunicator.readerSelected(readerName, readerType)

            if( readerType === 'firmware') {
                deviceCommunicator.getOTPSettings()
                deviceCommunicator.getEthereumWalletInfo()
            }

            deviceCommunicator.getDeviceInfo()
        }

        onNoDevicesConnected: {

            mainWindow.deviceDisconnected()

            deviceCommunicator.readerDeselected()
        }

        onMoreThanOneDeviceConnected: {

            mainWindow.tooManyDevices()

            deviceCommunicator.readerDeselected()
        }
    }

    Connections {
        target: deviceCommunicator

        onErrorOccured: {
            mainWindow.openSimplePopup(errorMessage)
        }

        onGetOTPSettingsReady: {
            otpControl.setCurrentOTPSettings(numberOfDigits, otpType)
        }

        onSetOTPSettingsReady: {
            deviceCommunicator.getOTPSettings()
        }

        onGetDeviceInfoReady: {
            firmwareUpdate.setDeviceInfo(deviceID, serialNumber, fwVersion, fsVersion, bootloaderVersion)
        }

        onFirmwareUpdateInfo: {
            firmwareUpdate.setPopupMessage(message)
        }

        onFirmwareUpdateReady: {
            firmwareUpdate.updateFinished()
            deviceFinder.restartMonitoring()
        }

        onFirmwareUpdateFailed: {
            firmwareUpdate.closePopup()
            mainWindow.openSimplePopup(errorMessage)
            simpleMessagePopup.onClosed.connect(restartDeviceMonitoring)
        }

        onGetFirmwareImageInfoReady: {
            firmwareUpdate.setFirmwareImageInfo(deviceID, fwVersion, fsVersion, bootloaderVersion)
        }

        onGeneratedOTPKeyReady: {
            otpControl.setKey(key)
        }

        onGetEthereumWalletInfoReady: {
            ethereumWallet.setWalletInfo(appVersion, walletInitialized, pinVerified)
        }

        onWipeoutEthereumWalletReady: {
            deviceCommunicator.getEthereumWalletInfo()
        }

        onRestoreEthereumWalletReady: {
            ethereumWallet.closePinAndSeedEntryMessagePopup()
            deviceCommunicator.getEthereumWalletInfo()
        }

        onCreateEthereumWalletReady: {
            ethereumWallet.closePinEntryMessagePopup()
            ethereumWallet.displaySeed(seed)
            deviceCommunicator.getEthereumWalletInfo()
        }

        function restartDeviceMonitoring() {
            deviceFinder.restartMonitoring()
            simpleMessagePopup.onClosed.disconnect(restartDeviceMonitoring)
        }
    }

    Connections {
        target: remoteScreenRoutines

        onErrorOccured: {
            mainWindow.openSimplePopup(errorMessage)
        }

        onIsMobilePhoneBindedReady: {
            remoteScreen.setRemoteScreenInfo(mobilePhoneBinded)

            if(mobilePhoneBinded === "Yes") {
                remoteScreenRoutines.startServer()
                remoteScreenRoutines.startZeroConf()
            }
            else {
                remoteScreenRoutines.stopServer()
                remoteScreenRoutines.stopZeroConf()
            }

        }

        onStartMobilePhoneBindingReady: {
            remoteScreen.displayBindingInfo()
        }

        onUnbindMobilePhonetReady: {
            remoteScreenRoutines.isMobilePhoneBinded()
        }

        onFinishMobilePhoneBindingReady: {
            remoteScreenRoutines.isMobilePhoneBinded()
        }

    }

}
