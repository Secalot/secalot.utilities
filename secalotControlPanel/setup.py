from setuptools import setup, find_packages

setup(
    name='secalotControlPanel',
    version='1.1',
    packages=['secalotCP'],
    install_requires=[
        'PyQt5>=5.8',
        'pyscard',
        'mnemonic'
    ],
    python_requires='>=3.5',
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
        ],
    },    
)
