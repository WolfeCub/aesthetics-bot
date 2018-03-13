def is_channel_valid(config, config_setting, message):
    return config.get(config_setting) is not None and message.channel.name not in config[config_setting]

def has_prefix(config, message):
    return message.content.startswith(config['prefix'])

def get_content_without_prefix(config, message):
    return message.content[len(config['prefix']):]
