import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
import QtQuick.Window 2.0

Popup {

    id: displayXrpSecretMessagePopup
    x: (parent.width - width) / 2
    y: (parent.height - height) / 2
    modal: true
    focus: true
    padding:20
    closePolicy: Popup.CloseOnEscape

    function clearAll() {
        displayXrpSecretMessage.secretTextArea.text = ""
    }

    function setXrpSecret(secret) {
        displayXrpSecretMessage.secretTextArea.text = secret
    }

    DisplayXrpSecretMessage {
        id: displayXrpSecretMessage

        okButton.onClicked: {
            displayXrpSecretMessagePopup.clearAll()
            displayXrpSecretMessagePopup.close()
        }
    }
}
