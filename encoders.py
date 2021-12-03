#! /usr/bin/python

import smbus2
from gpiozero import Button
from time import sleep
import i2cEncoderLibV2
import random
import subprocess

def map(x, in_min, in_max, out_min, out_max):
   return int((x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min)

initial_volume = 50

bus=smbus2.SMBus(1)
int_pin = Button(4)
address1 = 0x05
address2 = 0x04

encoder1 = i2cEncoderLibV2.i2cEncoderLibV2(bus,address1)
encoder2 = i2cEncoderLibV2.i2cEncoderLibV2(bus,address2)

encconfig=(i2cEncoderLibV2.INT_DATA | i2cEncoderLibV2.WRAP_DISABLE | i2cEncoderLibV2.DIRE_RIGHT | i2cEncoderLibV2.IPUP_ENABLE | i2cEncoderLibV2.RMOD_X1 | i2cEncoderLibV2.RGB_ENCODER)
encoder1.begin(encconfig)
encoder2.begin(encconfig)

encoder1.writeCounter(0)
encoder1.writeMax(100.0)
encoder1.writeMin(0)
encoder1.writeStep(2)
encoder1.writeInterruptConfig(0xff)

encoder2.writeCounter(initial_volume)
encoder2.writeMax(100.0)
encoder2.writeMin(0)
encoder2.writeStep(2)
encoder2.writeInterruptConfig(0xff)

# Controls how long the volume colors appears before going back to random colors
count = 0

# Volume write
def volume_write(volume):
   actual_min = 30
   actual_max = 100
   volume = map(volume, 0, 100, actual_min, actual_max)
   volume_command = "amixer set 'PCM' unmute {}%".format(volume)
   print volume_command
   p = subprocess.Popen(volume_command, shell=True, stdout=subprocess.PIPE)
   code = p.wait()
   if code != 0:
      print "VOLUME ERROR"
volume_write(initial_volume)


while True:
   encoder1.writeRGBCode(random.randrange(0xFFFFFF))
   if encoder2.updateStatus():
      vol = encoder2.readCounter8()
      color_red = int(vol*2.55)
      color_green = 255-color_red
      color_blue = 0
      color = color_blue | (color_green<<8) | (color_red<<16)
      encoder2.writeRGBCode(color)
      count = 16
      volume_write(vol)
   elif count==0:
      encoder2.writeRGBCode(random.randrange(0xFFFFFF))
   else:
      count -= 1
   sleep(0.25)
