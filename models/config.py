from pydantic import BaseModel
import os
import json

class Config(BaseModel):
    model: str
    secrets: dict

def load_config_dict():
    config_dict = dict()
    config_list_path = os.getenv("CONFIG_LIST_PATH")
    with open(config_list_path, "r") as file:
        json_data = json.load(file)

        for item in json_data:
            config = Config(**item)
            config_dict[config.model] = config.secrets
    
    return config_dict