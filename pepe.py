import RPi.GPIO as GPIO
import time
import socket
import threading

RELAY1_PIN = 17
EMISOR1_PIN = 23
RECEPTOR1_PIN = 24

RELAY2_PIN = 27
EMISOR2_PIN = 5
RECEPTOR2_PIN = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY1_PIN, GPIO.OUT)
GPIO.setup(EMISOR1_PIN, GPIO.OUT)
GPIO.setup(RECEPTOR1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RELAY2_PIN, GPIO.OUT)
GPIO.setup(EMISOR2_PIN, GPIO.OUT)
GPIO.setup(RECEPTOR2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.output(RELAY1_PIN, GPIO.HIGH)
GPIO.output(EMISOR1_PIN, GPIO.LOW)
GPIO.output(RELAY2_PIN, GPIO.HIGH)
GPIO.output(EMISOR2_PIN, GPIO.LOW)


def enviar_mensaje_linea3(mensaje):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(mensaje.encode(), (IP_DESTINO, PUERTO_DESTINO))
    sock.close()

def enviar_mensaje_linea4(mensaje,IP_DESTINO,PUERTO_DESTINO):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(mensaje.encode(), (IP_DESTINO, PUERTO_DESTINO))
    sock.close()

def activar_rele(pin_rele):
    print(f"Esperando 2 segundos antes de activar el relé en el pin {pin_rele}")
    time.sleep(2)
    print(f"Activando relé en pin {pin_rele} por 1 segundo")
    GPIO.output(pin_rele, GPIO.LOW)
    time.sleep(1)
    print(f"Desactivando relé en pin {pin_rele}")
    GPIO.output(pin_rele, GPIO.HIGH)


def controlar_rele1():

    while True:
        GPIO.output(EMISOR1_PIN, GPIO.HIGH)
        if GPIO.input(RECEPTOR1_PIN) == GPIO.HIGH:
            time.sleep(0.05)
            if GPIO.input(RECEPTOR1_PIN) == GPIO.HIGH:
                print("Se activó la señal en Receptor 1, activando relé 1")
                enviar_mensaje_linea4('linea2','192.168.101.42',12345)
                activar_rele(RELAY1_PIN)

        time.sleep(0.1)

def controlar_rele2():
    while True:
        GPIO.output(EMISOR2_PIN, GPIO.HIGH)
        if GPIO.input(RECEPTOR2_PIN) == GPIO.HIGH:
            time.sleep(0.05)
            if GPIO.input(RECEPTOR2_PIN) == GPIO.HIGH:
                print("Se activó la señal en Receptor 2, activando relé 2")
                activar_rele(RELAY2_PIN)


        time.sleep(0.1)

def main():
    hilo_rele1 = threading.Thread(target=controlar_rele1)
    hilo_rele2 = threading.Thread(target=controlar_rele2)

    hilo_rele1.start()
    hilo_rele2.start()

    hilo_rele1.join()
    hilo_rele2.join()

if __name__ == "__main__":
    main()
