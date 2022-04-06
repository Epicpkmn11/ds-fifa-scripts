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

from os.path import basename
from PIL import Image
from sys import exit


def png2dsb(args):
    for input in args.inputs:
        print(basename(input))

        if args.output:
            output = args.output
        else:
            output = open(input[:input.rfind(".")] + ".dsb", "wb")

        with Image.open(input) as img:
            if img.mode != "P":
                img = img.convert("RGB").quantize()

            # Write header
            # Last three are currently unknown
            colors = 63
            output.write(struct.pack("<LLLLH", *img.size, 1, 0, 0))

            print(f"{img.width}x{img.height}, {colors} colors")

            # Palette data
            if img.palette:
                pal = b""
                for i in range(256 - colors, 256):
                    r, g, b = [round(x * 31 / 255) & 0x1F for x in img.palette.palette[i * 3:i * 3 + 3]]
                    pal += struct.pack("<H", 1 << 15 | b << 10 | g << 5 | r)
                output.write(pal)

            # Bitmap data
            output.write(img.tobytes())


if __name__ == "__main__":
    png2dsbarg = argparse.ArgumentParser(description="Converts an image to a DSB")
    png2dsbarg.add_argument("inputs", metavar="in.png", nargs="*", type=str, help="input image(s)")
    png2dsbarg.add_argument("--output", "-o", metavar="out.dsb", type=argparse.FileType("wb"), help="output file")
    exit(png2dsb(png2dsbarg.parse_args()))
