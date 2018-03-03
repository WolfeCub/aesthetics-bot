def is_channel_valid(config, config_setting, message):
    return config.get(config_setting) is not None and message.channel.name not in config[config_setting]

