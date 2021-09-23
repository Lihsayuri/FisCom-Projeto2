#------------------------------------- IMPORTS -------------------------------------------

import random
import time
from typing import Text
from math import ceil  #arredonda uma número para cima
from datetime import datetime
from numpy.core.fromnumeric import size
from enlaceClient import *
from enlaceRxCLient import *
import time
import numpy as np
from PIL import Image
import io
import math
import os

#----------------------------------------------------------------------------------------

class Client:
    def __init__(self):
        self.serialName = "COM5"
        self.com1 = enlace(self.serialName)
        self.com1.enable()

        print("Comunicação aberta com sucesso!\n")

        self.tamanhoHead = 10
        self.tamanhoPayload = 114
        self.tamanhoEOP = 4

        self.ClientLog = []

        self.EOP = b'\xff\xaa\xff\xaa'

        self.messageType1 = b'\x01'  #client convidando o server para a comunicação
        self.messageType3 = b'\x03' #client dizendo que vai enviar o payload 
        self.messageType5 = b'\x05' # client indicando que deu time-out

        self.byteVazio = b'\x00'

        self.archiveId = b'\x0a'

        self.idSensor = b'\x02'
        self.idServer = b'\xf0'

        self.timer2Reset = False

        self.forcarErroNPacks = False

        self.forcarErroNbytes = False

    def head(self, messageType, idSensor, idServer, nTotalPack, nCurrentPack, handshakeOrData, reSend, lastSucessPack):
        h0 = messageType
        h1 = idSensor
        h2 = idServer
        h3 = nTotalPack
        h4 = nCurrentPack
        h5 = handshakeOrData
        h6 = reSend
        h7 = lastSucessPack
        h8 = b'\x00'
        h9 = b'\x01'
        Head = b''+ h0 + h1 + h2 + h3 + h4 + h5 + h6 + h7 + h8 + h9 
        return Head

    def getDataClient(self):
        hoursNow = datetime.now()
        dateNHours = hoursNow.strftime('%d/%m/%Y %H:%M:%S')

        return dateNHours
    
    # •Instante do envio ou recebimento
    # • Envio ou recebimento
    # • Tipo de mensagem (de acordo com o protocolo)
    # • Tamanho de bytes total
    # •Pacote enviado (caso tipo 3)
    # • Total de pacotes (caso tipo 3 )
    # • CRC do payload para mensagem tipo 3 (caso tenha implementado)

    #29/09/2020 13:34:23.089 / envio / 3 / 128 / 1 / 23/ F23F

    def clientLog(self,action,type,size,sentPckg,totalPckg):
        char = " / "
        if type == 3:
            log = str(self.getDataClient())+ char + action + char + "3" + char + str(size) + char + str(sentPckg) + char + str(totalPckg) # + CRC
        else:
            log = str(self.getDataClient())+ char + action + char + str(type) + char + str(size) # + CRC

        return log
    
    def datagramaHandshake(self):
        Head = self.head(self.messageType1, self.idSensor, self.idServer, self.byteVazio, self.byteVazio, self.archiveId, self.byteVazio, self.byteVazio)
        handshakeMessage = Head + self.EOP

        return handshakeMessage

    def sendHandshake(self,handshake):
        # 29/09/2020 13:34:23.089 / envio / 3 / 128 / 1 / 23/ F23F
        TentarNovamente = True
        HandshakeDeuCerto = False

        while TentarNovamente:
            print("-------------------------")
            print("         HANDSHAKE        ")
            print("-------------------------\n")
            print("Handshake pelo client sendo enviado em alguns segundos... \n")

            if not self.timer2Reset:
                timer2 = time.time()

            self.com1.sendData(handshake)
            self.ClientLog.append(self.clientLog("envio", int.from_bytes(self.messageType1, byteorder="big"), len(handshake), "", ""))

            print("Enviou: {0}".format(handshake))
            print("Aguardando a confirmação do Server\n")

            print("Número de bytes enviados:{0}".format(self.com1.tx.transLen))

            rxBufferHandshake, rxnHandshake, self.timer2Reset = self.com1.getData(14)
            self.ClientLog.append(self.clientLog("receb", int.from_bytes(rxBufferHandshake[0:1], byteorder="big"), len(rxBufferHandshake), "", ""))

            
            print("Recebeu o Handshake: {0}\n".format(rxBufferHandshake))

            if rxBufferHandshake[0:1] == b'\x02':
                print("Handshake feito com sucesso!")
                print("O server recebeu o byte: {0}".format(rxBufferHandshake))
                print("Vamos iniciar a transmissao do pacote\n")
                HandshakeDeuCerto = True
                TentarNovamente = False

            # quando o server não responde, essa resposta é autogerada
            else:
                resposta = input("Tentar novamente? S/N ")
                if resposta == "S":
                    TentarNovamente = True
                else: 
                    TentarNovamente = False
                    print("Ocorreu um erro e você não quis tentar novamente. Tente novamente depois então :/")
                    self.com1.disable()
        return HandshakeDeuCerto

    def payload(self,filePath):
        filepath = filePath
        sizePayload = self.tamanhoPayload

        packageList = []
        with open(filepath, "rb") as file:
            binRead = file.read()
            binArray = bytearray(binRead)
            lenPacks = (len(binArray)/sizePayload)
            for i in range(0, int(ceil(lenPacks))):
                packageList.append(binArray[:sizePayload])
                del(binArray[:sizePayload])
        return packageList


    def sendPackages(self, packageList):
        n = 0
        lenPacks_bin = len(packageList).to_bytes(1, byteorder="big")

        print("------------------------------------------")
        print("         INICIANDO ENVIO DE PACOTES      ")
        print("------------------------------------------\n")
        print("Pacote será enviado em alguns segundos... \n")

        while n < (len(packageList)):
            print(n)
            pacotePayload = packageList[n]

            # quanfo for False ele será resetado, porque significa que tudo ocorreu em menos de 5 segundos
            if not self.timer2Reset:
                timer2 = time.time()

            if self.forcarErroNPacks:
                currentPacks = int(n+2).to_bytes(1, byteorder="big")
                self.forcarErroNPacks = False
            else:
                currentPacks = int(n+1).to_bytes(1, byteorder="big")

            # print("ESSE É O CURRENTPACK: {0}".format(currentPacks))

            lastSucessPack = n.to_bytes(1, byteorder='big')
            #Enviando o tamanho do payload do próximo pacote

            if self.forcarErroNbytes:
                pacote_atual = packageList[n]
                BytesErrados =  pacote_atual[0:10] + self.EOP + pacote_atual[10:len(packageList[n])]
                payload_eop= BytesErrados
                datah5_payloadSize = (len(packageList[n])).to_bytes(1, byteorder="big") 
                Head = self.head(self.messageType3, self.idSensor, self.idServer, lenPacks_bin, currentPacks, datah5_payloadSize, self.byteVazio, lastSucessPack)
                pacote = Head + payload_eop
                print("BYTES ERRADOS:{0}".format(pacote))
                self.forcarErroNbytes = False
            else:
                print("ESSE É O TAMANHO DO PACOTE UAI:{0}".format(len(packageList[n])))
                datah5_payloadSize = (len(packageList[n])).to_bytes(1, byteorder="big") 
                print("ESSE É O TAMANHO PACOTE EM BYTES:{0}".format(datah5_payloadSize))
                Head = self.head(self.messageType3, self.idSensor, self.idServer, lenPacks_bin, currentPacks, datah5_payloadSize, self.byteVazio, lastSucessPack)
                pacote = Head + packageList[n] + self.EOP
            # datagramas.append(pacote)
            
            print("Vamos transmitir: {0} bytes".format(len(pacote)))

            print("Quero mandar esse pacote: {0}\n".format(pacote))

            self.com1.sendData(np.asarray(pacote))
            self.ClientLog.append(self.clientLog("envio", int.from_bytes(self.messageType3, byteorder="big"), len(pacote), int.from_bytes(pacote[4:5], byteorder="big"), int.from_bytes(pacote[3:4], byteorder="big")))

            if n != (len(packageList)-1):
                print("Entrei")
                rxNextPack, rxnNextPack, self.timer2Reset  = self.com1.getData(14)
                self.ClientLog.append(self.clientLog("receb", int.from_bytes(rxNextPack[0:1], byteorder="big"), len(rxNextPack), "", ""))
                print("Recebi: {0}".format(rxNextPack))


                cronometroTimer2 = time.time() - timer2
                if cronometroTimer2 >=20:
                    timeout = self.head(self.messageType5, self.idSensor, self.idServer, self.byteVazio, self.byteVazio, self.byteVazio, self.byteVazio, self.byteVazio)+ self.EOP
                    self.com1.sendData(timeout)
                    self.ClientLog.append(self.clientLog("envio", int.from_bytes(timeout[0:1], byteorder="big"), len(timeout), "", ""))
                    time.sleep(0.01)
                    self.com1.disable()
                    break
                elif rxNextPack[0:1] == b'\x04' and rxNextPack[7] == int(n+1):
                    print("O server deu o sinal verde, posso enviar o próximo pacote\n")
                    n+=1
                else:
                    print("Ops... Ocorreu um erro com os pacotes. Muito triste...")
                    print("Recebeu o pacote que é para reenviar {0}".format(rxNextPack))
            else:
                print("Transmissão encerrada!")
                print(self.ClientLog)
                self.com1.disable()
                return

    def logToFileClient(self):
        if os.path.exists('clientFile.txt'):
            os.remove('clientFile.txt')

        with open('clientFile.txt','w') as s:
            for i in range(len(self.ClientLog)):
                s.write("\n")
                s.write(self.ClientLog[i])
                s.write("\n")

