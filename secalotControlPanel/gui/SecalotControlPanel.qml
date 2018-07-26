import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
import QtQuick.Window 2.0

ApplicationWindow {
    id:mainWindow
    visible: true
    width: 680
    height: 680

    minimumHeight: 680
    minimumWidth: 680

    font.capitalization: Font.MixedCase

    title: qsTr("Secalot Control Panel 1.3")

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

        otpControl.resetGUI()
        firmwareUpdate.resetGUI()
        ethereumWallet.resetGUI()
        remoteScreen.resetGUI()

        swipeView.disableDeviceRelatedTabs()

        simpleMessagePopup.setSimpleMessageText(qsTr("Please connect a Secalot device."))

        simpleMessagePopup.open()
    }

    function tooManyDevices() {

        otpControl.resetGUI()
        firmwareUpdate.resetGUI()
        ethereumWallet.resetGUI()
        remoteScreen.resetGUI()

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
            ethereumWallet.enabled = false
        }

        function enableDeviceRelatedTabs() {
            otpControl.enabled = true
            firmwareUpdate.enabled = true
            ethereumWallet.enabled = true
        }

        function enableFirmwareModeOnlyRelatedTabs() {
            otpControl.enabled = false
            firmwareUpdate.enabled = true
            ethereumWallet.enabled = false
        }

        EthereumWallet {
            id: ethereumWallet
        }

        OtpControl {
            id: otpControl
        }

        FirmwareUpdate {
            id: firmwareUpdate
        }

        RemoteScreen {
            id: remoteScreen
        }
        Options {
            id: options
        }
    }

    footer: TabBar {
        id: tabBar
        currentIndex: swipeView.currentIndex
        TabButton {
            text: qsTr("Ethereum")
        }
        TabButton {
            text: qsTr("OTP")
        }
        TabButton {
            text: qsTr("Firmware update")
        }
        TabButton {
            text: qsTr("RemoteScreen")
        }
        TabButton {
            text: qsTr("Options")
        }
    }
}
