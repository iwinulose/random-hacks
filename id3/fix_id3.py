#!/usr/bin/env python
# Copyright (c) 2013, Charles Duyk
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
"""Update the ID3 tags of MP3s in the format "## Title - Composer.mp3"""
import glob
import os.path
import argparse
# requires mutagen https://code.google.com/p/mutagen/
from mutagen.easyid3 import EasyID3

class SongInfo(object):
	def __init__(self, path):
		filename = os.path.basename(path)
		name, _ = filename.split(".")
		name = name[3:]
		parts = name.split("-")
		self.title = parts[0].strip()
		self.composer = parts[1].strip()
	
	def __str__(self):
		return "SongInfo(title={}, composer={})".format(self.title, self.composer)


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("directory", help="Path to a directory", default=".", nargs="?")
	args = parser.parse_args()
	dir_path = args.directory
	if not os.path.isdir(dir_path):
		parser.error("Must specify a directory.")
	path = os.path.join(dir_path, "*.mp3")
	paths = glob.glob(path)
	id3s = [EasyID3(p) for p in paths]
	infos = [SongInfo(p) for p in paths]
	for id3, info in zip(id3s, infos):
		id3["title"] = info.title
		id3["composer"] = info.composer
		id3.save()


if __name__ == "__main__":
	main()

