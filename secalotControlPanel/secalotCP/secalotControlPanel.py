# Secalot utilities.
# Copyright (c) 2017 Matvey Mukha <matvey.mukha@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from PyQt5.QtCore import Qt, QCoreApplication, QUrl, pyqtSignal, pyqtSlot, QObject
from PyQt5.QtGui import QIcon
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtWidgets import QSystemTrayIcon, QApplication, QMenu, QAction

import sys
import os
import platform

import secalotCP.resources

from secalotCP.deviceFinder import DeviceFinder
from secalotCP.deviceCommunicator import DeviceCommunicator
from secalotCP.qmlHelperUtils import QmlHelperUtils
from secalotCP.remoteScreen import RemoteScreen


class SystemTray(QObject):
    openAppMenuItemClicked = pyqtSignal()
    exitMenuItemClicked = pyqtSignal()

    def __init__(self):
        QObject.__init__(self)

        menu = QMenu()

        openAction = QAction(self.tr("Open Secalot Control Panel"), self)
        exitAction = QAction(self.tr("Quit"), self)

        menu.addAction(openAction)
        menu.addAction(exitAction)

        openAction.triggered.connect(self.openAppMenuItemClicked)
        exitAction.triggered.connect(self.exitMenuItemClicked)

        self.trayIcon = QSystemTrayIcon(None)

        self.trayIcon.setContextMenu(menu)
        self.trayIcon.setIcon(QIcon(":/gui/icon.png"))
        self.trayIcon.show()

        self.trayIcon.activated.connect(self.iconClicked)

    @pyqtSlot("QSystemTrayIcon::ActivationReason")
    def iconClicked(self, i):
        if i == QSystemTrayIcon.DoubleClick:
            self.openAppMenuItemClicked.emit()


def main():
    # QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

    global app
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(":/gui/icon.png"))

    systemTray = SystemTray()

    os.putenv("QML_DISABLE_DISK_CACHE", "true");

    engine = QQmlApplicationEngine()

    deviceFinder = DeviceFinder()
    deviceCommunicator = DeviceCommunicator()
    qmlHelperUtils = QmlHelperUtils()
    remoteScreen = RemoteScreen(engine, deviceCommunicator)

    if platform.system() == 'Windows':
        if getattr(sys, 'frozen', False):
            engine.addImportPath(sys._MEIPASS)
            os.environ["PATH"] = sys._MEIPASS

    engine.rootContext().setContextProperty("deviceCommunicator", deviceCommunicator)
    engine.rootContext().setContextProperty("deviceFinder", deviceFinder)
    engine.rootContext().setContextProperty("qmlHelperUtils", qmlHelperUtils)
    engine.rootContext().setContextProperty("remoteScreenRoutines", remoteScreen)
    engine.rootContext().setContextProperty("systemTray", systemTray)

    engine.load(QUrl("qrc:/gui/SecalotControlPanel.qml"))

    deviceFinder.start()

    app.exec()

    deviceCommunicator.cleanup()


if __name__ == "__main__":
    main()
