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


def dst2png(args):
    for input in args.inputs:
        print(input.name)

        if(input.read(4) != b"DST1"):
            print("Error: Is this really a DST file?")
            exit()

        if args.output:
            output = args.output
        else:
            output = input.name[:input.name.rfind(".")] + ".png"

        # First two are currently unknown what they mean
        _, _, width, height, flags = struct.unpack("<LLHHH", input.read(0xE))
        alpha = flags & 1  # these are just guesses
        colors = 16 if flags & 0x10 else 256
        bitmapSize = width * height // (2 if colors == 16 else 1)

        print(f"{width}x{height}, {colors} colors {'alpha' if alpha else 'no alpha'}")

        if colors > 0:
            # Convert from DS style to normal RGB palette
            palette = [0] * colors * 3
            for i in range(colors):
                color = struct.unpack("<H", input.read(2))[0]
                palette[i * 3] = round((color & 0x1F) * 255 / 31)
                palette[i * 3 + 1] = round(((color >> 5) & 0x1F) * 255 / 31)
                palette[i * 3 + 2] = round(((color >> 10) & 0x1F) * 255 / 31)

            # Get bitmap data, if 16 color then extract the two nibbles
            data = b""
            if colors == 16:
                for byte in input.read(bitmapSize):
                    data += struct.pack("BB", byte & 0xF, byte >> 4)
            else:
                data = input.read(bitmapSize)

            img = Image.frombytes("P", (width, height), data)
            img.putpalette(palette)
        else:
            print("Error: No colors??")
            exit()

        # Save the image
        img.save(output)


if __name__ == "__main__":
    dst2pngarg = argparse.ArgumentParser(description="Converts a DST file to image(s)")
    dst2pngarg.add_argument("inputs", metavar="in.dst", nargs="*", type=argparse.FileType("rb"), help="input file(s)")
    dst2pngarg.add_argument("--output", "-o", metavar="out.png", type=str, help="output name")
    exit(dst2png(dst2pngarg.parse_args()))
