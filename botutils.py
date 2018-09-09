from datetime import datetime
from pytz import timezone

def is_channel_valid(config, config_setting, message):
    setting = config.get(config_setting)
    if setting == None:
        return True
    elif message.channel.name in config[config_setting]:
        return True
    elif '*' in setting:
        return True
    else:
        return False

def has_prefix(config, message):
    return message.content.startswith(config['prefix'])

def get_content_without_prefix(config, message):
    return message.content[len(config['prefix']):]

def timestamp():
    return datetime.now(timezone('Canada/Eastern'))
    #return datetime.now(timezone('Canada/Eastern')).timetuple()


__all__ = ['is_channel_valid', 'has_prefix', 'get_content_without_prefix']
