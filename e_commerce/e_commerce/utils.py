import os

import yaml


def load_secrets(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name)) as con_file:
        config = yaml.safe_load(con_file).get("secrets")
    return config


# TODO: сделать валидацию полей файла секретов
