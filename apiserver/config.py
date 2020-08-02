from pathlib import Path

import deserialize

from common.configutil import get_config


class Config:
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
        port: int
    api_server: APIServer


config_path = f'{Path(__file__).resolve().parent}/config'

config: Config = deserialize.deserialize(
    Config, get_config(config_path)
)
