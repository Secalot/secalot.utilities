import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
import QtQuick.Window 2.0

Popup {

    id: firmwareMessagePopup

    function showDoneButton() {
        firmwareUpdateMessage.button.visible = true
    }

    function hideDoneButton() {
        firmwareUpdateMessage.button.visible = false
    }

    function setFirmwareUpdateMessageText(text) {
        firmwareUpdateMessage.label.text = text
    }

    x: (parent.width - width) / 2
    y: (parent.height - height) / 2

    modal: true
    focus: true
    closePolicy: Popup.NoAutoClose

    FirmwareUpdateMessage {
        id: firmwareUpdateMessage

        button.onClicked: {
            firmwareMessagePopup.close()
        }

    }

}
