import network
import json

# Convert the dictionary to a JSON string
with open('config.json', 'r') as json_file:
    config_dict = json.load(json_file)

print(config_dict)

config_dict["Ssid"] = "your wi-fi"

print(config_dict)

config_json = json.dumps(config_dict)
# Write the JSON string to a file
with open('config.json', 'w') as json_file:
    json_file.write(config_json)


wlan_id = "House"
wlan_pass = "ag1l3mini"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

while not wlan.isconnected():
    wlan.connect(wlan_id, wlan_pass)
print("Connected... IP: " + wlan.ifconfig()[0]) 

from lib.Micropyserver.micropyserver import MicroPyServer


def hello_world(request):
    ''' request handler '''
    server.send(str(config_dict))


server = MicroPyServer()
''' add route '''
server.add_route("/", hello_world)
''' start server '''
server.start()