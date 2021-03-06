# Secalot utilities.
# Copyright (c) 2017 Matvey Mukha <matvey.mukha@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import smartcard.System
import base64
import os

READER_NAME = 'Secalot Secalot Dongle'


class NoReaderFoundError(Exception):
    pass


class InvalidCardResponseError(Exception):
    pass


def otp_key(string):
    if string.startswith('0x'):
        string = string[2:]
        if len(string) % 2 != 0:
            raise argparse.ArgumentTypeError('The value should contain an even number of digits')
        integer = int(string, 16)
        bytes = integer.to_bytes(int(len(string) / 2), 'big')
    else:
        string = string.replace(" ", "")
        string = string.upper()
        bytes = base64.b32decode(string)

    if len(bytes) < 10 or len(bytes) > 32:
        raise argparse.ArgumentTypeError('The value should be 10 to 32 bytes long')

    return bytes


def otp_type(string):
    if string != 'TOTP' and string != 'HOTP':
        raise argparse.ArgumentTypeError('Please specify TOTP or HOTP')
    return string


def number_of_digits(string):
    integer = int(string)
    if integer < 6 or integer > 8:
        raise argparse.ArgumentTypeError('The value should be between 6 and 8')
    return integer


def key_format(string):
    if string != 'hex' and string != 'base32':
        raise argparse.ArgumentTypeError('Please specify hex or base32')
    return string


def key_length(string):
    integer = int(string)
    if integer < 10 or integer > 32:
        raise argparse.ArgumentTypeError('The value should be between 10 and 32')
    return integer


def parse_arguments():
    parser = argparse.ArgumentParser(description='OTP control.')
    parser._optionals.title = 'Options'
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = True
    parserGetNumberOfDigitsAndType = subparsers.add_parser('getNumberOfDigitsAndType',
                                                           help='Get the number of OTP digits and OTP type.')
    parserSetNumberOfDigits = subparsers.add_parser('setNumberOfDigits',
                                                    help='Set the number of OTP digits. From 6 to 8.')
    parserSetNumberOfDigits.add_argument('numberOfDigits', type=number_of_digits, help=('Number of digits.'))
    parserSetKeyAndType = subparsers.add_parser('setKeyAndType', help='Set key and type.')
    parserSetKeyAndType.add_argument('key', type=otp_key, help=('Key.'))
    parserSetKeyAndType.add_argument('type', type=otp_type, help=('TOTP or HOTP'))
    parserGenerateKey = subparsers.add_parser('generateKey', help='Generate an OTP key.')
    parserGenerateKey.add_argument('keyFormat', type=key_format, help=('Key format: hex or base32.'))
    parserGenerateKey.add_argument('keyLength', type=key_length, help=('Key length in bytes. 10 to 32.'))

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


def getNumberOfDigitsAndType(connection):
    response, sw1, sw2 = connection.transmit(
        [0x00, 0xA4, 0x04, 0x00, 0x09, 0x4F, 0x54, 0x50, 0x41, 0x50, 0x50, 0x4C, 0x45, 0x54])
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()

    response, sw1, sw2 = connection.transmit([0x80, 0x02, 0x00, 0x00])
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()

    if len(response) != 2:
        raise InvalidCardResponseError()

    if response[1] == 1:
        type = 'HOTP'
    elif response[1] == 2:
        type = 'TOTP'
    else:
        raise InvalidCardResponseError()

    return response[0], type


def setNumberOfDigits(connection, numberOfDigits):
    response, sw1, sw2 = connection.transmit(
        [0x00, 0xA4, 0x04, 0x00, 0x09, 0x4F, 0x54, 0x50, 0x41, 0x50, 0x50, 0x4C, 0x45, 0x54])
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()

    response, sw1, sw2 = connection.transmit([0x80, 0x00, 0x00, 0x00, 0x01, numberOfDigits])
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()


def setKeyAndType(connection, key, type):
    response, sw1, sw2 = connection.transmit(
        [0x00, 0xA4, 0x04, 0x00, 0x09, 0x4F, 0x54, 0x50, 0x41, 0x50, 0x50, 0x4C, 0x45, 0x54])
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()

    if type == 'HOTP':
        type = 1
    else:
        type = 2

    response, sw1, sw2 = connection.transmit([0x80, 0x01, 0x00, 0x00, len(key) + 1] + [type] + list(key))
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()


def generateKey(format, length):
    key = os.urandom(length)

    if format == 'base32':
        key = base64.b32encode(key)
        key = key.decode("utf-8")
        key = key.lower()
        key = ' '.join(key[i:i + 4] for i in range(0, len(key), 4))
    else:
        key = '0x' + key.hex()

    return key


def main():
    arguments = parse_arguments()

    try:
        connection = findConnectedDevice()

        if arguments.subcommand == 'getNumberOfDigitsAndType':
            numberOfDigits, type = getNumberOfDigitsAndType(connection)
            print('')
            print('Number of digits: ' + str(numberOfDigits))
            print('Type: ' + type)
        elif arguments.subcommand == 'setNumberOfDigits':
            setNumberOfDigits(connection, arguments.numberOfDigits)
        elif arguments.subcommand == 'setKeyAndType':
            setKeyAndType(connection, arguments.key, arguments.type)
        elif arguments.subcommand == 'generateKey':
            key = generateKey(arguments.keyFormat, arguments.keyLength)
            print('Key: ' + key)

    except NoReaderFoundError:
        print("Error: please connect a device.");
    except InvalidCardResponseError:
        print("Error: invalid response received from the device.");


if __name__ == "__main__":
    main()
