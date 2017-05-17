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
import base64 

READER_NAME = 'Secalot Secalot Dongle'

class NoReaderFoundError(Exception):
    pass
class InvalidCardResponseError(Exception):
    pass

def otp_key(string):
    if string.startswith('0x'):
        string = string[2:]
        integer = int(string, 16)
        bytes = integer.to_bytes(int(len(string)/2), 'big')
    else:
        string = string.replace(" ", "")
        string = string.upper()
        bytes = base64.b32decode(string)

    if len(string) < 20 or len(string) > 64 or len(string)%2 != 0:
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

def parse_arguments():
    parser = argparse.ArgumentParser(description='OPT control.')
    parser._optionals.title = 'Options'
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required=True
    parserGetNumberOfDigitsAndType = subparsers.add_parser('getNumberOfDigitsAndType', help='Get the number of OTP digits and OTP type.')
    parserSetNumberOfDigits = subparsers.add_parser('setNumberOfDigits', help='Set the number of OTP digits. From 6 to 8.')
    parserSetNumberOfDigits.add_argument('numberOfDigits', type=number_of_digits, help=('Number of digits.'))
    parserSetKeyAndType = subparsers.add_parser('setKeyAndType', help='Set key and type.')
    parserSetKeyAndType.add_argument('key', type=otp_key, help=('Key.'))
    parserSetKeyAndType.add_argument('type', type=otp_type, help=('TOTP or HOTP'))
    args = parser.parse_args()
    return args

def findConnectedDevice():
    connectedReaders = smartcard.System.readers()

    reader = next((reader for reader in connectedReaders if reader.name.startswith(READER_NAME) ), None)

    if  reader != None:
        connection = reader.createConnection()
    else:
        raise NoReaderFoundError

    connection.connect()

    return connection

def getNumberOfDigitsAndType(connection):
    response, sw1, sw2 = connection.transmit([0x00, 0xA4, 0x04, 0x00, 0x09, 0x4F, 0x54, 0x50, 0x41, 0x50, 0x50, 0x4C, 0x45, 0x54])
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
    response, sw1, sw2 = connection.transmit([0x00, 0xA4, 0x04, 0x00, 0x09, 0x4F, 0x54, 0x50, 0x41, 0x50, 0x50, 0x4C, 0x45, 0x54])
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()

    response, sw1, sw2 = connection.transmit([0x80, 0x00, 0x00, 0x00, 0x01, numberOfDigits])
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()

def setKeyAndType(connection, key, type):
    response, sw1, sw2 = connection.transmit([0x00, 0xA4, 0x04, 0x00, 0x09, 0x4F, 0x54, 0x50, 0x41, 0x50, 0x50, 0x4C, 0x45, 0x54])
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()

    if type == 'HOTP':
        type = 1
    else:
        type = 2

    response, sw1, sw2 = connection.transmit([0x80, 0x01, 0x00, 0x00, len(key)+1] + [type] + list(key))
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()


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
    except NoReaderFoundError:
        print("Error: please connect a device.");
    except InvalidCardResponseError:
        print("Error: invalid response received from the device.");

if __name__ == "__main__":
    main()