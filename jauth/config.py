from pathlib import Path
from typing import List, Tuple

import deserialize

from jauth.util.configutil import get_config


class Config:
    @deserialize.default('internal_api_keys', [])
    @deserialize.parser('internal_api_keys', lambda arg: arg.split(','))
    @deserialize.default('event_callback_urls', [])
    @deserialize.parser('event_callback_urls', lambda arg: [url_set.split('|')[:2] for url_set in arg.split(',')])
    @deserialize.default('port', 8080)
    @deserialize.parser('port', int)
    @deserialize.default('logging_level', 'DEBUG')
    class APIServer:
        @deserialize.default('port', 3306)
        @deserialize.parser('port', int)
        class MySQL:
            host: str
            port: int
            user: str
            password: str
            database: str

        @deserialize.default('port', 6379)
        @deserialize.parser('port', int)
        class Redis:
            @deserialize.parser('database', int)
            class Database:
                database: int
            host: str
            port: int
            password: str

            token_cache: Database

        mysql: MySQL
        redis: Redis
        jwt_secret: str
        port: int

        # comma separated string with split by bar to list
        # e.g) https://xxx.xxx/callback|TOKEN,https://yyy.xxx/callback|TOKEN2
        # -> [['https://xxx.xxx/callback', 'TOKEN'], ['https://yyy.xxx/callback', 'TOKEN2']]
        event_callback_urls: List[List[str]]
        internal_api_keys: List[str]  # comma separated string to list
        logging_level: str

    api_server: APIServer


config_path = f'{Path(__file__).resolve().parent}/config'

config: Config = deserialize.deserialize(
    Config, get_config(config_path)
)
