import json
import network
from time import sleep
from machine import Pin, PWM
import neopixel
from umqtt.simple import MQTTClient

from lib.PiicoDev.PiicoDev_RFID import PiicoDev_RFID
from lib.PiicoDev.PiicoDev_Unified import sleep_ms


class config_manager:
    def __init__(self):
        return
    

    def load_config(self, filename):
        self.filename = filename
        with open(self.filename, 'r') as json_file:
            self.config = json.load(json_file)

        self.devices = self.config["devices"]
        self.settings = self.config["settings"]
        return
    
    
    def save_config(self):
        with open(self.filename, 'w') as json_file:
            json_file.write(json.dumps(self.config))
        return  
    
global config
config = config_manager()
config.load_config('config.json')

def sub_cb(topic, msg):
    print(topic.decode(), msg.decode())
    device = None
    for potential_device in config.devices:
        if config.devices[potential_device]["address"] == topic.decode():
            print("Device Found", potential_device)
            if config.devices[potential_device]["type"] == "servo":
                print("servo")
                device = config.devices[potential_device]
            else:
                print("Unknown Device Type")
    
    if device == None:
        print("Device Not Found")
        return
    
    if device["type"] == "servo":
        print("Servo")
        if msg.decode() == "THROWN":
            print("THROWN")
        elif msg.decode() == "CLOSED":
            print("CLOSED")
        else:
            print("Unknown State")


    


def connect():
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(config.settings["ssid"], config.settings["password"])
        while wlan.isconnected() == False:
            print('Waiting for connection to board...')
            sleep(1)
        ip = wlan.ifconfig()[0]
        print(f'Connected on {ip}')
        config.settings["ip"] = ip    
        mqtt = MQTTClient(client_id = config.settings["client_name"], server = config.settings["server_addr"], port = config.settings["MQTT_port"], user = config.settings["MQTT_user"], password = config.settings["MQTT_password"])
        try:
            print("Connecting to MQTT Server")
            mqtt.connect()
            mqtt.set_callback(sub_cb)
        except Exception as e:
            print(f"Error: Connection Failed: {e}")
            return None, None
        print("Connected to MQTT Server")
        
        return wlan, mqtt


    except Exception as e:
        print(f"Error: Connection Lost: {e}")
        return None, None
    

if __name__ == "__main__":

    while True:
        wlan, mqtt = connect()
        if wlan == None:
            print("Connection Failed, retrying...")
            continue

        for setting in config.settings:
            print(setting, config.settings[setting])
            if setting != "client_name" or setting != "ip":
                continue
            mqtt_address = str(config.settings["client_name"]) + "/" + str(setting)
            print(mqtt_address)
            mqtt.publish(mqtt_address, str(config.settings[setting]), qos=1)
            print("Published", mqtt_address, config.settings[setting])

            mqtt.subscribe(mqtt_address)
            print("Subscribed to", mqtt_address)

        for device in config.devices:
            mqtt.subscribe(config.devices[device]["address"])
            print("Subscribed to", config.devices[device]["address"])

        while wlan.isconnected():
            try:
                mqtt.check_msg()
            except Exception as e:
                print(f"Error: Connection Lost: {e}")
                break