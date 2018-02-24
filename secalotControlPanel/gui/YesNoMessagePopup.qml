import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
import QtQuick.Window 2.0

Popup {

    id: yesNoMessagePopup
    x: (parent.width - width) / 2
    y: (parent.height - height) / 2
    modal: true
    focus: true
    closePolicy: Popup.CloseOnEscape

    function setYesNoMessageText(text) {
        yesNoMessage.label.text = text
    }

    signal yesButtonClicked()

    YesNoMessage {
        id: yesNoMessage

        yesButton.onClicked: {
            yesButtonClicked()
            yesNoMessagePopup.close()
        }

        noButton.onClicked: {
            yesNoMessagePopup.close()
        }
    }
}
