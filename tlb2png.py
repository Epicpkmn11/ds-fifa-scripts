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


def tlb2png(args):
    for input in args.inputs:
        print(input.name)

        if args.output:
            output = args.output
        else:
            output = input.name[:input.name.rfind(".")] + ".png"

        imageCount = struct.unpack("<H", input.read(2))[0]

        for image in range(imageCount):
            type, widthShift, heightShift, bitmapSize = struct.unpack("<LLLL", input.read(0x10))

            # Get colors and if there's alpha from the 'type'
            colors = 0
            alpha = False
            if type & 0x04:  # Alpha only
                alpha = True
            elif type & 0x10:  # 16 color
                colors = 16
            elif (type & ~0x02) == 0:  # 256 color
                colors = 256
            else:
                print(f"Error: supported type ({type})")
                exit()

            if type & 0x02:
                alpha = True

            # For some reason the size is stored so you need to shift 8 to it
            width = 8 << widthShift
            height = 8 << heightShift

            print(f"Image {image}, {width}x{height}, {colors} colors, {'alpha' if alpha else 'no alpha'}")

            # Get bitmap data, if 16 color then extract the two nibbles
            data = b""
            if colors == 16:
                for byte in input.read(bitmapSize):
                    data += struct.pack("BB", byte & 0xF, byte >> 4)
            else:
                data = input.read(bitmapSize)

            if colors > 0:
                img = Image.frombytes("P", (width, height), data)

                # Convert from DS style to normal RGB palette
                palette = [0] * colors * 3
                for i in range(colors):
                    color = struct.unpack("<H", input.read(2))[0]
                    palette[i * 3] = round((color & 0x1F) * 255 / 31)
                    palette[i * 3 + 1] = round(((color >> 5) & 0x1F) * 255 / 31)
                    palette[i * 3 + 2] = round(((color >> 10) & 0x1F) * 255 / 31)
                img.putpalette(palette)

                if alpha and args.alpha:  # set color 0 to transparent
                    img = img.convert("RGBA")
                    alpha = Image.frombytes("L", (width, height), bytes([0 if x == 0 else 0xFF for x in data]))
                    img.putalpha(alpha)
            elif alpha:  # alpha only
                img = Image.frombytes("RGB", (width, height), b"\xFF" * width * height * 3)
                alpha = Image.frombytes("L", (width, height), data)
                img.putalpha(alpha)
            else:
                print("Error: No colors or alpha??")
                exit()

            # Save the image, if more than one image in the TBL append a number
            if(imageCount > 1):
                img.save(f"{output[:output.rfind('.')]}-{image}{output[output.rfind('.'):]}")
            else:
                img.save(output)


if __name__ == "__main__":
    tlb2pngarg = argparse.ArgumentParser(description="Converts a TLB file to image(s)")
    tlb2pngarg.add_argument("inputs", metavar="in.tlb", nargs="*", type=argparse.FileType("rb"), help="input file(s)")
    tlb2pngarg.add_argument("--output", "-o", metavar="out.png", type=str, help="output name")
    tlb2pngarg.add_argument("--alpha", "-a", action="store_true", help="make transparent pixel transparent instead of #FF00FF (may break reverse conversion)")
    exit(tlb2png(tlb2pngarg.parse_args()))
