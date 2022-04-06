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


def png2dst(args):
    for input in args.inputs:
        print(basename(input))

        if args.output:
            output = args.output
        else:
            output = open(input[:input.rfind(".")] + ".dst", "wb")

        with Image.open(input) as img:
            if img.mode != "P":
                img = img.convert("RGB").quantize()

            # Write header
            # First 8 bytes after magic are unknown atm
            colors = len(img.palette.palette) // 3
            output.write(b"DST1" + struct.pack("<LLHHH", 0x01010102, 3, *img.size, colors))

            print(f"{img.width}x{img.height}, {colors} colors")

            # Palette data
            if img.palette:
                pal = b""
                for i in range(len(img.palette.palette) // 3):
                    r, g, b = [round(x * 31 / 255) & 0x1F for x in img.palette.palette[i * 3:i * 3 + 3]]
                    pal += struct.pack("<H", 1 << 15 | b << 10 | g << 5 | r)
                output.write(pal)

            # Bitmap data
            if colors == 16:  # 16 color
                data = b""
                bytes = img.tobytes()
                for i in range(len(bytes) // 2):
                    lower, upper = bytes[i * 2:i * 2 + 2]
                    data += struct.pack("B", (lower & 0xF) | ((upper & 0xF) << 4))
                output.write(data)
            elif colors > 0:  # 256 color
                output.write(img.tobytes())
            else:
                print("Error: Invalid color count??")
                exit()


if __name__ == "__main__":
    png2dstarg = argparse.ArgumentParser(description="Converts an image to a DST")
    png2dstarg.add_argument("inputs", metavar="in.png", nargs="*", type=str, help="input image(s)")
    png2dstarg.add_argument("--output", "-o", metavar="out.dst", type=argparse.FileType("wb"), help="output file")
    exit(png2dst(png2dstarg.parse_args()))
