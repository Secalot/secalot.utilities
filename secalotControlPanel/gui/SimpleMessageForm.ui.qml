import QtQuick 2.4
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.3

ColumnLayout {
    id: columnLayout
    property alias button: button
    property alias label: label
    spacing: 20

    Label {
        id: label
        text: qsTr("")
        font.pointSize: 14
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
    }

    Button {
        id: button
        text: qsTr("OK")
        Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
    }
}
