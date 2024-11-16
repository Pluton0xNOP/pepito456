import RPi.GPIO as GPIO
import time
import socket
import threading

# Configuración de pines GPIO (asegúrate de definir los pines previamente)
GPIO.setmode(GPIO.BCM)  # Asegúrate de que la numeración de los pines sea correcta
GPIO.setup(RECEPTOR1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RELAY1_PIN, GPIO.OUT)
GPIO.setup(EMISOR1_PIN, GPIO.OUT)
GPIO.setup(RECEPTOR2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RELAY2_PIN, GPIO.OUT)
GPIO.setup(EMISOR2_PIN, GPIO.OUT)

# Inicialización de los pines de salida
GPIO.output(RELAY1_PIN, GPIO.HIGH)
GPIO.output(EMISOR1_PIN, GPIO.LOW)
GPIO.output(RELAY2_PIN, GPIO.HIGH)
GPIO.output(EMISOR2_PIN, GPIO.LOW)

# Función para enviar un mensaje UDP
def enviar_mensaje(mensaje, ip_destino, puerto_destino):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(mensaje.encode(), (ip_destino, puerto_destino))
    except Exception as e:
        print(f"Error enviando el mensaje: {e}")
    finally:
        sock.close()

# Función para activar un relé con un retraso de 3 segundos
def activar_rele(pin_rele):
    print(f"Esperando 3 segundos antes de activar el relé en el pin {pin_rele}")
    time.sleep(3)  # Espera de 3 segundos antes de activar el relé
    print(f"Activando relé en pin {pin_rele} por 1 segundo")
    GPIO.output(pin_rele, GPIO.LOW)  # Activar el relé (bajo para encender)
    time.sleep(1)  # Mantenerlo encendido por 1 segundo
    print(f"Desactivando relé en pin {pin_rele}")
    GPIO.output(pin_rele, GPIO.HIGH)  # Desactivar el relé (alto para apagar)

# Función para controlar el relé 1
def controlar_rele1():
    while True:
        GPIO.output(EMISOR1_PIN, GPIO.HIGH)  # Emitir señal al receptor
        if GPIO.input(RECEPTOR1_PIN) == GPIO.HIGH:  # Si el receptor detecta la señal
            time.sleep(0.05)  # Pequeña espera para estabilizar la señal
            if GPIO.input(RECEPTOR1_PIN) == GPIO.HIGH:  # Verificación final
                print("Se activó la señal en Receptor 1, activando relé 1")
                enviar_mensaje('linea2', '192.168.101.42', 12345)  # Enviar mensaje
                activar_rele(RELAY1_PIN)  # Activar relé con retraso de 3 segundos
        time.sleep(0.1)  # Reducir el uso de la CPU

# Función para controlar el relé 2
def controlar_rele2():
    while True:
        GPIO.output(EMISOR2_PIN, GPIO.HIGH)  # Emitir señal al receptor
        if GPIO.input(RECEPTOR2_PIN) == GPIO.HIGH:  # Si el receptor detecta la señal
            time.sleep(0.05)  # Pequeña espera para estabilizar la señal
            if GPIO.input(RECEPTOR2_PIN) == GPIO.HIGH:  # Verificación final
                print("Se activó la señal en Receptor 2, activando relé 2")
                activar_rele(RELAY2_PIN)  # Activar relé con retraso de 3 segundos
        time.sleep(0.1)  # Reducir el uso de la CPU

# Función principal para iniciar los hilos
def main():
    hilo_rele1 = threading.Thread(target=controlar_rele1)
    hilo_rele2 = threading.Thread(target=controlar_rele2)

    hilo_rele1.start()
    hilo_rele2.start()

    hilo_rele1.join()
    hilo_rele2.join()

# Bloque de ejecución principal
if __name__ == "__main__":
    try:
        main()
    finally:
        GPIO.cleanup()  # Limpiar pines GPIO al finalizar el programa
