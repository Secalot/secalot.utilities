import QtQuick 2.4

OtpControlForm {

    function setCurrentOTPSettings(numberOfDigits, type) {
        numberOfDigitsTypeLabel.text = numberOfDigits
        otpTypeValueLabel.text = type
    }

    function clearCurrentOTPSettings() {
        numberOfDigitsTypeLabel.text = ""
        otpTypeValueLabel.text = ""
    }

    signal setOtpSettingsRequested(string numberOfDigits, string type, string key)

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
}
