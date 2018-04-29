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


AppInfo = namedtuple('AppInfo', 'version walletInitialized')


def masterKey(mkText):

    if mkText.startswith('0X') or mkText.startswith('0x'):
        mkText = mkText[2:]

    try:
        mkText = bytearray.fromhex(mkText)
    except:
        raise argparse.ArgumentTypeError('Master key should be a hex string of 32 bytes')

    if len(mkText) != 32:
        raise argparse.ArgumentTypeError('Master key should be a hex string of 32 bytes')

    return mkText

def tweak(tweakText):

    if tweakText.startswith('0X') or tweakText.startswith('0x'):
        tweakText = tweakText[2:]

    try:
        tweakText = bytearray.fromhex(tweakText)
    except:
        raise argparse.ArgumentTypeError('Tweak should be a hex string of 1 to 10 bytes')

    if len(tweakText) < 1 or len(tweakText) > 10:
        raise argparse.ArgumentTypeError('Tweak should be a hex string of 1 to 10 bytes')

    return tweakText


def hash(hashText):

    if hashText.startswith('0X') or hashText.startswith('0x'):
        hashText = hashText[2:]

    try:
        hashText = bytearray.fromhex(hashText)
    except:
        raise argparse.ArgumentTypeError('Sha256 hash should be a hex string of 32 bytes')

    if len(hashText) != 32:
        raise argparse.ArgumentTypeError('Sha256 hash should be a hex string of 32 bytes')

    return hashText

def randomLength(length):

    length = int(length)

    if length < 0 or length > 256:
        raise argparse.ArgumentTypeError('Length should be between 1 and 256 bytes')

    return length


def parse_arguments():
    parser = argparse.ArgumentParser(description='Symetria control.')
    parser._optionals.title = 'Options'
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = True

    parserGetInfo = subparsers.add_parser('getInfo', help='Get wallet info')

    parserInitWallet = subparsers.add_parser('initWallet', help='Initialise the wallet')
    parserInitWallet._optionals.title = 'Options'
    parserInitWallet.add_argument('--masterKey', required=True, type=masterKey, help=('Master key. A 32 byte hex string'))

    parserWipeoutWallet = subparsers.add_parser('wipeoutWallet', help='Erase the wallet')

    parserGetPublicKey = subparsers.add_parser('getPublicKey', help='Get a public key')
    parserGetPublicKey._optionals.title = 'Options'
    parserGetPublicKey.add_argument('--tweak', required=True, type=tweak, help=('Tweak'))

    parserSignHash = subparsers.add_parser('signHash', help='Sign a hash')
    parserSignHash._optionals.title = 'Options'
    parserSignHash.add_argument('--hash', required=True, type=hash, help=('Sha256 hash'))
    parserSignHash.add_argument('--tweak', required=True, type=tweak, help=('Tweak'))

    parserGetRandom = subparsers.add_parser('getRandom', help='Get random data')
    parserGetRandom._optionals.title = 'Options'
    parserGetRandom.add_argument('--randomLength', required=True, type=randomLength, help=('Length'))

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
        [0x00, 0xA4, 0x04, 0x00, 0x09, 0x53, 0x59, 0x4D, 0x41, 0x50, 0x50, 0x4C, 0x45, 0x54])
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()


def getInfo(connection):

    selectApp(connection)

    response, sw1, sw2 = connection.transmit([0x80, 0x30, 0x00, 0x00])
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()

    if len(response) != 8:
        raise InvalidCardResponseError()

    appInfo = AppInfo(
        version = format(response[0], 'x') + '.' + format(response[1], 'x'),
        walletInitialized = (response[2] & 0x01 == 0x01)
    )

    return appInfo

def getRandom(connection, length):

    selectApp(connection)

    response, sw1, sw2 = connection.transmit([0x80, 0x40, 0x00, 0x00, length])
    if sw1 != 0x90 or sw2 != 00:
        raise InvalidCardResponseError()

    if len(response) != length:
        raise InvalidCardResponseError()

    return response

def initWallet(connection, masterKey):

    selectApp(connection)
    response, sw1, sw2 = connection.transmit([0x80, 0x10, 0x00, 0x00] + [len(masterKey)] + list(masterKey))
    if sw1 != 0x90 or sw2 != 00:
        if sw1 == 0x6d and sw2 == 0x00:
            raise WalletError("ALREADY_INIT", 'Wallet already initialized')
        else:
            raise InvalidCardResponseError()

def wipeoutWallet(connection):

    selectApp(connection)

    response, sw1, sw2 = connection.transmit([0x80, 0x50, 0x00, 0x00])
    if sw1 != 0x90 or sw2 != 00:
        if sw1 == 0x6d and sw2 == 0x00:
            raise WalletError("NOT_INIT", 'Wallet not initialized')
        else:
            raise InvalidCardResponseError()


def getPublicKey(connection, tweak):

    selectApp(connection)

    response, sw1, sw2 = connection.transmit([0x80, 0x20, 0x00, 0x00] + [len(tweak)] + list(tweak))

    if sw1 != 0x90 or sw2 != 00:
        if sw1 == 0x6d and sw2 == 0x00:
            raise WalletError("NOT_INIT", 'Wallet not initialized')
        else:
             raise InvalidCardResponseError()

    if len(response) != (65):
        raise InvalidCardResponseError()

    publicKey = bytes(response[:65])

    return publicKey


def signHash(connection, tweak, hash):

    selectApp(connection)

    data = bytearray()

    data.append(len(tweak))
    data += tweak
    data += hash

    response, sw1, sw2 = connection.transmit([0x80, 0x60, 0x00, 0x00] + [len(data)] + list(data))

    if sw1 != 0x90 or sw2 != 00:
        if sw1 == 0x6d and sw2 == 0x00:
            raise WalletError("NOT_INIT", 'Wallet not initialized')
        else:
             raise InvalidCardResponseError()

    if len(response) != (64):
        raise InvalidCardResponseError()

    signature = bytes(response[:64])

    return signature

def main():
    arguments = parse_arguments()

    try:
        connection = findConnectedDevice()
        if arguments.subcommand == 'initWallet':
            initWallet(connection, arguments.masterKey)
        elif arguments.subcommand == 'getPublicKey':
            publicKey = getPublicKey(connection, arguments.tweak)
            print('Public key: ' + ''.join(format(x, '02x') for x in publicKey))
        elif arguments.subcommand == 'signHash':
            signature = signHash(connection, arguments.tweak, arguments.hash)
            print('Signature: ' + ''.join(format(x, '02x') for x in signature))
        elif arguments.subcommand == 'getRandom':
            random = getRandom(connection, arguments.randomLength)
            print('Random: ' + ''.join(format(x, '02x') for x in random))
        elif arguments.subcommand == 'wipeoutWallet':
            wipeoutWallet(connection)
        elif arguments.subcommand == 'getInfo':
            info = getInfo(connection)
            print('')
            print('App version: ' + info.version)

            if info.walletInitialized == True:
                print('Wallet status: initialized')
            else:
                print('Wallet status: not initialized')

    except NoReaderFoundError:
        print('Error: please connect a device.')
    except InvalidCardResponseError:
        print('Error: invalid response received from the device.')
    except WalletError as e:
        print('Error: ' + e.message)

if __name__ == "__main__":
    main()
