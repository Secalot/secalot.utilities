import QtQuick 2.4
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.3

Item {
    id: mainItem
    property alias otpTypeValueLabel: otpTypeValueLabel
    property alias numberOfDigitsTypeLabel: numberOfDigitsTypeLabel
    property alias setNewSettingsButton: setNewSettingsButton
    property alias totpRadioButton: totpRadioButton
    property alias hotpRadioButton: hotpRadioButton
    property alias numberOfDigitsSpinBox: numberOfDigitsSpinBox
    property alias newKeyTextField: newKeyTextField

    ColumnLayout {
        id: mainColumnLayout
        anchors.left: parent.left
        anchors.leftMargin: 150
        anchors.right: parent.right
        anchors.rightMargin: 150
        spacing: 20
        anchors.verticalCenter: parent.verticalCenter

        GroupBox {
            id: currentSettingsGroupBox
            Layout.fillWidth: true
            title: qsTr("Curent settings")

            GridLayout {
                id: currentSettingsGridLayout
                anchors.fill: parent
                rows: 2
                columns: 2

                Label {
                    id: otpTypeTextLabel
                    text: qsTr("OTP type:")
                    horizontalAlignment: Text.AlignLeft
                }

                Label {
                    id: otpTypeValueLabel
                    text: qsTr("")
                    horizontalAlignment: Text.AlignHCenter
                    Layout.fillWidth: true
                }

                Label {
                    id: numberOfDigitsTextLabel
                    text: qsTr("Number of digits:")
                }

                Label {
                    id: numberOfDigitsTypeLabel
                    text: qsTr("")
                    horizontalAlignment: Text.AlignHCenter
                    Layout.fillWidth: true
                }
            }
        }

        GroupBox {
            id: newSettingsGroupBox
            Layout.fillWidth: true
            title: qsTr("Set new settings")

            GridLayout {
                id: newSettingsGridLayout
                anchors.fill: parent
                rows: 2
                columns: 2

                Label {
                    id: otpTypeTextLabel2
                    text: qsTr("OPT type:")
                }

                RowLayout {
                    id: otpTypeRowLayout
                    Layout.fillWidth: true

                    RadioButton {
                        id: totpRadioButton
                        text: qsTr("TOTP")
                        Layout.fillWidth: true
                        checked: true
                    }

                    RadioButton {
                        id: hotpRadioButton
                        text: qsTr("HOTP")
                        Layout.fillWidth: true
                    }
                }

                Label {
                    id: numberOfDigitsTextLabel2
                    text: qsTr("Number of digits:")
                }

                SpinBox {
                    id: numberOfDigitsSpinBox
                    Layout.fillWidth: true
                    to: 8
                    from: 6
                    value: 6
                }

                Label {
                    id: newKeyLabel
                    text: qsTr("New key:")
                }

                TextField {
                    id: newKeyTextField
                    text: qsTr("")
                    Layout.fillWidth: true
                }

                Label {
                    id: emptyLabel
                    text: qsTr("")
                }

                Button {
                    id: setNewSettingsButton
                    text: qsTr("Set")
                    Layout.fillWidth: true
                }
            }
        }
    }
}
