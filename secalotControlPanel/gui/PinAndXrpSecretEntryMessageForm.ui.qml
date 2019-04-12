import QtQuick 2.4
import QtQuick.Controls 2.4
import QtQuick.Layouts 1.11

ColumnLayout {
    id: columnLayout

    property alias secretTextArea: secretTextArea
    property alias cancelButton: cancelButton
    property alias restoreButton: restoreButton
    property alias newPinTextField: newPinTextField
    property alias repeatPinTextField: repeatPinTextField
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

    GroupBox {
        id: secretGroupBox
        Layout.fillWidth: true
        title: qsTr("Enter secret of your XRP wallet")

        ColumnLayout {
            id: secretColumnLayout
            anchors.fill: parent

            Item {
                id: item1
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                Layout.fillWidth: true
                Layout.minimumHeight: 100
                Layout.maximumHeight: 100

                ScrollView {
                    id: scrollView
                    anchors.fill: parent

                    clip: true
                    TextArea {
                        id: secretTextArea
                        wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                        clip: true
                    }
                }
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
            id: restoreButton
            text: qsTr("Restore wallet")
        }
    }
}
