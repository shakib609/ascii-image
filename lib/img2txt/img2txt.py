import sys
from PIL import Image
from lib.img2txt import ansi
from lib.img2txt.graphics_util import alpha_blend


def HTMLColorToRGB(colorstring):
    """ convert #RRGGBB to an (R, G, B) tuple """
    colorstring = colorstring.strip()
    if colorstring[0] == '#':
        colorstring = colorstring[1:]
    if len(colorstring) != 6:
        raise ValueError(
            "input #{0} is not in #RRGGBB format".format(colorstring))
    r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    return (r, g, b)


def generate_HTML_for_image(pixels, width, height):

    string = ""
    # first go through the height,  otherwise will rotate
    for h in xrange(height):
        for w in xrange(width):

            rgba = pixels[w, h]
            string += ("<span style=\"color:rgba({0}, {1}, {2}, {3});\">"
                       "▇</span>").format(
                rgba[0], rgba[1], rgba[2], rgba[3] / 255.0)

        string += "\n"

    return string


def generate_grayscale_for_image(pixels, width, height, bgcolor):

    color = "MNHQ$OC?7>!:-;. "
    string = ""

    for h in range(height):
        for w in range(width):

            rgba = pixels[w, h]

            # If partial transparency and we have a bgcolor, combine with bg
            # color
            if rgba[3] != 255 and bgcolor is not None:
                rgba = alpha_blend(rgba, bgcolor)

            # Throw away any alpha (either because bgcolor was partially
            # transparent or had no bg color)
            # Could make a case to choose character to draw based on alpha but
            # not going to do that now...
            rgb = rgba[:3]

            string += color[int(sum(rgb) / 3.0 / 256.0 * 16)]

        string += "\n"

    return string


def load_and_resize_image(imgname, antialias, maxLen, aspectRatio):

    if aspectRatio is None:
        aspectRatio = 1.0

    img = Image.open(imgname)

    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    if maxLen is not None or aspectRatio != 1.0:

        native_width, native_height = img.size

        new_width = native_width
        new_height = native_height

        if aspectRatio != 1.0:
            new_height = int(float(aspectRatio) * new_height)
        if maxLen is not None:
            rate = float(maxLen) / max(new_width, new_height)
            new_width = int(rate * new_width)
            new_height = int(rate * new_height)

        if native_width != new_width or native_height != new_height:
            img = img.resize((new_width, new_height),
                             Image.ANTIALIAS if antialias else Image.NEAREST)

    return img


def floydsteinberg_dither_to_web_palette(img):
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img = img.convert(mode="P", matrix=None,
                      dither=Image.FLOYDSTEINBERG,
                      palette=Image.WEB, colors=256)
    img = img.convert('RGBA')
    return img


def dither_image_to_web_palette(img, bgcolor):

    if bgcolor is not None:
        img = Image.alpha_composite(Image.new("RGBA", img.size, bgcolor), img)
        dithered_img = floydsteinberg_dither_to_web_palette(img)
    else:
        # Force image to RGBA if it isn't already
        # simplifies the rest of the code
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        rgb_img = img.convert('RGB')

        orig_pixels = img.load()
        rgb_pixels = rgb_img.load()
        width, height = img.size

        for h in xrange(height):  # set transparent pixels to black
            for w in xrange(width):
                if (orig_pixels[w, h])[3] != 255:
                    rgb_pixels[w, h] = (0, 0, 0)
                    # bashing in a new value changes it!

        dithered_img = floydsteinberg_dither_to_web_palette(rgb_img)
        dithered_pixels = dithered_img.load()  # must do it again
        for h in range(height):
            # restore original RGBA for transparent pixels
            for w in xrange(width):
                if (orig_pixels[w, h])[3] != 255:
                    dithered_pixels[w, h] = orig_pixels[w, h]
                    # bashing in a new value changes it!

    return dithered_img


def converter(imgname, antialias=False, bgcolor=None, clr=False, dither=False,
              do_ansi=False, fontSize=7, maxLen=100, target_aspect_ratio=1.0):

    try:
        maxLen = float(maxLen)
    except:
        maxLen = 100.0

    try:
        fontSize = int(fontSize)
    except:
        fontSize = 7

    try:
        bgcolor = HTMLColorToRGB(bgcolor) + (255, )
    except:
        bgcolor = None

    try:
        target_aspect_ratio = float(target_aspect_ratio)
    except:
        target_aspect_ratio = 1.0

    try:
        img = load_and_resize_image(imgname, antialias, maxLen,
                                    target_aspect_ratio)
    except IOError:
        exit("File not found: " + imgname)

    if dither:
        img = dither_image_to_web_palette(img, bgcolor)

    pixel = img.load()
    width, height = img.size

    if do_ansi:

        if bgcolor is not None:
            fill_string = ansi.getANSIbgstring_for_ANSIcolor(
                                            ansi.getANSIcolor_for_rgb(bgcolor))
        else:
            fill_string = "\x1b[49m"
        fill_string += "\x1b[K"
        sys.stdout.write(fill_string)
        sys.stdout.write(
            ansi.generate_ANSI_from_pixels(pixel, width, height, bgcolor)[0])
        sys.stdout.write("\x1b[0m\n")
    else:

        if clr:
            # TODO - should handle bgcolor - probably by setting it as BG on
            # the CSS for the pre
            string = generate_HTML_for_image(pixel, width, height)
        else:
            string = generate_grayscale_for_image(
                pixel, width, height, bgcolor)

        return string
