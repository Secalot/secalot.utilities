# Secalot utilities.
# Copyright (c) 2018 Matvey Mukha <matvey.mukha@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import smartcard.System
from collections import namedtuple


READER_NAME = 'Secalot Secalot Dongle'


class NoReaderFoundError(Exception):
    pass


class InvalidCardResponseError(Exception):
    pass


class WalletError(Exception):
    def __init__(self, reasonCode, message):
        super().__init__()
        self.reasonCode = reasonCode
        self.message = message


AppInfo = namedtuple('AppInfo', 'version walletInitialized pinVerified')


def privateKey(pkString):

    if pkString.startswith('0x'):
        pkString = pkString[2:]

    if len(pkString) != 64:
        raise argparse.ArgumentTypeError('Private key should be 32 bytes long')

    try:
        pkByteArray = bytearray.fromhex(pkString)
    except Exception:
        raise argparse.ArgumentTypeError('Invalid private key hex representation')

    return pkByteArray


def pin(string):
    if len(string) < 4 or len(string) > 32:
        raise argparse.ArgumentTypeError('Pin length should be between 4 and 32 bytes')

    return string.encode('utf-8')

def randomLength(length):

    length = int(length)

    if length > 128 or length < 0:
        raise argparse.ArgumentTypeError('Length should be between 0 and 128 bytes')

    return length

def dataToSign(dataString):
    if dataString.startswith('0x'):
        dataString = dataString[2:]

    if len(dataString) == 0:
        raise argparse.ArgumentTypeError('Data length should not be zero')

    try:
        dataByteArray = bytearray.fromhex(dataString)
    except Exception:
        raise argparse.ArgumentTypeError('Invalid data hex representation')

    return dataByteArray


def parse_arguments():
    parser = argparse.ArgumentParser(description='Ripple control.')
    parser._optionals.title = 'Options'
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = True

    parserGetInfo = subparsers.add_parser('getInfo', help='Get wallet info.')

    parserInitWallet = subparsers.add_parser('initWallet', help='Initialise the wallet')
    parserInitWallet._optionals.title = 'Options'
    parserInitWallet.add_argument('--key', required=True, type=privateKey,
                                  help=('Private key as a hex string'))
    parserInitWallet.add_argument('--pin', required=True, type=pin, help=('New PIN-code.'))

    parserVerifyPin = subparsers.add_parser('verifyPin', help='Verify PIN-code')
    parserVerifyPin._optionals.title = 'Options'
    parserVerifyPin.add_argument('--pin', required=True, type=pin, help=('PIN-code.'))

    parserWipeoutWallet = subparsers.add_parser('wipeoutWallet', help='Erase the wallet.')

    parserGetPublicKey = subparsers.add_parser('getPublicKey', help='Get a public key')
    parserGetPublicKey._optionals.title = 'Options'

    parserGetRandom = subparsers.add_parser('getRandom', help='Get random numbers')
    parserGetRandom.add_argument('--length', required=True, type=randomLength, help=('Number of random bytes to get'))
    parserGetRandom._optionals.title = 'Options'

    parserSign = subparsers.add_parser('sign', help='Sign data')
    parserSign.add_argument('--data', required=True, type=dataToSign, help=('Data to sign'))
    parserSign._optionals.title = 'Options'

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
        [0x00, 0xA4, 0x04, 0x00, 0x09, 0x58, 0x52, 0x50, 0x41, 0x50, 0x50, 0x4C, 0x45, 0x54])
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()


def getInfo(connection):
    selectApp(connection)

    response, sw1, sw2 = connection.transmit([0x80, 0xC4, 0x00, 0x00])
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()

    if len(response) != 8:
        raise InvalidCardResponseError()

    appInfo = AppInfo(
        version=format(response[0], 'x') + '.' + format(response[1], 'x'),
        walletInitialized=(response[2] & 0x01 == 0x01),
        pinVerified=(response[2] & 0x02 == 0x02)
    )

    return appInfo


def getRandom(connection, length):
    selectApp(connection)

    response, sw1, sw2 = connection.transmit([0x80, 0xC0, 0x00, 0x00, length])
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()

    if len(response) != length:
        raise InvalidCardResponseError()

    return response


def initWallet(connection, privateKey, pin):
    selectApp(connection)

    data = bytearray()

    data.append(len(pin))
    data += pin
    data += privateKey

    response, sw1, sw2 = connection.transmit([0x80, 0x20, 0x00, 0x00] + [len(data)] + list(data))
    if sw1 != 0x90 or sw2 != 00:
        if sw1 == 0x6d and sw2 == 0x00:
            raise WalletError("ALREADY_INIT", 'Wallet already initialized')
        else:
            raise InvalidCardResponseError()


