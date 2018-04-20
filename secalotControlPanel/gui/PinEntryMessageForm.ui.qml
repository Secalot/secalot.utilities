import QtQuick 2.4
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.3

ColumnLayout {
    id: columnLayout

    property alias cancelButton: cancelButton
    property alias newPinTextField: newPinTextField
    property alias repeatPinTextField: repeatPinTextField
    property alias createButton: createButton
    spacing: 20

    GroupBox {
        id: newPinGroupBox
        Layout.fillWidth: true
        title: qsTr("Enter a new PIN-code")

        ColumnLayout {
            id: newPinColumnLayout
            anchors.fill: parent

            Label {
                id: newPinLabel
                text: qsTr("New PIN-code:")
            }

            TextField {
                id: newPinTextField
                text: qsTr("")
                echoMode: TextInput.PasswordEchoOnEdit
                Layout.minimumWidth: 300
                Layout.fillWidth: true
            }

            Label {
                id: repeatPinLabel
                text: qsTr("Repeat new PIN-code:")
            }

            TextField {
                id: repeatPinTextField
                text: qsTr("")
                echoMode: TextInput.PasswordEchoOnEdit
                Layout.fillWidth: true
            }
        }
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
            id: createButton
            text: qsTr("Create wallet")
        }
    }
}
