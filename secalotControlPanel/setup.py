from setuptools import setup, find_packages

setup(
    name='secalotControlPanel',
    version='1.3',
    packages=['secalotCP'],
    install_requires=[
        'PyQt5>=5.11',
        'pyscard',
        'mnemonic',
        'qrcode',
        'zeroconf',
        'sip',
        'pillow',
        'tlslite-ng',
        'base58check',
    ],
    python_requires='>=3.6',
    url='https://github.com/Secalot/secalot.utilities/tree/master/secalotControlPanel',
    license='Mozilla Public License, v. 2.0',
    author='Matvey Mukha',
    author_email='matvey.mukha@gmail.com',
    description='Secalot Control Panel',
    
    entry_points={
        'gui_scripts': [
            'secalotControlPanel=secalotCP.secalotControlPanel:main',
        ],
        'console_scripts': [
            'scpUpdateFirmware=secalotCP.updateFirmware:main',
            'scpTotpService=secalotCP.totpService:main',
            'scpOtpControl=secalotCP.otpControl:main',            
            'scpEthControl=secalotCP.ethControl:main',
            'scpSslControl=secalotCP.sslControl:main',
            'scpXrpControl=secalotCP.xrpControl:main',
        ],
    },    
)
