import mysql.connector


class MySqlConnector:
    DEFAULT_HOST = "localhost"
    DEFAULT_USER = "root"
    DEFAULT_PASSWORD = ""
    DEFAULT_DATABASE = "xandra"

    def __init__(
        self,
        host: str = None,
        user: str = None,
        password: str = None,
        database: str = None,
    ) -> None:
        self.host = host or MySqlConnector.DEFAULT_HOST
        self.user = user or MySqlConnector.DEFAULT_USER
        self.password = password or MySqlConnector.DEFAULT_PASSWORD
        self.database = database or MySqlConnector.DEFAULT_DATABASE

    def getConnector(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
        )
