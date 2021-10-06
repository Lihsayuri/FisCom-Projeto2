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
import binascii
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
        self.forcarCrcErrado = False

        self.messageType2 = b'\x02'  #server recebeu mensagem do tipo 1 com identificador correto
        self.messageType4 = b'\x04' # servidor dizendo recebeu pacote corretamente, tudo perfeito
        self.messageType5 = b'\x05' # server indicando que deu time-out
        self.messageType6 = b'\x06' #server falando que deu erro no envio 

        self.sinal_verde = b''
        self.byteVazio = b'\x00'
        self.crcVazio = b'\x00\x00'
        self.archiveId = b'\x01'

        self.idSensor = b'\x02'
        self.idServer = b'\x0f'
        self.idClient = b'\x03'

        self.EnvioNaoCompleto = True




    def head(self, messageType, idSensor, idServer, nTotalPack, nCurrentPack, handshakeOrData, reSend, lastSuccessPack, CRC):
        h0 = messageType
        h1 = idSensor
        h2 = idServer
        h3 = nTotalPack
        h4 = nCurrentPack
        h5 = handshakeOrData
        h6 = reSend
        h7 = lastSuccessPack
        h8_h9 = CRC

        Head = b''+ h0 + h1 + h2 + h3 + h4 + h5 + h6 + h7 + h8_h9
        return Head

    def getDataServer(self):
        hoursNow = datetime.now()
        dateNHours = hoursNow.strftime('%d/%m/%Y %H:%M:%S')

        return dateNHours

    def serverLog(self,action,type,size,receivedPckg, totalPckg, CRC):
        char = " / "
        if type == 3:
            log = str(self.getDataServer())+ char + action + char + str(type) + char + str(size) + char + str(receivedPckg) + char + str(totalPckg)  + char + CRC.decode('ascii')
        else:
            log = str(self.getDataServer())+ char + action + char + str(type) + char + str(size) 
        return log

    def conferindoHandshake(self):        
        TentarNovamente = True
        HandshakedeuCerto = False

        while TentarNovamente:
            print("-------------------------")
            print("         HANDSHAKE        ")
            print("-------------------------\n")
            print("Vamos estabelecer o Handshake com o Client")

            if not self.timer2Reset:
                timer2 = time.time()

            txBufferHandshake, tRxHandshake, self.timer2Reset= self.com2.getData(14)  
            self.ServerLog.append(self.serverLog("receb", int.from_bytes(txBufferHandshake[0:1], byteorder="big"), len(txBufferHandshake), "", "", ""))

            print("Recebi do Client e agora vou mandar pro Server:{0}\n".format(txBufferHandshake))

            respostaServer = self.head(self.messageType2, self.idSensor, self.idServer, self.byteVazio, self.byteVazio, self.archiveId, self.byteVazio, self.byteVazio, self.crcVazio ) + self.EOP
            
            print("Essa é a resposta que o Server vai enviar:{0}".format(respostaServer))
            # de bytes transformando para decimal de novo, que é como iremos usar no resto da comunicação

            print("Agora servidor está enviando o Handshake de volta para o client\n")


            if txBufferHandshake[0:1] == b'\x01':
                self.com2.sendData(respostaServer)
                self.ServerLog.append(self.serverLog("envio", int.from_bytes(self.messageType2, byteorder="big"), len(respostaServer), "", "", ""))

                print("Respondi o Handshake e posso começar a transmissão")
                TentarNovamente = False
                HandshakedeuCerto = True
                print("Pronto para receber os pacotes\n")

            cronometroTimer2 = time.time() - timer2
            if cronometroTimer2 >= 20:
                self.com2.disable()
                break
        return HandshakedeuCerto

    def ReenviarPacoteServer(self):
        if self.sinal_verde== b'': 
            lastPackSucessfully = self.byteVazio
        else:
            lastPackSucessfully = (self.sinal_verde[7]).to_bytes(1, byteorder="big")
        CurrentPack = int.from_bytes(lastPackSucessfully, byteorder="big")+1
        CurrentPackByte = CurrentPack.to_bytes(1, byteorder="big")

        CurrentPackDatagrama = self.head(self.messageType6, self.idSensor, self.idClient, self.byteVazio, self.byteVazio, self.byteVazio, CurrentPackByte, lastPackSucessfully, self.crcVazio)+ self.EOP
        print(CurrentPackDatagrama)
        self.com2.sendData(CurrentPackDatagrama)
        self.ServerLog.append(self.serverLog("envio", int.from_bytes(CurrentPackDatagrama[0:1], byteorder="big"), len(CurrentPackDatagrama), "", "", ""))

    def conferindoMensagem(self):
        dataReceived = []
        
        nOldPackage = 0

        while self.EnvioNaoCompleto:
            # time.sleep(2)


            if not self.timer2Reset:
                timer2 = time.time()


            print("Vamos estabelecer o recebimento dos datagramas com o Client!\n")

            self.com2.fisica.flush()

            txBufferHead, tRxNHead, self.timer2Reset = self.com2.getData(10)

            qtdPayloadPacote = txBufferHead[5:6]
            print("O pacote tem o payload de {0}".format(qtdPayloadPacote))

            # pensando no pacote que estamos trabalhando, deveria ser 128
            qtdBytesPack = int.from_bytes(qtdPayloadPacote, byteorder="big") + 4

            print("O primeiro pacote (próximo a ser recebido) TEM TOTAL DE BYTES: {0}".format(qtdBytesPack))

            txPayloadPack, txnPayloadPack, self.timer2Reset = self.com2.getData(qtdBytesPack)

            txPack = txBufferHead + txPayloadPack
            qtdBytesTotal = qtdBytesPack+10

            if self.forcarCrcErrado:
                bytearrayTxPayloadPack = bytearray(txPayloadPack)
                bytearrayTxPayloadPack[10:11] = b'\xff'
                txPack = txBufferHead + bytearrayTxPayloadPack
                print(txPack)
                self.forcarCrcErrado = False

            if self.timer2Reset:
                self.com2.rx.getAllBuffer()
                time.sleep(0.05)

            print(txPayloadPack)

            cronometroTimer2 = time.time() - timer2

            if cronometroTimer2 >=20:
                # if int.from_bytes(txPack[4:5], byteorder="big") == 1:
                #     self.com2.sendData
                print("DEU TIMEOUT DE 20s\n")
                timeout = self.head(self.messageType5, self.idSensor, self.idClient, self.byteVazio, self.byteVazio, self.byteVazio, self.byteVazio, self.byteVazio, self.crcVazio)+ self.EOP
                self.com2.sendData(timeout)
                self.ServerLog.append(self.serverLog("envio", int.from_bytes(timeout[0:1], byteorder="big"), len(timeout), "", "", ""))
                time.sleep(0.01)
                self.com2.disable()
                break

            crc_Client = txPack[8:10]
            crc_Server = binascii.crc_hqx(txPack[10:len(txPack)-4], 0).to_bytes(2,'big')
            print(f"\nO CRC NO SERVER É: {binascii.hexlify(crc_Server)}")
            # crc_server_bytes = binascii.hexlify(crc_Server)

            self.ServerLog.append(self.serverLog("receb", int.from_bytes(txPack[0:1], byteorder="big"), len(txPack), int.from_bytes(txPack[4:5], byteorder="big"), int.from_bytes(txPack[3:4], byteorder="big"), binascii.hexlify(crc_Server)))


            print("\n-----------------------------------")
            print("        ANALISANDO PACOTES...    ")
            print("-----------------------------------\n")

            print("Pacote recebido:{0}\n".format(txPack))

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


            if nCurrentPack == (nOldPackage + 1) and EOP_confere == self.EOP and crc_Client == crc_Server:
                # CurrentPack passa a ser o antigo package recebido com sucesso

                if nCurrentPack == nTotalPacks:
                    dataReceived.append(txPack)
                    print("Recebi todos os pacotes!")
                    self.EnvioNaoCompleto = False
                    self.com2.disable()
                else:
                    self.sinal_verde = self.head(self.messageType4, self.idSensor, self.idClient, self.byteVazio, self.byteVazio, self.byteVazio, self.byteVazio, CurrentPack, self.crcVazio) + self.EOP
                    print(self.sinal_verde[7])
                    print("Pacote recebido está certo! Vou enviar o sinal verde: {0}".format(self.sinal_verde))
                    dataReceived.append(txPack)
                    self.com2.sendData(self.sinal_verde)
                    self.ServerLog.append(self.serverLog("envio", int.from_bytes(self.sinal_verde[0:1], byteorder="big"), len(self.sinal_verde), "", "", ""))
                    nOldPackage+= 1


            else:
                if nCurrentPack != (nOldPackage + 1) and EOP_confere == self.EOP:
                    print("Recebi o pacote errado!")
                    print("O Client vai ter que me enviar o mesmo pacote\n")
                    self.ReenviarPacoteServer()

                elif EOP_confere!= self.EOP:
                    print("Recebi o número de bytes errado! O EOP está fora de ordem")
                    print("O client vai ter que me reenviar o pacote\n")
                    self.ReenviarPacoteServer()

                elif crc_Client != crc_Server:
                    print("ERRO... CRC calculado pelo Server não é o mesmo calculado pelo Client")
                    self.ReenviarPacoteServer()

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

