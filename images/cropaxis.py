#!/usr/bin/env python
# Copyright (c) 2018 Charles Duyk
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# 
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from __future__ import print_function
from PIL import Image
import argparse
import os.path
import sys

AXIS_X = "x"
AXIS_Y = "y"

AXIS_CHOICES = (
	AXIS_X,
	AXIS_Y,
)


def main(args):
	upper_left_x = 0.0
	upper_left_y = 0.0
	bottom_right_x = 0.0
	bottom_right_y = 0.0

	ratio = args.ratio
	input_image_path = args.image
	output_image_path = args.output_image_path

	if not output_image_path:
		input_image_dir, input_image_filename = os.path.split(input_image_path)
		input_image_name, input_image_extension = os.path.splitext(input_image_filename)
		output_image_filename = "{}_cropped{}".format(input_image_name, input_image_extension)
		output_image_path = os.path.join(input_image_dir, output_image_filename)

	try:
		with Image.open(input_image_path) as im:
			width, height = im.size

			if args.axis == AXIS_X:
				upper_left_y = 0.0
				bottom_right_y = height
				if args.reverse:
					upper_left_x = width - ratio * width
					bottom_right_x = width
				else:
					upper_left_x = 0.0
					bottom_right_x = ratio * width
			else:
				upper_left_x = 0.0
				bottom_right_x = width
				if args.reverse:
					upper_left_y = height - ratio * height
					bottom_right_y = height
				else:
					upper_left_y = 0.0
					bottom_right_y = ratio * height

			crop_box = (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y)
			with im.crop(crop_box) as crop_im:
				crop_im.save(output_image_path)

	except IOError as e:
		print("Error cropping image: {}".format(e))


if __name__ == "__main__":
	ap = argparse.ArgumentParser(description="Crops images along a given axis")
	ap.add_argument("image")
	ap.add_argument("--output", "-o", dest="output_image_path")
	ap.add_argument("--ratio", "-r", type=float, default=0.5)
	ap.add_argument("--reverse", action="store_true", help="Crop from right-to-left (x axis) or bottom-to-top (y axis)")
	axis_group = ap.add_mutually_exclusive_group()
	axis_group.add_argument("--axis", default=AXIS_X, choices=AXIS_CHOICES)
	axis_group.add_argument("-x", dest="axis", const=AXIS_X, action="store_const")
	axis_group.add_argument("-y", dest="axis", const=AXIS_Y, action="store_const")
	args = ap.parse_args()

	if not os.path.exists(args.image):
		ap.error("No input image specified")

	if args.ratio < 0.0 or args.ratio > 1.0:
		ap.error("Ratio must be in the range {0.0, 1.0}")

	main(args)
