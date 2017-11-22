# Secalot utilities.
# Copyright (c) 2017 Matvey Mukha <matvey.mukha@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import smartcard.System
import time
import struct
from collections import namedtuple

READER_NAME = 'Secalot Secalot Dongle'
BOOTLOADER_READER_NAME = 'Secalot Secalot Bootloader'

MAGIC = int(0x424C4F42).to_bytes(4, 'big')
HEADER_LENGTH = 16
SIGNATURE_LENGTH = 64
CHUNK_LENGTH = 128

FIRMWARE_CHUNKS = 1664
BOOTLOADER_CHUNKS = 256


class InvalidUpdateImageError(Exception):
    pass


class NoReaderFoundError(Exception):
    pass


class InvalidCardResponseError(Exception):
    pass


class NotSuitableImageError(Exception):
    def __init__(self, reasonCode):
        super().__init__()
        self.reasonCode = reasonCode


DeviceInfo = namedtuple('DeviceInfo',
                        'deviceID serialNumber firmwareVersion fileSystemVersion bootloaderVersion fileSystemUpdateInProgress firmwareIsBootable bootloaderIsBootable')
ImageInfo = namedtuple('ImageInfo', 'deviceID firmwareVersion fileSystemVersion bootloaderVersion')


def parse_arguments():
    parser = argparse.ArgumentParser(description='Update firmware.')
    parser._optionals.title = 'Options'
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = True
    parserGetDeviceInfo = subparsers.add_parser('getDeviceInfo', help='Get information about a device.')
    parserGetUpdateImageInfo = subparsers.add_parser('getUpdateImageInfo',
                                                     help='Get information about an update image.')
    parserGetUpdateImageInfo._optionals.title = 'Options'
    parserGetUpdateImageInfo.add_argument('--imageFile', required=True, type=argparse.FileType('rb'),
                                          help=('File with an update image.'))
    parserSwitch = subparsers.add_parser('switch',
                                         help='Switch mode. Go to bootloader mode if in firmware mode and vice versa.')
    parserUpload = subparsers.add_parser('upload', help='Upload a an update image')
    parserUpload._optionals.title = 'Options'
    parserUpload.add_argument('--imageFile', required=True, type=argparse.FileType('rb'),
                              help=('File with an update image.'))
    parserUpload.add_argument('--cleanFileSystem', action='store_true',
                              help=('Reinstantiate a clean file system (all data will be lost).'))
    parserEnableManufacturerBootloader = subparsers.add_parser('enableManufacturerBootloader',
                                                               help='Enable manufacturer bootloader.')
    args = parser.parse_args()
    return args


def getUpdateImageInfo(imageFile):
    imageFile.seek(0, 0)

    if MAGIC != imageFile.read(4):
        raise InvalidUpdateImageError()

    header = imageFile.read(16)
    if len(header) != 16:
        raise InvalidUpdateImageError()

    imageInfo = ImageInfo._make(struct.unpack('>IIII', bytes(header[0:16])))

    return imageInfo


def updateImageToAPDUs(imageFile, cleanFileSystemRequested):
    fwApduList = []
    blApduList = []

    imageFile.seek(0, 0)

    if MAGIC != imageFile.read(4):
        raise InvalidUpdateImageError()

    header = imageFile.read(HEADER_LENGTH)
    if len(header) != HEADER_LENGTH:
        raise InvalidUpdateImageError()

    fwSignature = imageFile.read(SIGNATURE_LENGTH)
    if len(fwSignature) != SIGNATURE_LENGTH:
        raise InvalidUpdateImageError()

    blSignature = imageFile.read(SIGNATURE_LENGTH)
    if len(blSignature) != SIGNATURE_LENGTH:
        raise InvalidUpdateImageError()

    fwSetImageInfoAPDU = [0x80, 0x02, 0x00, 0x00, HEADER_LENGTH + SIGNATURE_LENGTH] + list(header) + list(fwSignature)
    fwApduList.append(fwSetImageInfoAPDU)

    blSetImageInfoAPDU = [0x80, 0x02, 0x00, 0x00, 8 + SIGNATURE_LENGTH] + list(header[0:4]) + list(
        header[12:16]) + list(blSignature)
    blApduList.append(blSetImageInfoAPDU)

    for count in range(0, FIRMWARE_CHUNKS):
        chunk = imageFile.read(CHUNK_LENGTH)
        if len(chunk) != CHUNK_LENGTH:
            raise InvalidUpdateImageError()
        loadImageDataAPDU = [0x80, 0x03, 0x00, 0x00, CHUNK_LENGTH] + list(chunk)
        fwApduList.append(loadImageDataAPDU)

    for count in range(0, BOOTLOADER_CHUNKS):
        chunk = imageFile.read(CHUNK_LENGTH)
        if len(chunk) != CHUNK_LENGTH:
            raise InvalidUpdateImageError()
        loadImageDataAPDU = [0x80, 0x03, 0x00, 0x00, CHUNK_LENGTH] + list(chunk)
        blApduList.append(loadImageDataAPDU)

    if cleanFileSystemRequested == True:
        fwApduList.append([0x80, 0x04, 0x00, 0x01])
    else:
        fwApduList.append([0x80, 0x04, 0x00, 0x00])

    blApduList.append([0x80, 0x04, 0x00, 0x00])

    return fwApduList, blApduList


