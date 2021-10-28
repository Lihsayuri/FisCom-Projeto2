import numpy as np

audio = [[ 0.0000000e+00],[ 0.0000000e+00], [-3.0517578e-05], [ 0.0000000e+00], [ 0.0000000e+00], [ 0.0000000e+00], [ 0.0000000e+00], [-3.0517578e-05], [ 0.0000000e+00], [ 0.0000000e+00]]

npAudio = np.ndarray(shape=(10,),dtype=np.float32) 

# print(npAudio)

for i in range(0,npAudio.shape[0]):
    print(npAudio.shape[0])
    npAudio[i] = audio[i][0]
    print(audio[i])
    print(npAudio[i])

print(npAudio)


def achaTecla(index, x):
    frqObtidaLista = [[], []]
    for frequencia in x[index]:
        #Linha
        if int(frequencia) in range(640, 990):
            frqObtidaLista[0].append(int(frequencia))
        #Coluna
        elif int(frequencia) in range(1160, 1680):
            frqObtidaLista[1].append(int(frequencia))

    tabelaDeFrequencias = {"1":[697, 1209], "2":[697, 1336], "3":[697, 1477], "A":[697, 1633], "4":[770, 1209], "5":[770, 1336], "6":[770, 1477], "B":[770, 1633], "7":[852, 1209], "8":[852, 1336], "9":[852, 1477], "C":[852, 1633], "X":[941, 1209], "0":[941, 1336], "#":[941, 1477], "D":[941, 1633]}

    character = "None"
    resolucao = 30
    for tecla, frequencias in tabelaDeFrequencias.items():
        #exemplo tecla 2, tenho 2 picos: [ 697.51581669 1335.53028413]. Quero que o primeiro esteja entre 667 <= x <= 727 e o segundo entre 1306 <= x <= 1366
        if (frqObtidaLista[0][0] <= frequencias[0] + resolucao) and (frqObtidaLista[0][0] >= frequencias[0] - resolucao) and (frqObtidaLista[1][0] <= frequencias[1] + resolucao) and (frqObtidaLista[1][0] >= frequencias[1] - resolucao):
            character = tecla
    
    print(f"\n[+]---Tecla referente ao som gravado: {character}")
