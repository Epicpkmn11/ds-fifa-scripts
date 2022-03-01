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


def png2tbf(args):
    for input in args.inputs:
        print(basename(input))

        with Image.open(input) as img:
            if args.output:
                output = args.output
            else:
                if img.size == (96, 122):  # wclogo.bin
                    output = open(input[:input.rfind(".")] + ".bin", "wb")
                else:
                    output = open(input[:input.rfind(".")] + ".tbf", "wb")

            if img.mode != "P":
                img = img.convert("RGB").quantize(256)

            # Get palette, converted to DS format
            for i in range(len(img.palette.palette) // 3):
                r, g, b = [round(x * 31 / 255) & 0x1F for x in img.palette.palette[i * 3:i * 3 + 3]]
                output.write(struct.pack("<H", 1 << 15 | b << 10 | g << 5 | r))

            # If the image is 128x128, write the image data
            if img.size == (128, 128) or img.size == (96, 122):
                output.write(img.tobytes())
            else:
                print("Error: Incorrect size")
                exit(1)


if __name__ == "__main__":
    png2tbfarg = argparse.ArgumentParser(description="Converts an image to a TBF")
    png2tbfarg.add_argument("inputs", metavar="in.png", nargs="*", type=str, help="input image(s)")
    png2tbfarg.add_argument("--output", "-o", metavar="out.tbf", type=argparse.FileType("wb"), help="output file")
    exit(png2tbf(png2tbfarg.parse_args()))