def wipeoutWallet(connection):
    selectApp(connection)

    response, sw1, sw2 = connection.transmit([0x80, 0xF0, 0x00, 0x00])
    if sw1 != 0x90 or sw2 != 00:
        if sw1 == 0x6d and sw2 == 0x00:
            raise WalletError("NOT_INIT", 'Wallet not initialized')
        else:
            raise InvalidCardResponseError()


def verifyPin(connection, pin):
    selectApp(connection)

    response, sw1, sw2 = connection.transmit([0x80, 0x22, 0x00, 0x00] + [len(pin)] + list(pin))

    if sw1 != 0x90 or sw2 != 00:
        if sw1 == 0x6d and sw2 == 0x00:
            raise WalletError("NOT_INIT", 'Wallet not initialized')
        elif sw1 == 0x69 and sw2 == 0x82:
            triesLeft = getPinTriesLeft(connection)
            raise WalletError("INVALID_PIN", 'Invalid PIN-code. ' + str(triesLeft) + ' tries left.')
        elif sw1 == 0x67 and sw2 == 0x00:
            raise WalletError("WRONG_LENGTH", 'Unsupported PIN-code length')
        elif sw1 == 0x69 and sw2 == 0x83:
            raise WalletError("PIN_BLOCKED", 'PIN-code blocked')
        else:
            raise InvalidCardResponseError()


def getPinTriesLeft(connection):
    selectApp(connection)

    response, sw1, sw2 = connection.transmit([0x80, 0x22, 0x80, 0x00])
    if sw1 != 0x63:
        if sw1 == 0x6d and sw2 == 0x00:
            raise WalletError("NOT_INIT", 'Wallet not initialized')
        else:
            raise InvalidCardResponseError()

    return (sw2 - 0xC0)


def getPublicKey(connection):
    selectApp(connection)

    response, sw1, sw2 = connection.transmit( [0x80, 0x40, 0x00, 0x00] )

    if sw1 != 0x90 or sw2 != 00:
        if sw1 == 0x6d and sw2 == 0x00:
            raise WalletError("NOT_INIT", 'Wallet not initialized')
        elif sw1 == 0x69 and sw2 == 0x82:
            raise WalletError("PIN_NOT_VERIFIED", 'PIN-code not verified.')
        else:
            raise InvalidCardResponseError()

    if len(response) != 65:
        raise InvalidCardResponseError()

    return bytes(response)


def sign(connection, dataToSign):
    firstChunk = True
    selectApp(connection)

    chunks = [dataToSign[i:i + 128] for i in range(0, len(dataToSign), 128)]


    for chunk in chunks:
        if firstChunk is True:
            response, sw1, sw2 = connection.transmit( [0x80, 0xf2, 0x00, 0x00] + [len(chunk)] + list(chunk))
            firstChunk = False;
        else:
            response, sw1, sw2 = connection.transmit([0x80, 0xf2, 0x01, 0x00] + [len(chunk)] + list(chunk))

        if sw1 != 0x90 or sw2 != 00:
            if sw1 == 0x6d and sw2 == 0x00:
                raise WalletError("NOT_INIT", 'Wallet not initialized')
            elif sw1 == 0x69 and sw2 == 0x82:
                raise WalletError("PIN_NOT_VERIFIED", 'PIN-code not verified.')
            else:
                raise InvalidCardResponseError()

    response, sw1, sw2 = connection.transmit([0x80, 0xf2, 0x02, 0x00])

    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()


    return bytes(response)


def main():
    arguments = parse_arguments()

    try:
        connection = findConnectedDevice()
        if arguments.subcommand == 'initWallet':
            initWallet(connection, arguments.key, arguments.pin)
        elif arguments.subcommand == 'getPublicKey':
            publicKey = getPublicKey(connection)
            print('Public key: ' + ''.join(format(x, '02x') for x in publicKey))
        elif arguments.subcommand == 'wipeoutWallet':
            wipeoutWallet(connection)
        elif arguments.subcommand == 'verifyPin':
            verifyPin(connection, arguments.pin)
        elif arguments.subcommand == 'getInfo':
            info = getInfo(connection)
            print('')
            print('App version: ' + info.version)

            if info.walletInitialized == True:
                print('Wallet status: initialized')
            else:
                print('Wallet status: not initialized')

            if info.pinVerified == True:
                print('Pin status: verified')
            else:
                print('Pin status: unverified')
        elif arguments.subcommand == 'getRandom':
            rand = getRandom(connection, arguments.length)
            print('Random string: ' + ''.join(format(x, '02x') for x in rand))
        elif arguments.subcommand == 'sign':
            print('Please confirm the action by tapping a touch button')
            signature = sign(connection, arguments.data)
            print('Signature: ' + ''.join(format(x, '02x') for x in signature))

    except NoReaderFoundError:
        print('Error: please connect a device.')
    except InvalidCardResponseError:
        print('Error: invalid response received from the device.')
    except WalletError as e:
        print('Error: ' + e.message)


if __name__ == "__main__":
    main()
