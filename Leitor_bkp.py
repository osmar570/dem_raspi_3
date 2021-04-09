#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
import os
import time

continue_reading = True
bloco = 4

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Press Ctrl-C to stop."

# This loop keeps checking for chips.  If one is near it will get the UID and
# authenticate
while continue_reading:

    try:
        # Busca por cartões
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        # Faz ao detectar o cartão no campo
        if status == MIFAREReader.MI_OK:
            print "\033[92m Cartão detectado"
        else:
            pass

        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:

            # Imprime UID em tela
            #print "ID unico do Cartão: " + str(uid[0]) + "," + str(uid[1]) + "," + str(uid[2]) + "," + str(uid[3])

            # Chave para autenticação da trilha
            key = [0x00 ,0x00 ,0x00 ,0x00 ,0x00 ,0x00]

            # Padrão de fábrica/acesso trilha principal
            #key = [0xFF ,0xFF ,0xFF ,0xFF ,0xFF ,0xFF]

            # Select the scanned tag
            MIFAREReader.MFRC522_SelectTag(uid)

            # Authenticate
            status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, bloco, key, uid)
            # Check if authenticated

            if status == MIFAREReader.MI_OK:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(22,GPIO.OUT)
                GPIO.output(22,True)
                time.sleep(.1)
                GPIO.output(22,False)

                #Captura a informação da trilha (linha ou bloco) todo
                valorCartaoBloco = MIFAREReader.MFRC522_ReadBlock(bloco)

                # Variavel que armazena o valor em hexadecimal
                hexaValorRecuperado = ""

                # Monta o valor em hexadecimal dentro de campo string
                for i in range(4, -1, -1):
                    hexaValorRecuperado += str(hex(valorCartaoBloco[i]).rstrip("L").lstrip("0x"))

                # Descomentar as Linhas abaixo para debug:
                # #Imprime o resultado da trilha em tela (decimal)
                # print(valorCartaoBloco)
                # print("Valor bruto:")
                # print(MIFAREReader.MFRC522_Read(bloco))
                # print("CPF (Setor 2 Bloco 4[4,3,2,1,0]) em hexa:")
                # print(hexaValorRecuperado)
                # print("CPF Literal: ")
                # print(int(hexaValorRecuperado, 16))
                # print("Imprimindo o valor no terminal")

                os.system("xte 'str " + str(int(hexaValorRecuperado, 16)) + "' 'key Return'")

                MIFAREReader.MFRC522_StopCrypto1()
            else:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(22,GPIO.OUT)

                GPIO.output(22,True)
                time.sleep(.08)
                GPIO.output(22,False)
                time.sleep(.08)
                GPIO.output(22,True)
                time.sleep(.08)
                GPIO.output(22,False)
                time.sleep(.08)
                GPIO.output(22,True)
                time.sleep(.08)
                GPIO.output(22,False)
                time.sleep(.08)

                print "Authentication error"
        except:
            print "Exception: " + sys.exc_info()[0]
