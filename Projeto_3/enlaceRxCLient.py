#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#17/02/2018
#  Camada de Enlace
####################################################

# Importa pacote de tempo
import time

# Threads
import threading

# Class
class RX(object):
  
    def __init__(self, fisica):
        self.fisica      = fisica
        self.buffer      = bytes(bytearray())
        self.threadStop  = False
        self.threadMutex = True
        self.READLEN     = 1024

    def thread(self): 
        while not self.threadStop:
            if(self.threadMutex == True):
                rxTemp, nRx = self.fisica.read(self.READLEN)
                if (nRx > 0):
                    self.buffer += rxTemp  
                time.sleep(0.01)

    def threadStart(self):       
        self.thread = threading.Thread(target=self.thread, args=())
        self.thread.start()

    def threadKill(self):
        self.threadStop = True

    def threadPause(self):
        self.threadMutex = False

    def threadResume(self):
        self.threadMutex = True

    def getIsEmpty(self):
        if(self.getBufferLen() == 0):
            return(True)
        else:
            return(False)

    def getBufferLen(self):
        return(len(self.buffer))

    def getAllBuffer(self, len):
        self.threadPause()
        b = self.buffer[:]
        self.clearBuffer()
        self.threadResume()
        return(b)

    def getBuffer(self, nData):
        self.threadPause()
        b           = self.buffer[0:nData]
        self.buffer = self.buffer[nData:]
        self.threadResume()
        return(b)

    def getNData(self, size):
        while(self.getBufferLen() < size):
            time.sleep(0.05)      
            # print("loop infinito. GetBufferLen:{0}".format(self.getBufferLen()))
        return(self.getBuffer(size))



    def clearBuffer(self):
        self.buffer = b""



# while TentarNovamente:
#         print("Handshake pelo client sendo enviado em alguns segundos... \n")

#         com1.sendData(np.asarray(handshake_message))

#         time.sleep(0.1)
#         print("Enviou: {0}".format(handshake_message))
#         print("Aguardando a confirmação do Server")

#         print("Número de bytes enviados:{0}".format(com1.tx.transLen))

#         rxBufferHandshake, rxnHandshake = com1.getData(1)

#         print("Recebeu o Handshake: {0}".format(rxBufferHandshake))

#     if handshake_message == rxBufferHandshake:
#         print("Handshake feito com sucesso!")
#         print("O server recebeu o mesmo que foi enviado pelo client: {0}".format(rxBufferHandshake))
#         com1.sendData(b'\x01')

#         TentarNovamente = False
#     else:
#         print("Servidor inativo")
#         resposta = input("Tentar novamente? S/N ")
#         if resposta == "S":
#             com1.sendData(b'S')
#             TentarNovamente = True
#         else: 
#             TentarNovamente = False
#             com1.sendData(b'N')
#             print("Ocorreu um erro e você não quis tentar novamente. Tente novamente depois então :/")


# #------------------------------------------------------------------------------------