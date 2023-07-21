import time
import RPi.GPIO as GPIO
import serial
import re
import subprocess
from pygame import mixer
from datetime import *
from omxplayer.player import OMXPlayer
from pathlib import Path
from time import sleep

#Variables
next="00"
playing = "00"
isAudioPlayed=False
v_w_audio=["2", "6", "4", "5", "8", "a", "1"]
v_positions = {
    "2": (0,7),  #Hola mi nombre es qhali
    "6": (10,15),  #Venimos hasta aqui
    "4": (20,28),  #Estare aqui acompanandote
    "5": (30,32),  #Hoy el se encargara de la sesion
    "8": (35,40),  #El es un especialista del hospital
    "a": (45,51),  #Claro que si Solo eran mis
    "1": (55,63),  #Fue un gusto poder acompañarte
    "3": (65,69),  #Cara feliz
    "0": (65,69),  #Cara feliz
    "7": (65,69),  #Cara estrella
    "b": (85,88),  #Cara ojos estrella
}

#Last audio played
file_save=open(r"/home/pi/Downloads/Serial_Videos/time.txt",'r')
last=datetime.strptime(file_save.read(), '%Y/%m/%d %H:%M:%S.%f')
file_save.close()

#Videos
video_1_path = Path("/home/pi/Downloads/Serial_Videos/Videos/Prueba_Top.mp4")
video_2_path = Path("/home/pi/Downloads/Serial_Videos/Videos/Prueba_Bottom.mp4")
player1 = OMXPlayer(video_1_path, args = ['--display=7','--orientation=180','--loop','--adev=local'],dbus_name='org.mpris.MediaPlayer2.omxplayer1')
player2 = OMXPlayer(video_2_path, args = ['--display=2','--orientation=180','--loop'], dbus_name='org.mpris.MediaPlayer2.omxplayer2')

#Initiaze JBL
def JBL_init():
    global last
    delta=timedelta(minutes=15)
    if (datetime.now()-last>delta):
        pin=40
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)
        sleep(5)
        GPIO.output(pin, GPIO.LOW)
        GPIO.cleanup()
        save_time()

def check_time():
    global last
    delta=timedelta(minutes=14)
    if (datetime.now()-last>delta):     
        mixer.init()
        mixer.music.load("/home/pi/Downloads/Serial_Videos/Audios/AudioSordo.mp3")
        mixer.music.play()
        save_time()
#Save current time
def save_time():
    global last   
    file_save=open(r"/home/pi/Downloads/Serial_Videos/time.txt",'w+')
    last = datetime.now()
    file_save.write(last.strftime("%Y/%m/%d %H:%M:%S.%f"))
    file_save.close()

#Control the displaying video
def video_handler(command):
    global playing, player1, player2, isAudioPlayed, last, next
    next="00"
    if len(command) == 2 : 
        #Select next video
        if isAudioPlayed == True :
            if command[1] == "2":
                if command[0] == "6":
                    next="42"
                elif command[0] == "4":
                    next="52" 
                elif command[0] == "5":
                    next="82"
                elif command[0] == "8":
                    next="00"
                elif command[0] == "a":
                    next="12"
                elif command[0]=="1":
                    next="22"
                elif command[0]=="2":
                    next="00"   
                else:
                    next="00"
            if command[1] == "0":
                next="00"
        else:
            next=command  
        print(next)

        player1.set_position(v_positions[next[0]][0])
        print(v_positions[next[0]][0])
        player2.set_position(v_positions[next[0]][0])
        playing = next
        if next[0] in v_w_audio:
            isAudioPlayed=True
        else:
            isAudioPlayed=False
        print(isAudioPlayed)

        if(command[0] in v_w_audio):
            last=datetime.now()
            save_time()
               
JBL_init()

serial_port = serial.Serial(
port="/dev/ttyS0",
baudrate=115200,
bytesize=serial.EIGHTBITS,
parity=serial.PARITY_NONE,
stopbits=serial.STOPBITS_ONE,
timeout=0,)

sleep(1)
print("Interfaz de pantallas")

while True:
    #JBL audio
    check_time()   
    #UART
    if serial_port.inWaiting() > 0:
        data = serial_port.read(2)
        data=data.decode() 
        print(data)
        video_handler(data)
    #Video Loop
    position = player1.position()
    print(position)
    if (position> v_positions[playing[0]][1]+0.3 or position< v_positions[playing[0]][0]-0.3):
        video_handler(playing)