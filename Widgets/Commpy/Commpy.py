import os
import subprocess
import sqlite3
import sys
import re
import time
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi
from threading import Thread

from Utils.PathHelper import PathHelper


class Commpy(QMainWindow):
    def __init__(self, tmux: str, sn, directory: str, fixtureId: int, parent=None):
        super(Commpy, self).__init__()
        loadUi("Widgets/Commpy/console_3.ui", self)
        self.process = QtCore.QProcess(self)
        self.terminal = QtWidgets.QWidget(self)
        self.coo.addWidget(self.terminal)
        self._rootPath = PathHelper().get_root_path() + "/Widgets/Commpy/"
        self._sql = sqlite3.connect(f"{self._rootPath}test.db")
        self._directory = directory
        subprocess.Popen(["tmux", "new", "-d", "-s", tmux])
        self.tmux = tmux
        self.sn = sn
        self.fixtureId = fixtureId
        self.setWindowTitle(tmux.upper())
        self.process.start(
            "xterm",
            [
                "-into",
                str(int(self.winId())),
                "-g",
                "183x70",
                "-e",
                "tmux",
                "a",
                "-t",
                "%s" % tmux,
            ],
        )
        "# Aqui declaro a que widget redirigen los botones superiores "
        self.bt_ipmiol.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pg_ipmi)
        )
        self.bt_ipmiol_2.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.Nitro)
        )
        self.bt_usbs.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pg_usb)
        )
        self.bt_adv.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pg_adv)
        )
        self.bt_test.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pg_ipmi)
        )
        self.bt_ip.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.ipfix)
        )
        self.bt_usr_com.clicked.connect(lambda: self.kv4_ip())
        "# Aqui declaro las acciones para obtener la ip "
        self.getip1.stateChanged.connect(lambda: self.egg_ip(1, 0))
        self.getip1_2.stateChanged.connect(lambda: self.egg_ip(1, 1))
        self.getip1_3.stateChanged.connect(lambda: self.egg_ip(1, 2))
        self.getip1_4.stateChanged.connect(lambda: self.egg_ip(1, 3))
        self.getip1_5.stateChanged.connect(lambda: self.egg_ip(1, 4))
        self.getip1_6.stateChanged.connect(lambda: self.egg_ip(1, 5))
        self.getip1_7.stateChanged.connect(lambda: self.egg_ip(1, 6))
        self.getip1_8.stateChanged.connect(lambda: self.egg_ip(1, 7))
        self.getip1_9.stateChanged.connect(lambda: self.egg_ip(1, 8))
        self.getip1_10.stateChanged.connect(lambda: self.egg_ip(1, 9))

        # Seleccion automática de fixtura
        if self.fixtureId == 1:
            self.getip1.setChecked(True)
        else:
            getattr(self, f"getip1_{self.fixtureId}").setChecked(True)

        "# Aqui declaro a que widget redirigen los botones de la pagina advance de IPMIOL "
        self.bt_cycle.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.ipfix)
        )
        self.bt_advfru.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pg_fur_adv)
        )
        self.bt_adv_sdr.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pg_sdr_adv)
        )
        self.bt_sol.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pg_sol)
        )
        self.bt_ipmi.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.adv_ipmi)
        )
        self.bt_mc_2.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.mc)
        )
        self.bt_boot.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.bootstrap)
        )
        self.bt_linux.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.Linux_adv)
        )
        self.btn_sol.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.ntr_sol)
        )
        self.btn_sensor.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.ntr_sdr)
        )
        self.btn_coap.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.coap)
        )
        self.btn_up.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.update)
        )
        self.bt_test.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.tests)
        )
        self.bt_stop.clicked.connect(lambda: self.linuxx("^C", "", "1"))
        "# Aqui declaro las acciones de los botones de ipmmiol"
        self.bt_pwr_off.clicked.connect(lambda: self.keto("power off", "", "1"))
        self.bt_pwr_on.clicked.connect(lambda: self.keto("power on", "", "1"))
        self.bt_pwr_cyc.clicked.connect(
            lambda: self.keto("chassis power cycle", "", "1")
        )
        self.bt_fru.clicked.connect(lambda: self.keto("fru", "", "1"))
        self.bt_sel.clicked.connect(lambda: self.keto("sel elist", "", "1"))
        self.bt_mc.clicked.connect(lambda: self.keto("mc info", "", "1"))
        self.bt_sensor.clicked.connect(lambda: self.keto("sensor", "", "1"))
        self.bt_sel_clr.clicked.connect(lambda: self.keto("sel clear", "", "1"))
        self.bt_sdr.clicked.connect(lambda: self.keto("sdr", "", "1"))
        self.bt_host_ip.clicked.connect(lambda: self.keto("0x00", "", "1"))
        self.bt_k2t_ip.clicked.connect(lambda: self.keto("0x02", "", "1"))
        self.bt_ok_fru.clicked.connect(
            lambda: self.keto("fru", self.line_grep_fru, "2")
        )
        self.bt_ok_3.clicked.connect(lambda: self.keto("sdr", self.line_sdrg, "2"))
        self.bt_ok_2.clicked.connect(
            lambda: self.keto("sensor", self.line_grepsen, "2")
        )
        self.bt_okis.clicked.connect(lambda: self.keto(self.line_ipmi, "", ""))
        self.bt_ok_sol2.clicked.connect(lambda: self.keto(self.line_raw, "", ""))
        self.bt_ok_sol.clicked.connect(lambda: self.keto(self.line_com, "", ""))
        self.bt_0x00.clicked.connect(lambda: self.keto("raw 0x34 0x61 0x00", "", "1"))
        self.bt_0x02.clicked.connect(lambda: self.keto("raw 0x34 0x61 0x02", "", "1"))
        self.bt_sola.clicked.connect(lambda: self.keto("sol activate", "", "1"))
        self.bt_sold.clicked.connect(lambda: self.keto("sol deactivate", "", "3"))
        self.bt_cold.clicked.connect(lambda: self.keto("mc reset cold", "", "1"))
        self.bt_mci.clicked.connect(lambda: self.keto("mc info", "", "1"))
        self.bt_start2.clicked.connect(
            lambda: self.keto("apos_chk_k2v4_bootstrap.sh", self.sn1, "")
        )
        self.bt_start.clicked.connect(
            lambda: self.keto("apos_chk_k2v4_bootstrap.sh", self.sn1_2, "")
        )
        self.pushButton.clicked.connect(lambda: self.keto("mc reset cold", "", "c"))
        "#botones para el aptado de linux y set up del pxe"
        self.bt_arp.clicked.connect(lambda: self.linuxx("arp -n", "", "1"))
        self.bt_dhcpd.clicked.connect(
            lambda: self.linuxx("systemctl restart dhcpd.service", "", "1")
        )
        self.bt_ifcong.clicked.connect(lambda: self.linuxx("ifconfig", "", "1"))
        self.bt_pwd.clicked.connect(lambda: self.linuxx("pwd", "", "1"))
        self.bt_unamer.clicked.connect(lambda: self.linuxx("uname -a", "", "1"))
        self.bt_unamer_2.clicked.connect(
            lambda: self.linuxx("sh /home/root/nat.sh", "", "1")
        )
        self.bt_lspci.clicked.connect(lambda: self.linuxx("lspci", "", "1"))
        self.bt_okl3.clicked.connect(lambda: self.linuxx("ping", self.sn1_5, "2"))
        self.bt_okl2.clicked.connect(lambda: self.linuxx("ifconfig", self.sn1_4, "2"))
        self.bt_okl.clicked.connect(
            lambda: self.linuxx("arp -n |grep", self.sn1_3, "2")
        )
        self.bt_ifd.clicked.connect(lambda: self.linuxx("ifdown", self.comboBox, "3"))
        self.bt_ifu.clicked.connect(lambda: self.linuxx("ifup", self.comboBox, "3"))
        self.bt_etool.clicked.connect(
            lambda: self.linuxx("ethtool -i", self.comboBox_2, "3")
        )
        "# Aqui declaro a que widget redirigen los botones de la pagina Nitro "
        self.nt_sol_a.clicked.connect(
            lambda: self.keto("sol select channel-id", self.ntr_sol_select, "n3")
        )
        self.nt_sol_d.clicked.connect(lambda: self.keto("sol deactivate", "", "3"))
        self.nt_ok.clicked.connect(
            lambda: self.keto("sensors list", self.line_sdrg_nt, "n2")
        )
        self.nt_chk_sen.clicked.connect(lambda: self.keto("sensors list", "", "n1"))
        "# Aqui asigno la funcion de lo botones de accion "
        self.ts_see_db.clicked.connect(lambda: self.test())
        self.egg_ip(sn, 0)

    def thres(self):
        t1 = Thread(target=self.kv4_ip)
        t1.start()

    def kv4_ip(self):
        global k2v4, ip
        k2v4 = "dhkjasjhdksa"
        while True:
            # k2v4_mac = os.popen("'ipmitool -I lanplus -H %s -U admin -P admin fru print 12|tail -27|head -n 1|awk '{print $4}'' " % (ip.rstrip())).read()
            k2v4_mac = "1D3G5H7T9R1R"
            k2v4_mac = str(k2v4_mac)
            mac_conut = len(k2v4_mac)
            if k2v4_mac != "" and mac_conut == 12:
                a1 = k2v4_mac[0:2].lower()
                a2 = k2v4_mac[2:4].lower()
                a3 = k2v4_mac[4:6].lower()
                a4 = k2v4_mac[6:8].lower()
                a5 = k2v4_mac[8:10].lower()
                a6 = k2v4_mac[10:12].lower()
                mac = a1 + ":" + a2 + ":" + a3 + ":" + a4 + ":" + a5 + ":" + a6
                print(mac)
                pi = os.popen("arp -n |grep -i %s" % mac).read()
                print("this is the ip:", pi)
                if pi == "":
                    self.lb_mensaje.setText("k2v4 iniciando.")
                    time.sleep(1)
                    self.lb_mensaje.setText("k2v4 iniciando..")
                    time.sleep(1)
                    self.lb_mensaje.setText("k2v4 iniciando...")
                    time.sleep(1)
                    self.lb_mensaje.setText("k2v4 iniciando....")
                    time.sleep(1)
                elif pi != "":
                    k2v4 = pi
                else:
                    break

    def cs_go(self, bmcip):
        global ip
        ip = bmcip
        print(ip)
        # TODO self.thres()

    def egg_ip(self, sn, num_fix):
        ip_exist_file = os.path.isfile("%s/log/%s/bmcip.txt" % (self._directory, sn))
        mac_exist_file = os.path.isfile("%s/log/%s/bmcmac.txt" % (self._directory, sn))
        if ip_exist_file:
            ip = (
                os.popen("cat %s/log/%s/bmcip.txt" % (self._directory, sn))
                .read()
                .rstrip()
            )
            self.cs_go(ip)
        elif mac_exist_file:
            mac = (
                os.popen("cat %s/log/%s/bmcmac.txt" % (self._directory, sn))
                .read()
                .rstrip()
            )
            ip = (
                os.popen("%s/get_bmcip_mac.sh -s %s" % (self._rootPath, mac))
                .read()
                .rstrip()
            )
            self.cs_go(ip)
        elif not ip_exist_file and not mac_exist_file:
            file1 = open("%s/log/golden_bmcmac.txt" % self._directory, "r")
            rr = file1.readlines()[num_fix]
            ip = (
                os.popen("%s/get_bmcip_mac.sh -s %s" % (self._rootPath, rr))
                .read()
                .rstrip()
            )
            self.cs_go(ip)
        else:
            ip = ""
            self.cs_go(ip)

    def keto(self, arch_1, blue_label, switch):
        if switch == "1":
            os.system(
                'tmux send-keys -t %s "ipmitool -I lanplus -H %s -U admin -P admin %s" Enter'
                % (self.tmux, ip.rstrip(), arch_1)
            )
            print(ip)
        elif switch == "2":
            grep_egg = blue_label.text()
            os.system(
                'self.tmux send-keys -t %s "ipmitool -I lanplus -H %s -U admin -P admin %s |grep %s" Enter'
                % (self.tmux, ip.rstrip(), arch_1, grep_egg)
            )
        elif switch == "3":
            os.system(
                "ipmitool -I lanplus -H %s -U admin -P admin %s" % (ip.rstrip(), arch_1)
            )
        elif switch == "n1":
            os.system(
                'tmux send-keys -t %s "sh %s -i %s %s" Enter'
                % (self.tmux, self._get_nitro_bmc_path(), ip.rstrip(), arch_1)
            )
        elif switch == "n2":
            cb = blue_label.text()
            cb = cb.rstrip()
            os.system(
                'tmux send-keys -t %s "sh %s -i %s %s |grep %s" Enter'
                % (self.tmux, self._get_nitro_bmc_path(), ip.rstrip(), arch_1, cb)
            )
        elif switch == "n3":
            cb = blue_label.currentText()
            cb = cb[0:2]
            os.system(
                'tmux send-keys -t %s "sh %s -i %s %s %s" Enter'
                % (self.tmux, self._get_nitro_bmc_path(), ip.rstrip(), arch_1, cb)
            )
            time.sleep(2)
            os.system(
                'tmux send-keys -t %s "sh %s -i %s sol activate -u admin -p admin" Enter'
                % (self.tmux, self._get_nitro_bmc_path(), ip.rstrip())
            )
        elif switch == "c":
            os.system(
                'tmux send-keys -t %s "coap -O65001,0 -Y coaps+tcp://%s/%s" Enter'
                % (self.tmux, self._directory, k2v4.rstrip())
            )

    def _get_nitro_bmc_path(self):
        path1 = "%s/tool/Nitro/1.0.353.0/nitro-bmc" % (self._directory)
        if os.path.isfile(path1):
            return path1
        return "%s/tool/Nitro/nitro-bmc" % (self._directory)

    def fru_burn(self, arch, lb1, lb2, lb3, select):
        if select == "1":
            print("")
        elif select == "2":
            print("")

    def linuxx(self, info, arch, switch):
        if switch == "1":
            os.system('tmux send-keys -t %s "%s" Enter' % (self.tmux, info))
        elif switch == "2":
            grep_egg = arch.text()
            os.system(
                'tmux send-keys -t %s "%s %s" Enter'
                % (self.tmux, info, grep_egg.rstrip())
            )
        elif switch == "3":
            cb = arch.currentText()
            os.system(
                'tmux send-keys -t %s "%s %s" Enter' % (self.tmux, info, cb.rstrip())
            )
        elif switch == "4":
            os.system('tmux send-keys -t %s "systemctl stop ntpd.service" Enter')
            time.sleep(1)
            os.system('tmux send-keys -t %s "systemctl disable ntpd.service" Enter')

    def sh(self, test):
        os.system(
            'tmux send-keys -t %s "sh %s/script/%s -s %s" Enter'
            % (self.tmux, self._directory, test.rstrip(), self.sn)
        )

    def test(self):
        cur = self._sql.cursor()
        sqlquery = "SELECT * FROM pruebas"
        self.test_select.setRowCount(168)
        tablerow = 0
        for row in cur.execute(sqlquery):
            self.test_select.setItem(tablerow, 0, QtWidgets.QTableWidgetItem(row[0]))
            pybuton = QtWidgets.QPushButton("start", self)
            texto = row[0]
            pybuton.clicked.connect(lambda checked, text=texto: self.sh(text))
            self.test_select.setCellWidget(tablerow, 1, pybuton)
            tablerow += 1
        os.system(
            'tmux send-keys -t %s "cd %s/script/" Enter ' % (self.tmux, self._directory)
        )

    def nitro_5(self):
        print()

    def coap(self):
        print()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_app = Commpy()
    my_app.show()
    sys.exit(app.exec_())
