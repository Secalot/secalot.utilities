# Secalot utilities.
# Copyright (c) 2017 Matvey Mukha <matvey.mukha@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import smartcard.System
import time
import struct

READER_NAME = 'Secalot Secalot Dongle'


def sendTime(connection):
    response, sw1, sw2 = connection.transmit(
        [0x00, 0xA4, 0x04, 0x00, 0x09, 0x4F, 0x54, 0x50, 0x41, 0x50, 0x50, 0x4C, 0x45, 0x54])
    if sw1 != 0x90 or sw2 != 00:
        raise Exception()

    epoch_time = int(time.time())

    epoch_time = epoch_time.to_bytes(4, 'big')

    response, sw1, sw2 = connection.transmit([0x80, 0x03, 0x00, 0x00, len(epoch_time)] + list(epoch_time))
    if sw1 != 0x90 or sw2 != 00:
        raise Exception()


def main():
    readers = []
    addedReaders = []

    while True:
        time.sleep(1)
        try:
            currentReaders = smartcard.System.readers()
            addedReaders = []
            if currentReaders != readers:
                for reader in currentReaders:
                    if not reader in readers:
                        addedReaders.append(reader)
                readers = currentReaders;
            for reader in addedReaders:
                if reader.name.startswith(READER_NAME):
                    try:
                        connection = reader.createConnection()
                        connection.connect()
                        sendTime(connection)
                        connection.disconnect()

                    except Exception as e:
                        pass
        except smartcard.pcsc.PCSCExceptions.ListReadersException:
            smartcard.pcsc.PCSCContext.PCSCContext.instance = None


if __name__ == "__main__":
    main()
