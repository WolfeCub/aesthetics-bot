def is_channel_valid(config, config_setting, message):
    return config.get(config_setting) is not None and message.channel.name in config[config_setting]

def has_prefix(config, message):
    return message.content.startswith(config['prefix'])

def get_content_without_prefix(config, message):
    return message.content[len(config['prefix']):]


__all__ = ['is_channel_valid', 'has_prefix', 'get_content_without_prefix']
