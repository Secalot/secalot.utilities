import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
import QtQuick.Window 2.0

Popup {

    id: pinAndXrpSecretEntryMessagePopup
    x: (parent.width - width) / 2
    y: (parent.height - height) / 2
    modal: true
    focus: true
    padding:20
    closePolicy: Popup.CloseOnEscape

    function clearAll() {
        pinAndXrpSecretEntryMessage.secretTextArea.text = ""
        pinAndXrpSecretEntryMessage.newPinTextField.text = ""
        pinAndXrpSecretEntryMessage.repeatPinTextField.text = ""
    }

    function getEnteredData() {

        return {
          secret: pinAndXrpSecretEntryMessage.secretTextArea.text,
          newPin: pinAndXrpSecretEntryMessage.newPinTextField.text,
          repeatPin: pinAndXrpSecretEntryMessage.repeatPinTextField.text
        }
    }

    signal restoreButtonClicked()

    PinAndXrpSecretEntryMessage {
        id: pinAndXrpSecretEntryMessage

        cancelButton.onClicked: {
            pinAndXrpSecretEntryMessagePopup.close()
        }

        restoreButton.onClicked: {
            pinAndXrpSecretEntryMessagePopup.restoreButtonClicked()
        }
    }
}
