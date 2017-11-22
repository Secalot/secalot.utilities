import QtQuick 2.4
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.3

Item {
    id: mainItem
    property alias fileSystemValueLabel: fileSystemValueLabel
    property alias firmwareVersionValueLabel: firmwareVersionValueLabel
    property alias deviceIDValueLabel: deviceIDValueLabel
    property alias bootloaderVersionValueLabel: bootloaderVersionValueLabel
    property alias deviceIDValueLabel2: deviceIDValueLabel2
    property alias firmwareVersionValueLabel2: firmwareVersionValueLabel2
    property alias fileSystemValueLabel2: fileSystemValueLabel2
    property alias bootloaderVersionValueLabel2: bootloaderVersionValueLabel2
    property alias eraseFSCheckBox: eraseFSCheckBox
    property alias selectFirmwareImageButton: selectFirmwareImageButton
    property alias flashFirmwareButton: flashFirmwareButton
    property alias serialNumberValueLabel: serialNumberValueLabel

    ColumnLayout {
        id: mainColumnLayout
        anchors.right: parent.right
        anchors.rightMargin: 150
        anchors.left: parent.left
        anchors.leftMargin: 150
        anchors.verticalCenter: parent.verticalCenter
        spacing: 20

        GroupBox {
            id: deviceInfoGroupBox
            title: "Device info"
            Layout.fillWidth: true

            GridLayout {
                id: deviceInfoGridLayout
                anchors.fill: parent
                rows: 5
                columns: 2

                Label {
                    id: deviceIDTextLabel
                    text: qsTr("Device ID:")
                }

                Label {
                    id: deviceIDValueLabel
                    text: qsTr("")
                    horizontalAlignment: Text.AlignHCenter
                    Layout.fillWidth: true
                }

                Label {
                    id: serialNumberTextLabel
                    text: qsTr("Serial number:")
                }

                Label {
                    id: serialNumberValueLabel
                    text: qsTr("")
                    horizontalAlignment: Text.AlignHCenter
                    Layout.fillWidth: true
                }

                Label {
                    id: firmwareVersionTextLabel
                    text: qsTr("Firmware version:")
                }

                Label {
                    id: firmwareVersionValueLabel
                    text: qsTr("")
                    horizontalAlignment: Text.AlignHCenter
                    Layout.fillWidth: true
                }

                Label {
                    id: fileSystemTextLabel
                    text: qsTr("File system version:")
                }

                Label {
                    id: fileSystemValueLabel
                    text: qsTr("")
                    horizontalAlignment: Text.AlignHCenter
                    Layout.fillWidth: true
                }

                Label {
                    id: bootloaderVersionTextLabel
                    text: qsTr("Bootloader version:")
                }

                Label {
                    id: bootloaderVersionValueLabel
                    text: qsTr("")
                    horizontalAlignment: Text.AlignHCenter
                    Layout.fillWidth: true
                }
            }
        }

        GroupBox {
            id: updateFirmwareGroupBox
            Layout.fillWidth: true
            title: qsTr("Update firmware")

            ColumnLayout {
                id: updateFirmwareColumnLayout
                anchors.fill: parent

                GroupBox {
                    id: firmwareImageInfoGroupBox
                    Layout.fillWidth: true
                    title: qsTr("Firmware image info")

                    GridLayout {
                        id: firmwareImageInfoGridLayout
                        anchors.fill: parent
                        rows: 4
                        columns: 2

                        Label {
                            id: deviceIDTextLabel2
                            text: qsTr("Device ID:")
                        }

                        Label {
                            id: deviceIDValueLabel2
                            text: qsTr("")
                            horizontalAlignment: Text.AlignHCenter
                            Layout.fillWidth: true
                        }

                        Label {
                            id: firmwareVersionTextLabel2
                            text: qsTr("Firmware version:")
                        }

                        Label {
                            id: firmwareVersionValueLabel2
                            text: qsTr("")
                            horizontalAlignment: Text.AlignHCenter
                            Layout.fillWidth: true
                        }

                        Label {
                            id: fileSystemTextLabel2
                            text: qsTr("File system version:")
                        }

                        Label {
                            id: fileSystemValueLabel2
                            text: qsTr("")
                            horizontalAlignment: Text.AlignHCenter
                            Layout.fillWidth: true
                        }

                        Label {
                            id: bootloaderVersionTextLabel2
                            text: qsTr("Bootloader version:")
                        }

                        Label {
                            id: bootloaderVersionValueLabel2
                            text: qsTr("")
                            horizontalAlignment: Text.AlignHCenter
                            Layout.fillWidth: true
                        }
                    }
                }

                Frame {
                    id: eraseFSFrame
                    Layout.fillWidth: true

                    CheckBox {
                        id: eraseFSCheckBox
                        text: qsTr("Erase file system")
                        Layout.fillWidth: true
                    }
                }

                Button {
                    id: selectFirmwareImageButton
                    text: qsTr("Select firmware image")
                    Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                    Layout.fillWidth: true
                }

                Button {
                    id: flashFirmwareButton
                    text: qsTr("Flash new firmware")
                    Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                    Layout.fillWidth: true
                }
            }
        }
    }
}
