import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
import QtQuick.Window 2.0

Popup {

    id: pinAndSeedEntryMessagePopup
    x: (parent.width - width) / 2
    y: (parent.height - height) / 2
    modal: true
    focus: true
    padding:20
    closePolicy: Popup.CloseOnEscape

    function clearAll() {
        pinAndSeedEntryMessage.seedTextArea.text = ""
        pinAndSeedEntryMessage.newPinTextField.text = ""
        pinAndSeedEntryMessage.repeatPinTextField.text = ""
    }

    function getEnteredData() {

        return {
          seed: pinAndSeedEntryMessage.seedTextArea.text,
          newPin: pinAndSeedEntryMessage.newPinTextField.text,
          repeatPin: pinAndSeedEntryMessage.repeatPinTextField.text
        }
    }

    signal restoreButtonClicked()

    PinAndSeedEntryMessage {
        id: pinAndSeedEntryMessage

        cancelButton.onClicked: {
            pinAndSeedEntryMessagePopup.close()
        }

        restoreButton.onClicked: {
            pinAndSeedEntryMessagePopup.restoreButtonClicked()
        }
    }
}
