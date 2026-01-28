#!/usr/bin/env python3
import time
import json
import board
import busio
import neopixel
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import ssl 
from PIL import Image, ImageDraw, ImageFont
from mfrc522 import MFRC522
import adafruit_bme280.advanced as adafruit_bme280
import lib.oled.SSD1331 as SSD1331

# --- KONFIGURACJA MQTT (Z SZYFROWANIEM) ---
BROKER = "localhost"
PORT = 8883  # <--- ZMIANA PORTU NA 8883 (MQTTS)
CA_CERT = "/home/pi/ca.crt" 

TOPIC_SENSORS = "home/sensors"
TOPIC_ACCESS_REQ = "home/access/request"
TOPIC_ACCESS_RES = "home/access/response"


PIN_BUZZER = 23
PIN_WS2812 = board.D18
LED_COUNT = 8


current_temp = 0.0
current_hum = 0.0
current_press = 0.0
last_sensor_time = 0
SENSOR_INTERVAL = 5


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_BUZZER, GPIO.OUT)
GPIO.output(PIN_BUZZER, 1) 


pixels = neopixel.NeoPixel(PIN_WS2812, LED_COUNT, brightness=0.5, auto_write=False)


i2c = busio.I2C(board.SCL, board.SDA)
try:
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
    bme280.standby_period = adafruit_bme280.STANDBY_TC_500
    bme280.iir_filter = adafruit_bme280.IIR_FILTER_X16
except Exception as e:
    print(f"Blad BME280: {e}")
    bme280 = None


disp = SSD1331.SSD1331()
disp.Init()
disp.clear()


image = Image.new("RGB", (disp.width, disp.height), "BLACK")
draw = ImageDraw.Draw(image)
try:
    fontBig = ImageFont.truetype('./lib/oled/Font.ttf', 12)
    fontSmall = ImageFont.truetype('./lib/oled/Font.ttf', 9)
except:
    fontBig = ImageFont.load_default()
    fontSmall = ImageFont.load_default()


reader = MFRC522()



def sound_beep(duration=0.1):
    GPIO.output(PIN_BUZZER, 0) 
    time.sleep(duration)
    GPIO.output(PIN_BUZZER, 1)

def sound_alarm():
    for _ in range(3):
        GPIO.output(PIN_BUZZER, 0)
        time.sleep(0.1)
        GPIO.output(PIN_BUZZER, 1)
        time.sleep(0.1)

def set_leds(color):
    pixels.fill(color)
    pixels.show()

def update_oled(status_msg, color="WHITE"):
    draw.rectangle((0, 0, disp.width, disp.height), fill="BLACK")
    
    draw.text((2, 0), "STATUS:", font=fontSmall, fill="WHITE")
    draw.text((2, 12), status_msg, font=fontBig, fill=color)
    
    draw.line((0, 26, 96, 26), fill="BLUE")
    
    # Dane srodowiskowe
    draw.text((2, 29), f"Temp: {current_temp:.1f} C", font=fontSmall, fill="WHITE")
    draw.text((2, 39), f"Wilg: {current_hum:.1f} %", font=fontSmall, fill="WHITE")
    draw.text((2, 49), f"Cisn: {current_press:.0f} hPa", font=fontSmall, fill="WHITE")

    disp.ShowImage(image, 0, 0)




def on_connect(client, userdata, flags, rc):
    print(f"Polaczono z MQTT (Kod: {rc})")
    client.subscribe(TOPIC_ACCESS_RES)

def on_message(client, userdata, msg):

    payload = msg.payload.decode("utf-8")
    print(f"Otrzymano rozkaz: {payload}")
    
    if payload == "GRANT":
        update_oled("WSTEP WOLNY", "GREEN")
        set_leds((0, 255, 0)) 
        sound_beep(0.2)
        time.sleep(2)        
        set_leds((0, 0, 0))   
        update_oled("CZEKANIE...") 
        
    elif payload == "DENY":
        update_oled("ODMOWA", "RED")
        set_leds((255, 0, 0))
        sound_alarm()
        set_leds((0, 0, 0))
        update_oled("CZEKANIE...")




def main():
    global current_temp, current_hum, current_press, last_sensor_time
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.tls_set(ca_certs=CA_CERT, tls_version=ssl.PROTOCOL_TLSv1_2)
        client.tls_insecure_set(True)
        print("Konfiguracja TLS zaladowana poprawnie.")
    except Exception as e:
        print(f"Blad konfiguracji TLS: {e}")
        return
    
    try:
        print(f"Laczenie z brokerem {BROKER} na porcie {PORT}...")
        client.connect(BROKER, PORT, 60)
        client.loop_start() 
    except Exception as e:
        print(f"Nie mozna polaczyc z MQTT: {e}")
        return

    print("System uruchomiony. Czekam na karty...")
    update_oled("START...")
    time.sleep(1)
    update_oled("CZEKANIE...")

    try:
        while True:
            if time.time() - last_sensor_time > SENSOR_INTERVAL:
                if bme280:
                    current_temp = bme280.temperature
                    current_hum = bme280.humidity
                    current_press = bme280.pressure
                    
                    payload = {
                        "temperature": round(current_temp, 2),
                        "humidity": round(current_hum, 2),
                        "pressure": round(current_press, 2)
                    }
                    
                    client.publish(TOPIC_SENSORS, json.dumps(payload))
                    print(f"Wyslano dane: {payload}")
                    
                last_sensor_time = time.time()


            (status, TagType) = reader.MFRC522_Request(reader.PICC_REQIDL)
            if status == reader.MI_OK:
                (status, uid) = reader.MFRC522_Anticoll()
                if status == reader.MI_OK:
                    
                    uid_str = ":".join([hex(x)[2:].upper().zfill(2) for x in uid])
                    print(f"Wykryto karte: {uid_str}")
                    
                    update_oled("SPRAWDZANIE", "BLUE")
                    
                    req_payload = {"uid": uid_str}
                    client.publish(TOPIC_ACCESS_REQ, json.dumps(req_payload))
                    
                    time.sleep(1.0)
            
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nZamykanie systemu...")
        set_leds((0,0,0))
        disp.clear()
        GPIO.cleanup()
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
