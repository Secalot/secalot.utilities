# Secalot utilities.
# Copyright (c) 2017 Matvey Mukha <matvey.mukha@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
import smartcard.System
import time

READER_NAME = 'Secalot Secalot Dongle'
BOOTLOADER_READER_NAME = 'Secalot Secalot Bootloader'


class DeviceFinder(QThread):
    moreThanOneDeviceConnected = pyqtSignal()
    noDevicesConnected = pyqtSignal()
    oneDeviceConnected = pyqtSignal(str, str, arguments=['readerName', 'readerType'])

    deviceAdded = pyqtSignal(str, str)
    deviceRemoved = pyqtSignal(str)

    knownReaders = []

    firstRun = True

    monitoringStopped = False

    def __init__(self):
        super().__init__()

    def run(self):

        while True:
            try:
                time.sleep(0.1)

                if not self.monitoringStopped:

                    connectedFirmwareReaders, connectedBootloaderReaders = self.getAllReaders()

                    connectedReaders = connectedFirmwareReaders + connectedBootloaderReaders

                    newReaders = [reader for reader in connectedReaders if reader not in self.knownReaders]

                    removedReaders = [reader for reader in self.knownReaders if reader not in connectedReaders]

                    for reader in newReaders:
                        self.deviceAdded.emit(str(reader), reader.type)

                    for reader in removedReaders:
                        self.deviceRemoved.emit(str(reader))

                    if (len(connectedReaders) > 1) and (len(self.knownReaders) <= 1):
                        self.moreThanOneDeviceConnected.emit()
                    elif (len(connectedReaders) == 0) and ((len(self.knownReaders) != 0) or (self.firstRun == True)):
                        self.noDevicesConnected.emit()
                        self.firstRun = False
                    elif (len(connectedReaders) == 1) and (
                                (len(self.knownReaders) != 1) or (connectedReaders[0] != self.knownReaders[0])):
                        self.oneDeviceConnected.emit(str(connectedReaders[0]), connectedReaders[0].type)

                    self.knownReaders = connectedReaders

            except Exception:
                continue

    @staticmethod
    def getAllReaders():

        connectedReaders = []

        try:
            connectedReaders = smartcard.System.readers()
        except smartcard.pcsc.PCSCExceptions.ListReadersException:
            smartcard.pcsc.PCSCContext.PCSCContext.instance = None
        except Exception:
            pass

        connectedFirmwareReaders = []
        connectedBootloaderReaders = []

        for reader in connectedReaders:
            if reader.name.startswith(BOOTLOADER_READER_NAME):
                reader.type = "bootloader"
                connectedBootloaderReaders.append(reader)
            elif reader.name.startswith(READER_NAME):
                reader.type = "firmware"
                connectedFirmwareReaders.append(reader)

        return connectedFirmwareReaders, connectedBootloaderReaders

    @pyqtSlot()
    def stopMonitoring(self):
        self.monitoringStopped = True
        pass

    @pyqtSlot()
    def restartMonitoring(self):
        self.knownReaders = []
        self.firstRun = True
        smartcard.pcsc.PCSCContext.PCSCContext.instance = None
        self.monitoringStopped = False
