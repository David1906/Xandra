# Comandos

## Comandos de terminal

Xandra cuenta con distintos comandos que pueden ejecutarse directamente en la terminal para facilitar la interacción con el usuario. La lista completa es la siguiente:

* `xandra` - Inicia Xandra y todas sus dependencias.
* `xandra-testing` - Inicia Xandra en modo de pruebas.
* `xandra-config` - Abre el archivo de configuración de Xandra en un editor de texto gráfico.
* `xandra-path` - Ingresa a la carpeta de instalación de Xandra mediante el comando cd.
* `xandra-update` - Actualiza y configura Xandra a su versión más reciente.
* `xandra-kill` - Cierra xandra terminando el proceso python3 sobre el cual se ejecuta.
* `xandra-docs` - Abre la documentación de Xandra.
* `xandra-pyenv-activate` - Ingresa a la carpeta de instalación de Xandra mediante el comando cd y activa el entorno virtual de python.
* `xandra-pyenv-deactivate` - Desactiva el entorno virtual de python.

## Atajos de teclado

Dentro de Xandra es posible utilizar distintos atajos de teclado para activar alguna funcionalidad o agilizar el trabajo del usuario, se ha optado por ésta opción sobre la incorporación de menús debido a que se pretende reducir al mínimo la incorrecta manipulación del sistema por parte de usuarios no capacitados para éste fin, como lo puede ser un operador.

* `Ctrl+Shift+A` - Inicia la terminal de todas las fixturas que se encuentren detenidas.
* `Ctrl+Shift+S` - Detiene la terminal de todas las fixturas que se encuentren iniciadas.
* `Ctrl+Shift+G` - Habilita o deshabilita el modo retest (requiere contraseña).
* `Ctrl+Shift+T` - Si se encuentra habilitado el modo retest, con este atajo se permite desbloquear o bloquear el selector de trazabilidad (requiere contraseña).
* `Ctrl+Shift+L` - Habilita o deshabilita el bloqueo de las fixturas (requiere contraseña).

## Comandos para desarrollo

* Crear nueva migración: 
``` shell
alembic revision --autogenerate -m ""
```

* Aplicar migración: 
``` shell
alembic upgrade head
```

* Servir documentación: 
``` shell
mkdocs serve 
```

* Hacer build de documentación: 
``` shell
mkdocs build -d ../../../docs  
```

* Hacer build de traduccion (.mo): 
``` shell
msgfmt -o Resources/locales/es/LC_MESSAGES/base.mo Resources/locales/es/LC_MESSAGES/base
```

* Generar plantilla de traduccion (.pot): 
``` shell
xgettext -d fixture_view -o MainWindow.pot ../../Views/MainWindow.py 
```