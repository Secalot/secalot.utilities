import QtQuick 2.4
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.3

ColumnLayout {
    id: columnLayout

    property alias okButton: okButton
    property alias warningLabel: warningLabel
    property alias secretTextArea: secretTextArea
    spacing: 20

    Label {
        id: warningLabel
        text: qsTr("<b>The secret of your new XRP wallet is written below. Please save it in a safe place, so you would be able to restore your wallet in case your Secalot device gets stolen or damaged.
<br>Please note that:
<br>1. Anybody getting access to your XRP secret would have access to you wallet and everything on it.
<br>2. It is safer to store your XRP secret in a non-electronic form, for example on paper.</b>")
        Layout.maximumWidth: 400
        wrapMode: Text.WordWrap
        textFormat: Text.RichText
        Layout.fillWidth: true
    }

    TextArea {
        id: secretTextArea
        text: qsTr("")
        Layout.fillWidth: true
        wrapMode: Text.WordWrap
    }

    Button {
        id: okButton
        text: qsTr("OK")
        Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
    }
}
