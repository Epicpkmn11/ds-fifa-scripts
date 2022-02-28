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
from os import SEEK_END, SEEK_SET
from PIL import Image
import struct

parser = argparse.ArgumentParser(description="Converts a TBF file to an image")
parser.add_argument("input", metavar="in.tbf", type=argparse.FileType("rb"), help="input file")
parser.add_argument("--output", "-o", metavar="out.png", type=str, help="output name")

args = parser.parse_args()

if not args.output:
	args.output = args.input.name[:args.input.name.rfind(".")] + ".png"

print(args.input.name)

# Check file size
args.input.seek(0, SEEK_END)
size = args.input.tell()
args.input.seek(0, SEEK_SET)

# Either a 16 or 256 color palette, sometimes bitmap data sometimes not
if (size % 0x4000) == 0x20:
	colors = 16
elif (size % 0x4000) == 0x200:
	colors = 256

# Get palette
palette = [0] * colors * 3  # 256 color palette with RGB separated
for i in range(colors):
	color = struct.unpack("<H", args.input.read(2))[0]
	palette[i * 3] = round((color & 0x1F) * 255 / 31)
	palette[i * 3 + 1] = round(((color >> 5) & 0x1F) * 255 / 31)
	palette[i * 3 + 2] = round(((color >> 10) & 0x1F) * 255 / 31)

# If there's bitmap data it's a 128x128 image
if size > 0x4000:
	size = (128, 128)
	data = args.input.read()
else:  # Otherwise just put the colors
	size = (colors, 1)
	data = bytes([i for i in range(colors)])

img = Image.frombytes("P", size, data)
img.putpalette(palette)

img.save(args.output)
