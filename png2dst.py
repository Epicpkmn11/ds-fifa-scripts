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
from os.path import basename
from PIL import Image
import struct

parser = argparse.ArgumentParser(description="Converts an image to a DST")
parser.add_argument("input", metavar="in.png", type=str, help="input image")
parser.add_argument("output", metavar="out.dst", type=argparse.FileType("wb"), help="output file")

args = parser.parse_args()

print(basename(args.input))

with Image.open(args.input) as img:
	if img.mode != "P":
		img = img.convert("RGB").quantize()

	# Write header
	# First 8 bytes after magic are unknown atm
	colors = len(img.palette.palette) // 3
	args.output.write(b"DST1" + struct.pack("<LLHHH", 0x01010102, 3, *img.size, colors))

	print(f"{img.width}x{img.height}, {colors} colors")

	# Palette data
	if img.palette:
		pal = b""
		for i in range(len(img.palette.palette) // 3):
			r, g, b = [round(x * 31 / 255) & 0x1F for x in img.palette.palette[i * 3:i * 3 + 3]]
			pal += struct.pack("<H", 1 << 15 | b << 10 | g << 5 | r)
		args.output.write(pal)

	# Bitmap data
	if colors == 16:  # 16 color
		data = b""
		bytes = img.tobytes()
		for i in range(len(bytes) // 2):
			lower, upper = bytes[i * 2:i * 2 + 2]
			data += struct.pack("B", (lower & 0xF) | ((upper & 0xF) << 4))
		args.output.write(data)
	elif colors > 0:  # 256 color
		args.output.write(img.tobytes())
	else:
		print("Error: Invalid color count??")
		exit()
