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
serialName2 = "COM4"        #CABO AZUL

def main():
    try:
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName1)
        com2 = enlace(serialName2)
    
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()
        com2.enable()
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Comunicação aberta com sucesso!")
        cronometro_client = time.time()
        print(cronometro_client)

        valor_sorteado = random.randint(10, 30)
        lista_comandos = ['00FF','00', '0F', 'F0', 'FF00', 'FF']

        #agora vamos sortear os termos dessa lista e organizar a qtd de comando a partir do valor_sorteado

        comandos = random.choices(lista_comandos, k = valor_sorteado)

        print("valor sorteado:"+ str(valor_sorteado))
        print("os comandos:" + str(comandos))
        
        #aqui você deverá gerar os dados a serem transmitidos. 
        #seus dados a serem transmitidos são uma lista de bytes a serem transmitidos. Gere esta lista com o 
        #nome de txBuffer. Esta sempre irá armazenar os dados a serem enviados.

        '''with open("./loss.bmp","rb") as img:
            #primeiro é necessário LER a imagem
            readImg = img.read()
            txBuffer = bytearray(readImg)'''
        
        txBuffer = comandos
    
        #faça aqui uma conferência do tamanho do seu txBuffer, ou seja, quantos bytes serão enviados.
        print(len(txBuffer))
       
            
        #finalmente vamos transmitir os dados. Para isso usamos a funçao sendData que é um método da camada enlace.
        #faça um print para avisar que a transmissão vai começar.
        print("Tan dan: A transmissão vai começar")
        #tente entender como o método send funciona!
        #Cuidado! Apenas trasmitimos arrays de bytes! Nao listas!
          
        
        com1.sendData(np.asarray(txBuffer))
       
        # A camada enlace possui uma camada inferior, TX possui um método para conhecermos o status da transmissão
        # Tente entender como esse método funciona e o que ele retorna
        txSize = com1.tx.getStatus()
        #Agora vamos iniciar a recepção dos dados. Se algo chegou ao RX, deve estar automaticamente guardado
        #Observe o que faz a rotina dentro do thread RX
        #print um aviso de que a recepção vai começar.
        print("A recepção dos bytes vai começar!!!")
        
        #Será que todos os bytes enviados estão realmente guardadas? Será que conseguimos verificar?
        #Veja o que faz a funcao do enlaceRX  getBufferLen
      
        #acesso aos bytes recebidos
        txLen = len(txBuffer)
        rxBuffer, nRx = com2.getData(txLen)
        print("recebeu {}" .format(nRx))
        # ao invés do rxBuffer nRx    
    
        # converte os bytes já direto
        '''output_image = Image.open(io.BytesIO(rxBuffer))
        output_image.save('proj2_recebido.png') '''

        # print("Imagem recebida de volta com sucesso e salva!")
        print("Comandos recebidos com sucesso!")

        cronometro_client_final = time.time()
        tempo_para_execucao = cronometro_client_final - cronometro_client
        print(tempo_para_execucao)
        print("velocidade:" + str(txLen/tempo_para_execucao))

        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        com2.disable()

    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
