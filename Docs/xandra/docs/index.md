# Inicio

Xandra es un envoltorio al secuenciador FctHostControl intencionado a controlar y monitorear el yield de cada fixtura, de igual manera cuenta con múltiples herramientas para facilitar el mantenimiento y debuggeo de fallas relacionadas con el producto Lunar Bahubali.

## Commands

* `xandra` - Inicia Xandra y todas sus dependencias.
* `xandra-config` - Abre el archivo de configuración de xandra.
* `tmux new -d "python3 /usr/local/Foxconn/automation/Xandra/xandra.py"` - Inicia el programa xandra desprendido de la terminal.
* `systemctl start xampp.service` - Inicia el servidor Xampp que contiene la base de datos utilizada por Xandra.

## Agregar qué es cada configuración

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.
