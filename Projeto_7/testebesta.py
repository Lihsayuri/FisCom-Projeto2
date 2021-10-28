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
