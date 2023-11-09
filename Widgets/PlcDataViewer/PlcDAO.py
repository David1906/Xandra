import logging
from timeit import default_timer as timer
from Widgets.PlcDataViewer.NullPlcStatus import NullPlcStatus
from Widgets.PlcDataViewer.PlcAddress import PlcAdress
from Widgets.PlcDataViewer.PlcStatus import PlcStatus
import modbus_tk.defines as cst
import modbus_tk.modbus_tcp as modbus_tcp
import os


class PlcDAO:
    def __init__(self, ip: str, port: int) -> None:
        self._ip = ip
        self.modbusMaster = modbus_tcp.TcpMaster(ip, port)
        self.modbusMaster.set_timeout(10)
        self._debounceTimer = timer()
        self._lastStatus: PlcStatus = None
        self._statusRetry = 0

    def get_status_debounced(
        self, seconds: float = 2.0, maxRetry: int = 3
    ) -> PlcStatus:
        try:
            if self.is_time_elapsed(seconds) or self._lastStatus == None:
                self._lastStatus = self.get_status()
                self._debounceTimer = timer()
        except Exception as e:
            if self._statusRetry >= maxRetry or self._lastStatus == None:
                self._lastStatus = NullPlcStatus()
                self._statusRetry = 0
            else:
                self._statusRetry += 1
            logging.error(str(e))
            print(str(e))
        return self._lastStatus

    def is_time_elapsed(self, seconds: float) -> bool:
        return (timer() - self._debounceTimer) >= seconds

    def get_status(self) -> PlcStatus:
        if not self.can_ping():
            raise Exception(f"Can't ping {self._ip}")
        chunk_1 = self.modbusMaster.execute(
            1,
            cst.READ_HOLDING_REGISTERS,
            PlcAdress.START_CHUNK1,
            PlcAdress.CHUNK1_LEN,
        )
        chunk_2 = self.modbusMaster.execute(
            1,
            cst.READ_HOLDING_REGISTERS,
            PlcAdress.START_CHUNK2,
            PlcAdress.CHUNK2_LEN,
        )
        chunk_3 = self.modbusMaster.execute(
            1,
            cst.READ_HOLDING_REGISTERS,
            PlcAdress.START_CHUNK3,
            PlcAdress.CHUNK3_LEN,
        )
        plcStatus = PlcStatus()
        plcStatus.set_data(rawData=chunk_1 + chunk_2 + chunk_3)
        return plcStatus

    def can_ping(self) -> bool:
        rep = os.system("timeout 1s ping -c1 " + self._ip + " > 1")
        return rep == 0
