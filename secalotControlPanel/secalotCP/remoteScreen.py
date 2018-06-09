# Secalot utilities.
# Copyright (c) 2018 Matvey Mukha <matvey.mukha@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QSettings, QSize
from PyQt5.QtQuick import QQuickImageProvider
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QTcpServer, QTcpSocket, QHostAddress, QSslConfiguration, QSslCipher, QSslSocket, QSslError, QSslPreSharedKeyAuthenticator

import uuid
import os

import qrcode
from io import BytesIO

import json
import base64

from zeroconf import ServiceInfo, Zeroconf, DNSQuestion, _TYPE_PTR, _TYPE_ANY


class RemoteScreenException(Exception):
    def __init__(self, reason):
        super().__init__()
        self.reason = reason


class RemoteScreen(QObject):

    SERVER_PORT = 19380

    class QSslServer(QTcpServer):

        sslErrors = pyqtSignal([])
        peerVerifyError = pyqtSignal(QSslError)
        newEncryptedConnection = pyqtSignal()
        preSharedKeyAuthenticationRequired = pyqtSignal('QSslPreSharedKeyAuthenticator*')

        def __init__(self, parent):
            super().__init__(parent)
            self.m_sslConfiguration = QSslConfiguration.defaultConfiguration()

        def setSslConfiguration(self, sslConfiguration):
            self.m_sslConfiguration = sslConfiguration

        def sslConfiguration(self):
            return self.m_sslConfiguration

        def nextPendingConnection(self):
            return super().nextPendingConnection()

        def incomingConnection(self, socket):
            pSslSocket = QSslSocket(self)

            pSslSocket.setSslConfiguration(self.m_sslConfiguration)

            if pSslSocket.setSocketDescriptor(socket):
                pSslSocket.peerVerifyError.connect(self.peerVerifyError)
                pSslSocket.sslErrors.connect(self.sslErrors)
                pSslSocket.encrypted.connect(self.newEncryptedConnection)
                pSslSocket.preSharedKeyAuthenticationRequired.connect(self.preSharedKeyAuthenticationRequired)

                self.addPendingConnection(pSslSocket);

                pSslSocket.startServerEncryption()


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

    class ZeroConfServer(Zeroconf):

        def handle_query(self, msg, addr, port):
            for question in msg.questions:
                if question.type == _TYPE_PTR:
                    for service in self.services.values():
                        if question.name == service.type:
                            new_question = DNSQuestion(service.name, _TYPE_ANY, question.class_)
                            msg.questions.append(new_question)

            super(RemoteScreen.ZeroConfServer, self).handle_query(msg, addr, port)

    errorOccured = pyqtSignal(str, arguments=['errorMessage'])
    isMobilePhoneBindedReady = pyqtSignal(str, arguments=['mobilePhoneBinded'])
    unbindMobilePhonetReady = pyqtSignal()
    startMobilePhoneBindingReady = pyqtSignal()
    finishMobilePhoneBindingReady = pyqtSignal()
    startServerReady = pyqtSignal()
    stopServerReady = pyqtSignal()
    startZeroConfReady = pyqtSignal()
    stopZeroConfReady = pyqtSignal()

    sendRemoteScreenCommand = pyqtSignal(bytes)

    def __init__(self, engine, deviceCommunicator):

        super().__init__()

        self.qrCodeImageProvider = self.QRCodeImageProvider()

        self.guid = None
        self.key = None
        self.qrCodeImageProvider.qrCodeImageData = None

        self.server = None

        self.zeroConf = None
        self.zeroConfInfo = None

        self.connection = None

        engine.addImageProvider("qrCode", self.qrCodeImageProvider)

        self.deviceCommunicator = deviceCommunicator

        self.deviceCommunicator.remoteScreenErrorOccured.connect(self.remoteScreenErrorOccured)
        self.deviceCommunicator.remoteScreenCommandSent.connect(self.remoteScreenCommandSent)

        self.sendRemoteScreenCommand.connect(deviceCommunicator.sendRemoteScreenCommand)

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
            self.errorOccured.emit(self.tr("A RemoteScreen error occurred."))


    @pyqtSlot()
    def unbindMobilePhone(self):
        try:
            settings = QSettings('Secalot', 'Secalot Control Panel')
            settings.remove('mobilePhoneBinded')
            settings.remove('removeScreenUID')
            settings.remove('removeScreenKey')

            self.unbindMobilePhonetReady.emit()

        except Exception as e:
            self.errorOccured.emit(self.tr("A RemoteScreen error occurred."))


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
            self.errorOccured.emit(self.tr("A RemoteScreen error occurred."))


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
            self.errorOccured.emit(self.tr("A RemoteScreen error occurred."))
        finally:
            self.clearMobilePhoneBindingState()


    @pyqtSlot()
    def startZeroConf(self):

        try:

            settings = QSettings('Secalot', 'Secalot Control Panel')
            guid = settings.value('removeScreenUID', '', str)

            self.zeroConfInfo = ServiceInfo('_secalot._tcp.local.',
                               guid + '._secalot._tcp.local.',
                               None, self.SERVER_PORT, 0, 0,
                               {'version': '1'}, "secalot")

            self.zeroConf = self.ZeroConfServer()

            self.zeroConf.register_service(self.zeroConfInfo)

            self.startZeroConfReady.emit()

        except Exception as e:
            self.errorOccured.emit(self.tr("A RemoteScreen error occurred."))


    @pyqtSlot()
    def stopZeroConf(self):

        try:

            if self.zeroConf != None:
                self.zeroConf.unregister_service(self.zeroConfInfo)
                self.zeroConf.close()
                self.zeroConf = None

            self.stopZeroConfReady.emit()

        except Exception as e:
            self.errorOccured.emit(self.tr("A RemoteScreen error occurred."))


    @pyqtSlot()
    def startServer(self):

        try:

            self.server = self.QSslServer(self)

            config = self.server.sslConfiguration()
            config.setPreSharedKeyIdentityHint("RemoteScreen".encode('utf-8'))
            cipher = QSslCipher("PSK-AES256-CBC-SHA")
            config.setCiphers([cipher])
            self.server.setSslConfiguration(config)

            self.server.newEncryptedConnection.connect(self.handleConnection)
            self.server.preSharedKeyAuthenticationRequired.connect(self.preSharedKeyAuthenticationRequired)

            if not self.server.listen(QHostAddress(QHostAddress.Any), self.SERVER_PORT):
                raise RemoteScreenException("Can not start RemoteScreen server")

            self.startServerReady.emit()

        except RemoteScreenException as e:
            self.errorOccured.emit(e.reason)
        except Exception as e:
            self.errorOccured.emit(self.tr("A RemoteScreen error occurred."))


    @pyqtSlot()
    def stopServer(self):

        try:

            if self.connection != None:
                self.connection.disconnectFromHost()
                self.connection = None

            if self.server != None:
                self.server.close()
                self.server = None

            self.stopServerReady.emit()

        except Exception as e:
            self.errorOccured.emit(self.tr("A RemoteScreen error occurred."))


    @pyqtSlot()
    def handleConnection(self):
        try:
            if self.connection != None:
                self.connection.disconnectFromHost()
                self.connection.readyRead.disconnect(self.dataReceived)
                self.connection = None

            self.connection = self.server.nextPendingConnection()

            self.connection.readyRead.connect(self.dataReceived)

        except Exception as e:
            self.errorOccured.emit(self.tr("A RemoteScreen error occurred."))


    @pyqtSlot('QSslPreSharedKeyAuthenticator*')
    def preSharedKeyAuthenticationRequired(self, authenticator):
        try:
            settings = QSettings('Secalot', 'Secalot Control Panel')
            key = settings.value('removeScreenKey', '', str)
            key = bytearray.fromhex(key)
            authenticator.setPreSharedKey(key)

        except Exception as e:
            self.errorOccured.emit(self.tr("A RemoteScreen error occurred."))

    @pyqtSlot()
    def dataReceived(self):
        try:
            while self.connection.canReadLine() == True:
                command = (bytes)(self.connection.readLine())
                self.processCommand(command)
        except Exception as e:
            self.errorOccured.emit(self.tr("A RemoteScreen error occurred."))

    def processCommand(self, command):

        command = json.loads(command)

        if command["command"] == "Ping":
            response = {"response": "Pong", "arguments": []}
            response = json.dumps(response) + '\n'
            response = response.encode('utf-8')
            self.connection.write(response)
        elif command["command"] == "SendAPDU":
            if( len(command["arguments"]) != 1):
                raise RemoteScreenException("Invalid RemoteScreen command received")
            apdu = base64.b64decode(command["arguments"][0])
            self.sendRemoteScreenCommand.emit(apdu)
        else:
            raise RemoteScreenException("Invalid RemoteScreen command received")

    @pyqtSlot(str)
    def remoteScreenErrorOccured(self, errorMessage):
        response = {"response": "Error", "arguments": [errorMessage]}
        response = json.dumps(response) + '\n'
        response = response.encode('utf-8')
        self.connection.write(response)


    @pyqtSlot(bytes)
    def remoteScreenCommandSent(self, response):
        response = {"response": "SendAPDU", "arguments": [base64.b64encode(response).decode('utf8')]}
        try:
            response = json.dumps(response) + '\n'
        except Exception as e:
            pass
        response = response.encode('utf-8')
        self.connection.write(response)






