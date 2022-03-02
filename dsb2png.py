#!/usr/bin/env python3

# Requirements:
# pip3 install pillow

"""
Copyright © 2022 Pk11

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
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