def findConnectedDevice():
    connectedReaders = smartcard.System.readers()

    firmwareReader = next((reader for reader in connectedReaders if reader.name.startswith(READER_NAME)), None)
    bootloaderReader = next((reader for reader in connectedReaders if reader.name.startswith(BOOTLOADER_READER_NAME)),
                            None)

    if bootloaderReader != None:
        connection = bootloaderReader.createConnection()
        device = "bootloader"
    elif firmwareReader != None:
        connection = firmwareReader.createConnection()
        device = "firmware"
    else:
        raise NoReaderFoundError

    connection.connect()

    return device, connection


def switchModes(device, connection):
    if device == 'bootloader':
        targetReaderName = READER_NAME
        modeSwitchingTo = 'firmware'
    elif device == 'firmware':
        targetReaderName = BOOTLOADER_READER_NAME
        modeSwitchingTo = 'bootloader'
    else:
        raise Exception

    if device == 'firmware':
        response, sw1, sw2 = connection.transmit(
            [0x00, 0xA4, 0x04, 0x00, 0x0A, 0x42, 0x4C, 0x44, 0x52, 0x41, 0x50, 0x50, 0x4C, 0x45, 0x54])
        if sw1 != 0x90 or sw2 != 00:
            raise InvalidCardResponseError()
        response, sw1, sw2 = connection.transmit([0x80, 0x05, 0x00, 0x00])
        if sw1 != 0x90 or sw2 != 00:
            raise InvalidCardResponseError()
    else:
        response, sw1, sw2 = connection.transmit([0x80, 0x01, 0x00, 0x00])
        if sw1 != 0x90 or sw2 != 00:
            raise InvalidCardResponseError()

    connection.disconnect()

    print('Switching to ' + modeSwitchingTo + ' mode. Please replug the device.')

    while True:
        time.sleep(0.1)
        try:
            connectedReaders = smartcard.System.readers()
        except smartcard.pcsc.PCSCExceptions.ListReadersException:
            smartcard.pcsc.PCSCContext.PCSCContext.instance = None
        reader = next((reader for reader in connectedReaders if reader.name.startswith(targetReaderName)), None)
        if reader != None:
            time.sleep(0.5)
            break

    print('Mode switched.')


def getDeviceInfo(device, connection):
    if device == 'firmware':
        response, sw1, sw2 = connection.transmit(
            [0x00, 0xA4, 0x04, 0x00, 0x0A, 0x42, 0x4C, 0x44, 0x52, 0x41, 0x50, 0x50, 0x4C, 0x45, 0x54])
        if sw1 != 0x90 or sw2 != 00:
            raise InvalidCardResponseError()

    response, sw1, sw2 = connection.transmit([0x80, 0x00, 0x00, 0x00])
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()

    if len(response) != 23:
        raise InvalidCardResponseError()

    deviceInfo = DeviceInfo._make(struct.unpack('>IIIII???', bytes(response)))
    return deviceInfo


def printDeviceInfo(device, deviceInfo):
    print('')
    if device == 'firmware':
        print('Device is in firmware mode.')
    elif device == 'bootloader':
        print('Device is in bootloader mode.')
    else:
        raise Exception

    print('Device ID: ' + hex(deviceInfo.deviceID))
    print('Serial number: ' + hex(deviceInfo.serialNumber)[2:].zfill(8))
    print('Firmware version: ' + hex(deviceInfo.firmwareVersion))
    print('File system version: ' + hex(deviceInfo.fileSystemVersion))
    print('Bootloader version: ' + hex(deviceInfo.bootloaderVersion))


def printUpdateImageInfo(imageInfo):
    print('')
    print('Device ID: ' + hex(imageInfo.deviceID))
    print('Firmware version: ' + hex(imageInfo.firmwareVersion))
    print('File system version: ' + hex(imageInfo.fileSystemVersion))
    print('Bootloader version: ' + hex(imageInfo.bootloaderVersion))


