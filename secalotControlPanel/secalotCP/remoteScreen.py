# Secalot utilities.
# Copyright (c) 2018 Matvey Mukha <matvey.mukha@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QSettings, QSize
from PyQt5.QtQuick import QQuickImageProvider
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtGui import QPixmap

import uuid
import os

import qrcode
from io import BytesIO

import json

class RemoteScreenException(Exception):
    def __init__(self, reason):
        super().__init__()
        self.reason = reason


class RemoteScreen(QObject):


    class QRCodeImageProvider(QQuickImageProvider):

        qrCodeImageData = None

        def __init__(self):
            super().__init__(QQuickImageProvider.Pixmap)

        def requestPixmap(self, id, size):

            pixmap = QPixmap(0, 0)

            if id == "qrCode.png" and self.qrCodeImageData != None:
                pixmap.loadFromData(self.qrCodeImageData, "PNG")
                pixmap = pixmap.scaledToHeight(300)

            return pixmap, QSize(300, 300)

    errorOccured = pyqtSignal(str, arguments=['errorMessage'])
    isMobilePhoneBindedReady = pyqtSignal(str, arguments=['mobilePhoneBinded'])
    unbindMobilePhonetReady = pyqtSignal()
    startMobilePhoneBindingReady = pyqtSignal()
    finishMobilePhoneBindingReady = pyqtSignal()


    def __init__(self, engine):

        super().__init__()

        self.qrCodeImageProvider = self.QRCodeImageProvider()

        self.guid = None
        self.key = None
        self.qrCodeImageProvider.qrCodeImageData = None

        engine.addImageProvider("qrCode", self.qrCodeImageProvider)

    @pyqtSlot()
    def isMobilePhoneBinded(self):

        try:
            settings = QSettings('Secalot', 'Secalot Control Panel')
            mobilePhoneBinded = settings.value('mobilePhoneBinded', False, bool)

            if mobilePhoneBinded == True:
                mobilePhoneBindedString = 'Yes'
            else:
                mobilePhoneBindedString = 'No'

            self.isMobilePhoneBindedReady.emit(mobilePhoneBindedString)
        except Exception as e:
            self.errorOccured.emit(self.tr("An error occurred."))


    @pyqtSlot()
    def unbindMobilePhone(self):
        try:
            settings = QSettings('Secalot', 'Secalot Control Panel')
            settings.remove('mobilePhoneBinded')
            settings.remove('removeScreenUID')
            settings.remove('removeScreenKey')

            self.unbindMobilePhonetReady.emit()

        except Exception as e:
            self.errorOccured.emit(self.tr("An error occurred."))


    @pyqtSlot()
    def startMobilePhoneBinding(self):

        try:
            self.guid = str(uuid.uuid4())
            self.key = os.urandom(32).hex()

            jsonString = json.dumps({"guid": self.guid, "key": self.key})

            image = qrcode.make(jsonString)
            output = BytesIO()
            image.save(output, 'PNG')
            self.qrCodeImageProvider.qrCodeImageData = output.getvalue()
            output.close()

            self.startMobilePhoneBindingReady.emit()

        except Exception as e:
            self.clearMobilePhoneBindingState()
            self.errorOccured.emit(self.tr("An error occurred."))


    def clearMobilePhoneBindingState(self):
        try:
            self.guid = None
            self.key = None
            self.qrCodeImageProvider.qrCodeImageData = None
        except Exception as e:
            pass

    @pyqtSlot()
    def finishMobilePhoneBinding(self):

        try:
            settings = QSettings('Secalot', 'Secalot Control Panel')

            settings.setValue('removeScreenUID', self.guid)
            settings.setValue('removeScreenKey', self.key)
            settings.setValue('mobilePhoneBinded', True)

            self.finishMobilePhoneBindingReady.emit()

        except Exception as e:
            self.cancelMobilePhoneBinding()
            self.errorOccured.emit(self.tr("An error occurred."))
        finally:
            self.clearMobilePhoneBindingState()


