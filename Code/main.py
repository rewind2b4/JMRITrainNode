import json
import network
from time import sleep, ticks_us
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
    if topic.decode() == config.settings["client_name"] + "/client_name":
        print("Changing client name to", msg.decode())
        config.settings["client_name"] = msg.decode()
        config.save_config()
        return

    device = None
    for potential_device in config.devices:
        if config.devices[potential_device]["address"] == topic.decode():
            device = config.devices[potential_device]
            break
    
    if device == None:
        return
    
    if device["current_state"]["state"] != msg.decode():
        for state in device["states"]:
            if msg.decode() == state:
                device["current_state"]["state"] = state
                config.save_config()
                print(device["type"], device["address"], device["current_state"]["state"], device["states"][device["current_state"]["state"]])
                return
        print(f"{msg.decode()}: invalid state, no change:", device["type"], device["address"], device["current_state"]["state"], device["states"][device["current_state"]["state"]])
        return


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


def process_inputs():
    pass

def process_outputs():
    for device in config.devices:
        if config.devices[device]["io"] == "OUTPUT":
            position = config.devices[device]["current_state"]["position"]
            if position != config.devices[device]["states"][config.devices[device]["current_state"]["state"]]:
                print(config.devices[device]["address"], config.devices[device]["current_state"]["state"], "position", config.devices[device]["current_state"]["position"], "to", config.devices[device]["states"][config.devices[device]["current_state"]["state"]])
                
                ## select the device type 

                ## SERVO
                if config.devices[device]["type"] == "servo":
                    servo = PWM(Pin(config.devices[device]["args"]["pin"]))
                    servo.freq(config.devices[device]["args"]["freq"])
                    if config.devices[device]["args"]["ramp"]:
                        step = config.devices[device]["args"]["step"]

                        if position > config.devices[device]["states"][config.devices[device]["current_state"]["state"]]:
                            config.devices[device]["current_state"]["position"] -= step
                        else:
                            config.devices[device]["current_state"]["position"] += step
                    else:
                        config.devices[device]["current_state"]["position"] = config.devices[device]["states"][config.devices[device]["current_state"]["state"]]
                    servo.duty_u16(config.devices[device]["current_state"]["position"])
                    config.save_config()


if __name__ == "__main__":

    while True:
        wlan, mqtt = connect()
        if wlan == None:
            print("Connection Failed, retrying...")
            continue

        for setting in config.settings:
            if setting == "client_name" or setting == "ip" or setting == "cycle_time":
                mqtt_address = str(config.settings["client_name"]) + "/" + str(setting)
                mqtt.publish(mqtt_address, str(config.settings[setting]), qos=1)
                print("Published", mqtt_address, config.settings[setting])
                if setting == "client_name":
                    mqtt.subscribe(mqtt_address)
                    print("Subscribed to", mqtt_address)

        for device in config.devices:
            mqtt.subscribe(config.devices[device]["address"])
            print("Subscribed to", config.devices[device]["address"])

        counter = 0
        while wlan.isconnected():
            try:
                start_time = ticks_us()
                mqtt.check_msg()
                process_inputs()
                process_outputs()
                finish_time = ticks_us()
                config.settings["cycle_time"] = finish_time - start_time
                if counter == 10000:
                    mqtt_address = str(config.settings["client_name"]) + "/" + "cycle_time"
                    mqtt.publish(mqtt_address, str(config.settings["cycle_time"]), qos=1)
                    counter = 0
                counter += 1 

            except Exception as e:
                print(f"Error: Connection Lost: {e}")
                break