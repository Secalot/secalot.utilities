# Secalot utilities.
# Copyright (c) 2018 Matvey Mukha <matvey.mukha@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import smartcard.System
from collections import namedtuple
from mnemonic import Mnemonic

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


class EnglishMnemonic(Mnemonic):
    @classmethod
    def list_languages(cls):
        return ['english']


AppInfo = namedtuple('AppInfo', 'version walletInitialized pinVerified')


def seed(seedText):

    mnemonic = EnglishMnemonic('english')

    if seedText.startswith('0X') or seedText.startswith('0x'):
        seedText = seedText[2:]

    seedIsANumber = True

    try:
        seed = bytearray.fromhex(seedText)
    except:
        seedIsANumber = False

    if seedIsANumber == False:
        if mnemonic.check(seedText) == False:
            raise argparse.ArgumentTypeError('The seed mnemonic is invalid')
        seed = mnemonic.to_seed(seedText)
    else:
        if len(seed) > 64 or len(seed) < 32:
            raise argparse.ArgumentTypeError('The value should be 32 to 64 bytes long')

    return seed


def pin(string):

    if len(string) < 4 or len(string) > 32:
        raise argparse.ArgumentTypeError('Pin length should be between 4 and 32 bytes')

    return string.encode('utf-8')

def derivationPath(string):

    if not string.startswith('m/'):
        raise argparse.ArgumentTypeError('Invalid derivation path')

    string = string[2:]

    indexList = string.split('/')

    if len(indexList) < 1 or len(indexList) > 10:
        raise argparse.ArgumentTypeError('Invalid derivation path')

    intIndexes = []

    for index in indexList:
        try:
            if index.endswith('\''):
                index = index[:-1]
                index = int(index) | 0x80000000
            else:
                index = int(index)

            intIndexes.append(index)
        except ValueError:
            raise argparse.ArgumentTypeError('Invalid derivation path')

    return intIndexes


def parse_arguments():
    parser = argparse.ArgumentParser(description='Ethereum control.')
    parser._optionals.title = 'Options'
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = True

    parserGetInfo = subparsers.add_parser('getInfo', help='Get wallet info.')

    parserInitWallet = subparsers.add_parser('initWallet', help='Initialise the wallet')
    parserInitWallet._optionals.title = 'Options'
    parserInitWallet.add_argument('--seed', required=True, type=seed, help=('Bip32 seed. As a hex number or as a Bip39 mnemonic.'))
    parserInitWallet.add_argument('--pin', required=True, type=pin, help=('New PIN-code.'))

    parserVerifyPin = subparsers.add_parser('verifyPin', help='Verify PIN-code')
    parserVerifyPin._optionals.title = 'Options'
    parserVerifyPin.add_argument('--pin', required=True, type=pin, help=('PIN-code.'))

    parserWipeoutWallet = subparsers.add_parser('wipeoutWallet', help='Erase the wallet.')

    parserGetPublicKey = subparsers.add_parser('getPublicKey', help='Get a public key')
    parserGetPublicKey._optionals.title = 'Options'
    parserGetPublicKey.add_argument('--derivationPath', required=True, type=derivationPath, help=('Bip32 derivation path'))

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
        [0x00, 0xA4, 0x04, 0x00, 0x09, 0x45, 0x54, 0x48, 0x41, 0x50, 0x50, 0x4C, 0x45, 0x54])
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
        version = format(response[0], 'x') + '.' + format(response[1], 'x'),
        walletInitialized = (response[2] & 0x01 == 0x01),
        pinVerified = (response[2] & 0x02 == 0x02)
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

def initWallet(connection, seed, pin):

    selectApp(connection)

    data = bytearray()

    data.append(len(pin))
    data += pin
    data.append(len(seed))
    data += seed

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

def getPublicKey(connection, derivationPath):

    selectApp(connection)

    indexArray = bytearray()

    for index in derivationPath:
        indexArray += index.to_bytes(4, 'big')

    response, sw1, sw2 = connection.transmit([0x80, 0x40, 0x00, 0x00] + [len(indexArray)+1] + [len(derivationPath)] + list(indexArray))

    if sw1 != 0x90 or sw2 != 00:
        if sw1 == 0x6d and sw2 == 0x00:
            raise WalletError("NOT_INIT", 'Wallet not initialized')
        elif sw1 == 0x69 and sw2 == 0x82:
            raise WalletError("PIN_NOT_VERIFIED", 'PIN-code not verified.')
        else:
             raise InvalidCardResponseError()

    if len(response) != (65+32):
        raise InvalidCardResponseError()

    publicKey = bytes(response[:65])
    chainCode = bytes(response[65:])

    return publicKey, chainCode

def main():
    arguments = parse_arguments()

    try:
        connection = findConnectedDevice()
        if arguments.subcommand == 'initWallet':
            initWallet(connection, arguments.seed, arguments.pin)
        elif arguments.subcommand == 'getPublicKey':
            publicKey, chainCode = getPublicKey(connection, arguments.derivationPath)
            print('Public key: ' + ''.join(format(x, '02x') for x in publicKey))
            print('Chaincode: ' + ''.join(format(x, '02x') for x in chainCode))
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

    except NoReaderFoundError:
        print('Error: please connect a device.')
    except InvalidCardResponseError:
        print('Error: invalid response received from the device.')
    except WalletError as e:
        print('Error: ' + e.message)

if __name__ == "__main__":
    main()
