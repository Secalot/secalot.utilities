import QtQuick 2.4
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.3

Item {
    id: mainItem
    property alias appVersionValueLabel: appVersionValueLabel
    property alias walletStatusValueLabel: walletStatusValueLabel
    property alias wipeoutWalletButton: wipeoutWalletButton
    property alias createWalletGroupBox: createWalletGroupBox
    property alias restoreWalletGroupBox: restoreWalletGroupBox
    property alias wipeoutWalletGroupBox: wipeoutWalletGroupBox
    property alias restoreWalletButton: restoreWalletButton
    property alias createWalletButton: createWalletButton

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
            title: "Wallet info"
            Layout.fillWidth: true

            GridLayout {
                id: deviceInfoGridLayout
                anchors.fill: parent
                rows: 3
                columns: 2

                Label {
                    id: appVersionTextLabel
                    text: qsTr("App version:")
                }

                Label {
                    id: appVersionValueLabel
                    text: qsTr("")
                    horizontalAlignment: Text.AlignHCenter
                    Layout.fillWidth: true
                }

                Label {
                    id: walletStatusTextLabel
                    text: qsTr("Wallet status:")
                }

                Label {
                    id: walletStatusValueLabel
                    text: qsTr("")
                    horizontalAlignment: Text.AlignHCenter
                    Layout.fillWidth: true
                }
            }
        }

        GroupBox {
            id: createWalletGroupBox
            title: "Create wallet"
            Layout.fillWidth: true

            enabled: false

            ColumnLayout {
                id: createWalletColumnLayout
                anchors.fill: parent

                Button {
                    id: createWalletButton
                    text: qsTr("Create wallet")
                    Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                    Layout.fillWidth: true
                }
            }
        }

        GroupBox {
            id: restoreWalletGroupBox
            title: "Restore wallet"
            Layout.fillWidth: true

            enabled: false

            ColumnLayout {
                id: restoreWalletColumnLayout
                anchors.fill: parent

                Button {
                    id: restoreWalletButton
                    text: qsTr("Restore wallet")
                    Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                    Layout.fillWidth: true
                }
            }
        }

        GroupBox {
            id: wipeoutWalletGroupBox
            title: "Delete wallet"
            Layout.fillWidth: true

            enabled: false

            ColumnLayout {
                id: wipeoutWalletColumnLayout
                anchors.fill: parent

                Button {
                    id: wipeoutWalletButton
                    text: qsTr("Delete wallet")
                    Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                    Layout.fillWidth: true
                }
            }
        }
    }
}
