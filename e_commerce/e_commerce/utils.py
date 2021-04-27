import os
from typing import Any, Dict

import yaml


def load_secrets(file_name: str) -> Dict[str, Any]:
    """This function loads secrets from the YAML file by given name.

    :param file_name: name of the YAML file with secrets
    :type file_name: str
    """
    with open(os.path.join(os.path.dirname(__file__), file_name)) as con_file:
        config = yaml.safe_load(con_file).get("secrets")
    return config


# TODO: сделать валидацию полей файла секретов
