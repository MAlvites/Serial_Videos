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
playing = "50"
audio_count=0
v_w_audio=["40"]
v_positions = {
    "0": (0,5),
    "1": (0,5),
    "2": (0,5),
    "3": (0,5),
    "4": (0,5),
    "5": (0,5),
    "6": (10,15),
    "8": (20,25),
}

#Last audio played
file_save=open(r"/home/pi/Downloads/Serial_Videos/time.txt",'r')
last=datetime.strptime(file_save.read(), '%Y/%m/%d %H:%M:%S.%f')
file_save.close()

#Videos
video_1_path = Path("/home/pi/Downloads/Serial_Videos/Videos/Pru.mp4")
video_2_path = Path("/home/pi/Downloads/Serial_Videos/Videos/Presentacion_bottom.mp4")
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
        print("here")
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
    global playing, player1, player2, audio_count, last
    if len(command) == 2 :
        if(command in v_w_audio):
            if (audio_count==0):
                audio_count=audio_count+1
            else:
                #Last audio played
                last=datetime.now()
                save_time()
                #Change to no Audio
                command="50"
                audio_count=0

        if (command[0] in v_positions.keys()) and command[1] == "0":
            print("here")
            #player1.pause()
            #player2.pause()
            player1.set_position(v_positions[command[0]][0])
            print(v_positions[command[0]][0])
            player2.set_position(v_positions[command[0]][0])
            playing = command
            
        if (command[1] in v_positions.keys()) and command[0] == "0":
            player1.set_position(v_positions[command[1]][0])
            player2.set_position(v_positions[command[1]][0])
            playing = command

#def main(e,):
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
    print(last)    
    #UART
    if serial_port.inWaiting() > 0:
        data = serial_port.read(2)
        data=data.decode() 
        print(data)
        video_handler(data)
    #Video Loop
    position = player1.position()
    print(position)
    if (playing[1]=="0" and position>= v_positions[playing[0]][1]):
        video_handler(playing)
        
    if (playing[0]=="0" and position>= v_positions[playing[1]][1]):
        video_handler(playing)