#%%
import serial
from time import sleep
import sys
import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np
import cv2
import time

########## Read Label.txt ##########
def load_labels(path):
  with open(path, 'r') as f:
    return {i: line.strip() for i, line in enumerate(f.readlines())}

########## Serial ##########
COM_PORT = 'COM3'
BAUD_RATES = 9600
ser = serial.Serial(COM_PORT, BAUD_RATES)
send_freq= 2

########## Teachable Machine ##########
np.set_printoptions(4, suppress=True)
model = tensorflow.keras.models.load_model('keras_model.h5')
label = load_labels('labels.txt')
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

########## Open Camera ##########
cap = cv2.VideoCapture(1)

########## Debounce ##########
pre_time = time.time()
send_clock = pre_time
text, pre_text = ' ', ' '
read_sec = 0

########## Show Divider ##########
div = '-'*30

try:
    print(f'Start Detected\n\n{div}\n')

    while(True):

        ret, frame = cap.read()

        ########## Inference ##########

        trg_frame = cv2.resize(frame, (224, 224))

        normalized_image_array = (trg_frame.astype(np.float32) / 127.0) - 1

        data[0] = normalized_image_array
            
        prediction = model.predict(data)

        label_name = str(label[np.argmax(prediction)])

        ########## Send to 7697 by UART ##########
        
        text = label_name.split(' ')[0]

        if text != pre_text:
            send_clock = time.time()
            pre_text = text
        else :
            read_sec = time.time()- send_clock
            if(read_sec >= send_freq):
                send_text = '{}\n'.format(text).encode()
                print(f'Detected Label:{label_name}\tSend Data:{send_text}\n\n{div}\n')
                ser.write(send_text)

                send_clock = time.time()      
        
        cv2.putText(frame ,str(int(read_sec)) , (500,50), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),3)

        ########## Display ##########
        cv2.putText(frame ,label_name , (30,50), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),3)  
        cv2.imshow('camera', frame)

        key = cv2.waitKey(1)

        if key==ord('q'):
            print('Exit System')
            break

        ########## Save pre data ##########
        if time.time()- pre_time == 1:
            pre_data = data

    ########## Close ##########
    cap.release()
    cv2.destroyAllWindows()
    ser.close()

except KeyboardInterrupt:
    cap.release()
    ser.close()
    cv2.destroyAllWindows()
    print('強制離開')

# %%
