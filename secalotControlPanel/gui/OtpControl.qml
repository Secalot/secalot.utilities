import QtQuick 2.4

OtpControlForm {

    function setCurrentOTPSettings(numberOfDigits, type) {
        numberOfDigitsTypeLabel.text = numberOfDigits
        otpTypeValueLabel.text = type
    }

    function resetGUI() {
        clearCurrentOTPSettings()
    }

    function clearCurrentOTPSettings() {
        numberOfDigitsTypeLabel.text = ""
        otpTypeValueLabel.text = ""
    }

    function setKey(key) {
        newKeyTextField.text = key
    }

    signal setOtpSettingsRequested(string numberOfDigits, string type, string key)
    signal generateNewKeyRequested(string keyFormat, string keyLength)

    setNewSettingsButton.onClicked: {

        var numberOfDigits
        var type
        var key

        numberOfDigits = numberOfDigitsSpinBox.value

        if(totpRadioButton.checked === true) {
            type = "TOTP"
        }
        else {
            type = "HOTP"
        }

        key = newKeyTextField.text

        setOtpSettingsRequested(numberOfDigits, type, key)
    }

    genKeyButton.onClicked: {

        var keyFormat
        var keyLength

        keyFormat = genKeyFormatComboBox.currentText
        keyLength = genKeyLengthSpinBox.value

        if(keyFormat === 'Hexadecimal') {
            keyFormat = 'hex'
        }
        else {
            keyFormat = 'base32'
        }

        generateNewKeyRequested(keyFormat, keyLength)
    }
}
