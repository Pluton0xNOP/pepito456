import RPi.GPIO as GPIO
import time
import socket
import threading

RELAY1_PIN = 16
EMISOR1_PIN = 19
RECEPTOR1_PIN = 26

RELAY2_PIN = 12
EMISOR2_PIN = 20
RECEPTOR2_PIN = 21

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

# Umbral mínimo de tiempo (en segundos) para confirmar una señal válida
DELAY_SIGNALS = 6  # 6 segundos

# Función para enviar el mensaje
def enviar_mensaje_linea(mensaje, IP_DESTINO, PUERTO_DESTINO):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(mensaje.encode(), (IP_DESTINO, PUERTO_DESTINO))
        time.sleep(0.5)
    except Exception as e:
        print(f"Error al enviar el mensaje: {e}")
    finally:
        sock.close()

# Función para activar el relé
def activar_rele(pin_rele):
    print(f"Esperando 4 segundos antes de activar el relé en el pin {pin_rele}")
    time.sleep(2.5)  # Puede reducirse si es necesario
    print(f"Activando relé en pin {pin_rele} por 1 segundo")
    GPIO.output(pin_rele, GPIO.LOW)
    time.sleep(1.2)
    print(f"Desactivando relé en pin {pin_rele}")
    GPIO.output(pin_rele, GPIO.HIGH)

# Función para controlar el relé 1
def controlar_rele1():
    last_trigger_time = 0  # Tiempo del último evento válido

    while True:
        GPIO.output(EMISOR1_PIN, GPIO.HIGH)
        if GPIO.input(RECEPTOR1_PIN) == GPIO.HIGH:
            # Si la señal está activa, esperamos un poco para asegurarnos de que no es una señal falsa
            time.sleep(0.05)
            if GPIO.input(RECEPTOR1_PIN) == GPIO.HIGH:
                current_time = time.time()  # Tiempo actual
                # Verificamos si ha pasado suficiente tiempo desde la última activación
                if current_time - last_trigger_time >= DELAY_SIGNALS:
                    print("Se activó la señal en Receptor 1, activando relé 1")
                    enviar_mensaje_linea('linea2', '192.168.101.37', 12345)
                    time.sleep(0.5)
                    activar_rele(RELAY1_PIN)
                    last_trigger_time = current_time  # Actualizamos el tiempo del último evento

        time.sleep(0.1)

# Función para controlar el relé 2
def controlar_rele2():
    last_trigger_time = 0  # Tiempo del último evento válido

    while True:
        GPIO.output(EMISOR2_PIN, GPIO.HIGH)
        if GPIO.input(RECEPTOR2_PIN) == GPIO.HIGH:
            # Si la señal está activa, esperamos un poco para asegurarnos de que no es una señal falsa
            time.sleep(0.05)
            if GPIO.input(RECEPTOR2_PIN) == GPIO.HIGH:
                current_time = time.time()  # Tiempo actual
                # Verificamos si ha pasado suficiente tiempo desde la última activación
                if current_time - last_trigger_time >= DELAY_SIGNALS:
                    print("Se activó la señal en Receptor 2, activando relé 2")
                    enviar_mensaje_linea('linea1', '192.168.101.52', 12345)
                    time.sleep(0.5)
                    activar_rele(RELAY2_PIN)
                    last_trigger_time = current_time  # Actualizamos el tiempo del último evento

        time.sleep(0.1)

def main():
    try:
        # Iniciar los hilos para controlar los relés
        hilo_rele1 = threading.Thread(target=controlar_rele1)
        hilo_rele2 = threading.Thread(target=controlar_rele2)

        hilo_rele1.start()
        hilo_rele2.start()

        # Esperar a que los hilos terminen (en este caso, nunca terminarán)
        hilo_rele1.join()
        hilo_rele2.join()

    except KeyboardInterrupt:
        # Capturar Ctrl+C para terminar el script de manera controlada
        print("Deteniendo el script...")
        GPIO.cleanup()  # Limpiar GPIO para liberar los pines
