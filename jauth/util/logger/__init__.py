import logging

from pythonjsonlogger import jsonlogger

from jauth.config import config

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logging.basicConfig(level=config.api_server.logging_level, handlers=[logHandler])
