#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
import os
import time
import sys

continue_reading = True
bloco = 4
pinoBuzzer = 22

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C capturado, Finalizando Leitura."
    continue_reading = False
    GPIO.cleanup()

def escreve_erro_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pinoBuzzer,GPIO.OUT)
    GPIO.output(pinoBuzzer,True)
    time.sleep(.08)
    GPIO.output(pinoBuzzer,False)
    time.sleep(.08)
    GPIO.output(pinoBuzzer,True)
    time.sleep(.08)
    GPIO.output(pinoBuzzer,False)
    time.sleep(.08)
    GPIO.output(pinoBuzzer,True)
    time.sleep(.08)
    GPIO.output(pinoBuzzer,False)
    time.sleep(.08)
    print "bip bip bip"

def escreve_ok_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pinoBuzzer,GPIO.OUT)
    GPIO.output(pinoBuzzer,True)
    time.sleep(.1)
    GPIO.output(pinoBuzzer,False)
    print "bip"

def escreve_token_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pinoBuzzer,GPIO.OUT)
    GPIO.output(pinoBuzzer,True)
    time.sleep(.8)
    GPIO.output(pinoBuzzer,False)
    print "biiiiiiiiiiiiip"

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Pressione Ctrl-C para finalizar."

# This loop keeps checking for chips.  If one is near it will get the UID and
# authenticate
while continue_reading:
    try:
        # print "Busca por cartões"
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
                #print(int(hexaValorRecuperado, 16))
                # print("Imprimindo o valor no terminal")

		print "Valor Recuperado: " + "\033[32m" + str(int(hexaValorRecuperado,16)) + "\033[0;0m"		

		if str(int(hexaValorRecuperado,16)) == "99999999999":
			print "\033[31m"+ "TOKEN DE EMERGÊNCIA. ACIONANDO SCRIPT..." + "\033[0;0m"
			escreve_token_gpio()
			os.system("sudo reboot")
		else:
			print "Escrevendo no teclado"
			os.system("xte 'str " + str(int(hexaValorRecuperado, 16)) + "' 'key Return'")
			escreve_ok_gpio()
		time.sleep(1)
                #MIFAREReader.MFRC522_StopCrypto1()                
            else:
                print  "\033[33m" + "Erro de autenticação do cartão" + "\033[0;0m"
                escreve_erro_gpio()
    except Exception, e:
        print "\033[33m" + "Exception: " + str(sys.exc_info()[0]) + "\033[0;0m"
        escreve_erro_gpio()
        pass
    finally:
        MIFAREReader.MFRC522_StopCrypto1()
        time.sleep(.6)
