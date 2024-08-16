# Ssid = 'Layout_MQTT'
# Password = '20200527'
Ssid = 'Test_Layout_MQTT'
Password = '20200527'
Installation_Ssid = 'Test_Layout_MQTT'
Installation_Password = '20200527'
Server_addr = '192.168.168.138'
Client_name = 'Roundhouse_Board'
MQTT_User = 'MQTT_USER'
MQTT_Password = '20200527'
MQTT_Port = 1883

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
MQTT_Addresses = [["pastrains/track/turnout/10", "CLOSED", "OUTPUT", "Servo", [0, 6000, 8100, 1]], 
                  ["pastrains/track/light/13", "OFF", "OUTPUT", "Neopixel", [0, [0, 255, 0], [255, 0, 0]]],
                  ["pastrains/track/turnout/12", "CLOSED", "OUTPUT", "General", []],
                  ["pastrains/track/sensor/13", "CLOSED", "INPUT", "Button_Latching", [2, 0]]]

# Available Device Types
    # Servo [PWM Pin, Min PWM, Max PWM, Ramp Enable] (OUTPUT)
    # Neopixel [Neopixel Index, Color ON, Color OFF] (OUTPUT)
    # LED [LED Pin] (OUTPUT)
    # Pin [Pin] (OUTPUT)
    # General_OUT [] (OUTPUT)
    # Button_Latching [Button Pin, Pin State High] (INPUT)
    # Pin_Scan [Pin, Pin State High] (INPUT)
    # General_IN [] (INPUT)