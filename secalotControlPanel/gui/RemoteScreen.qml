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

    property bool propMobilePhoneBinded: false
    property bool propSupportedDeviceConnected: false

    function setMobilePhoneBindingInfo(mobilePhoneBinded) {

        bindingStatusValueLabel.text = mobilePhoneBinded

        if(mobilePhoneBinded === 'Yes') {
            bindMobilePhoneGroupBox.enabled = false
            unbindMobilePhoneGroupBox.enabled = true
            propMobilePhoneBinded = true
        }
        else {
            if(propSupportedDeviceConnected == true) {
                bindMobilePhoneGroupBox.enabled = true
            }

            unbindMobilePhoneGroupBox.enabled = false
            propMobilePhoneBinded = false
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

        bindMobilePhoneGroupBox.enabled = false
        propSupportedDeviceConnected = false
        clearFingerprint()
    }

    function supportedDeviceConnected() {
        propSupportedDeviceConnected = true

        if(propMobilePhoneBinded == false) {
            bindMobilePhoneGroupBox.enabled = true
        }
    }

    function clearFingerprint() {
        fingerprintValueLabel.text = ""
    }

    function setFingerprint(fingerprint) {
        fingerprintValueLabel.text = fingerprint
    }

}
