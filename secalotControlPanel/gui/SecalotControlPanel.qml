import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
import QtQuick.Window 2.0

ApplicationWindow {
    id:mainWindow
    visible: true
    width: 640
    height: 640

    minimumHeight: 640
    minimumWidth: 640

    title: qsTr("Secalot Control Panel 1.0")

    onClosing: {
         close.accepted = false
         mainWindow.hide()
     }

    Wiring {
    }

    function deviceConnected(readerType) {

        simpleMessagePopup.close()

        if( readerType === 'firmware') {
            swipeView.enableDeviceRelatedTabs()
        }
        else {
            swipeView.enableFirmwareModeOnlyRelatedTabs()
        }
    }

    function deviceDisconnected() {

        otpControl.clearCurrentOTPSettings()
        firmwareUpdate.clearDeviceInfo()

        swipeView.disableDeviceRelatedTabs()

        simpleMessagePopup.setSimpleMessageText(qsTr("Please connect a Secalot device."))

        simpleMessagePopup.open()
    }

    function tooManyDevices() {

        otpControl.clearCurrentOTPSettings()
        firmwareUpdate.clearDeviceInfo()

        swipeView.disableDeviceRelatedTabs()

        simpleMessagePopup.setSimpleMessageText(qsTr("Please connect exactly one Secalot device."))

        simpleMessagePopup.open()
    }

    function openSimplePopup(errorMessage) {
        simpleMessagePopup.setSimpleMessageText(errorMessage)
        simpleMessagePopup.open()
    }

    SimpleMessagePopup {
        id: simpleMessagePopup
    }

    SwipeView {
        id: swipeView
        anchors.fill: parent
        currentIndex: tabBar.currentIndex

        function disableDeviceRelatedTabs() {
            otpControl.enabled = false
            firmwareUpdate.enabled = false
        }

        function enableDeviceRelatedTabs() {
            otpControl.enabled = true
            firmwareUpdate.enabled = true
        }

        function enableFirmwareModeOnlyRelatedTabs() {
            otpControl.enabled = false
            firmwareUpdate.enabled = true
        }

        OtpControl {
            id: otpControl
        }

        FirmwareUpdate {
            id: firmwareUpdate
        }

        Options {
            id: options
        }
    }

    footer: TabBar {
        id: tabBar
        currentIndex: swipeView.currentIndex
        TabButton {
            text: qsTr("OTP configuration")
        }
        TabButton {
            text: qsTr("Firmware update")
        }
        TabButton {
            text: qsTr("Options")
        }
    }
}