def checkImageInfo(imageInfo, deviceInfo, cleanFileSystemRequested):
    if imageInfo.deviceID != deviceInfo.deviceID:
        print('This update is targeting a different device version.')
        raise NotSuitableImageError(1)
    if imageInfo.firmwareVersion < deviceInfo.firmwareVersion:
        print('A downgrade can not be performed.')
        raise NotSuitableImageError(2)
    if imageInfo.bootloaderVersion < deviceInfo.bootloaderVersion:
        print('A downgrade can not be performed.')
        raise NotSuitableImageError(3)
    if imageInfo.fileSystemVersion < deviceInfo.fileSystemVersion:
        print('A downgrade can not be performed.')
        raise NotSuitableImageError(4)
    if cleanFileSystemRequested == False and imageInfo.fileSystemVersion > deviceInfo.fileSystemVersion:
        print(
            'This update can only be applied together with cleaning a file system. Please use a --cleanFileSystem option.')
        raise NotSuitableImageError(5)
    if cleanFileSystemRequested == False and deviceInfo.fileSystemUpdateInProgress == True:
        print(
            'An update performed on this device was interrutped while cleaning a file system. Please use a --cleanFileSystem option.')
        raise NotSuitableImageError(6)
    if (imageInfo.bootloaderVersion != deviceInfo.bootloaderVersion) and deviceInfo.firmwareIsBootable == False:
        print('Previous update was interrupted. Please continue with the exact same update image file.')
        raise NotSuitableImageError(7)


def loadTheImage(connection, apduList):
    print('Loading image.')
    for apdu in apduList:
        response, sw1, sw2 = connection.transmit(apdu)
        if sw1 != 0x90 or sw2 != 00:
            raise InvalidCardResponseError()
    print('Done.')


def performUpdate(device, connection, fwApduList, blApduList, imageInfo, deviceInfo):
    if device == 'bootloader':
        if deviceInfo.bootloaderVersion != imageInfo.bootloaderVersion:
            switchModes(device, connection)
            device, connection = findConnectedDevice()
            loadTheImage(connection, blApduList)
            switchModes(device, connection)
            device, connection = findConnectedDevice()
    else:
        if (deviceInfo.bootloaderVersion != imageInfo.bootloaderVersion) or deviceInfo.bootloaderIsBootable == False:
            loadTheImage(connection, blApduList)
        switchModes(device, connection)
        device, connection = findConnectedDevice()

    loadTheImage(connection, fwApduList)
    switchModes(device, connection)
    device, connection = findConnectedDevice()


def enableManufacturerBootloader(device, connection):
    print('Enabling manufacturer bootloader.')

    if device != 'firmware':
        print('This command is only available in firmware mode')
        return

    response, sw1, sw2 = connection.transmit(
        [0x00, 0xA4, 0x04, 0x00, 0x0A, 0x42, 0x4C, 0x44, 0x52, 0x41, 0x50, 0x50, 0x4C, 0x45, 0x54])
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()

    response, sw1, sw2 = connection.transmit([0x80, 0x80, 0x00, 0x00])
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()

    print('Done.')


def main():
    arguments = parse_arguments()

    try:

        if arguments.subcommand != 'getUpdateImageInfo':
            device, connection = findConnectedDevice()

        if arguments.subcommand == 'getDeviceInfo':
            deviceInfo = getDeviceInfo(device, connection)
            printDeviceInfo(device, deviceInfo)
        elif arguments.subcommand == 'getUpdateImageInfo':
            imageInfo = getUpdateImageInfo(arguments.imageFile)
            printUpdateImageInfo(imageInfo)
        elif arguments.subcommand == 'switch':
            switchModes(device, connection)
        elif arguments.subcommand == 'upload':
            imageInfo = getUpdateImageInfo(arguments.imageFile)
            fwApduList, blApduList = updateImageToAPDUs(arguments.imageFile, arguments.cleanFileSystem)
            deviceInfo = getDeviceInfo(device, connection)
            checkImageInfo(imageInfo, deviceInfo, arguments.cleanFileSystem)
            performUpdate(device, connection, fwApduList, blApduList, imageInfo, deviceInfo)
        elif arguments.subcommand == 'enableManufacturerBootloader':
            enableManufacturerBootloader(device, connection)
    except InvalidUpdateImageError:
        print("Error: invalid update image file.");
    except NoReaderFoundError:
        print("Error: please connect a device.");
    except InvalidCardResponseError:
        print("Error: invalid response received from the device.");
    except NotSuitableImageError:
        pass


if __name__ == "__main__":
    main()
