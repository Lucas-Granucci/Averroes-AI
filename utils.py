import yaml


def load_config():
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    return config
