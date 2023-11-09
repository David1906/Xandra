from PlcAddress import PlcAdress
from PlcStatus import PlcStatus
import modbus_tk.defines as cst
import modbus_tk.modbus_tcp as modbus_tcp
import os
import time


class PlcDAO:
    def __init__(self, ip: str, port: int) -> None:
        self._ip = ip
        self.modbusMaster = modbus_tcp.TcpMaster(ip, port)
        self.modbusMaster.set_timeout(10)

    def get_plc_status(self) -> PlcStatus:
        try:
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
        except:
            print("Error get plc status")
            time.sleep(10)

    def ping(self) -> bool:
        rep = os.system("ping -c 1 " + self._ip + " > 1")
        return rep == 0
