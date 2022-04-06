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

from os import SEEK_END, SEEK_SET
from PIL import Image
from sys import exit


def tbf2png(args):
    for input in args.inputs:
        print(input.name)

        if args.output:
            output = args.output
        else:
            output = input.name[:input.name.rfind(".")] + ".png"

        # Check file size
        input.seek(0, SEEK_END)
        fsize = input.tell()
        input.seek(0, SEEK_SET)

        # Either a 16 or 256 color palette, sometimes bitmap data sometimes not
        if (fsize % 0x4000) == 0x20:
            colors = 16
        elif (fsize % 0x4000) == 0x200 or fsize == 0x2FC0:
            colors = 256
        else:
            print("Error: Is this a TBF?")
            exit(1)

        # Get palette
        palette = [0] * colors * 3  # 256 color palette with RGB separated
        for i in range(colors):
            color = struct.unpack("<H", input.read(2))[0]
            palette[i * 3] = round((color & 0x1F) * 255 / 31)
            palette[i * 3 + 1] = round(((color >> 5) & 0x1F) * 255 / 31)
            palette[i * 3 + 2] = round(((color >> 10) & 0x1F) * 255 / 31)

        if fsize == 0x2FC0:  # Special case, wclogo.bin
            size = (96, 122)
            data = input.read()
        elif fsize > 0x4000:  # If there's bitmap data it's a 128x128 image
            size = (128, 128)
            data = input.read()
        else:  # Otherwise just put the colors
            size = (colors, 1)
            data = bytes([i for i in range(colors)])

        img = Image.frombytes("P", size, data)
        img.putpalette(palette)

        img.save(output)


if __name__ == "__main__":
    tbf2pngarg = argparse.ArgumentParser(description="Converts a TBF file (or wclogo.bin) to an image")
    tbf2pngarg.add_argument("inputs", metavar="in.tbf", nargs="*", type=argparse.FileType("rb"), help="input file(s)")
    tbf2pngarg.add_argument("--output", "-o", metavar="out.png", type=str, help="output name")
    exit(tbf2png(tbf2pngarg.parse_args()))
