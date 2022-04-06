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


def png2tlb(args):
    print(" ".join([basename(x) for x in args.inputs]))

    if args.output:
        output = args.output
    else:
        output = open(args.inputs[0][:args.inputs[0].rfind(".")] + ".tlb", "wb")

    # Image count
    output.write(struct.pack("<H", len(args.inputs)))

    for i, image in enumerate(args.inputs):
        img = Image.open(image)

        # Quantize if given an RGB(A) image unless alpha only (solid white + alpha)
        alpha = img.mode == "RGBA"
        if img.mode != "P" and img.convert("RGB").tobytes() != b"\xFF" * img.width * img.height * 3:
            img = img.convert("RGB").quantize(colors=args.colors)

        if img.palette and (0xFF, 0x00, 0xFF) in img.palette.colors and img.palette.colors[(0xFF, 0x00, 0xFF)] == 0:
            alpha = True

        # Image header
        type = 0x00
        colors = 0
        if img.mode == "RGBA":
            type = 0x04
        else:
            if len(img.palette.colors) <= 16:
                type = 0x10
                colors = 16
            else:
                colors = 256

            if alpha:
                type |= 0x02

        widthShift = 0
        while (8 << widthShift) < img.width:
            widthShift += 1
        if 8 << widthShift > img.width:
            print(f"Error: Invalid width ({img.width})")
            exit()

        heightShift = 0
        while (8 << heightShift) < img.height:
            heightShift += 1
        if 8 << heightShift > img.height:
            print(f"Error: Invalid height ({img.height})")
            exit()

        bitmapSize = img.width * img.height
        if colors == 16:
            bitmapSize //= 2

        print(f"Image {i}, type 0x{type:X}, shift size {widthShift}x{heightShift}, bitmap 0x{bitmapSize:X} bytes")

        output.write(struct.pack("<LLLL", type, widthShift, heightShift, bitmapSize))

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
        else:  # alpha
            output.write(img.getchannel("A").tobytes())

        # Palette data
        if img.palette:
            pal = b""
            for i in range(len(img.palette.palette) // 3):
                r, g, b = [round(x * 31 / 255) & 0x1F for x in img.palette.palette[i * 3:i * 3 + 3]]
                pal += struct.pack("<H", 1 << 15 | b << 10 | g << 5 | r)
            output.write(pal)


if __name__ == "__main__":
    png2tlbarg = argparse.ArgumentParser(description="Converts image(s) to a TLB")
    png2tlbarg.add_argument("inputs", metavar="in.png", nargs="*", type=str, help="input image(s)")
    png2tlbarg.add_argument("--output", "-o", metavar="out.tlb", type=argparse.FileType("wb"), help="output file")
    png2tlbarg.add_argument("--colors", "-c", type=int, help="number of colors in the palette (only used if input is RGB(A))")
    exit(png2tlb(png2tlbarg.parse_args()))
