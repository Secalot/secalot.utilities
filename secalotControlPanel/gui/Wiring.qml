import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
import QtQuick.Window 2.0

Item {

    Component.onCompleted: {
        qmlHelperUtils.getCurrentSettings()
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
        target: deviceFinder

        onOneDeviceConnected: {

            mainWindow.deviceConnected(readerType)

            deviceCommunicator.readerSelected(readerName, readerType)

            if( readerType === 'firmware') {
                deviceCommunicator.getOTPSettings()
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
            firmwareUpdate.setDeviceInfo(deviceID, fwVersion, fsVersion, bootloaderVersion)
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

        function restartDeviceMonitoring() {
            deviceFinder.restartMonitoring()
            simpleMessagePopup.onClosed.disconnect(restartDeviceMonitoring)
        }
    }
}
