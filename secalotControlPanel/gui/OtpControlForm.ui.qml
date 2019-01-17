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
    property alias genKeyButton: genKeyButton
    property alias genKeyLengthSpinBox: genKeyLengthSpinBox
    property alias genKeyFormatComboBox: genKeyFormatComboBox

    ColumnLayout {
        id: mainColumnLayout
        anchors.left: parent.left
        anchors.leftMargin: 170
        anchors.right: parent.right
        anchors.rightMargin: 170
        spacing: 20
        anchors.verticalCenter: parent.verticalCenter

        GroupBox {
            id: currentSettingsGroupBox
            Layout.fillWidth: true
            title: qsTr("Current settings")

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

            ColumnLayout {
                id: newSettingsColumnLayout
                anchors.fill: parent
                Layout.fillWidth: true

                GridLayout {
                    id: newSettingsGridLayout
                    rows: 3
                    columns: 2

                    Label {
                        id: otpTypeTextLabel2
                        text: qsTr("OTP type:")
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
                }

                Button {
                    id: setNewSettingsButton

                    text: qsTr("Set")
                    Layout.fillWidth: true
                }
            }
        }

        GroupBox {
            id: genKeyGroupBox
            Layout.fillWidth: true
            title: qsTr("Generate a key")

            GridLayout {
                id: genKeyGridLayout
                anchors.fill: parent
                rows: 2
                columns: 2

                Label {
                    id: genKeyFormatLabel
                    text: qsTr("Format:")
                }

                ComboBox {
                    id: genKeyFormatComboBox
                    model: ["Hexadecimal", "Base32"]
                    currentIndex: 0
                    Layout.fillWidth: true
                }

                Label {
                    id: genKeyLengthLabel
                    text: qsTr("Length:")
                }

                SpinBox {
                    id: genKeyLengthSpinBox
                    Layout.fillWidth: true
                    to: 32
                    from: 10
                    value: 20
                }

                Label {
                    id: genKeyEmptyLabel
                    text: qsTr("")
                }

                Button {
                    id: genKeyButton

                    text: qsTr("Generate")
                    Layout.fillWidth: true
                }
            }
        }
    }
}
