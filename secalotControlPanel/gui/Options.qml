import QtQuick 2.4

OptionsForm {

    function setCheckboxState(state) {
        checkBox.checked = state
    }

    signal checkBoxClicked(bool state)

    checkBox.onClicked: {
        checkBoxClicked(checkBox.checked)
    }

}
