import QtQuick 2.4
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.3

ColumnLayout {
    id: columnLayout
    property alias yesButton: yesButton
    property alias noButton: noButton
    property alias label: label
    spacing: 20

    Label {
        id: label
        text: qsTr("")
        Layout.fillWidth: true
    }

    RowLayout {
        id: rowLayout
        Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
        Layout.fillWidth: true

        Button {
            id: yesButton
            text: qsTr("Yes")
        }

        Button {
            id: noButton
            text: qsTr("No")
        }
    }
}
