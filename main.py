from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from notify2 import init as notify_init, Notification

import os
import sys
import subprocess
import signal
import shutil
import logging

def pyinstaller_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class App(QSystemTrayIcon):
    def __init__(self,  parent=None, app_name="EnigmaCurry.com", app_url="https://www.enigmacurry.com"):
        # Fix the app so Ctrl-C works : https://stackoverflow.com/a/1357015/56560
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        notify_init(os.path.basename(__file__), 'glib')

        self._app_name=app_name
        self._app_url = app_url
        self._q_app = QApplication([])
        self._q_app.setQuitOnLastWindowClosed(False)

        QSystemTrayIcon.__init__(self, parent)
        self.setIcon(QIcon(pyinstaller_resource_path("icon.png")))
        self.show()
        self.activated.connect(self.onTrayIconActivated)

        menu = QMenu()
        open_action = QAction(QIcon("SP_ComputerIcon"), "Open App", menu)
        open_action.triggered.connect(self.open)
        menu.addAction(open_action)
        quit_action = QAction(QIcon("application-exit"), "&Exit", menu)
        quit_action.triggered.connect(self.quit)
        menu.addAction(quit_action)
        self.setContextMenu(menu)

        self._notifications = []
        self.notify("title", "hello")

    def onTrayIconActivated(self, reason):
        if reason == 3: # Left Click
            self.open()

    def quit(self):
        for notification in self._notifications:
            notification.close()
        try:
            self._browser_process.kill()
        except AttributeError:
            pass
        sys.exit(0)

    def open(self, *args, **kwargs):
        try:
            self._browser_process.wait(0.1)
        except subprocess.TimeoutExpired:
            return # app already open
        except AttributeError:
            pass
        self._browser_process = subprocess.Popen(("electron", self._app_url))

    def notify(self, title, message, timeout=10):
        n = Notification("{app} - {title}".format(app=self._app_name, title=title),
                     message, pyinstaller_resource_path("icon.png"))
        n.timeout = timeout * 1000
        n.add_action("open", "Open App", self.open)
        n.show()
        self._notifications.append(n)

    def run(self):
        if not shutil.which("electron"):
            print("You must install electron - https://github.com/electron/electron/releases/latest")
            sys.exit(1)
        self._q_app.exec_()

def main():
    logging.basicConfig(level=logging.INFO)
    app = App()
    app.run()

if __name__ == "__main__":
    main()

