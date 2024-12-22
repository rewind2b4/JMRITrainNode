import json
import network
from time import sleep
from machine import Pin, PWM
import neopixel
import user
from umqtt.simple import MQTTClient

from lib.PiicoDev.PiicoDev_RFID import PiicoDev_RFID
from lib.PiicoDev.PiicoDev_Unified import sleep_ms


class config_manager:
    def __init__(self):
        return

    def load_config(self):
        with open('config.json', 'r') as json_file:
            self.config = json.load(json_file)

        self.devices = self.config["devices"]
        self.settings = self.config["settings"]
        return
    
    def save_config(self):
        with open('config.json', 'w') as json_file:
            json_file.write(json.dumps(self.config))
        return
        
    













def connect(Ssid, Password):
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(Ssid, Password)
    while wlan.isconnected() == False:
        print('Waiting for connection to board...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return wlan


def publish(address, mqtt):
    if address[2] == "INPUT":
        mqtt_address = address[0]
        state = address[1]
        mqtt.publish(mqtt_address, state, qos=1)
        print("Published", mqtt_address, state)


def sub_cb(topic, msg):

    mqtt_address = topic.decode()

    slash_pos = 0
    addr_str = ""
    for x in range(len(mqtt_address)-1, 0, -1):
        if mqtt_address[x] == '/':
            slash_pos = x 
            break

    for y in range(slash_pos+1, len(mqtt_address), 1):
        addr_str += mqtt_address[y]

    topic_prefix = mqtt_address[:len(mqtt_address) - len(addr_str) - 1]


    state = msg.decode()
    if state != config.turnout_HIGH and state != config.turnout_LOW and state != config.light_HIGH and state != config.light_LOW:
        print("Error: Invalid State", state)
        return
    
    for address in MQTTStruct:
        if address[0] == mqtt_address:
            prev_state = address[1]
            break

    if prev_state != state:
        if topic_prefix == config.MQTT_Prefix + "turnout":
            return _turnout(address, state)
        elif topic_prefix == config.MQTT_Prefix + "light":
            return _light(address, state)
            

def _turnout(address, state):
    if address[3] == "Servo":
        return servo(address, state)
    elif address[3] == "General_OUT":
        return general_out(address, state)
    elif address[3] == "Pin":
        return update_pin(address, state)


def _light(address, state):
    if address[3] == "LED":
        return update_pin(address, state)
    elif address[3] == "Neopixel":
        return neopixel_handler(address, state)



def update_pin(address, state):
    addr_str = str(address[0])
    PWM_pin = address[4][0]
    if state == config.turnout_HIGH or state == config.light_HIGH:
        print("Received", addr_str, state)
        Pin(PWM_pin).high()


    elif state == config.turnout_LOW or state == config.light_LOW:
        print("Received", addr_str, state)
        Pin(PWM_pin).low()

    address[1] = state 


def general_out(address, state):
    addr_str = str(address[0])
    if state == config.turnout_HIGH or state == config.light_HIGH:
        print("Received", addr_str, state)

    elif state == config.turnout_LOW or state == config.light_LOW:
        print("Received", addr_str, state)

    address[1] = state 


def servo(address, state):
    addr_str = str(address[0])
    PWM_pin = address[4][0]
    PWM_Limit_1 = address[4][1]
    PWM_Limit_2 = address[4][2]
    Ramp_PWM = address[4][3]
    PWM(Pin(PWM_pin)).freq(config.PWM_Freq)
    if state == config.turnout_HIGH:
        print("Received", addr_str, state, PWM_Limit_1, PWM_Limit_2)

        if Ramp_PWM == True:
            for i in range(PWM_Limit_2, PWM_Limit_1, -1):
                PWM(Pin(PWM_pin)).duty_u16(i)
                sleep(config.Ramp_Rate)    
        else:
            PWM(Pin(PWM_pin)).duty_u16(PWM_Limit_1)

    elif state == config.turnout_LOW:
        print("Received", addr_str, state, PWM_Limit_1, PWM_Limit_2)
        if Ramp_PWM == True:
            for i in range(PWM_Limit_1, PWM_Limit_2, 1):
                PWM(Pin(PWM_pin)).duty_u16(i)
                sleep(config.Ramp_Rate)    
        else:
            PWM(Pin(PWM_pin)).duty_u16(PWM_Limit_2)

    address[1] = state 


def latching_button(address, publish_mqtt = True, mqtt = None):
    state = address[1]
    pin_read = Pin(address[4][0], Pin.IN, Pin.PULL_UP).value()
    if pin_read == address[4][1]:
        if address[1] == config.sensor_LOW:
            state = config.sensor_HIGH
        else:
            state = config.sensor_LOW

    if state != address[1]:
        sleep(config.Debounce_delay) ## Debounce
        pin_check = Pin(address[4][0], Pin.IN, Pin.PULL_UP).value() ## Check that the pin state is stable
        if pin_check == pin_read:
            address[1] = state
            if publish_mqtt == True:
                if mqtt != None:
                    publish(address, mqtt)
            while Pin(address[4][0], Pin.IN, Pin.PULL_UP).value() == address[4][1]:
                sleep(0.001)


def pin_scan(address, publish_mqtt = True, mqtt = None):
    state = address[1]
    pin_read = Pin(address[4][0], Pin.IN, Pin.PULL_UP).value()
    state = pin_read

    if state != address[1]:
        sleep(config.Debounce_delay) ## Debounce
        pin_check = Pin(address[4][0], Pin.IN, Pin.PULL_UP).value() ## Check that the pin state is stable
        if pin_check == pin_read:
            address[1] = state
            if publish_mqtt == True:
                if mqtt != None:
                    publish(address, mqtt)
            while Pin(address[4][0], Pin.IN, Pin.PULL_UP).value() == address[4][1]:
                sleep(0.001)


def nfc_scan(address, publish_mqtt = True, mqtt = None):
    rfid = PiicoDev_RFID()   # Initialise the RFID module
    if rfid.tagPresent():    # if an RFID tag is present
        id = rfid.readID()   # get the id 
        if id != address[1]: ## TODO: work out how to do maths for address state
            if id != '':
                address[1] = id
                if publish_mqtt == True:
                    if mqtt != None:
                        publish(address, mqtt)
                    

def neopixel_handler(address, state):

    addr_str = str(address[0])
    neopixel_addr = address[4][0]
    if state == config.light_HIGH:
        print("Received", addr_str, state)
        if neopixel_struct is not None:
            neopixel_struct[neopixel_addr] = address[4][1]
            neopixel_struct.write()

    elif state == config.light_LOW:
        print("Received", addr_str, state)
        if neopixel_struct is not None:
            neopixel_struct[neopixel_addr] = address[4][2]
            neopixel_struct.write()
    address[1] = state 


if __name__ == "__main__":
    global user_config
    user_config = load_config()

    neopixel_count = 0
    for address in MQTTStruct:
        if address[3] == "Neopixel":
            neopixel_count += 1
    if neopixel_count > 0:
        global neopixel_struct
        neopixel_struct = neopixel.NeoPixel(Pin(config.Neopixel_pin), neopixel_count)
        for i in range(neopixel_count):
            neopixel_struct[i] = (0, 0, 0) ## Turn off all neopixels
    

    while True:
        try:
            wlan = connect(config.Ssid, config.Password)
            print("Connected to WLAN, Connecting to MQTT...")
            mqtt = MQTTClient(config.Client_name, config.Server_addr, config.MQTT_Port, config.MQTT_User, config.MQTT_Password)
            mqtt.connect()
            mqtt.set_callback(sub_cb)
            print("Connected to MQTT")
        except Exception as e:
            print(f"Error: Connection Lost: {e}")
            continue
        
        mqtt_publish = []
        for address in MQTTStruct:
            if address[2] == "OUTPUT":
                mqtt.subscribe( str(address[0]))
            else:
                mqtt_publish.append(address)

        
        while wlan.isconnected():
            try:
                mqtt.check_msg() ## Check for incoming messages and act on them

                user.custom_node_functions(MQTTStruct) ## Run user defined functions

                for address in mqtt_publish: ## Scan the input pins and publish their state if it has changed
                    if address[2] == "INPUT":
                        if address[3] == "Button_Latching":
                            latching_button(address, True, mqtt)
                        elif address[3] == "Pin_Scan":
                            pin_scan(address, True, mqtt)
                        elif address[3] == "General_IN":
                            publish(address, mqtt)
                        elif address[3] == "NFC_BlockOC":
                            nfc_scan(address, True, mqtt)
            except Exception as e:
                print("Error: MQTT Error", e)
                break    

            sleep(0.001)
