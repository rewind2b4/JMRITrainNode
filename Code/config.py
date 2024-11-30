Ssid = 'SSID'
Password = 'Password'
Server_addr = '192.168.168.138'
Client_name = 'TrainNode'
MQTT_User = 'MQTT_USER'
MQTT_Password = 'MQTT_Password'
MQTT_Port = 1883

## MQTT Channel (see https://www.jmri.org/help/en/html/hardware/mqtt/index.shtml)
MQTT_Prefix = 'mychannel/track/'

# The HIGH / LOW values sent to the MQTT server
turnout_HIGH = "THROWN"
turnout_LOW = "CLOSED"
light_HIGH = "ON"
light_LOW = "OFF"
sensor_HIGH = "ACTIVE"
sensor_LOW = "INACTIVE"

# Servo Settings
Ramp_Rate = 0.001 # PWM Ramp delay per step in seconds
PWM_Freq = 50 # PWM Frequency in Hz

# Switch Settings
Debounce_delay = 0.050 # Debounce delay in seconds

# Neopixel Settings
Neopixel_pin = 1 # Neopixel Pin (None if not used)

# MQTT Address, State, Device Type, Device Specific Arguments
MQTT_Addresses = [["mychannel/track/turnout/10", "CLOSED", "OUTPUT", "Servo", [0, 6000, 8100, 1]], 
                  ["mychannel/track/light/13", "OFF", "OUTPUT", "Neopixel", [0, [0, 255, 0], [255, 0, 0]]],
                  ["mychannel/track/turnout/12", "CLOSED", "OUTPUT", "General", []],
                  ["mychannel/track/sensor/13", "CLOSED", "INPUT", "Button_Latching", [2, 0]]]

# Available Device Types
    # Servo [PWM Pin, Min PWM, Max PWM, Ramp Enable] (OUTPUT)
    # Neopixel [Neopixel Index, Color ON, Color OFF] (OUTPUT)
    # LED [LED Pin] (OUTPUT)
    # Pin [Pin] (OUTPUT)
    # General_OUT [] (OUTPUT)
    # Button_Latching [Button Pin, Pin State High] (INPUT)
    # Pin_Scan [Pin, Pin State High] (INPUT)
    # NFC_BlockOC [] (INPUT)
    # General_IN [] (INPUT)
