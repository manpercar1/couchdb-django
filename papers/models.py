#from django.db import models

from django.conf import settings
from couchdb import Server
from couchdb.mapping import Document, TextField

# instalación de la conexión a CouchDB con las tablas
SERVER = Server(getattr(settings, 'COUCHDB_SERVER', 'http://127.0.0.1:5984'))
SERVER.resource.credentials =  ('manpercar1', 'vivanavas227sevilla')

if ('equipos' not in SERVER):
    SERVER.create('equipos')

if ('jugadores' not in SERVER):
    SERVER.create('jugadores')


# Create your models here.

class Equipo(Document):
    nombre = TextField()
    codigo = TextField()
    domicilio = TextField()
    codigoPostal = TextField()
    localidad = TextField()
    provincia = TextField()
    categoria = TextField()
    email = TextField()
    
    def __str__(self):
        return self.nombre + ", " + self.localidad + "(" + self.provincia + ")"

class Jugador(Document):
    nombre = TextField()
    apellidos = TextField()
    
    def __str__(self):
        return self.nombre + " " + self.apellidos
