## Installation

Primero, instalar CouchDB en el equipo y crear una cuenta de administrador con las credenciales
introducidas en el instalador. Esto se hace desde la interfaz de CouchDB a la que se puede acceder
mediante la url http://127.0.0.1:5984/

Ejecutar los siguientes comandos para instalar las dependencias y arrancar el servidor

```
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```