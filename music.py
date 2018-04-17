import re

__MUSIC_REGEX = re.compile(r'!music (.*?)')
def __check_music_regex(message):
    matches = __MUSIC_REGEX.match(message.content)
    if matches:
        return matches.group(1)
    return None

async def handle(client, config, message):
    match = __check_music_regex(message)
    
    if not match:
        return
    
    voice = await client.join_voice_channel(message.author.voice.voice_channel)
    #player = await voice.create_ffmpeg_player(match)
    #if player:
        #player.start()

        OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']
        
        
def load_opus_lib(opus_libs=OPUS_LIBS):
    if opus.is_loaded():
        return True

    for opus_lib in opus_libs:
        try:
            opus.load_opus(opus_lib)
            return
        except OSError:
            pass

raise RuntimeError('Could not load an opus lib. Tried %s' % (', '.join(opus_libs)))