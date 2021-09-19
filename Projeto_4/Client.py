#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 
import random
import time
from typing import Text
from math import ceil  #arredonda uma número para cima

from classeClient import Client
from numpy.core.fromnumeric import size
from enlaceClient import *
from enlaceRxCLient import *
import time
import numpy as np
from PIL import Image
import io
import math

# voce deverá descomentar e configurar a porta com através da qual irá fazer comunicação
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName1 = "COM5"       #MEU CABO           # Windows(variacao de)
com1 = enlace(serialName1)


def main():
    try:
        
        client = Client()

        handshakeMessage = client.datagramaHandshake()

        client.sendHandshake(handshakeMessage)

        listPackage = client.payload("./payload.txt")

        client.sendPackages(listPackage)

        # tempo_final = time.time()
        # tempo_total = tempo_final - cronometro_client
        # # velocidade = len(txBuffer)/tempo_total

        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")

        client.com1.disable()


    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        client.com1.disable()
        
    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
