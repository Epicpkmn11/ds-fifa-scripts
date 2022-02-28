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
from PIL import Image
import struct

parser = argparse.ArgumentParser(description="Converts a DST file to image(s)")
parser.add_argument("input", metavar="in.dst", type=argparse.FileType("rb"), help="input file")
parser.add_argument("output", metavar="out.png", type=str, help="output name")

args = parser.parse_args()

print(args.input.name)

if(args.input.read(4) != b"DST1"):
	print("Error: Is this really a DST file?")
	exit()

# First two are currently unknown what they mean
_, _, width, height, colors = struct.unpack("<LLHHH", args.input.read(0xE))
bitmapSize = width * height // (2 if colors == 16 else 1)

print(f"{width}x{height}, {colors} colors")

if colors > 0:
	# Convert from DS style to normal RGB palette
	palette = [0] * colors * 3
	for i in range(colors):
		color = struct.unpack("<H", args.input.read(2))[0]
		palette[i * 3] = round((color & 0x1F) * 255 / 31)
		palette[i * 3 + 1] = round(((color >> 5) & 0x1F) * 255 / 31)
		palette[i * 3 + 2] = round(((color >> 10) & 0x1F) * 255 / 31)

	# Get bitmap data, if 16 color then extract the two nibbles
	data = b""
	if colors == 16:
		for byte in args.input.read(bitmapSize):
			data += struct.pack("BB", byte & 0xF, byte >> 4)
	else:
		data = args.input.read(bitmapSize)

	img = Image.frombytes("P", (width, height), data)
	img.putpalette(palette)
else:
	print("Error: No colors??")
	exit()

# Save the image
img.save(args.output)
