import QtQuick 2.4
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.3

ColumnLayout {
    id: columnLayout
    property alias label: label
    property alias button: button
    property alias busyIndicator: busyIndicator
    spacing: 20

    BusyIndicator {
        id: busyIndicator
        Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
    }

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
        visible: false
        text: qsTr("OK")
        Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
    }
}
