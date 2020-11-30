#!/usr/bin/python
'''
    practica3.py
    Programa principal que realiza el análisis de tráfico sobre una traza PCAP.
    Autor: Javier Ramos <javier.ramos@uam.es>
    2020 EPS-UAM
'''


import sys
import argparse
from argparse import RawTextHelpFormatter
import time
import logging
import shlex
import subprocess
import pandas as pd
from io import StringIO
import os
import warnings
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import math

'''
    Función: calcularECDF
    Entrada: 
        -datos: lista con los datos sobre los que calcular la ECDF
    Salida: :
        -datos: lista con los valores x (datos de entrada)
        -y: lista con los valores de probabilidad acumulada para cada dato de entrada
    Descripción:  Esta función recibe una lista de datos y calcula la función empírica de distribución 
    acumulada sobre los mismos. Los datos se devuelven listos para ser pintados.
'''
def calcularECDF(datos):
    datos.sort()
    n = len (datos)
    y = [(i-1)/n for i in range(1,n+1)]

    return datos,y



'''
    Función: ejecutarComandoObtenerSalida
    Entrada: 
        -comando: cadena de caracteres con el comando a ejecutar
    Salida: 
        -codigo_retorno: código numérico que indica el retorno del comando ejecutado.
        Si este valor es 0, entonces el comando ha ejecutado correctamente.
        -salida_retorno: cadena de caracteres con el retorno del comando. Este retorno
        es el mismo que obtendríamos por stdout al ejecutar un comando de terminal.

    Descripción: Esta función recibe una cadena con un comando a ejecutar, lo ejecuta y retorna
    tanto el código de resultado de la ejecución como la salida que el comando produzca por stdout
'''
def ejecutarComandoObtenerSalida(comando):
    proceso = subprocess.Popen(shlex.split(comando), stdout=subprocess.PIPE)
    salida_retorno = ''
    while True:
        
        salida_parcial = proceso.stdout.readline()
        if salida_parcial.decode() == '' and proceso.poll() is not None:
            break
        if salida_parcial:
            salida_retorno += salida_parcial.decode()
    codigo_retorno = proceso.poll()
    return codigo_retorno,salida_retorno


'''
    Función: pintarECDF
    Entrada:
        -datos: lista con los datos que se usarán para calcular y pintar la ECDF
        -nombre_fichero: cadena de caracteres con el nombre del fichero donde se guardará la imagen
        (por ejemplo figura.png)
        -titulo: cadena de caracteres con el título a pintar en la gráfica
        -titulo_x: cadena de caracteres con la etiqueta a usar para el eje X de la gráfica
        -titulo_y: cadena de caracteres con la etiqueta a usar para el eje Y de la gráfica
    Salida: 
        -Nada

    Descripción: Esta función pinta una gráfica ECDF para unos datos de entrada y la guarda en una imagen
'''
def pintarECDF(datos,nombre_fichero,titulo,titulo_x,titulo_y):
    
    x, y = calcularECDF(datos)
    x.append(x[-1])
    y.append(1) 
    fig1, ax1 = plt.subplots()
    plt.step(x, y, '-')
    _ = plt.xticks(rotation=45)
    plt.title(titulo)
    fig1.set_size_inches(12, 10)
    plt.tight_layout()
    plt.locator_params(nbins=20)
    ax1.set_xlabel(titulo_x)
    ax1.set_ylabel(titulo_y)
    plt.savefig(nombre_fichero, bbox_inches='tight')


