import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
import QtQuick.Window 2.0

Popup {

    id: pinEntryMessagePopup
    x: (parent.width - width) / 2
    y: (parent.height - height) / 2
    modal: true
    focus: true
    padding:20
    closePolicy: Popup.CloseOnEscape

    function clearAll() {
        pinEntryMessage.newPinTextField.text = ""
        pinEntryMessage.repeatPinTextField.text = ""
    }

    function getEnteredData() {

        return {
          newPin: pinEntryMessage.newPinTextField.text,
          repeatPin: pinEntryMessage.repeatPinTextField.text
        }
    }

    signal createButtonClicked()

    PinEntryMessage {
        id: pinEntryMessage

        cancelButton.onClicked: {
            pinEntryMessagePopup.close()
        }

        createButton.onClicked: {
            pinEntryMessagePopup.createButtonClicked()
        }
    }
}
