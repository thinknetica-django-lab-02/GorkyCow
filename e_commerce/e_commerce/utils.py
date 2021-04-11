import os
import yaml


def load_secrets(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name)) as config_file:
        config = yaml.load(config_file)['config']
    return config