'''
    Función: pintarSerieTemporal
    Entrada:
        -x: lista de tiempos en formato epoch y granularidad segundos
        -y: lista con los valores a graficar
        -nombre_fichero: cadena de caracteres con el nombre del fichero donde se guardará la imagen
        (por ejemplo figura.png)
        -titulo: cadena de caracteres con el título a pintar en la gráfica
        -titulo_x: cadena de caracteres con la etiqueta a usar para el eje X de la gráfica
        -titulo_y: cadena de caracteres con la etiqueta a usar para el eje Y de la gráfica
    Salida: 
        -Nada

    Descripción: Esta función pinta una serie temporal dados unos datos x e y de entrada y la guarda en una imagen
'''
def pintarSerieTemporal(x,y,nombre_fichero,titulo,titulo_x,titulo_y):
    fig1, ax1 = plt.subplots()
    plt.plot(x, y, '-')
    _ = plt.xticks(rotation=45)
    plt.title(titulo)
    fig1.set_size_inches(12, 10)
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_locator(mtick.FixedLocator(x))
    plt.gca().xaxis.set_major_formatter(mtick.FuncFormatter(lambda pos,_: time.strftime("%d-%m-%Y %H:%M:%S",time.localtime(pos))))
    plt.tight_layout()
    plt.locator_params(nbins=20)
    ax1.set_xlabel(titulo_x)
    ax1.set_ylabel(titulo_y)
    plt.savefig(nombre_fichero, bbox_inches='tight')


'''
    Función: pintarTarta
    Entrada:
        -etiquetas: lista con cadenas de caracteres que contienen las etiquetas a usar en el gráfico de tarta
        -valores: lista con los valores a graficar
        -nombre_fichero: cadena de caracteres con el nombre del fichero donde se guardará la imagen
        (por ejemplo figura.png)
        -titulo: cadena de caracteres con el título a pintar en la gráfica
    Salida:
        -Nada

    Descripción: Esta función pinta un gráfico de tarta dadas unas etiquetas y valores de entrada y lo guarda en una imagen
'''
def pintarTarta(etiquetas,valores,nombre_fichero,titulo):
    explode = tuple([0.05]*(len(etiquetas)))

    fig1, ax1 = plt.subplots()
    plt.pie(valores, autopct='%1.1f%%', startangle=90, pctdistance=0.85)
    plt.legend(etiquetas, loc="best")
    plt.title(titulo)
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig1 = plt.gcf()
    fig1.gca().add_artist(centre_circle)
    fig1.set_size_inches(12, 10)
    ax1.axis('equal')  
    plt.tight_layout()
    plt.savefig(nombre_fichero, bbox_inches='tight')


'''
    Función: topDict
    Entrada:
        -dictionary: el diccionario de valores enteros sobre el que obtener el top.
        -N: el número de posiciones del top.
    Salida: :
        -top: diccionario con los N primeros pares de dictionary

    Descripción: Devuelve las primeras N entradas de un diccionario con valores
    enteros. La comparación se hace por valores, siendo los primeros los mayores.
'''
def topDict(dictionary, N):
    top = dict()
    for i in range(N):
        maxN = 0
        maxDir = 0
        for key in dictionary.keys():
            if dictionary[key] > maxN:
                maxN = dictionary[key]
                maxDir = key
        top[maxDir] = maxN
        del dictionary[maxDir]

    return top

'''
    Función: cuentaTopBytes
    Entrada: 
        -salida: salida de la ejecucion de tshark
    Salida: :
        -top: diccionario con los pares (dir, numBytes) obtenidos

    Descripción:  Esta función recibe la salida de tshark con dos columnas, siendo la segunda de bytes.
    Devuelve el top 5 de elementos de la primea columna que mas bytes sumen.
'''
def cuentaTopBytes(salida):
    count = dict()
    for line in salida.split('\n'):
        if line != '':
            split = line.split('\t')
            if split[0] != '':
                if split[0] in count:
                    count[split[0]] += int(split[1])
                else:
                    count[split[0]] = int(split[1])

    return topDict(count, 5)

