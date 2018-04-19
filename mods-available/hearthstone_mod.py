import io
from botutils import *
from base64 import b64decode

def __read_varint(stream):
    shift = 0
    result = 0
    while True:
        c = stream.read(1)
        if c == "":
            raise EOFError("Unexpected EOF while reading varint")
        i = ord(c)
        result |= (i & 0x7f) << shift
        shift += 7
        if not (i & 0x80):
            break

    return result

async def handle(client, config, message):
    if not has_prefix(config, message):
        return

    content = get_content_without_prefix(config, message)
    args = content.split()

    if args[0] != 'hs':
        return

    stream = io.BytesIO(b64decode(args[1]))
    print(f'Header: {__read_varint(stream)}')
    print(f'Version: {__read_varint(stream)}')
    print(f'Format: {__read_varint(stream)}')
    print(f'Num Hero: {__read_varint(stream)}')
    print(f'Hero: {__read_varint(stream)}')
    print('Cards')
    for c in range(__read_varint(stream)):
        print(f'{__read_varint(stream)}x1')
    for c in range(__read_varint(stream)):
        print(f'{__read_varint(stream)}x2')
    for c in range(__read_varint(stream)):
        print(f'{__read_varint(stream)}x{__read_varint(stream)}')
