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
import requests
import argparse
import urlparse
import posixpath
import sys
import os

parser = None
client_id = "7259c2beefdb373"

def improper_usage(msg):
	if msg:
		sys.stderr.write(msg)
	parser.print_help(file=sys.stderr)
	sys.exit(1)

def is_imgur_url(url):
	base = url.netloc
	if len(url.scheme) == 0:
		# If the url was provided without the scheme, search the path instead
		base = url.path
	return "imgur.com" in base.lower()

def parse_album_url(url):
	# for now we only care about album URLs with the album as the last component
	path = url.path
	# trim any trailing slashes
	while path[-1] == '/' and len(path):
		path = path[:-1]
	_, tail = posixpath.split(path)
	return tail

def prepare_destination(path):
	# technically a race here.
	if os.path.exists(path):
		return os.path.isdir(path) and os.access(path, os.W_OK)
	else:
		try:
			os.mkdir(path)
		except:
			return False
		return True

def album_api_url(name):
	return "https://api.imgur.com/3/album/%s/images" % name

def main():
	global parser
	parser = argparse.ArgumentParser()
	parser.add_argument("url", help="Imgur album url")
	parser.add_argument("-o", "--output", help="Output directory. It is created if it does not exist. (default: same as album name)")
	parser.add_argument("-p", "--prefix", help="Image prefix. If present, each image is saved with the given prefix, follwed by a hyphen, a unique digit, and the extension. (e.g. prefix-%%u.ext)")
	args = parser.parse_args()
	prefix = args.prefix
	url_arg = args.url
	url = urlparse.urlparse(url_arg)
	if not is_imgur_url(url):
		improper_usage("Must provide an imgur url (found %s)\n" % url_arg)
	album_name = parse_album_url(url)
	if not album_name:
		improper_usage("Could not parse album name from url %s\n" % url_arg)
	output_path = args.output
	if output_path is None:
		output_path = album_name
	ok = prepare_destination(output_path)
	if not ok:
		improper_usage("Invalid output path %s\n" % output_path)
	auth_header = {"Authorization" : "Client-ID %s" % client_id}
	album_url = album_api_url(album_name)
	album_response = requests.get(album_url, headers=auth_header)
	response_json = album_response.json()
	image_list = response_json["data"]
	i = 0
	for image_json in image_list:
		try:
			image_url_str = image_json["link"]
			image_url = urlparse.urlparse(image_url_str)
			_, file_name = posixpath.split(image_url.path)
			if prefix:
				_, extension = posixpath.splitext(file_name)
				file_name = "%s-%u%s" % (prefix, i, extension)
				i += 1
			destination = os.path.join(output_path, file_name)
			print "Downloading %s to %s" % (image_url_str, destination)
			image_response = requests.get(image_url_str, headers=auth_header)
			image_response.raise_for_status()
			with open(destination, "w") as f:
				f.write(image_response.content)
		except Exception as e:
			sys.stderr.write("Could not fetch %s: %s\n" % (image_url_str, e))

if __name__ == "__main__":
	main()

