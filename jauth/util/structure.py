import deserialize


def default_object(cls) -> object:
    return deserialize.deserialize(cls, {})