'''
    Función: cuentaTopPaquetes
    Entrada: 
        -salida: salida de la ejecucion de tshark
    Salida: :
        -top: diccionario con los pares (dir, numPacks) obtenidos

    Descripción:  Esta función recibe la salida de tshark con una columna.
    Devuelve el top 5 de elementos de la primea columna que mas se repitan y su frecuencia.
'''
def cuentaTopPaquetes(salida):
    count = dict()
    for line in salida.split('\n'):
        if line != '':
            split = line.split('\t')
            if split[0] != '':
                if split[0] in count:
                    count[split[0]] += 1
                else:
                    count[split[0]] = 1

    return topDict(count, 5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Programa principal que realiza el análisis de tráfico sobre una traza PCAP',
    formatter_class=RawTextHelpFormatter)
    parser.add_argument('--trace', dest='tracefile', default=False,help='Fichero de traza a usar',required=True)
    parser.add_argument('--mac', dest='mac', default=False,help='MAC usada para filtrar',required=True)
    parser.add_argument('--ip_flujo_tcp', dest='ip_flujo_tcp', default=False,help='IP para filtrar por el flujo TCP',required=True)
    parser.add_argument('--port_flujo_udp', dest='port_flujo_udp', default=False,help='Puerto para filtrar por el flujo UDP',required=True)
    parser.add_argument('--debug', dest='debug', default=False, action='store_true',help='Activar Debug messages')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level = logging.DEBUG, format = '[%(asctime)s %(levelname)s]\t%(message)s')
    else:
        logging.basicConfig(level = logging.INFO, format = '[%(asctime)s %(levelname)s]\t%(message)s')

    #Creamos un directorio a donde volcaremos los resultado e imágenes

    if not os.path.isdir('resultados'):
        os.mkdir('resultados')

    #Ejemplo de ejecución de comando tshark y parseo de salida. Se parte toda la salida en líneas usando el separador \n
    logging.info('Ejecutando tshark para obtener el número de paquetes')
    codigo,salida = ejecutarComandoObtenerSalida('tshark -r {} -T fields -e frame.number'.format(args.tracefile))
    if codigo: #En caso de error
        sys.exit(-1)

    nlineas = 0
    for linea in salida.split('\n'):
        if linea != '':
            #print(linea)
            nlineas +=1

    print('{} paquetes en la traza {}'.format(nlineas,args.tracefile))


    #Analisis de protocolos
    #TODO: Añadir código para obtener el porcentaje de tráfico IPv4 y NO-IPv4
    logging.info('Ejecutando tshark para obtener el porcentaje de tráfico IPv4 y NO-IPv4')
    codigo, salida = ejecutarComandoObtenerSalida("tshark -r {} -Y 'ip'".format(args.tracefile))
    if codigo:
        sys.exit(-1)

    nIP = 0
    for linea in salida.split('\n'):
        nIP += (linea != '')

    print('{0:.2f}% de paquetes IPv4 ({1:.2f}% no-IPv4)'.format(100.0*nIP/nlineas, 100.0*(nlineas - nIP)/nlineas))

    #TODO: Añadir código para obtener el porcentaje de tráfico TPC,UDP y OTROS sobre el tráfico IP
    logging.info('Ejecutando tshark para obtener el porcentaje de tráfico TPC,UDP y OTROS sobre el tráfico IP')
    # Paquetes TCP
    codigo, salida = ejecutarComandoObtenerSalida("tshark -r {} -Y 'tcp and ip and (not icmp)'".format(args.tracefile))
    if codigo:
        sys.exit(-1)

    nTCP = 0
    for linea in salida.split('\n'):
        nTCP += (linea != '')
    # Paquetes UDP
    codigo, salida = ejecutarComandoObtenerSalida("tshark -r {} -Y 'udp and ip and (not icmp)'".format(args.tracefile))
    if codigo:
        sys.exit(-1)

    nUDP = 0
    for linea in salida.split('\n'):
        nUDP += (linea != '')

    print('{0:.2f}% de paquetes TCP, {1:.2f}% de paquetes UDP ({2:.2f}% otros)'.format(100.0*nTCP/nIP, 100.0*nUDP/nIP,
                                                                                       100.0*(nIP - nTCP - nUDP)/nIP))

    #Obtención de top 5 direcciones IP
    #TODO: Añadir código para obtener los datos y generar la gráfica de top IP origen por bytes
    logging.info('Ejecutando tshark para obtener el top direcciones IP origen por bytes')
    codigo,salida = ejecutarComandoObtenerSalida('tshark -r {} -T fields -e ip.src -e frame.len'.format(args.tracefile))
    if codigo:
        sys.exit(-1)

    top = cuentaTopBytes(salida)

    pintarTarta(top.keys(), top.values(), "topIPSrcBytes.png", "Top direcciones IP origen por numero de bytes")


    #TODO: Añadir código para obtener los datos y generar la gráfica de top IP origen por paquetes
    logging.info('Ejecutando tshark para obtener el top direcciones IP origen por paquetes')
    codigo,salida = ejecutarComandoObtenerSalida('tshark -r {} -T fields -e ip.src'.format(args.tracefile))
    if codigo:
        sys.exit(-1)

    top = cuentaTopPaquetes(salida)

    pintarTarta(top.keys(), top.values(), "topIPSrcPaquetes.png", "Top direcciones IP origen por numero de paquetes")

    #TODO: Añadir código para obtener los datos y generar la gráfica de top IP destino por paquetes
    logging.info('Ejecutando tshark para obtener el top direcciones IP destino por paquetes')
    codigo,salida = ejecutarComandoObtenerSalida('tshark -r {} -T fields -e ip.dst'.format(args.tracefile))
    if codigo:
        sys.exit(-1)

    top = cuentaTopPaquetes(salida)

    pintarTarta(top.keys(), top.values(), "topIPDestPaquetes.png", "Top direcciones IP destino por numero de paquetes")

    #TODO: Añadir código para obtener los datos y generar la gráfica de top IP destino por bytes
    logging.info('Ejecutando tshark para obtener el top direcciones IP destino por bytes')
    codigo,salida = ejecutarComandoObtenerSalida('tshark -r {} -T fields -e ip.dst -e frame.len'.format(args.tracefile))
    if codigo:
        sys.exit(-1)

    top = cuentaTopBytes(salida)

    pintarTarta(top.keys(), top.values(), "topIPDestBytes.png", "Top direcciones IP destino por numero de bytes")

    #Obtención de top 5 puertos TCP
    #TODO: Añadir código para obtener los datos y generar la gráfica de top puerto origen TCP por bytes
    logging.info('Ejecutando tshark para obtener el top puertos TCP origen por bytes')
    codigo,salida = ejecutarComandoObtenerSalida('tshark -r {} -T fields -e tcp.srcport -e frame.len'.format(args.tracefile))
    if codigo:
        sys.exit(-1)

    top = cuentaTopBytes(salida)

    pintarTarta(top.keys(), top.values(), "topTCPSrcBytes.png", "Top puertos TCP origen por numero de bytes")

    #TODO: Añadir código para obtener los datos y generar la gráfica de top puerto destino TCP por bytes
    logging.info('Ejecutando tshark para obtener el top puertos TCP destino por bytes')
    codigo,salida = ejecutarComandoObtenerSalida('tshark -r {} -T fields -e tcp.dstport -e frame.len'.format(args.tracefile))
    if codigo:
        sys.exit(-1)

    top = cuentaTopBytes(salida)

    pintarTarta(top.keys(), top.values(), "topTCPDestBytes.png", "Top puertos TCP destino por numero de bytes")

    #TODO: Añadir código para obtener los datos y generar la gráfica de top puerto origen TCP por paquetes
    logging.info('Ejecutando tshark para obtener el top puertos TCP origen por paquetes')
    codigo,salida = ejecutarComandoObtenerSalida('tshark -r {} -T fields -e tcp.srcport'.format(args.tracefile))
    if codigo:
        sys.exit(-1)

    top = cuentaTopPaquetes(salida)

    pintarTarta(top.keys(), top.values(), "topTCPSrcPaquetes.png", "Top puertos TCP origen por numero de paquetes")

    #TODO: Añadir código para obtener los datos y generar la gráfica de top puerto destino  TCP por paquetes
    logging.info('Ejecutando tshark para obtener el top puertos TCP destino por paquetes')
    codigo,salida = ejecutarComandoObtenerSalida('tshark -r {} -T fields -e tcp.dstport'.format(args.tracefile))
    if codigo:
        sys.exit(-1)

    top = cuentaTopPaquetes(salida)

    pintarTarta(top.keys(), top.values(), "topTCPDestPaquetes.png", "Top puertos TCP destino por numero de paquetes")

    #Obtención de top 10 puertos UDP
    #TODO: Añadir código para obtener los datos y generar la gráfica de top puerto origen UDP por bytes
    logging.info('Ejecutando tshark para obtener el top puertos UDP origen por bytes')
    codigo,salida = ejecutarComandoObtenerSalida('tshark -r {} -T fields -e udp.srcport -e frame.len'.format(args.tracefile))
    if codigo:
        sys.exit(-1)

    top = cuentaTopBytes(salida)

    pintarTarta(top.keys(), top.values(), "topUDPSrcBytes.png", "Top puertos UDP origen por numero de bytes")

    #TODO: Añadir código para obtener los datos y generar la gráfica de top puerto destino UDP por bytes
    logging.info('Ejecutando tshark para obtener el top puertos UDP destino por bytes')
    codigo,salida = ejecutarComandoObtenerSalida('tshark -r {} -T fields -e udp.dstport -e frame.len'.format(args.tracefile))
    if codigo:
        sys.exit(-1)

    top = cuentaTopBytes(salida)

    pintarTarta(top.keys(), top.values(), "topUDPDestBytes.png", "Top puertos UDP destino por numero de bytes")

    #TODO: Añadir código para obtener los datos y generar la gráfica de top puerto origen UDP por paquetes
    logging.info('Ejecutando tshark para obtener el top puertos UDP origen por paquetes')
    codigo,salida = ejecutarComandoObtenerSalida('tshark -r {} -T fields -e udp.srcport'.format(args.tracefile))
    if codigo:
        sys.exit(-1)

    top = cuentaTopPaquetes(salida)

    pintarTarta(top.keys(), top.values(), "topUDPSrcPaquetes.png", "Top puertos UDP origen por numero de paquetes")

    #TODO: Añadir código para obtener los datos y generar la gráfica de top puerto destino UDP por paquetes
    logging.info('Ejecutando tshark para obtener el top puertos UDP destino por paquetes')
    codigo,salida = ejecutarComandoObtenerSalida('tshark -r {} -T fields -e udp.dstport'.format(args.tracefile))
    if codigo:
        sys.exit(-1)

    top = cuentaTopPaquetes(salida)

    pintarTarta(top.keys(), top.values(), "topUDPDestPaquetes.png", "Top puertos UDP destino por numero de paquetes")


    #Obtención de series temporales de ancho de banda
    #TODO: Añadir código para obtener los datos y generar la gráfica de la serie temporal de ancho de banda con MAC como origen
    logging.info('Ejecutando tshark para obtener la serie temporal de ancho de banda con MAC como origen')
    codigo,salida = ejecutarComandoObtenerSalida("tshark -r {} -T fields -e frame.time_epoch -e frame.len -Y 'eth.src eq {}'".format(args.tracefile, args.mac))
    if codigo:
        sys.exit(-1)

    count = dict()
    for line in salida.split('\n'):
        if line != '':
            elems = line.split('\t')  
            if math.floor(float(elems[0])) in count:
                count[math.floor(float(elems[0]))] += int(elems[1])*8
            else:
                count[math.floor(float(elems[0]))] = int(elems[1])*8

    for i in range(min(count.keys()), max(count.keys()) + 1):
        if i not in count:
            count[i] = 0

    #pintarSerieTemporal(count.keys(), count.values(), "anchoBandaMACSrc.png", "Ancho de banda con MAC como origen", "Tiempo epoch(s)", "Ancho de banda (b/s)")

    #TODO: Añadir código para obtener los datos y generar la gráfica de la serie temporal de ancho de banda con MAC como destino
    logging.info('Ejecutando tshark para obtener la serie temporal de ancho de banda con MAC como destino')
    codigo,salida = ejecutarComandoObtenerSalida("tshark -r {} -T fields -e frame.time_epoch -e frame.len -Y 'eth.dst eq {}'".format(args.tracefile, args.mac))
    if codigo:
        sys.exit(-1)

    count = dict()
    for line in salida.split('\n'):
        if line != '':
            elems = line.split('\t')
            if math.floor(float(elems[0])) in count:
                count[math.floor(float(elems[0]))] += int(elems[1])*8
            else:
                count[math.floor(float(elems[0]))] = int(elems[1])*8

    for i in range(min(count.keys()), max(count.keys()) + 1):
        if i not in count:
            count[i] = 0

    #pintarSerieTemporal(count.keys(), count.values(), "anchoBandaMACSrc.png", "Ancho de banda con MAC como origen", "Tiempo epoch(s)", "Ancho de banda (b/s)")

    #Obtención de las ECDF de tamaño de los paquetes
    #TODO: Añadir código para obtener los datos y generar la gráfica de la ECDF de los tamaños de los paquetes a nivel 2
    logging.info('Ejecutando tshark para obtener la ECDF de los tamaños de paquetes a nivel 2')
    codigo,salida = ejecutarComandoObtenerSalida("tshark -r {} -T fields -e frame.len -Y 'eth.src eq {}'".format(args.tracefile, args.mac))
    if codigo:
        sys.exit(-1)

    tamanos = []
    for line in salida.split('\n'):
        if line != '':
            tamanos.append(int(line))

    pintarECDF(tamanos, "ECDFMACSrc.png", "Tamaño de paquetes a nivel 2 con MAC como origen", "Tamaño (B)", "P{x<X}")
    
    codigo,salida = ejecutarComandoObtenerSalida("tshark -r {} -T fields -e frame.len -Y 'eth.dst eq {}'".format(args.tracefile, args.mac))
    if codigo:
        sys.exit(-1)

    tamanos = []
    for line in salida.split('\n'):
        if line != '':
            tamanos.append(int(line))

    pintarECDF(tamanos, "ECDFMACDest.png", "Tamaño de paquetes a nivel 2 con MAC como destino", "Tamaño (B)", "P{x<X}")
    
    #Obtención de las ECDF de tamaño de los tiempos entre llegadas
    #TODO: Añadir código para obtener los datos y generar la gráfica de la ECDF de los tiempos entre llegadas para el flujo TCP
    logging.info('Ejecutando tshark para obtener la ECDF del flujo TCP')
    codigo,salida = ejecutarComandoObtenerSalida("tshark -r {0} -T fields -e frame.time_delta -Y 'ip.src eq {1} or ip.dst eq {1}'".format(args.tracefile, args.ip_flujo_tcp))
    if codigo:
        sys.exit(-1)

    tiempos = []
    for line in salida.split('\n'):
        if line != '':
            tiempos.append(int(line))

    pintarECDF(tiempos, "ECDFdeltaTCP.png", "Tiempo entre paquetes para flujo TCP", "Tiempo (s)", "P{x<X}")
    #TODO: Añadir código para obtener los datos y generar la gráfica de la ECDF de los tiempos entre llegadas para el flujo UDP
    logging.info('Ejecutando tshark para obtener la ECDF del flujo UDP')
    codigo,salida = ejecutarComandoObtenerSalida("tshark -r {0} -T fields -e frame.time_delta -Y 'udp.srcport eq {1} or udp.dstport eq {1}'".format(args.tracefile, args.port_flujo_udp))
    if codigo:
        sys.exit(-1)

    tiempos = []
    for line in salida.split('\n'):
        if line != '':
            tiempos.append(int(line))

    pintarECDF(tiempos, "ECDFdeltaUDP.png", "Tiempo entre paquetes para flujo UDP", "Tiempo (s)", "P{x<X}")
