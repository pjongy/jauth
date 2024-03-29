from tortoise import Tortoise


async def init_db(host, port, user, password, db, generate=True):
    await Tortoise.init(
        {
            "connections": {"default": f"mysql://{user}:{password}@{host}:{port}/{db}"},
            "apps": {
                "models": {
                    "models": [
                        "jauth.model.user",
                        "jauth.model.token",
                    ],
                    # If no default_connection specified, defaults to 'default'
                    "default_connection": "default",
                }
            },
        }
    )
    if generate:
        # Generate the schema
        await Tortoise.generate_schemas(safe=True)
