from pathlib import Path
from typing import List

import deserialize

from jauth.util.configutil import get_config


class Config:
    @deserialize.default('internal_api_keys', [])
    @deserialize.parser('internal_api_keys', lambda arg: arg.split(','))
    @deserialize.default('port', 8080)
    @deserialize.parser('port', int)
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
        internal_api_keys: List[str]  # comma separated string to list

    api_server: APIServer


config_path = f'{Path(__file__).resolve().parent}/config'

config: Config = deserialize.deserialize(
    Config, get_config(config_path)
)
