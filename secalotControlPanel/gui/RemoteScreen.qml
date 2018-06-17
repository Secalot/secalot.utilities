import QtQuick 2.4

RemoteScreenForm {

    BindingMessagePopup {
        id: bindingMessagePopup
    }

    Connections {
        target: bindingMessagePopup

        onFinishButtonClicked: {
            mobilePhoneBindingFinished()
        }
    }

    signal mobilePhoneBindingStarted()
    signal mobilePhoneBindingFinished()
    signal mobilePhoneUnbind()

    function setRemoteScreenInfo(mobilePhoneBinded) {

        bindingStatusValueLabel.text = mobilePhoneBinded

        if(mobilePhoneBinded === 'Yes') {
            bindMobilePhoneGroupBox.enabled = false
            unbindMobilePhoneGroupBox.enabled = true
        }
        else {
            bindMobilePhoneGroupBox.enabled = true
            unbindMobilePhoneGroupBox.enabled = false
        }
    }

    function displayBindingInfo() {

        bindingMessagePopup.refreshImage()
        bindingMessagePopup.open()
    }

    bindMobilePhoneButton.onClicked: {

        mobilePhoneBindingStarted()
    }

    unbindMobilePhoneButton.onClicked: {

        mobilePhoneUnbind()
    }

    function resetGUI() {
        clearFingerprint()
    }

    function clearFingerprint() {
        fingerprintValueLabel.text = ""
    }

    function setFingerprint(fingerprint) {
        fingerprintValueLabel.text = fingerprint
    }

}
