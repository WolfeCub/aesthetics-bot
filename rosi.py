from discord.ext import commands

class Rosi(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', description="MCSS Discord Bot")
        self.__config = {}

    def set_config(self, config):
        self.__config = config

    def get_config(self, key):
        return self.__config[key]
