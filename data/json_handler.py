import json

def json_upsert(config_file, new_data):
    """Load, update (or insert), and save the config data."""
    if config_file.exists():
        with open(config_file, 'r') as file:
            try:
                config = json.load(file)
            except json.JSONDecodeError:
                config = {}
    else:
        config = {}

    config.update(new_data)

    with open(config_file, 'w') as file:
        json.dump(config, file, indent=4)

    return config

