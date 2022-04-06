#!/usr/bin/env python3

# Requirements:
# pip3 install pillow

"""
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>
"""

import argparse
import struct

from PIL import Image
from sys import exit


def dsb2png(args):
    for input in args.inputs:
        print(input.name)

        if args.output:
            output = args.output
        else:
            output = input.name[:input.name.rfind(".")] + ".png"

        # Last three are currently unknown
        width, height, _, _, _ = struct.unpack("<LLLLH", input.read(0x12))
        colors = 63
        bitmapSize = width * height // (2 if colors == 16 else 1)

        print(f"{width}x{height}, {colors} colors")  # , {'alpha' if alpha else 'no alpha'}")

        # Convert from DS style to normal RGB palette
        palette = [0] * colors * 3
        for i in range(colors):
            color = struct.unpack("<H", input.read(2))[0]
            palette[i * 3] = round((color & 0x1F) * 255 / 31)
            palette[i * 3 + 1] = round(((color >> 5) & 0x1F) * 255 / 31)
            palette[i * 3 + 2] = round(((color >> 10) & 0x1F) * 255 / 31)

        # Use #FF00FF for color 0, pad real palette until the end
        palette = ([0xFF, 0x00, 0xFF] + [0] * (256 - colors - 1) * 3) + palette

        # Get bitmap data
        data = input.read(bitmapSize)

        img = Image.frombytes("P", (width, height), data)
        img.putpalette(palette)

        # Save the image
        img.save(output)


if __name__ == "__main__":
    dsb2pngarg = argparse.ArgumentParser(description="Converts a DSB file to image(s)")
    dsb2pngarg.add_argument("inputs", metavar="in.dsb", nargs="*", type=argparse.FileType("rb"), help="input file(s)")
    dsb2pngarg.add_argument("--output", "-o", metavar="out.png", type=str, help="output name")
    exit(dsb2png(dsb2pngarg.parse_args()))
