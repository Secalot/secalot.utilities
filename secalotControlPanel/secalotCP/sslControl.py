# Secalot utilities.
# Copyright (c) 2018 Matvey Mukha <matvey.mukha@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import smartcard.System
import hashlib

READER_NAME = 'Secalot Secalot Dongle'


class NoReaderFoundError(Exception):
    pass


class InvalidCardResponseError(Exception):
    pass


def parse_arguments():
    parser = argparse.ArgumentParser(description='SSL control.')
    parser._optionals.title = 'Options'
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = True

    parserGetPublicKeyFingerprint = subparsers.add_parser('getPublicKeyFingerprint', help='Get public key fingerprint.')
    parserGetPublicKey = subparsers.add_parser('getPublicKey', help='Get public key.')

    args = parser.parse_args()
    return args


def findConnectedDevice():
    connectedReaders = smartcard.System.readers()

    reader = next((reader for reader in connectedReaders if reader.name.startswith(READER_NAME)), None)

    if reader != None:
        connection = reader.createConnection()
    else:
        raise NoReaderFoundError

    connection.connect()

    return connection


def selectApp(connection):
    response, sw1, sw2 = connection.transmit(
        [0x00, 0xA4, 0x04, 0x00, 0x09, 0x53, 0x53, 0x4C, 0x41, 0x50, 0x50, 0x4C, 0x45, 0x54])
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()


def getPublicKeyFingerprint(connection):
    selectApp(connection)

    response, sw1, sw2 = connection.transmit([0x80, 0x10, 0x00, 0x00])
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()

    if len(response) != 65:
        raise InvalidCardResponseError()

    response = response[1:]

    hash = hashlib.sha256(bytes(response)).hexdigest()

    return hash[:16]


def getPublicKey(connection):
    selectApp(connection)

    response, sw1, sw2 = connection.transmit([0x80, 0x10, 0x00, 0x00])
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()

    if len(response) != 65:
        raise InvalidCardResponseError()

    return bytes(response[1:]).hex()


def main():
    arguments = parse_arguments()

    try:
        connection = findConnectedDevice()
        if arguments.subcommand == 'getPublicKeyFingerprint':
            fingerprint = getPublicKeyFingerprint(connection)
            print('Public key fingerprint: ' + fingerprint)
        elif arguments.subcommand == 'getPublicKey':
            key = getPublicKey(connection)
            print('Public key: ' + key)

    except NoReaderFoundError:
        print('Error: please connect a device.')
    except InvalidCardResponseError:
        print('Error: invalid response received from the device.')


if __name__ == "__main__":
    main()
