import QtQuick 2.4
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.3

Item {
    id: item1
    property alias checkBox: checkBox

    ColumnLayout {
        id: columnLayout
        spacing: 20
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter

        GroupBox {
            id: groupBox
            Layout.fillWidth: true
            title: qsTr("Options")

            CheckBox {
                id: checkBox
                text: qsTr("Enable TOTP service")
                checked: true
            }
        }
    }
}
