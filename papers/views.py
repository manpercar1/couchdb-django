from django.shortcuts import render

from papers.models import Equipo, SERVER
from papers.forms import BusquedaEquipo

from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from bs4 import BeautifulSoup
import urllib.request, http.cookiejar

from selenium import webdriver

import sys

sys.setrecursionlimit(10000)

db_equipos = SERVER['equipos']
db_jugadores = SERVER['jugadores']

equipoSeleccionado = {}
jugadoresSeleccionados = []
#---------------------------------PARTE DE BUSCAR EQUIPOS-----------------------------------------------------

def extraer_datos_pagina_equipo(url_pagina):

    lista =[]
    #El sitio al que queremos acceder requiere la aceptación previa de Cookies. Por lo tanto, construimos
    #un OpenerDirector con la clase HTTPCookieProcesor para "esquivar" ese paso
    cj = http.cookiejar.CookieJar()
    f = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    #Ahora, podemos acceder a la url
    r = f.open(url_pagina)
    s = BeautifulSoup(r,"lxml")
    l = s.find_all("tr")

    if len(l) == 0:
        return redirect("/errorBS")

    for i in l:
        elementos = i.find_all("td")
        if len(elementos) == 0: #El primer tr que se va a encontrar es de la cabecera de la tabla, que no contiene td
            continue
        codigo = elementos[0].string
        nombre = elementos[2].find_all("a")[0].string
        urlEquipo = elementos[2].find_all("a")[0]['href']
        categoria = elementos[5].string
        
        lista.append((codigo,nombre,urlEquipo,categoria))
    
    return lista

def buscarEquipo(request):

    formulario = BusquedaEquipo()
    resultado = None
    context = []

    if request.method=='POST':
        formulario = BusquedaEquipo(request.POST)
        if formulario.is_valid():
            #PARTE DE BEAUTIFULSOUP
            nombreEquipo = formulario.cleaned_data['nombre']
            nombreEquipo = nombreEquipo.replace(' ', '+') #Sustituimos los espacios en blanco si es un nombre compuesto por el caracter + que es lo que se utiliza en el navegador

            resultado = extraer_datos_pagina_equipo("https://www.rfaf.es/pnfg/NPcd/NFG_LstEquipos?" +
                "cod_primaria=1000119&nueva_ventana=&Buscar=1&orden=&Sch_Clave_Acceso_Club=&" +
                "Sch_Codigo_Club=&Sch_Codigo_Categoria=&Sch_Codigo_Delegacion=&Sch_Clave_Acceso_Campo=&" +
                "Campo=&Sch_Nombre_Equipo="+ str(nombreEquipo) +"&Sch_Categoria_Club=&Sch_Fecha_Inicio=&" +
                "Sch_Fecha_Fin=&NPcd_PageLines=20")

            for equipo in resultado:
                cod = equipo[0]
                nom = equipo[1]
                url = equipo[2]
                cat = equipo[3]

                equ = url[61] + url[62] + url[63] + url[64] + url[65] + url[66]

                #parseamos la categoría para poder mandarla en el enlace luego
                categoria = equipo[3].split(" ")
                numeroCategoria = str(categoria[0]).replace("ª", "")
                categoriaParseada = numeroCategoria + "-" + categoria[1] + "-" + categoria[2]

                aux = {
                    'codigo':cod,
                    'nombre':nom,
                    'codEquipo':equ,
                    'categoria':cat,
                    'categoriaParseada':categoriaParseada
                }

                context.append(aux)

    return render(request, 'papers/buscarEquipo.html', {'formulario':formulario, 'resultado':resultado, 'context':context})

#---------------------------------FIN PARTE DE BUSCAR EQUIPOS-------------------------------------------------

#-----------------------------------PARTE DE DETALLES EQUIPO--------------------------------------------------
def extraer_datos_pagina_detalles_equipo(url, codEquipo):
    
    datos = []
    jugadores = []

    cj = http.cookiejar.CookieJar()
    f = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    #Ahora, podemos acceder a la url
    r = f.open(url)
    s = BeautifulSoup(r,"lxml")
    
    nombre = s.find_all("h2")[0].string

    correspondencia = s.find_all("div", {'style' : 'margin-top: 10px;'})[1].contents
    domicilio = correspondencia[5].contents[1]
    localidad = correspondencia[7].contents[1]
    provincia = correspondencia[9].contents[1]
    codPostal = correspondencia[11].contents[1]
    email = correspondencia[13].contents[1]

    tablaJugadores = s.find_all("table", class_="table table-striped table-hover listadolic")[0]
    listaJugadores = tablaJugadores.find_all("tr")
    
    for i in listaJugadores:
        elementos = i.find_all("td")
        if len(elementos) == 0: #El primer tr que se va a encontrar es de la cabecera de la tabla, que no contiene td
            continue
        
        for elemento in elementos:
            jugador = elemento.h5.string.strip()
            jugadores.append(jugador)

    datos = [nombre, domicilio, localidad, provincia, codPostal, email, codEquipo, jugadores]

    return datos

def guardarEquipo(codEquipo, jugadores, equipo):

    #guardamos el equipo en CouchDB
    db_equipos[str(codEquipo)] = equipo

    #guardamos los jugadores en CouchDB
    for jugador in jugadores:
        id_jugador = str(codEquipo) + "_" + jugador['nombre'] + "_" + jugador['apellidos']
        db_jugadores[id_jugador] = jugador

def detallesEquipo(request, codClub, codEquipo, categoria):

    datos = extraer_datos_pagina_detalles_equipo("https://www.rfaf.es/pnfg/NPcd/NFG_VisEquipos?cod_primaria=1000119&Codigo_Equipo=" + str(codEquipo), codEquipo)

    #volvemos a poner la categoría como estaba antes
    categoriaAux = categoria.split("-")
    categoriaNormal = categoriaAux[0] + "ª " + categoriaAux[1] + " " + categoriaAux[2]
    aux = {
        'codigo':codClub,
        'categoria':categoriaNormal,
        'nombre':datos[0],
        'domicilio':datos[1],
        'localidad':datos[2],
        'provincia':datos[3],
        'codPostal':datos[4],
        'email':datos[5],
        'codEquipo':datos[6]
    }

    # aux = {
    #     'codigo':1321,
    #     'categoria':"4ª ANDALUZA CADETE",
    #     'nombre':"CLUB JORGE JUAN ANTONIO ULLOA",
    #     'domicilio':" C/ Amor, s/n",
    #     'localidad':" Sevilla",
    #     'provincia':" Sevilla",
    #     'codPostal':" 41006",
    #     'email':" cdjorgejuan@gmail.com ",
    #     'codEquipo':132117
    # }

    jugadores = []

    for jugador in datos[7]:
        
        jugadorApellidosNombre = jugador.split(",")
        nombre = jugadorApellidosNombre[1]
        apellidos = jugadorApellidosNombre[0]

        auxJugadores = {
            'nombre':nombre,
            'apellidos':apellidos
        }

        jugadores.append(auxJugadores)

    guardarEquipo(datos[6], jugadores, aux)

    return render(request, 'papers/detallesEquipo.html', {'context':aux, 'jugadores':jugadores})


#---------------------------------FIN PARTE DE DETALLES EQUIPO------------------------------------------------

def misEquipos(request):

    equipos = []

    for id in db_equipos.__iter__:
        equipos.append(db_equipos[id])

    return render(request, 'principal/misEquipos.html', {'equipos':equipos})

