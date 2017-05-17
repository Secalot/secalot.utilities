# -*- mode: python -*-

import os

block_cipher = None

qtPath = os.path.normpath(os.environ['QTDIR'])
qtBinPath = os.path.join(qtPath, 'bin')
qtQmlPath = os.path.join(qtPath, 'qml')
extraLibsPath = os.path.normpath(os.environ['SECALOT_LIBS'])
ucrtLibPath = os.path.join(extraLibsPath, 'ucrt')
openglLibPath = os.path.join(extraLibsPath, 'opengl')

a = Analysis(['secalotControlPanel.py'],
             pathex=[qtBinPath, ucrtLibPath],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

a.binaries += Tree(ucrtLibPath, prefix='', typecode='BINARY' )
a.binaries += Tree(openglLibPath, prefix='', typecode='BINARY' )
             
a.binaries += Tree(os.path.join(qtQmlPath, 'Qt'), prefix='Qt', typecode='DATA' )
a.binaries += Tree(os.path.join(qtQmlPath, 'QtQml'), prefix='QtQml', typecode='DATA' )
a.binaries += Tree(os.path.join(qtQmlPath, 'QtQuick'), prefix='QtQuick', typecode='DATA' )
a.binaries += Tree(os.path.join(qtQmlPath, 'QtQuick.2'), prefix='QtQuick.2', typecode='DATA' )

a.binaries += [ ('Qt5Quick.dll', os.path.join(qtBinPath, 'Qt5Quick.dll'), 'BINARY' ) ]
a.binaries += [ ('Qt5QuickControls2.dll', os.path.join(qtBinPath, 'Qt5QuickControls2.dll'), 'BINARY' ) ]
a.binaries += [ ('Qt5QuickParticles.dll', os.path.join(qtBinPath, 'Qt5QuickParticles.dll'), 'BINARY' ) ]
a.binaries += [ ('Qt5QuickTemplates2.dll', os.path.join(qtBinPath, 'Qt5QuickTemplates2.dll'), 'BINARY' ) ]
a.binaries += [ ('Qt5QuickTest.dll', os.path.join(qtBinPath, 'Qt5QuickTest.dll'), 'BINARY' ) ]
a.binaries += [ ('Qt5QuickWidgets.dll', os.path.join(qtBinPath, 'Qt5QuickWidgets.dll'), 'BINARY' ) ]
             
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='secalotControlPanel',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon='gui\\icon.ico')
