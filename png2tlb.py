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

parser = argparse.ArgumentParser(description="Converts image(s) to a TLB")
parser.add_argument("input", metavar="in.png", nargs="*", type=str, help="input image(s)")
parser.add_argument("output", metavar="out.tlb", type=argparse.FileType("wb"), help="output file")
parser.add_argument("--colors", "-c", type=int, help="number of colors in the palette (only used if input is RGB(A))")

args = parser.parse_args()

print(" ".join([basename(x) for x in args.input]))

# Image count
args.output.write(struct.pack("<H", len(args.input)))

for i, image in enumerate(args.input):
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

	args.output.write(struct.pack("<LLLL", type, widthShift, heightShift, bitmapSize))

	# Bitmap data
	if colors == 16:
		data = b""
		bytes = img.tobytes()
		for i in range(len(bytes) // 2):
			lower, upper = bytes[i * 2:i * 2 + 2]
			data += struct.pack("B", (lower & 0xF) | ((upper & 0xF) << 4))
		args.output.write(data)
	else:
		args.output.write(img.getchannel("A").tobytes())

	# Palette data
	if img.palette:
		pal = b""
		for i in range(len(img.palette.palette) // 3):
			r, g, b = [round(x * 31 / 255) & 0x1F for x in img.palette.palette[i * 3:i * 3 + 3]]
			pal += struct.pack("<H", 1 << 15 | b << 10 | g << 5 | r)
		args.output.write(pal)
