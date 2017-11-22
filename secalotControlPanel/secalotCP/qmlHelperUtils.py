# Secalot utilities.
# Copyright (c) 2017 Matvey Mukha <matvey.mukha@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QSettings

class QmlHelperUtilsException(Exception):
    def __init__(self, reason):
        super().__init__()
        self.reason = reason


class QmlHelperUtils(QObject):
    currentSettingsReady = pyqtSignal(bool, arguments=['sendCurrentTimeToDevice'])

    def __init__(self):
        super().__init__()

    @pyqtSlot()
    def getCurrentSettings(self):
        settings = QSettings('Secalot', 'Secalot Control Panel')
        sendCurrentTimeToDevice = settings.value('sendCurrentTimeToDevice', True, bool)
        self.currentSettingsReady.emit(sendCurrentTimeToDevice)

    @pyqtSlot(bool)
    def setCurrentSettings(self, sendCurrentTimeToDevice):
        settings = QSettings('Secalot', 'Secalot Control Panel')
        settings.setValue('sendCurrentTimeToDevice', sendCurrentTimeToDevice)
        del settings
