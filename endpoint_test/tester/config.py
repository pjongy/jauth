import os

import deserialize

from jauth.util.configutil import replace_key


class Config:
    class Tester:
        endpoint: str
        internal_api_key: str

    tester: Tester


def get_config_by_env() -> dict:
    config_ = {}
    for key, value in os.environ.items():
        attribute = key.lower().split("__")
        replace_key(config_, attribute, value)
    return config_


config: Config = deserialize.deserialize(Config, get_config_by_env())
