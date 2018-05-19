import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
import QtQuick.Window 2.0

Popup {

    id: bindingMessagePopup
    x: (parent.width - width) / 2
    y: (parent.height - height) / 2
    modal: true
    focus: true
    padding:20
    closePolicy: Popup.CloseOnEscape

    signal finishButtonClicked()

    function refreshImage(source) {
        bindingMessage.image.source = ""
        bindingMessage.image.source = "image://qrCode/qrCode.png"
    }

    BindingMessage {
        id: bindingMessage

        cancelButton.onClicked: {
            bindingMessagePopup.close()
        }

        finishButton.onClicked: {
            bindingMessagePopup.finishButtonClicked()
            bindingMessagePopup.close()
        }
    }
}
