import QtQuick 2.4
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.3

ColumnLayout {
    id: columnLayout
    property alias finishButton: finishButton
    property alias cancelButton: cancelButton
    property alias image: image

    spacing: 20

    Label {
        id: instructionsLabel
        text: qsTr("<b>Please scan the QR code displayed below using Secalot RemoteScreen app on your mobile phone.</b>")
        Layout.maximumWidth: 400
        wrapMode: Text.WordWrap
        textFormat: Text.RichText
        Layout.fillWidth: true
    }

    Image {
        Layout.fillWidth: true
        id: image
        fillMode: Image.PreserveAspectFit
        source: ""
        cache: false
    }

    RowLayout {
        id: rowLayout
        Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
        Layout.fillWidth: true

        Button {
            id: cancelButton
            text: qsTr("Cancel")
        }

        Button {
            id: finishButton
            text: qsTr("Finish")
        }
    }
}
