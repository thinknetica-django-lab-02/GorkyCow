import os

import yaml


def load_secrets(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name)) as config_file:
        config = yaml.safe_load(config_file).get("secrets")
    return config


# TODO: сделать валидацию полей файла секретов
