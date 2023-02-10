import subprocess
import time


while True:
    cmd = f"XANDRA_FIXTURE_IP=192.167.1.134 /home/david/Xandra/Resources/chk_station_yield.sh -f 1"
    print(cmd)
    subprocess.call(cmd, shell=True)
    time.sleep(1)
