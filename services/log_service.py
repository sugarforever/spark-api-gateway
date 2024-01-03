import os
import logging
import logging.config
import yaml

def __get_project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def load_logging_config():
    project_root = __get_project_root()
    with open(os.path.join(project_root, 'logging.yaml'), 'rt') as f:
        config = yaml.safe_load(f.read())

    logging.config.dictConfig(config)
