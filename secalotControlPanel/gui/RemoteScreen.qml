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

    property bool propMobilePhoneBound: false
    property bool propSupportedDeviceConnected: false

    function setMobilePhoneBindingInfo(mobilePhoneBound) {

        bindingStatusValueLabel.text = mobilePhoneBound

        if(mobilePhoneBound === 'Yes') {
            bindMobilePhoneGroupBox.enabled = false
            unbindMobilePhoneGroupBox.enabled = true
            propMobilePhoneBound = true
        }
        else {
            if(propSupportedDeviceConnected == true) {
                bindMobilePhoneGroupBox.enabled = true
            }

            unbindMobilePhoneGroupBox.enabled = false
            propMobilePhoneBound = false
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

        if(propMobilePhoneBound == false) {
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
