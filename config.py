import yaml


class ConfigData:
    def __init__(self, filename: str):
        with open(filename, 'r') as file:
            self.data = yaml.safe_load(file)

    def get(self, key: str = None, default=None):
        return self.data if key is None else self.data.get(key, default)
        # if key is None:
        #     return self.data
        # else:
        #     return self.data.get(key, default)

    def get_values(self):
        values = []
        for key, value in self.data.items():
            if isinstance(value, dict):
                values.extend(self.get_nested_values(value))
            else:
                values.append(value)
        return values

    def get_keys(self):
        keys = []
        for key, value in self.data.items():
            if isinstance(value, dict):
                keys.extend(self.get_nested_keys(key, value))
            else:
                keys.append(key)
        return keys

    def get_nested_values(self, nested_dict):
        values = []
        for key, value in nested_dict.items():
            if isinstance(value, dict):
                values.extend(self.get_nested_values(value))
            else:
                values.append(value)
        return values

    def get_nested_keys(self, parent_key, nested_dict):
        keys = []
        for key, value in nested_dict.items():
            full_key = f'{parent_key}.{key}'
            if isinstance(value, dict):
                keys.extend(self.get_nested_keys(full_key, value))
            else:
                keys.append(full_key)
        return keys
