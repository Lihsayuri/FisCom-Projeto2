# from datetime import datetime

# data_e_hora_atual = datetime.now()
# data_e_hora = data_e_hora_atual.strftime('%d/%m/%Y %H:%M:%S')

# # print(data_e_hora)

# n = 0

# intn = n.to_bytes(1, byteorder="big")

# datah5_payloadSize = int(114).to_bytes(1, byteorder="big") 
# intdenovo = int.from_bytes(datah5_payloadSize, byteorder="big")

# PAU = b'r'

# PAUINT = int.from_bytes(PAU, byteorder="big")

# # print(datah5_payloadSize)
# # print(intdenovo)
# # print(PAUINT)

# rx = b'\x04\x02\x0f\x00\x00\x00\x00\x01\x00\x01\xff\xaa\xff\xaa'

# pacote = b'\x03\x02\xf0\x04\x03-\x00\x03\x00\x01o, isto E quem somos, e e tudo. Perene flui a interminavel hora Que nos confessa nulos. No mesmo hausto Em que viv\xff\xaa\xff\xaa'

# # print(rx[0:1])
# # print(rx[7])

# teste = int(45).to_bytes(1, byteorder="big")
# testeint = int.from_bytes(teste, byteorder="big")
# qtdBytes = testeint + 10 + 4

# print(len(pacote))

# print(pacote[qtdBytes-4 : qtdBytes]) 


from tqdm import tqdm
import time

for i in tqdm(range(int(9e6)),desc = "Progresso do Handshake: "):
    time.sleep(0.5)
