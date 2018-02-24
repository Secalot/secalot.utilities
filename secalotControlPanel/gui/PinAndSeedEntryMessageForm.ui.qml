import QtQuick 2.4
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.3

ColumnLayout {
    id: columnLayout

    property alias seedTextArea: seedTextArea
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
                Layout.fillWidth: true
            }
        }
    }

    GroupBox {
        id: seedGroupBox
        Layout.fillWidth: true
        title: qsTr("Enter your wallet's seed")

        ColumnLayout {
            id: seedColumnLayout
            anchors.fill: parent

            TextArea {
                id: seedTextArea
                Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                Layout.fillWidth: true
                text: qsTr("")
                wrapMode: Text.WordWrap
                Layout.minimumHeight: 100
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
