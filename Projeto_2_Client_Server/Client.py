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

        #Quantidade sorteada de 10 a 30 que será o número de comandos que serão enviados
        valor_sorteado = random.randint(10, 30)
        lista_comandos = [b'\x00\xff',b'\x00', b'\x0f', b'\xf0', b'\xff\x00', b'\xff']

        #Agora vamos sortear os termos dessa lista e organizar a qtd de comandos a partir do valor_sorteado
        comandos = random.choices(lista_comandos, k = valor_sorteado)

        print("O valor sorteado foi: "+ str(valor_sorteado))
        print("Os comandos que quero enviar são: " + str(comandos))
        
        #Iremos trabalhar com uma String de bytes
        string_bytes = b'' 
        
        # Isso servirá para identificar no servidor quais são os comandos recebidos, é como se b'\xaa fosse uma vírgula 
        for byte in comandos:
            if len(byte) == 2:
                string_bytes+= byte + b'\xaa'
            else:
                string_bytes += byte + b'\xaa'

        # Transformei os comandos em array só para contar de fato o número de COMANDOS (não bytes) a serem enviados
        txBufferComandos = np.array(comandos)

        # Os bytes que serão enviados em uma string de bytes, que possuem b'\xaa como separadores
        txBuffer = string_bytes

        len_string = len(string_bytes)

        print("Bytes que serão enviados com o separador:{0} ".format(string_bytes))

        print("Número de bytes a serem enviados: {0} ".format(len_string))

        print("Vou enviar essa quantidade de comandos:{0}".format(len(txBufferComandos)))
       
        print("Vou começar com um CABEÇALHO para estabelecer a comunicação, assim, mandar o número de comandos \n")

        # ------------------------------------------------------------------------------------------------------

        # Esse é o cabeçalho, quando serão enviados 2 bytes para o Server para iniciar essa comunicação. 
        # Esses dois bytes enviados no começo são o número total de bytes a serem enviados


        # Antes vamos começar a transformando esse tamanho decimal em bytes, que são lidos da esquerda para direita.
        txBufferInicial = len_string.to_bytes(2, byteorder="big")

        #Agora vou mandar esses dois bytes com a função send, lembrando que precisa ser em array!
        com1.sendData(np.asarray(txBufferInicial))

        #------------------------------------------------------------------------------------

        #HANDSHAKE

        print("Agora o Handshake será feito em alguns instantes ....")

        # Recebendo de volta os dois bytes que enviei para conferir
        rxBufferInicial, nRx = com1.getData(2)

        if txBufferInicial == rxBufferInicial:
            print("Deu certo! Handshake pronto!")

            print("Agora simm! Dados sendo transmitidos para o servidor")
            com1.sendData(txBuffer)

            print("Aguardando confirmação do envio...")

            # Conferindo de volta todos os bytes que foram enviados
            rxBufferResposta, nRxResposta = com1.getData(len_string)


        print("Resposta recebida pelo servidor:"+ str(rxBufferResposta)+" Tamanho da informação:" + str(nRxResposta))
        #Vamos ver agora se o que foi recebido (PS: contém os bytes a mais que são os separadores)

        #------------------------------------------------------------------------------------------------

        #Agora sim, conferir os dados tratados no servidor e comparar
        print("Vamos receber o número de comandos que o server recebeu")
        rxNumeroComandos, nRxComandos = com1.getData(1)
        rxComandosResposta = int.from_bytes(rxNumeroComandos, byteorder="big")

        if rxComandosResposta == len(txBufferComandos):
            print("Número de comandos que foram recebidos pelo servidor é o mesmo que foi enviado pelo client:{0}".format(rxComandosResposta))

        tempo_final = time.time()
        tempo_total = tempo_final - cronometro_client
        velocidade = len(txBuffer)/tempo_total

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
