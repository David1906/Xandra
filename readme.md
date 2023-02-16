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
    "App_Path": "**-Path al script chk_station_yield.sh dentro de la carpeta Xandra/Resources-**",
    "App_Args": "",
    "Delay": 2000
},

## Dependencias
-Python 3.8+
-PyQt5 5.15.9+
-xterm
-tmux
-pip install requests