import json

# Convert the dictionary to a JSON string
with open('config.json', 'r') as json_file:
    config_dict = json.load(json_file)

print(config_dict)

config_dict["Ssid"] = "your wi-fi"

print(config_dict)

config_json = json.dumps(config_dict, indent=4)
# Write the JSON string to a file
with open('config.json', 'w') as json_file:
    json_file.write(config_json)