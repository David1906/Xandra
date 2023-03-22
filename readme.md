## Modificar xandra_config.json
- Especificar carpeta donde se guardará el archivo json con la ip de los fixtures deshabilitados "disabledFixturesJson".
- Especificar ruta del archivo FCT Host Control "fctHostControl"
- Especificar ruta del archivo de configuración relacionado con  FCT Host Control "fctHostControlConfig" (De este archivo se obtienen los fixtures y sus respectivas ip)
- Especificar cual es el porcentaje de yield mínimo a partir del cual el fixture se bloqueará.

## Configurar script para validar yield
- Dar permisos de ejecución al script chk_station_yield.sh (chkmod +rwx chk_station_yield.sh)
- En el archivo FCTHostControl.config, en la sección "Check_Station" escribir lo siguiente:
"Check_Station": {
    "Enable": true,
    "App_Path": "/usr/local/Foxconn/automation/Xandra/Resources/chk_station_is_disabled.py",
    "App_Args": "",
    "Delay": 5000
},
"Test_End_Call": {
    "Enable": true,
    "App_Path": "/usr/local/Foxconn/automation/Xandra/Resources/chk_station_test_finished.py",
    "App_Args": "",
    "Delay": 5000
},

## Dependencias
-Python 3.8+
-PyQt5 5.15.9+
-xterm
-tmux
pip install requests-futures
pip3 install -r requirements.txt
pip install pymysql
alembic

## shortcut
[Desktop Entry]
Name=Xandra
Exec=tmux new -d "cd /usr/local/Foxconn/automation/Xandra && python3 /usr/local/Foxconn/automation/Xandra/xandra.py"
Terminal=true
Type=Application
Icon=/usr/local/Foxconn/automation/Xandra/Static/icon.png

## Xampp
https://cytranet.dl.sourceforge.net/project/xampp/XAMPP%20Linux/8.2.0/xampp-linux-x64-8.2.0-0-installer.run

cd /etc/systemd/system/
systemctl enable xampp.service
systemctl start xampp.service

## xampp.service
[Unit]
Description = Xampp server

[Service]
ExecStart =/opt/lampp/lampp start
ExecStop =/opt/lampp/lampp stop
Type=forking
  
[Install]
WantedBy = multi-user.target


## Script x permissions
sed -i -e 's/\r$//' Resources/chk_station_is_disabled.sh

## Migrations
alembic revision --autogenerate -m ""
alembic upgrade head

## SCRIPT CMDS
yum install -y tmux xterm
pip3 install --upgrade pip
pip3 install -r requirements.txt

## Aliases
gedit ~/.bashrc
if [ -f ~/.bash_aliases ]; then
. ~/.bash_aliases
fi

gedit ~/.bash_aliases

# Alias to open Xandra
alias xandra='tmux new -d "cd /usr/local/Foxconn/automation/Xandra && python3 /usr/local/Foxconn/automation/Xandra/xandra.py"'

# Alias to open Xandra in testing mode
alias xandra-testing='ENV=testing python3 /usr/local/Foxconn/automation/Xandra/xandra.py'

# Alias to open Xandra config
alias xandra-config='tmux new -d "gedit /usr/local/Foxconn/automation/Xandra/xandra_config.json"'

# Alias to cd Xandra path
alias xandra-path='cd /usr/local/Foxconn/automation/Xandra'

# Alias to update Xandra
alias xandra-update='chmod +x /usr/local/Foxconn/automation/Xandra/update.sh && /usr/local/Foxconn/automation/Xandra/update.sh'