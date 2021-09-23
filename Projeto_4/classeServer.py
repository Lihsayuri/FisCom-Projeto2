#------------------------------------- IMPORTS -------------------------------------------

import random
import time
from typing import Text
from math import ceil  #arredonda uma número para cima
from datetime import datetime 
from numpy.core.fromnumeric import size
# from enlaceClient import *
# from enlaceRxCLient import *
from enlaceRxServer import *
from enlaceServer import *
import time
import numpy as np
from PIL import Image
import io
import math
import os
import traceback

#----------------------------------------------------------------------------------------

class Server:
    def __init__(self):
        self.serialName = "COM4"
        self.com2 = enlace(self.serialName)
        self.com2.enable()

        self.com2.fisica.flush()            

        print("Comunicação aberta com sucesso!\n")

        self.tamanhoHead = 10
        self.tamanhoPayload = 114
        self.tamanhoEOP = 4

        self.EOP = b'\xff\xaa\xff\xaa'

        self.ServerLog = []

        self.timer2Reset = False

        self.messageType2 = b'\x02'  #server recebeu mensagem do tipo 1 com identificador correto
        self.messageType4 = b'\x04' # servidor dizendo recebeu pacote corretamente, tudo perfeito
        self.messageType5 = b'\x05' # server indicando que deu time-out
        self.messageType6 = b'\x06' #server falando que deu erro no envio 

        self.byteVazio = b'\x00'
        self.archiveId = b'\x01'

        self.idSensor = b'\x02'
        self.idServer = b'\x0f'
        self.idClient = b'\x03'

        self.EnvioNaoCompleto = True
        self.forcarErroNPacks = True
        self.forcarErroNbytes = False


    def head(self, messageType, idSensor, idServer, nTotalPack, nCurrentPack, handshakeOrData, reSend, lastSuccessPack):
        h0 = messageType
        h1 = idSensor
        h2 = idServer
        h3 = nTotalPack
        h4 = nCurrentPack
        h5 = handshakeOrData
        h6 = reSend
        h7 = lastSuccessPack
        h8 = b'\x00'
        h9 = b'\x01'

        Head = b''+ h0 + h1 + h2 + h3 + h4 + h5 + h6 + h7 + h8 + h9 
        return Head

    def getDataServer(self):
        hoursNow = datetime.now()
        dateNHours = hoursNow.strftime('%d/%m/%Y %H:%M:%S')

        return dateNHours

    def serverLog(self,action,type,size,receivedPckg, totalPckg):
        char = " / "
        if type == 3:
            log = str(self.getDataServer())+ char + action + char + str(type) + char + str(size) + char + str(receivedPckg) + char + str(totalPckg) # + CRC
        else:
            log = str(self.getDataServer())+ char + action + char + str(type) + char + str(size) # + CRC
        return log

    def conferindoHandshake(self):        
        TentarNovamente = True

        while TentarNovamente:
            print("-------------------------")
            print("         HANDSHAKE        ")
            print("-------------------------\n")
            print("Vamos estabelecer o Handshake com o Client")

            # os mesmos 2 bytes que foram enviados vão ser recebidos aqui: que são exatamente o tamanho total de byte

            txBufferHandshake, tRxHandshake, self.timer2Reset= self.com2.getData(14)  
            self.ServerLog.append(self.serverLog("receb", int.from_bytes(txBufferHandshake[0:1], byteorder="big"), len(txBufferHandshake), "", ""))

            print("Recebi do Client e agora vou mandar pro Server:{0}".format(txBufferHandshake))

            respostaServer = self.head(self.messageType2, self.idSensor, self.idServer, self.byteVazio, self.byteVazio, self.archiveId, self.byteVazio, self.byteVazio ) + self.EOP
            
            print("Essa é a resposta que o Server vai enviar:{0}".format(respostaServer))
            # de bytes transformando para decimal de novo, que é como iremos usar no resto da comunicação

            print("Agora servidor está enviando o Handshake de volta para o client")


            if txBufferHandshake[0:1] == b'\x01':
                self.com2.sendData(respostaServer)
                self.ServerLog.append(self.serverLog("envio", int.from_bytes(self.messageType2, byteorder="big"), len(respostaServer), "", ""))

                print("Respondi o Handshake e posso começar a transmissão")
                TentarNovamente = False
                print("Pronto para receber os pacotes\n")

    def conferindoMensagem(self):
        dataReceived = []
        
        nOldPackage = 0

        while self.EnvioNaoCompleto:
            # time.sleep(2)

            if not self.timer2Reset:
                timer2 = time.time()

            print("Vamos estabelecer o recebimento dos datagramas com o Client!\n")

            txBufferHead, tRxNHead, self.timer2Reset = self.com2.getData(10)

            qtdPayloadPacote = txBufferHead[5:6]
            print("O pacote tem o payload de {0}".format(qtdPayloadPacote))

            # pensando no pacote que estamos trabalhando, deveria ser 128
            qtdBytesPack = int.from_bytes(qtdPayloadPacote, byteorder="big") + 4

            print("O primeiro pacote (próximo a ser recebido) TEM TOTAL DE BYTES: {0}".format(qtdBytesPack))

            txPayloadPack, txnPayloadPack, self.timer2Reset = self.com2.getData(qtdBytesPack)

            txPack = txBufferHead + txPayloadPack
            qtdBytesTotal = qtdBytesPack+10

            cronometroTimer2 = time.time() - timer2
            if cronometroTimer2 >=20:
                # if int.from_bytes(txPack[4:5], byteorder="big") == 1:
                #     self.com2.sendData
                print("DEU TIMEOUT DE 20s\n")
                timeout = self.head(self.messageType5, self.idSensor, self.idClient, self.byteVazio, self.byteVazio, self.byteVazio, self.byteVazio, self.byteVazio)+ self.EOP
                self.com2.sendData(timeout)
                self.ServerLog.append(self.serverLog("envio", int.from_bytes(timeout[0:1], byteorder="big"), len(timeout), "", ""))
                time.sleep(0.01)
                self.com2.disable()
                break


            self.ServerLog.append(self.serverLog("receb", int.from_bytes(txPack[0:1], byteorder="big"), len(txPack), int.from_bytes(txPack[4:5], byteorder="big"), int.from_bytes(txPack[3:4], byteorder="big") ))


            print("-----------------------------------")
            print("        ANALISANDO PACOTES...    ")
            print("-----------------------------------\n")

            print("Pacote recebido:{0}\n".format(txPack))

            if self.forcarErroNbytes:
                BytesErrados = txPack[0:10] + b'\x00\x01\x02\x00\x00\x00\x02' + txPack[11:qtdBytesTotal]
                txPack = BytesErrados
                print("BYTES ERRADOS:{0}".format(BytesErrados))

            # lembrando, h5 fala o número de bytes no payload por pacote

            EOP_confere = txPack[(qtdBytesTotal-4): qtdBytesTotal]

            print("Esse é o EOP do pacote:{0}\n".format(EOP_confere))
            
            CurrentPack = txPack[4:5]

            print("-------------------------\n")
            print("Pacote atual:{0}".format(CurrentPack))

            nCurrentPack = int.from_bytes(CurrentPack, byteorder="big")
            print("Pacote atual em int:{0}\n".format(nCurrentPack))


            TotalPacks = txPack[3:4]
            nTotalPacks = int.from_bytes(TotalPacks, byteorder="big")
            print("-------------------------\n")

            print("Número total de pacotes :{0}\n".format(nTotalPacks))

            # sinal_verde = b'HEAD\x01/\x01\x00\x00\x00' + b'\x0F'+ EOP

            if self.forcarErroNPacks:
                nCurrentPack -=1

            if nCurrentPack == (nOldPackage + 1) and EOP_confere == self.EOP:
                # CurrentPack passa a ser o antigo package recebido com sucesso

                if nCurrentPack == nTotalPacks:
                    dataReceived.append(txPack)
                    print("Recebi todos os pacotes!")
                    self.EnvioNaoCompleto = False
                    self.com2.disable()
                else:
                    sinal_verde = self.head(self.messageType4, self.idSensor, self.idClient, self.byteVazio, self.byteVazio, self.byteVazio, self.byteVazio, CurrentPack) + self.EOP
                    print("Pacote recebido está certo! Vou enviar o sinal verde: {0}".format(sinal_verde))
                    dataReceived.append(txPack)
                    self.com2.sendData(sinal_verde)
                    self.ServerLog.append(self.serverLog("envio", int.from_bytes(sinal_verde[0:1], byteorder="big"), len(sinal_verde), "", ""))

                    nOldPackage+= 1


            # elif nCurrentPack != (nOldPackage + 1) or EOP != b'\x00\x00\x00\x01':
            else:
                if self.forcarErroNPacks:
                    print("Recebi o pacote errado!")
                    print("O Client vai ter que me enviar o mesmo pacote")
                    self.forcarErroNPacks = False
                    if nCurrentPack == 0:
                        lastPackSucessfully = self.byteVazio
                    else:
                        lastPackSucessfully = (nCurrentPack-1).to_bytes(1, byteorder="big")
                    CurrentPackDatagrama = self.head(self.messageType6, self.idSensor, self.idClient, self.byteVazio, self.byteVazio, self.byteVazio, CurrentPack, lastPackSucessfully)+ self.EOP
                    print(CurrentPackDatagrama)
                    self.com2.sendData(CurrentPackDatagrama)
                    self.ServerLog.append(self.serverLog("envio", int.from_bytes(CurrentPackDatagrama[0:1], byteorder="big"), len(CurrentPackDatagrama), "", ""))

                elif self.forcarErroNbytes:
                    print("Recebi o número de bytes errado! O EOP está fora de ordem")
                    print("O client vai ter que me reenviar o pacote")
                    self.forcarErroNbytes = False
                    if nCurrentPack == 0:
                        lastPackSucessfully = self.byteVazio
                    else:
                        lastPackSucessfully = (nCurrentPack-1).to_bytes(1, byteorder="big")
                    CurrentPackDatagrama = self.head(self.messageType6, self.idSensor, self.idClient, self.byteVazio, self.byteVazio, self.byteVazio, CurrentPack, lastPackSucessfully)+ self.EOP
                    print(CurrentPackDatagrama)
                    self.com2.sendData(CurrentPackDatagrama)
                    self.ServerLog.append(self.serverLog("envio", int.from_bytes(CurrentPackDatagrama[0:1], byteorder="big"), len(CurrentPackDatagrama), "", ""))


        return dataReceived
    
    def organizeData(self,dataReceived):
        organizedData = b''

        for j in range(len(dataReceived)):
            currentByteStr = dataReceived[j]
            lenCurrentByteStr = len(currentByteStr)
            payload = currentByteStr[10:(lenCurrentByteStr-4)]
            organizedData += payload

        print(organizedData)

        print(self.ServerLog)
        # encoding = 'utf-8'
        # Criou o arquivoooooooo YAAAAAAAAAY
        with open('receivedFile.txt','wb') as f:
            f.write(organizedData)

        return organizedData

    def logToFileServer(self):
        if os.path.exists('serverFile.txt'):
            os.remove('serverFile.txt')

        with open('serverFile.txt','w') as s:
            for i in range(len(self.ServerLog)):
                s.write("\n")
                s.write(self.ServerLog[i])
                s.write("\n")

