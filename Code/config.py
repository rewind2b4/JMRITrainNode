Ssid = 'House'
Password = 'ag1l3mini'
Server_addr = '192.168.168.38'
Client_name = 'TrainNode'
MQTT_User = 'mqtt-user'
MQTT_Password = '9te%BM3u$ps77dMoR$B7@DJyBZ'
MQTT_Port = 1883

## MQTT Channel (see https://www.jmri.org/help/en/html/hardware/mqtt/index.shtml)
MQTT_Prefix = 'pastrains/track/'

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
MQTT_Addresses = [["pastrains/track/reporter/10", "CLOSED", "INPUT", "NFC_BlockOC", []]]

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
