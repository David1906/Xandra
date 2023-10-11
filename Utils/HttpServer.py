from DataAccess.FixtureDAO import FixtureDAO
from http.server import HTTPServer, BaseHTTPRequestHandler
from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from urllib import parse
import json


class HttpServer(QtCore.QThread):
    PORT = 5002
    HOST = "127.0.0.1"

    def __init__(self, parent: QObject) -> None:
        super().__init__(parent)

    def run(self):
        print(f"Listening on http://{self.HOST}:{self.PORT}")
        self._server = HTTPServer((self.HOST, self.PORT), RequestHandler)
        self._server.serve_forever()

    def stop(self):
        self._server.shutdown()
        self._server.socket.close()
        self.wait()
        print("Server stopped")


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/fixture/status"):
            self._get_fixture_status()
        else:
            self.send_error(404)

    def _get_fixture_status(self):
        fixtureIp = self._extract_first_param("fixtureIp")
        response = {
            "fixtureIp": fixtureIp,
            "shouldAbortTest": FixtureDAO().should_abort_test(fixtureIp),
        }
        self._send_ok_headers()
        self.wfile.write(json.dumps(response).encode(encoding="utf_8"))

    def _extract_first_param(self, param: str):
        params = self._extract_params_from_path()[param]
        if params == None:
            return ""
        return params[0]

    def _extract_params_from_path(self) -> "dict[str, list[str]]":
        parsed_path = parse.urlparse(self.path)
        return parse.parse_qs(parsed_path.query)

    def _send_ok_headers(self):
        self.protocol_version = "HTTP/1.1"
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def log_message(self, format, *args):
        return
