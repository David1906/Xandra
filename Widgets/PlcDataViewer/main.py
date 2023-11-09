from datetime import datetime
from PlcDAO import PlcDAO
import os
import time
import re


ip = ""
isValidIP = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
while not isValidIP.match(ip):
    ip = input("Enter plc ip: ")

plcDAO = PlcDAO(ip, port=502)
while True:
    try:
        if plcDAO.ping():
            plcStatus = plcDAO.get_plc_status()
            attributes = vars(plcStatus)
            os.system("clear")
            for attribute, value in attributes.items():
                print(attribute, "=", value)
            print(datetime.today())
            time.sleep(2)
        else:
            print("Ping error")
    except Exception as e:
        print("Error: " + str(e))
