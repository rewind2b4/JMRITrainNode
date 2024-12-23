import json
import network
from time import sleep, ticks_us
try:
    from umqtt.simple import MQTTClient
    import neopixel
    from machine import Pin, PWM
    PC_run = False
except:
    print("Running on PC")
    PC_run = True
import re
import user

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
    
    elif config.settings["client_name"] in topic.decode():
        decoded_topic = re.sub(config.settings["client_name"] + "/", "", topic.decode())
        device_num = decoded_topic.split("/")[0]
        setting = decoded_topic.split("/")[1]
        print("device_num", device_num, "setting", setting, "to", msg.decode())
        ## TODO: set the setting to the value in msg.decode()
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
    

def check_mqtt_msg(mqtt):
    if PC_run == False:
        mqtt.check_msg()
    else:
        pass


def publish_mqtt(mqtt, address, msg):
    if PC_run == False:
        mqtt.publish(address, msg, qos=1)
    else:
        print("Published", address, msg)



def sub_mqtt(mqtt, address):
    if PC_run == False:
        mqtt.subscribe(address)
    else:
        print("Subscribed to", address)


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
    

def servo(device):
    servo = PWM(Pin(config.devices[device]["args"]["pin"]))
    servo.freq(config.devices[device]["args"]["freq"])
    if config.devices[device]["args"]["ramp"]:
        step = config.devices[device]["args"]["step"]

        if config.devices[device]["current_state"]["position"] > config.devices[device]["states"][config.devices[device]["current_state"]["state"]]:
            config.devices[device]["current_state"]["position"] -= step
        else:
            config.devices[device]["current_state"]["position"] += step
    else:
        config.devices[device]["current_state"]["position"] = config.devices[device]["states"][config.devices[device]["current_state"]["state"]]
    servo.duty_u16(config.devices[device]["current_state"]["position"])
    config.save_config()


def pin_output(device):
    pin = Pin(config.devices[device]["args"]["pin"], Pin.OUT)
    pin.value(config.devices[device]["states"][config.devices[device]["current_state"]["state"]])
    config.devices[device]["current_state"]["position"] = config.devices[device]["states"][config.devices[device]["current_state"]["state"]]
    config.save_config()


def pin_input(device):
    if config.devices[device]["args"]["pullup"]:
        pin = Pin(config.devices[device]["args"]["pin"], Pin.IN, Pin.PULL_UP)
    else:
        pin = Pin(config.devices[device]["args"]["pin"], Pin.IN)
    state = pin.value()
    for config_state in config.devices[device]["states"]:
        if config.devices[device]["states"][config_state] == state:
            state_to_set = str(config_state)
            break
    if state_to_set != config.devices[device]["current_state"]["state"]:
        sleep(config.devices[device]["args"]["debounce"])
        pin_check = pin.value()
        if pin_check == state:
            config.devices[device]["current_state"]["state"] = state_to_set
            publish_mqtt(mqtt, config.devices[device]["address"], state_to_set)
            print(config.devices[device]["type"], config.devices[device]["address"], config.devices[device]["current_state"]["state"])
            config.save_config()
        ## TODO: Test this function


def neopixel_process(device):
    ##neo = neopixel.NeoPixel(Pin(config.devices[device]["args"]["pin"]), config.devices[device]["args"]["pixel_count"])
    ##neo[config.devices[device]["args"]["pixel"]] = config.devices[device]["states"][config.devices[device]["current_state"]["state"]]
    ##neo.write()
    pass ## TODO: Need to implement neopixel_process properly


def rfid_process(device):
    rfid = PiicoDev_RFID() ## TODO: add address to rfid
    if rfid.tagPresent():
        id = rfid.readID()
        if id != config.devices[device]["current_state"]["state"]:
            if id != '':
                config.devices[device]["current_state"]["state"] = id
                config.save_config()
                print(config.devices[device]["type"], config.devices[device]["address"], config.devices[device]["current_state"]["state"])
                publish_mqtt(mqtt, config.devices[device]["address"], config.devices[device]["current_state"]["state"])


