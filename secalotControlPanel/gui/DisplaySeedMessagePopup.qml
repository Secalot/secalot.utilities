import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
import QtQuick.Window 2.0

Popup {

    id: displaySeedMessagePopup
    x: (parent.width - width) / 2
    y: (parent.height - height) / 2
    modal: true
    focus: true
    padding:20
    closePolicy: Popup.CloseOnEscape

    function clearAll() {
        displaySeedMessage.seedTextArea.text = ""
    }

    function setSeed(seed) {
        displaySeedMessage.seedTextArea.text = seed
    }

    DisplaySeedMessage {
        id: displaySeedMessage

        okButton.onClicked: {
            displaySeedMessagePopup.clearAll()
            displaySeedMessagePopup.close()
        }
    }
}
