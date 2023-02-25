from PyQt5 import QtCore
import select
import socket
from DataAccess.FixtureData import FixtureData
import pickle


class FixtureSocket(QtCore.QThread):
    HEADER_LENGTH = 10
    testing_status_changed = QtCore.pyqtSignal(str, bool)

    def __init__(self) -> None:
        QtCore.QThread.__init__(self)

        self._fixtureData = FixtureData()

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((socket.gethostname(), 5001))
        self._socket.listen()
        self.sockets_list = [self._socket]

    def run(self):
        while True:
            read_sockets, _, exception_sockets = select.select(
                self.sockets_list, [], self.sockets_list)

            for notified_socket in read_sockets:
                if notified_socket == self._socket:
                    client_socket, client_address = self._socket.accept()
                    self.sockets_list.append(client_socket)
                else:
                    data = self.receive_data(notified_socket)
                    if data is None:
                        self.sockets_list.remove(notified_socket)
                        continue
                    self.process(notified_socket, data)

            for notified_socket in exception_sockets:
                self.sockets_list.remove(notified_socket)

    def receive_data(self, client_socket):
        try:
            message_header = client_socket.recv(FixtureSocket.HEADER_LENGTH)
            if not len(message_header):
                return None
            message_length = int(message_header.decode('utf-8').strip())
            return pickle.loads(client_socket.recv(message_length))
        except Exception as e:
            print("error: ", str(e))
            return None

    def process(self, notified_socket, data: dict):
        if (data["message"] == "TEST_START"):
            fixture = self._fixtureData.find(data["fixtureIp"])
            if fixture != None:
                fixtureData = {"fixtureIp": fixture.ip,
                               "isDisabled": fixture.is_disabled()}
                notified_socket.send(pickle.dumps(fixtureData))
            self.testing_status_changed.emit(data["fixtureIp"], True)
        elif (data["message"] == "TEST_END"):
            self.testing_status_changed.emit(data["fixtureIp"], False)
