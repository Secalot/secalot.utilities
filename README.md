# Secalot Utilities

[Secalot](http://secalot.com) is a small USB dongle that carries four applications on board: a bitcoin wallet, an OpenPGP smart card, a U2F authenticator and a one time passwords generator.

This repository contains utilities that help operating the device.

##Utilities:
###prepareFirmwareUpdateFile
A python script to prepare Secalot firmware update images.
###secalotControlPanel
A GUI application. It can be used to:

 - Change Secalot OTP settings.
 - Flash firmware updates to the device.
 - Start and stop a TOTP service.

## Run With

Please use Python 3 to run the applications.

## License

This project is licensed under the Mozilla Public License Version 2.0 - see the [LICENSE](LICENSE) file for details.
