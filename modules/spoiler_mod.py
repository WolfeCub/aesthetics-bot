from PIL import Image, ImageDraw, ImageFont
import textwrap 
import os
from botutils import has_prefix, get_content_without_prefix

def __newImage(width, height, color):
    return Image.new("L", (width, height), color)

async def __handle_spoiler(client, message, text):
    await client.delete_message(message)

    margin = (5, 5)
    fontSize = 16
    fontColor = 200
    font = ImageFont.truetype('font/arial.ttf', fontSize)

    textLines = []
    for line in text.splitlines():
        textLines.extend(textwrap.wrap(line, width=60, replace_whitespace=False))

    title = 'Spoiler! (Hover to see)'
    width = font.getsize(title)[0] + 50
    height = 0

    for line in textLines:
        size = font.getsize(line)
        width = max(width, size[0])
        height += size[1] + 2

    width += margin[0]*2
    height += margin[1]*2

    textFull = '\n'.join(textLines)

    spoilIMG = [__newImage(width, height, '#23272A') for _ in range(4)]
    spoilText = [title, textFull]

    for img, txt in zip(spoilIMG, spoilText):
        canvas = ImageDraw.Draw(img)
        canvas.multiline_text(margin, txt, font=font, fill=fontColor, spacing=4)

    path = f'/tmp/{message.id}.gif'

    spoilIMG[0].save(path, format='GIF', save_all=True, append_images=[spoilIMG[1]], duration=[0, 0xFFFF], loop=0)
    await client.send_file(message.channel, path)

    os.remove(path)


async def handle(client, config, message):
    if not has_prefix(config, message):
        return

    content = get_content_without_prefix(config,message)
    args = content.split()

    if args[0] != 'spoiler':
        return
    if len(args) > 1:
        await __handle_spoiler(client, message, content[len(args[0])+1:]) 
