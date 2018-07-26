import QtQuick 2.4
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.3

Item {
    id: mainItem
    property alias fingerprintValueLabel: fingerprintValueLabel
    property alias bindingStatusValueLabel: bindingStatusValueLabel
    property alias bindMobilePhoneButton: bindMobilePhoneButton
    property alias unbindMobilePhoneButton: unbindMobilePhoneButton
    property alias bindMobilePhoneGroupBox: bindMobilePhoneGroupBox
    property alias unbindMobilePhoneGroupBox: unbindMobilePhoneGroupBox

    ColumnLayout {
        id: mainColumnLayout
        anchors.right: parent.right
        anchors.rightMargin: 150
        anchors.left: parent.left
        anchors.leftMargin: 150
        anchors.verticalCenter: parent.verticalCenter
        spacing: 20

        GroupBox {
            id: remoteScreenInfoGroupBox
            title: "Remote screen info"
            Layout.fillWidth: true

            GridLayout {
                id: remoteScreenInfoGridLayout
                anchors.fill: parent
                rows: 2
                columns: 2

                Label {
                    id: bindingStatusTextLabel
                    text: qsTr("Mobile phone bound:")
                }

                Label {
                    id: bindingStatusValueLabel
                    text: qsTr("")
                    horizontalAlignment: Text.AlignHCenter
                    Layout.fillWidth: true
                }

                Label {
                    id: fingerprintTextLabel
                    text: qsTr("Device fingerprint:")
                }

                Label {
                    id: fingerprintValueLabel
                    text: qsTr("")
                    horizontalAlignment: Text.AlignHCenter
                    Layout.fillWidth: true
                }
            }
        }

        GroupBox {
            id: bindMobilePhoneGroupBox
            title: "Bind mobile phone"
            Layout.fillWidth: true

            enabled: false

            ColumnLayout {
                id: bindMobilePhoneColumnLayout
                anchors.fill: parent

                Button {
                    id: bindMobilePhoneButton
                    text: qsTr("Bind mobile phone")
                    Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                    Layout.fillWidth: true
                }
            }
        }

        GroupBox {
            id: unbindMobilePhoneGroupBox
            title: "Unbind mobile phone"
            Layout.fillWidth: true

            enabled: false

            ColumnLayout {
                id: unbindMobilePhoneColumnLayout
                anchors.fill: parent

                Button {
                    id: unbindMobilePhoneButton
                    text: qsTr("Unbind mobile phone")
                    Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                    Layout.fillWidth: true
                }
            }
        }
    }
}

