from pydantic import BaseModel
import os
import json

class Config(BaseModel):
    model: str
    secrets: dict

class ConfigDict:

    def __init__(self, configs = []) -> None:
        self.config_dict = dict()

        if configs is not None and len(configs) > 0:
            for config in configs:
                self.config_dict[config.model] = config.secrets

    def get(self, model, key) -> str:
        if not model in self.config_dict:
            return None
        
        if not key in self.config_dict[model]:
            return None
        
        return self.config_dict[model][key]

def load_config_dict():
    configs = []
    config_list_path = os.getenv("CONFIG_LIST_PATH")

    if config_list_path is not None and os.path.exists(config_list_path):
        with open(config_list_path, "r") as file:
            json_data = json.load(file)

            for item in json_data:
                config = Config(**item)
                configs.append(config)
    
    return ConfigDict(configs)