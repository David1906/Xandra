from datetime import datetime
from Widgets.PlcDataViewer.PlcDAO import PlcDAO
import os
import re
import time


ip = ""
isValidIP = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
while not isValidIP.match(ip):
    ip = input("Enter plc ip: ")

plcDAO = PlcDAO(ip, port=502)
f = open(f"plclog_{ip}.txt", "w")
try:
    while True:
        try:
            msg = "Ping error"
            if plcDAO.can_ping():
                plcStatus = plcDAO.get_status()
                attributes = vars(plcStatus)
                msg = ""
                for attribute, value in attributes.items():
                    msg += f"{attribute} = {value}\n"
                msg += str(datetime.today())
        except Exception as e:
            msg = "Error: " + str(e)
        finally:
            result = f"{ '*' * 20}\n{msg}\n"
            f.write(result)
            print(result)
            time.sleep(2)
except KeyboardInterrupt:
    f.close()
