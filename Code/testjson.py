import json

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

config = config_manager()
config.load_config('config.json')
for setting in config.settings:
    print(setting, config.settings[setting])
for device in config.devices:
    for key in config.devices[device]:
        if key == "args":
            for arg in config.devices[device][key]:
                print(device, key, arg, config.devices[device][key][arg])
        else:
            print(device, key, config.devices[device][key])