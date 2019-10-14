#  Created by Andrey Tolkachev
#  andre.deform@gmail.com
#
#  Copyright © 2019
#
#  Graphical PyQt 5 client to work with the chat server
#
import sys
from PyQt5 import QtWidgets
from gui import design

from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineOnlyReceiver


class Client(LineOnlyReceiver):
    factory: 'Connector'

    def connectionMade(self):
        self.factory.window.protocol = self

    def lineReceived(self, line: bytes):
        message = line.decode()
        self.factory.window.plainTextEdit.appendPlainText(message)


class Connector(ClientFactory):
    window: 'ChatWindow'
    protocol = Client

    def __init__(self, app_window):
        self.window = app_window


class ChatWindow(QtWidgets.QMainWindow, design.Ui_MainWindow):
    protocol: Client
    reactor = None

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_handlers()

    def init_handlers(self):
        self.pushButton.clicked.connect(self.send_message)

    def closeEvent(self, event):
        self.reactor.callFromThread(self.reactor.stop)

    def send_message(self):
        message = self.lineEdit.text()

        self.protocol.sendLine(message.encode())
        self.lineEdit.setText('')


app = QtWidgets.QApplication(sys.argv)

from qt5reactor import install

window = ChatWindow()
window.show()

install()

from twisted.internet import reactor

reactor.connectTCP(
    "localhost",
    7410,
    Connector(window)
)

window.reactor = reactor
reactor.run()
