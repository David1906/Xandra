import socket
import pickle


class SocketClient:
    HEADER_LENGTH = 10
    SOCKET_PORT = 5002

    def __init__(self) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(5.0)

    def get_is_disabled(self, fixtureIP: str) -> bool:
        self._socket.connect((socket.gethostname(), SocketClient.SOCKET_PORT))
        message = pickle.dumps({"message": "PRE_TEST_START", "fixtureIp": fixtureIP})
        message_header = f"{len(message):<{SocketClient.HEADER_LENGTH}}".encode("utf-8")
        self._socket.send(message_header + message)
        fixture = pickle.loads(self._socket.recv(1024))
        self._socket.close()
        return fixture["shouldAbortTest"]

    def notify_test_start(self, fixtureIP: str):
        self._socket.connect((socket.gethostname(), SocketClient.SOCKET_PORT))
        message = pickle.dumps(
            {
                "message": "TEST_START",
                "fixtureIp": fixtureIP,
            }
        )
        message_header = f"{len(message):<{SocketClient.HEADER_LENGTH}}".encode("utf-8")
        self._socket.send(message_header + message)
        self._socket.close()

    def notify_test_end(
        self,
        fixtureIP: str,
        serialNumber: str = "",
        logFileName: str = "",
        currentTest: str = "",
    ):
        self._socket.connect((socket.gethostname(), SocketClient.SOCKET_PORT))
        message = pickle.dumps(
            {
                "message": "TEST_END",
                "fixtureIp": fixtureIP,
                "serialNumber": serialNumber,
                "logFileName": logFileName,
                "currentTest": currentTest,
            }
        )
        message_header = f"{len(message):<{SocketClient.HEADER_LENGTH}}".encode("utf-8")
        self._socket.send(message_header + message)
        self._socket.close()