def latch_button(device):
    if config.devices[device]["args"]["pullup"]:
        pin = Pin(config.devices[device]["args"]["pin"], Pin.IN, Pin.PULL_UP)
    else:
        pin = Pin(config.devices[device]["args"]["pin"], Pin.IN)
    state = pin.value()
    if state == config.devices[device]["args"]["prev_state"]:
        return
    for config_state in config.devices[device]["states"]:
        if config.devices[device]["states"][config_state] == state:
            state_to_set = str(config_state)
            break
    if state_to_set != config.devices[device]["current_state"]["state"]:
        sleep(config.devices[device]["args"]["debounce"])
        pin_check = pin.value()
        if pin_check == state:
            config.devices[device]["current_state"]["state"] = state_to_set
            publish_mqtt(mqtt, config.devices[device]["address"], state_to_set)
            print(config.devices[device]["type"], config.devices[device]["address"], config.devices[device]["current_state"]["state"])
            config.save_config()
        ## TODO: Test this function
    

def process_inputs():
    for device in config.devices:
        if config.devices[device]["io"] == "INPUT":
            if config.devices[device]["type"] == "rfid":
                rfid_process(device)
            elif config.devices[device]["type"] == "button":
                latch_button(device)
            elif config.devices[device]["type"] == "pin_input":
                pin_input(device)


def process_outputs():
    for device in config.devices:
        if config.devices[device]["io"] == "OUTPUT":
            position = config.devices[device]["current_state"]["position"]
            if position != config.devices[device]["states"][config.devices[device]["current_state"]["state"]]:
                print(config.devices[device]["address"], config.devices[device]["current_state"]["state"], "position", config.devices[device]["current_state"]["position"], "to", config.devices[device]["states"][config.devices[device]["current_state"]["state"]])
                
                ## select the device type 

                if config.devices[device]["type"] == "servo":
                    servo(device)
                elif config.devices[device]["type"] == "pin":
                    pin_output(device)
                elif config.devices[device]["type"] == "neopixel":
                    neopixel_process(device)


if __name__ == "__main__":

    while True:
        wlan, mqtt = connect()
        if wlan == None:
            print("Connection Failed, retrying...")
            continue

        for setting in config.settings:
            if setting == "client_name" or setting == "ip" or setting == "cycle_time":
                mqtt_address = str(config.settings["client_name"]) + "/" + str(setting)
                publish_mqtt(mqtt, mqtt_address, str(config.settings[setting]))
                print("Published", mqtt_address, config.settings[setting])
                if setting == "client_name":
                    sub_mqtt(mqtt, mqtt_address)
                    print("Subscribed to", mqtt_address)

        for device in config.devices:
            device_num = str(device)
            sub_mqtt(mqtt, config.devices[device]["address"])
            print("Subscribed to", config.devices[device]["address"])

            for setting in config.devices[device]:
                mqtt_address = str(config.settings["client_name"]) + "/" + device_num + "/" + str(setting)
                publish_mqtt(mqtt, mqtt_address, str(config.devices[device][setting]))
                print("Published", mqtt_address, str(config.devices[device][setting]))
                sub_mqtt(mqtt, mqtt_address)
                print("Subscribed to", str(setting))

        counter = 0
        while wlan.isconnected():
            try:
                start_time = ticks_us()
                check_mqtt_msg(mqtt)
                user.custom_node_functions(config.devices)
                if PC_run == False:
                    process_inputs()
                    process_outputs()
                else:
                    for device in config.devices:
                        print(str(device), config.devices[device]["current_state"]["state"])    
                finish_time = ticks_us()
                if counter == 10000:
                    config.settings["cycle_time"] = finish_time - start_time
                    mqtt_address = str(config.settings["client_name"]) + "/" + "cycle_time"
                    publish_mqtt(mqtt, mqtt_address, str(config.settings["cycle_time"]))
                    counter = 0
                counter += 1 

            except Exception as e:
                print(f"Error: Connection Lost: {e}")
                break