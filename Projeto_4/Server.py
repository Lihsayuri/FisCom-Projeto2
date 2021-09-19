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

from classeServer import Server
from numpy.core.fromnumeric import size
from enlace import *
import time
import numpy as np
from PIL import Image
import io
from enlaceRx import * 
# from Client import *

# txLen = ""
# voce deverá descomentar e configurar a porta com através da qual irá fazer comunicação
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)

serialName2 = "COM4"        #CABO AZUL
com2 = enlace(serialName2)
def main():
    try:
        
        server = Server()

        server.conferindoHandshake()

        receivedData = server.conferindoMensagem()

        organizedData = server.organizeData(receivedData)

        print(organizedData)


        # tempo_final = time.time()
        # tempo_total = tempo_final - tempo_inicial
        # # velocidade = lenRx/ tempo_total

        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        # print("Velocidade: {0}".format(velocidade))
        server.com2.disable()
    
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        server.com2.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
