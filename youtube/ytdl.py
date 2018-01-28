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
import argparse
import pytube


class ProgressMonitor(object):
	def __init__(self):
		self._last_percentage = 0
	
	def progress_callback(self, stream, chunk, file, bytes_remaining):
		progress = 1.0 - float(bytes_remaining)/float(stream.filesize)
		percentage = int(100 * progress)
		if percentage > self._last_percentage:
			self._last_percentage = percentage
			print("{}%".format(percentage))
		

def main(args):
	progress = ProgressMonitor()
	video = pytube.YouTube(args.url, on_progress_callback=progress.progress_callback)
	title = video.title
	stream = video.streams.first()
	file_size_mb = float((stream.filesize)/(1024 * 1024))
	print("Title: {}".format(title))
	print("Filename: {}".format(stream.default_filename))
	print("File size: {:.2f} MB".format(file_size_mb))
	print("Downloading...")
	stream.download()
	print("Download complete.")


if __name__ == "__main__":
	ap = argparse.ArgumentParser(description="A simple utility for downloading YouTube videos")
	ap.add_argument("url", help="A YouTube URL")
	args = ap.parse_args()
	main(args)

