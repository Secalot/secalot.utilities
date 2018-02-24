import QtQuick 2.4
import QtQuick.Dialogs 1.1

EthereumWalletForm {

    YesNoMessagePopup {
        id: yesNoMessagePopup
    }

    PinAndSeedEntryMessagePopup {
        id: pinAndSeedEntryMessagePopup
    }

    PinEntryMessagePopup {
        id: pinEntryMessagePopup
    }

    DisplaySeedMessagePopup {
        id: displaySeedMessagePopup
    }

    Connections {
        target: yesNoMessagePopup

        onYesButtonClicked: {
            wipeoutRequested()
        }
    }

    Connections {
        target: pinAndSeedEntryMessagePopup

        onRestoreButtonClicked: {
            var enteredData = pinAndSeedEntryMessagePopup.getEnteredData()
            restoreRequested(enteredData.seed, enteredData.newPin, enteredData.repeatPin)
        }
    }

    Connections {
        target: pinEntryMessagePopup

        onCreateButtonClicked: {
            var enteredData = pinEntryMessagePopup.getEnteredData()
            createRequested(enteredData.newPin, enteredData.repeatPin)
        }
    }

    function closePinAndSeedEntryMessagePopup() {
        pinAndSeedEntryMessagePopup.close()
    }

    function closePinEntryMessagePopup() {
        pinEntryMessagePopup.close()
    }

    function displaySeed(seed) {

        displaySeedMessagePopup.setSeed(seed)
        displaySeedMessagePopup.open()
    }

    function setWalletInfo(appVersion, walletInitialized, pinVerified) {

        if(appVersion == '0.0') {
            createWalletGroupBox.enabled = false
            restoreWalletGroupBox.enabled = false
            wipeoutWalletGroupBox.enabled = false

            appVersionValueLabel.text = qsTr('Not present')
            walletStatusValueLabel.text = qsTr('Unknown')
        }
        else {
            appVersionValueLabel.text = appVersion
            walletStatusValueLabel.text = walletInitialized

            if(walletInitialized === qsTr("initialized")) {
                createWalletGroupBox.enabled = false
                restoreWalletGroupBox.enabled = false
                wipeoutWalletGroupBox.enabled = true
            }
            else {
                createWalletGroupBox.enabled = true
                restoreWalletGroupBox.enabled = true
                wipeoutWalletGroupBox.enabled = false
            }
        }
    }

    function clearDeviceInfo() {

        appVersionValueLabel.text = ""
        walletStatusValueLabel.text = ""

        createWalletGroupBox.enabled = false
        restoreWalletGroupBox.enabled = false
        wipeoutWalletGroupBox.enabled = false
    }

    function resetGUI() {
        clearDeviceInfo()
        yesNoMessagePopup.close()
        pinAndSeedEntryMessagePopup.close()
        pinEntryMessagePopup.close()
    }

    signal wipeoutRequested()
    signal restoreRequested(string seed, string newPin, string repeatPin)
    signal createRequested(string newPin, string repeatPin)

    wipeoutWalletButton.onClicked: {

        yesNoMessagePopup.setYesNoMessageText(qsTr("Are you sure you want to delete your wallet?"))
        yesNoMessagePopup.open()
    }

    restoreWalletButton.onClicked: {

        pinAndSeedEntryMessagePopup.clearAll()
        pinAndSeedEntryMessagePopup.open()
    }

    createWalletButton.onClicked: {

        pinEntryMessagePopup.clearAll()
        pinEntryMessagePopup.open()
    }

}
