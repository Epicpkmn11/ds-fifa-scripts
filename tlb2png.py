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

parser = argparse.ArgumentParser(description="Converts a TLB file to image(s)")
parser.add_argument("input", metavar="in.tlb", type=argparse.FileType("rb"), help="input file")
parser.add_argument("output", metavar="out.png", type=str, help="output name")

args = parser.parse_args()

print(args.input.name)

imageCount = struct.unpack("<H", args.input.read(2))[0]

for image in range(imageCount):
	type, widthShift, heightShift, bitmapSize = struct.unpack("<LLLL", args.input.read(0x10))

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
		for byte in args.input.read(bitmapSize):
			data += struct.pack("BB", byte & 0xF, byte >> 4)
	else:
		data = args.input.read(bitmapSize)

	if colors > 0:
		img = Image.frombytes("L", (width, height), data)

		# Convert from DS style to normal RGB palette
		palette = [0] * colors * 3
		for i in range(colors):
			color = struct.unpack("<H", args.input.read(2))[0]
			palette[i * 3] = round((color & 0x1F) * 255 / 31)
			palette[i * 3 + 1] = round(((color >> 5) & 0x1F) * 255 / 31)
			palette[i * 3 + 2] = round(((color >> 10) & 0x1F) * 255 / 31)
		img.putpalette(palette)

		if alpha:  # set color 0 to transparent
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
		img.save(f"{args.output[:args.output.rfind('.')]}-{image}{args.output[args.output.rfind('.'):]}")
	else:
		img.save(args.output)
