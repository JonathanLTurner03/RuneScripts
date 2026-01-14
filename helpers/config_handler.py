import json

class ConfigHandler:

    def __init__(self, config_file):
        self.config_file = config_file
        self.config_data = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}
    
    def save_config(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.config_data, file, indent=4)
    
    def get(self, key, default=None):
        return self.config_data.get(key, default)
    
    def set(self, key, value):
        self.config_data[key] = value
        self.save_config()

    def delete(self, key):
        if key in self.config_data:
            del self.config_data[key]
            self.save_config()