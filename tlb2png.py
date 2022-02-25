#!/usr/bin/env python3

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
	mode, widthShift, heightShift, bitmapSize = struct.unpack("<LLLL", args.input.read(0x10))

	# Get colors and if there's alpha from the 'mode'
	colors = 0
	alpha = False
	if mode & 0x04:  # Alpha only
		alpha = True
	elif mode & 0x10:  # 16 color
		colors = 16
	elif (mode & ~0x02) == 0:  # 256 color
		colors = 256
	else:
		print(f"Error: supported mode ({mode})")
		exit()
	
	if mode & 0x02:
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
