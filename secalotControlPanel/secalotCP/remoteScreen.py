# Secalot utilities.
# Copyright (c) 2018 Matvey Mukha <matvey.mukha@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QSettings, QSize, QThread, QCoreApplication, QMetaObject, Q_ARG
from PyQt5.QtQuick import QQuickImageProvider
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QTcpServer, QTcpSocket, QHostAddress

import uuid
import os

import qrcode
from io import BytesIO

import json
import base64

from zeroconf import ServiceInfo, Zeroconf, DNSQuestion, _TYPE_PTR, _TYPE_ANY

import socket
from tlslite import *


class RemoteScreenException(Exception):
    def __init__(self, reason):
        super().__init__()
        self.reason = reason


class RemoteScreen(QObject):

    SERVER_PORT = 19380

    class TCPSocketWorker(QObject):

        lineRead = pyqtSignal(object)

        def __init__(self, parent):
            super().__init__(parent)
            self.connection = None
            self.data = bytes()

        @pyqtSlot()
        def closeConnection(self):
            try:
                if self.connection is not None:
                    self.connection.close()
                    self.connection = None
            except Exception as e:
                pass

        @pyqtSlot(object)
        def newConnection(self, connection):
            try:
                self.closeConnection()
                self.connection = connection
            except Exception as e:
                pass

        @pyqtSlot()
        def readLine(self):

            while True:
                try:
                    gen = self.connection.readAsync()
                    for data in gen:
                        if isinstance(data, int):
                            if data == 0:
                                QCoreApplication.processEvents()
                                if self.connection is None:
                                    return
                        elif isinstance(data, bytes):
                            if len(data) == 0:
                                self.closeConnection()
                                return
                            else:
                                self.data += data
                                test = data[-1:]
                                if data[-1:] == b'\n':
                                    self.lineRead.emit(self.data)
                                    self.data = bytes()
                                    return
                except Exception as e:
                    return

        @pyqtSlot(object)
        def writeLine(self, data):
            try:
                self.connection.write(data)
            except Exception as e:
                pass



    class TCPServer(QTcpServer):

        newConnection = pyqtSignal(object)

        def __init__(self, parent):
            super().__init__(parent)

        def incomingConnection(self, sock):
            try:
                sock = socket.fromfd(sock, socket.AF_INET, socket.SOCK_STREAM)
                connection = TLSConnection(sock)

                settings = QSettings('Secalot', 'Secalot Control Panel')
                key = settings.value('removeScreenKey', '', str)
                key = bytearray.fromhex(key)

                verifierDB = VerifierDB()
                verifierDB.create()
                entry = VerifierDB.makeVerifier("user", key, 2048)
                verifierDB[b"user"] = entry

                connection.handshakeServer(verifierDB=verifierDB)

                self.newConnection.emit(connection)
            except Exception as e:
                pass

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
    getDevicePublicKey = pyqtSignal()

    requestOpen = pyqtSignal(object)
    requestRead = pyqtSignal()
    requestWrite = pyqtSignal(object)
    requestClose = pyqtSignal()

    def __init__(self, engine, deviceCommunicator):

        super().__init__()

        self.qrCodeImageProvider = self.QRCodeImageProvider()

        self.guid = None
        self.srpKey = None
        self.qrCodeImageProvider.qrCodeImageData = None

        self.server = None

        self.zeroConf = None
        self.zeroConfInfo = None

        engine.addImageProvider("qrCode", self.qrCodeImageProvider)

        self.deviceCommunicator = deviceCommunicator

        self.deviceCommunicator.remoteScreenErrorOccured.connect(self.remoteScreenErrorOccured)
        self.deviceCommunicator.remoteScreenCommandSent.connect(self.remoteScreenCommandSent)

        self.sendRemoteScreenCommand.connect(deviceCommunicator.sendRemoteScreenCommand)

        self.getDevicePublicKey.connect(self.deviceCommunicator.getSslPublicKey)

        self.tcpSocketWorkerThread = QThread(self)
        self.tcpSocketWorker = self.TCPSocketWorker(None)
        self.tcpSocketWorker.moveToThread(self.tcpSocketWorkerThread)
        self.tcpSocketWorkerThread.start()

        self.requestClose.connect(self.tcpSocketWorker.closeConnection)
        self.requestOpen.connect(self.tcpSocketWorker.newConnection)
        self.requestWrite.connect(self.tcpSocketWorker.writeLine)
        self.requestRead.connect(self.tcpSocketWorker.readLine)

        self.tcpSocketWorker.lineRead.connect(self.dataReceived)


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
            self.clearMobilePhoneBindingState()

            self.guid = str(uuid.uuid4())
            self.srpKey = os.urandom(32).hex()

            self.deviceCommunicator.getSslPublicKeyReady.connect(self.startMobilePhoneBinding2nd)

            self.getDevicePublicKey.emit()

        except Exception as e:
            self.clearMobilePhoneBindingState()
            self.errorOccured.emit(self.tr("A RemoteScreen error occurred."))

    @pyqtSlot(str)
    def startMobilePhoneBinding2nd(self, publicKey):

        try:

            self.deviceCommunicator.getSslPublicKeyReady.disconnect(self.startMobilePhoneBinding2nd)

            jsonString = json.dumps({"guid": self.guid, "srpKey": self.srpKey, "publicKey": publicKey})

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
            self.srpKey = None
            self.qrCodeImageProvider.qrCodeImageData = None
        except Exception as e:
            pass


    @pyqtSlot()
    def finishMobilePhoneBinding(self):

        try:
            settings = QSettings('Secalot', 'Secalot Control Panel')

            settings.setValue('removeScreenUID', self.guid)
            settings.setValue('removeScreenKey', self.srpKey)
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
            self.server = self.TCPServer(self)

            self.server.newConnection.connect(self.newConnection)

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
            self.requestClose.emit()

            if self.server != None:
                self.server.close()
                self.server = None

            self.stopServerReady.emit()

        except Exception as e:
            self.errorOccured.emit(self.tr("A RemoteScreen error occurred."))


    @pyqtSlot(object)
    def newConnection(self, connection):
        try:
            self.requestOpen.emit(connection)
            self.requestRead.emit()
        except Exception as e:
            self.errorOccured.emit(self.tr("A RemoteScreen error occurred."))

    @pyqtSlot(object)
    def dataReceived(self, command):
        try:
            self.processCommand(command)
        except RemoteScreenException as e:
            self.errorOccured.emit(e.reason)
        except Exception as e:
            self.errorOccured.emit(self.tr("A RemoteScreen error occurred."))
        finally:
            self.requestRead.emit()

    def processCommand(self, command):

        command = json.loads(command)

        if command["command"] == "Ping":
            response = {"response": "Pong", "arguments": []}
            response = json.dumps(response) + '\n'
            response = response.encode('utf-8')
            self.requestWrite.emit(response)
        elif command["command"] == "SendAPDU":
            if( len(command["arguments"]) != 1):
                raise RemoteScreenException("Invalid RemoteScreen command received")
            apdu = base64.b64decode(command["arguments"][0])
            self.sendRemoteScreenCommand.emit(apdu)
        else:
            raise RemoteScreenException("Invalid RemoteScreen command received")

    @pyqtSlot(str)
    def remoteScreenErrorOccured(self, errorMessage):
        try:
            response = {"response": "Error", "arguments": [errorMessage]}
            response = json.dumps(response) + '\n'
            response = response.encode('utf-8')
            self.requestWrite.emit(response)
        except Exception as e:
            self.errorOccured.emit(self.tr("A RemoteScreen error occurred."))

    @pyqtSlot(bytes)
    def remoteScreenCommandSent(self, response):
        try:
            response = {"response": "SendAPDU", "arguments": [base64.b64encode(response).decode('utf8')]}
            try:
                response = json.dumps(response) + '\n'
            except Exception as e:
                pass
            response = response.encode('utf-8')
            self.requestWrite.emit(response)
        except Exception as e:
            self.errorOccured.emit(self.tr("A RemoteScreen error occurred."))





