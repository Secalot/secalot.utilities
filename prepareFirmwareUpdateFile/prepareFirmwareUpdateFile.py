# Secalot utilities.
# Copyright (c) 2017 Matvey Mukha <matvey.mukha@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import argparse
from intelhex import IntelHex
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

BOOTLOADER_START_ADDRESS = 0x00002000
BOOTLOADER_END_ADDRESS = 0x00009FFF
FIRMWARE_START_ADDRESS = 0x0000C000
FIRMWARE_END_ADDRESS = 0x00037FFF
FILESYSTEM_START_ADDRESS = 0x00038000
FILESYSTEM_END_ADDRESS = 0x0003FFFF

IMAGE_TYPE_BOOTLOADER = '1'
IMAGE_TYPE_FIRMWARE = '2'

MAGIC = int(0x424C4F42).to_bytes(4, 'big')

RANDOM_KEY_X = 0x0ddbded14a380c6547ef3cddf506a63a6e0f024ac5a9dbcc079814443885202d
RANDOM_KEY_Y = 0xbab67c2ba1ee610d5a79bee9d43a5ac657bbb42a0ebdce8647bf999c8ee0a582

def hex_dword(string):
    integer = int(string, 16)
    if integer.bit_length() > 32:
        raise argparse.ArgumentTypeError('The value should fit in 4 bytes')
    return integer.to_bytes(4, 'big')

def ecdsa_key(string):
    integer = int(string, 16)
    if len(string) != 64:
        raise argparse.ArgumentTypeError('The value should be 32 bytes long')
    return integer

def parse_arguments():
    parser = argparse.ArgumentParser(description='Prepare a firmware update file.')
    parser._optionals.title = 'Options'
    parser.add_argument('--devID', required=True, type=hex_dword, help='Device ID.')
    parser.add_argument('--fwVer', required=True, type=hex_dword, help='Firmware version.')
    parser.add_argument('--fsVer', required=True, type=hex_dword, help='File system version.')
    parser.add_argument('--blVer', required=True, type=hex_dword, help='Bootloader version.')
    parser.add_argument('--privateKey', required=True, type=ecdsa_key, help='256 bit ECDSA private key to sign the firmware.')
    parser.add_argument('--blHexFile', required=True, type=argparse.FileType('r'), help='File with a bootloader hex image.')
    parser.add_argument('--fwHexFile', required=True, type=argparse.FileType('r'), help='File with a firmware hex image.')
    parser.add_argument('--fsHexFile', required=True, type=argparse.FileType('r'), help=('File with a filesystem hex image. If this parameter is specified, '
                                                        'the generated firmware update file will contain both a firmware and a filesystem.'))
    parser.add_argument('--outputFile', required=True, type=argparse.FileType('wb'), help='Firmware update file to generate.')
    args = parser.parse_args()
    return args

def get_firmware_hex_image(firmwareFile, filesystemFile):
    hex = IntelHex(firmwareFile)
    hex.padding = 0x00

    filesystemHex = IntelHex(filesystemFile)
    filesystemHex.padding = 0x00
    hex.merge(filesystemHex)

    hexImage = hex.tobinstr(FIRMWARE_START_ADDRESS, FILESYSTEM_END_ADDRESS)
    return hexImage

def get_bootloader_hex_image(bootoaderFile):
    hex = IntelHex(bootoaderFile)
    hex.padding = 0x00

    hexImage = hex.tobinstr(BOOTLOADER_START_ADDRESS, BOOTLOADER_END_ADDRESS)
    return hexImage

def sign_image(privateKey, header, hexImage):
    ecPrivateKey = ec.EllipticCurvePrivateNumbers(privateKey, ec.EllipticCurvePublicNumbers(RANDOM_KEY_X, RANDOM_KEY_Y, ec.SECP256R1())).private_key(default_backend())
    signer = ecPrivateKey.signer(ec.ECDSA(hashes.SHA256()))
    signer.update(header)
    signer.update(hexImage)
    signature = signer.finalize()
    rAndS = utils.decode_dss_signature(signature)
    return rAndS[0].to_bytes(32, 'big') + rAndS[1].to_bytes(32, 'big')


def main():
    arguments = parse_arguments()

    print('Generating firmware...')

    fwSignatureHeader = hex_dword(IMAGE_TYPE_FIRMWARE) + arguments.devID + arguments.fwVer + arguments.fsVer + arguments.blVer
    blSignatureHeader = hex_dword(IMAGE_TYPE_BOOTLOADER) + arguments.devID + arguments.blVer
    fileHeader = arguments.devID + arguments.fwVer + arguments.fsVer + arguments.blVer

    blHexImage = get_bootloader_hex_image(arguments.blHexFile)
    fwHexImage = get_firmware_hex_image(arguments.fwHexFile, arguments.fsHexFile)
    blSignature = sign_image(arguments.privateKey, blSignatureHeader, blHexImage)
    fwSignature = sign_image(arguments.privateKey, fwSignatureHeader, fwHexImage)

    arguments.outputFile.write(MAGIC)
    arguments.outputFile.write(fileHeader)
    arguments.outputFile.write(fwSignature)
    arguments.outputFile.write(blSignature)
    arguments.outputFile.write(fwHexImage)
    arguments.outputFile.write(blHexImage)
    arguments.outputFile.close()

    print('Done.')

if __name__ == "__main__":
	main()

