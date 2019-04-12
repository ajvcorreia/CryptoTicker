#!/usr/bin/python
#--------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#  lcd_16x2.py
#  16x2 LCD Test Script
#
# Author : Matt Hawkins
# Date   : 06/04/2015
#
# http://www.raspberrypi-spy.co.uk/
#
# Copyright 2015 Matt Hawkins
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#--------------------------------------

# The wiring for the LCD is as follows:
# 1 : GND
# 2 : 5V
# 3 : Contrast (0-5V)*
# 4 : RS (Register Select)
# 5 : R/W (Read Write)       - GROUND THIS PIN
# 6 : Enable or Strobe
# 7 : Data Bit 0             - NOT USED
# 8 : Data Bit 1             - NOT USED
# 9 : Data Bit 2             - NOT USED
# 10: Data Bit 3             - NOT USED
# 11: Data Bit 4
# 12: Data Bit 5
# 13: Data Bit 6
# 14: Data Bit 7
# 15: LCD Backlight +5V**
# 16: LCD Backlight GND

#import
import RPi.GPIO as GPIO
import time
import feedparser
from datetime import datetime
from time import sleep
from coinmarketcap import Market
import json
import urllib2
from weather import Weather, Unit
import socket
import fcntl
import struct



# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18


# Define some device constants
LCD_WIDTH = 20    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94
LCD_LINE_4 = 0xD4

global line1
global line2
global line3
global line4

line1 = ""
line2 = ""
line3 = ""
line4 = ""
# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

def main():
    sleep(30)
  # Main program block
    global line1
    global line2
    global line3
    global line4
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
    GPIO.setup(LCD_E, GPIO.OUT)  # E
    GPIO.setup(LCD_RS, GPIO.OUT) # RS
    GPIO.setup(LCD_D4, GPIO.OUT) # DB4
    GPIO.setup(LCD_D5, GPIO.OUT) # DB5
    GPIO.setup(LCD_D6, GPIO.OUT) # DB6
    GPIO.setup(LCD_D7, GPIO.OUT) # DB7


  # Initialise display
    lcd_init()

    currencies = ['bitcoin', 'litecoin', 'dogecoin']

    now = datetime.now()
    mm = str(now.month)
    dd = str(now.day)
    yyyy = str(now.year)
    hour = str(now.hour)
    mi = str(now.minute)
    ss = str(now.second)
    DateTime = mm + "/" + dd + "/" + yyyy + " " + hour + ":" + mi + ":" + ss
    wlan = (get_interface_ipaddress('wlan0'))
    #eth = (get_interface_ipaddress('eth0'))
    lcd_string("   Crypto Ticker    ",LCD_LINE_1)
    lcd_string(DateTime,LCD_LINE_2)
    #lcd_string("eth  : " + eth,LCD_LINE_3)
    lcd_string(wlan,LCD_LINE_4)
    sleep(5)

    while True:
        now = datetime.now()
        mm = str(now.month)
        dd = str(now.day)
        yyyy = str(now.year)
        hour = str(now.hour)
        mi = str(now.minute)
        ss = str(now.second)
        if hour < 10:
            hour = "0" + hour
        if mi < 10:
            mi = "0" + mi
        if ss < 10:
            ss = "0" + ss
        print_lcd(mm + "/" + dd + "/" + yyyy + " " + hour + ":" + mi + ":" + ss, 0)

        for currency in currencies:
            ticker=''
            url = "https://api.coinmarketcap.com/v1/ticker/%s/" % currency
            data = json.load(urllib2.urlopen(url))[0]
            ticker += '%s ' % data['symbol']
            ticker += '$%s ' % data['price_usd']
            print_lcd(ticker,0)


        #print(ticker)
        sleep(3)
        weather = Weather(unit=Unit.CELSIUS)
        loc = 'london'
        location = weather.lookup_by_location(loc)
        condition = location.condition
        #print_lcd(">"+condition.text+"<",2)
        forecasts = location.forecast
        temps = 0
        for forecast in forecasts:
            print_lcd(forecast.date,0)
            print_lcd(loc + " " + forecast.text,0)
            print_lcd("High: "+forecast.high+" Low: "+forecast.low,0)
            print_lcd("",3)
            if temps >= 1:
                break
            temps += 1

        d = feedparser.parse('http://pplware.sapo.pt/feed/')

        print_lcd(d['feed']['title'],0)

        for post in d.entries:
            print_lcd(post.title,1)
        #    l = len(post.title)
        #    for x in range(0, l, 20):
        #        line = post.title[30:20]
        #        print (len(post.title))
        #        print_lcd(line,1)
        # Send some test
        #print line1
        #print line2
        #print line3
        #print line4
        #print_lcd(ticker)
        #print_lcd("BTC/USD 7453")
        #print_lcd("BTC/GBP 5453")
        #print_lcd("LTC/EUR 107")
        #print_lcd("NiceHash 110000")
        time.sleep(1)

def print_lcd(text, time):
    #file = open("crypto.log","a")
    #file.write(text + '\n')
    #file.close()
  # Scroll text in on lcd and write a new line
    global line1
    global line2
    global line3
    global line4
    line1 = line2
    line2 = line3
    line3 = line4
    line4 = text
    lcd_string(line1,LCD_LINE_1)
    lcd_string(line2,LCD_LINE_2)
    lcd_string(line3,LCD_LINE_3)
    lcd_string(line4,LCD_LINE_4)
    sleep(time)

def get_interface_ipaddress(network):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', network[:15])
    )[20:24])


def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display




  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("Goodbye!",LCD_LINE_1)
    GPIO.cleanup()
