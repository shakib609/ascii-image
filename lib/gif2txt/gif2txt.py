#! /usr/bin/env python3
from PIL import Image


def gif2txt(filename, maxLen=80, output_file='out.html'):
    try:
        maxLen = int(maxLen)
    except:
        maxLen = 80

    chs = "MNHQ$OC?7>!:-;. "

    try:
        img = Image.open(filename)
    except IOError:
        exit("file not found: {}".format(filename))

    width, height = img.size
    rate = float(maxLen) / max(width, height)
    width = int(rate * width)
    height = int(rate * height)

    palette = img.getpalette()
    strings = []

    try:
        while 1:
            img.putpalette(palette)
            im = Image.new('RGB', img.size)
            im.paste(img)
            im = im.resize((width, height))
            string = ''
            for h in range(height):
                for w in range(width):
                    rgb = im.getpixel((w, h))
                    string += chs[int(sum(rgb) / 3.0 / 256.0 * 16)]
                string += '\n'
            strings.append(string)
            img.seek(img.tell() + 1)

    except EOFError:
        return strings

