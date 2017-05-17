import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
import QtQuick.Window 2.0

Popup {

    id: simpleMessagePopup

    function setSimpleMessageText(text) {
        simpleMessage.label.text = text
    }

    x: (parent.width - width) / 2
    y: (parent.height - height) / 2

    modal: true
    focus: true
    closePolicy: Popup.CloseOnEscape

    SimpleMessage {
        id: simpleMessage

        button.onClicked: {
            simpleMessagePopup.close()
        }
    }
}
