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
from enlace import *
import time
import numpy as np
from PIL import Image
import io

# voce deverá descomentar e configurar a porta com através da qual irá fazer comunicação
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName1 = "COM5"       #MEU CABO           # Windows(variacao de)

def main():
    try:
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName1)

        #Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()

        print("Comunicação aberta com sucesso!")

        # Contabilizando o tempo inicial
        cronometro_client = time.time()

        my_str = "hello world"
        my_str_as_bytes = str.encode(my_str)
        handshake_message = my_str_as_bytes

        print("Primeira mensagem em bytes que será enviada para o server: {0}".format(handshake_message))
        print(len(handshake_message))

        # ------------------------------------------------------------------------------------------------------

        #Handshake a ser estabelecido entre Client e Server
        
        TentarNovamente = True

        while TentarNovamente:
            print("Handshake pelo cliente sendo enviado em alguns segundos... \n")

            com1.sendData(np.asarray(handshake_message))

            print("Aguardando a confirmação do Server")

            rxBufferHandshake, rxnHandshake = com1.getData(11)

            time.sleep(5)


            if handshake_message == rxBufferHandshake:
                print("Handshake feito com sucesso!")
                print("O server recebeu o mesmo que foi enviado pelo client: {0}".format(rxBufferHandshake))
                com1.sendData(b't')

                TentarNovamente = False
            else:
                print("Xii... parece que falhou!")
                resposta = input("Quer tentar novamente? Y/N ")
                if resposta == "Y":
                    com1.sendData(b'Y')
                    TentarNovamente = True
                else: 
                    TentarNovamente = False

        #------------------------------------------------------------------------------------


        
 
        tempo_final = time.time()
        tempo_total = tempo_final - cronometro_client
        # velocidade = len(txBuffer)/tempo_total

        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")

        com1.disable()
    
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
