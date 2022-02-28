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

parser = argparse.ArgumentParser(description="Converts an image to a TBF")
parser.add_argument("input", metavar="in.png", type=str, help="input image")
parser.add_argument("--output", "-o", metavar="out.tbf", type=argparse.FileType("wb"), help="output file")

args = parser.parse_args()

if not args.output:
	args.output = open(args.input[:args.input.rfind(".")] + ".tbf", "wb")

print(basename(args.input))

with Image.open(args.input) as img:
	if img.mode != "P":
		img = img.convert("RGB").quantize(256)

	# Get palette, converted to DS format
	for i in range(len(img.palette.palette) // 3):
		r, g, b = [round(x * 31 / 255) & 0x1F for x in img.palette.palette[i * 3:i * 3 + 3]]
		args.output.write(struct.pack("<H", 1 << 15 | b << 10 | g << 5 | r))

	# If the image is 128x128, write the image data
	if img.size == (128, 128):
		args.output.write(img.tobytes())
