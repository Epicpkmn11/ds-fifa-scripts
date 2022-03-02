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
