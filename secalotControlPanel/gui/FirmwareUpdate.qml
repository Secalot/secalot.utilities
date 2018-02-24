import QtQuick 2.4
import QtQuick.Dialogs 1.0

FirmwareUpdateForm {



    property var selectFirmwareImageFile: ""

    FileDialog {
        id: fileDialog
        title: "Please select a firmware image"
        folder: shortcuts.home
        nameFilters: "*.bin"
        visible: false
        onAccepted: {
            firmwareImageInfoRequested(getPath())
        }

        function getPath() {
            var path = fileUrl.toString()
            return path
        }
    }

    FirmwareUpdatePopup {
        id: firmwareUpdatePopup
    }

    function setPopupMessage(message) {
        firmwareUpdatePopup.setFirmwareUpdateMessageText(message)
    }

    function closePopup() {
        firmwareUpdatePopup.close()
    }

    function setDeviceInfo(deviceID, serialNumber, firmwareVersion, fileSystemVersion, bootloaderVersion) {

        deviceIDValueLabel.text = deviceID
        serialNumberValueLabel.text = serialNumber
        firmwareVersionValueLabel.text = firmwareVersion
        fileSystemValueLabel.text = fileSystemVersion
        bootloaderVersionValueLabel.text = bootloaderVersion
    }

    function resetGUI() {
        clearDeviceInfo()
    }

    function clearDeviceInfo() {

        deviceIDValueLabel.text = ""
        serialNumberValueLabel.text = ""
        firmwareVersionValueLabel.text = ""
        fileSystemValueLabel.text = ""
        bootloaderVersionValueLabel.text = ""
    }

    function setFirmwareImageInfo(deviceID, firmwareVersion, fileSystemVersion, bootloaderVersion) {
        deviceIDValueLabel2.text = deviceID
        firmwareVersionValueLabel2.text = firmwareVersion
        fileSystemValueLabel2.text = fileSystemVersion
        bootloaderVersionValueLabel2.text = bootloaderVersion
        selectFirmwareImageFile = fileDialog.getPath()
    }

    function clearFirmwareImageInfo() {
        deviceIDValueLabel2.text = ""
        firmwareVersionValueLabel2.text = ""
        fileSystemValueLabel2.text = ""
        bootloaderVersionValueLabel2.text = ""
        selectFirmwareImageFile = ""
    }

    function updateFinished() {
        firmwareUpdatePopup.setFirmwareUpdateMessageText(qsTr("Update finished."))
        firmwareUpdatePopup.showDoneButton()
    }

    signal updateRequested(string fileName, bool cleanFileSystemRequested)
    signal firmwareImageInfoRequested(string fileName)

    selectFirmwareImageButton.onClicked: {
        clearFirmwareImageInfo()
        fileDialog.open()
    }

    flashFirmwareButton.onClicked: {

        if(selectFirmwareImageFile === "") {
            mainWindow.openSimplePopup(qsTr("Please select an update image file."))
        }
        else {
            firmwareUpdatePopup.hideDoneButton()
            firmwareUpdatePopup.setFirmwareUpdateMessageText("")
            updateRequested(selectFirmwareImageFile, eraseFSCheckBox.checked)
            firmwareUpdatePopup.open()
        }
    }

}
