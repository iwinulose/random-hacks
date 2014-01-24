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

client_id = "7259c2beefdb373"
auth_header = {"Authorization" : "Client-ID %s" % client_id}

def improper_usage(msg, parser):
	if msg:
		sys.stderr.write(msg)
	parser.print_help(file=sys.stderr)
	sys.exit(1)

def last_component(url_parts):
	path = url_parts.path.rstrip("/")
	_, tail = posixpath.split(path)
	return tail

def is_album_url(url_parts):
	return "/a/" in url_parts.path

def is_image_url(url_parts):
	last = last_component(url_parts)
	name, ext = posixpath.splitext(last)
	return not ext

def subdir_for_url(url_parts):
	path = ""
	if is_album_url(url_parts):
		path = last_component(url_parts)
	return path

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

def album_api_url(id):
	return "https://api.imgur.com/3/album/%s/images" % id 

def image_api_url(id):
	return "https://api.imgur.com/3/image/%s" % id

def images(url_parts):
	if is_album_url(url_parts):
		album_id = last_component(url_parts) 
		album_url = album_api_url(album_id)
		album_response = requests.get(album_url, headers=auth_header)
		response_json = album_response.json()
		image_list = response_json["data"]
		for image_json in image_list:
			yield image_json["link"]
	elif is_image_url(url_parts):
		image_id = last_component(url_parts)
		image_url = image_api_url(image_id)
		image_response = requests.get(image_url, headers=auth_header)
		response_json = image_response.json()
		image = response_json["data"]
		yield image["link"]
	else:
		yield urlparse.urlunparse(url_parts)

def download(url, destination):
	response = requests.get(url, headers=auth_header)
	response.raise_for_status()
	with open(destination, "w") as f:
		f.write(response.content)

def is_imgur_url(url_parts):
	base = url_parts.netloc
	if len(url_parts.scheme) == 0:
		# If the url was provided without the scheme, search the path instead
		base = url_parts.path
	return "imgur.com" in base.lower()

def urls_for_args(in_arg, is_filename):
	urls = None
	if is_filename or not in_arg:
		in_file = sys.stdin
		if in_arg:
			try:
				in_file = open(in_arg, "r")
			except IOError as e:
				sys.stderr.write("Unable to open file {}".format(in_arg))
		urls = [line.strip() for line in in_file]
	else:
		urls = [in_arg]
	urls = map(urlparse.urlparse, urls)
	return urls

def make_filename(url, prefix, counter):
	imgur_filename = posixpath.basename(url)
	base, ext = posixpath.splitext(imgur_filename)
	if prefix == "":
		base = "{}".format(counter)
	elif prefix:
		base = "{}-{}".format(prefix, counter)
	return "{}{}".format(base, ext)

def process(url_parts, output_dir=".", prefix=None, counter=0):
	for url in images(url_parts):
		filename = make_filename(url, prefix, counter)
		filename = os.path.join(output_dir, filename)
		print "Downloading {} to {}".format(url, filename)
		download(url, filename)
		counter += 1
	return counter

def main(args):
	in_arg = args.arg
	is_filename = args.file
	output_directory = args.output
	prefix = args.prefix
	should_flatten = args.flatten

	urls = urls_for_args(in_arg, is_filename)
	urls = filter(is_imgur_url, urls)
	if not urls:
		print "No imgur urls provided"
		return 0
	
	print "Downloading from {} urls".format(len(urls))

	dest_ok = prepare_destination(output_directory)
	if not dest_ok:
		print "Could not write to {}".format(output_directory)
		return -1

	counter = 0
	for url_parts in urls:
		final_output_dir = output_directory
		if not should_flatten:
			subdir = subdir_for_url(url_parts)
			final_output_dir = os.path.join(output_directory, subdir)
		dest_ok = prepare_destination(final_output_dir)
		if not dest_ok:
			print "Could not write to {}".format(final_output_dir)
			continue
		counter += process(url_parts, final_output_dir, prefix, counter)
	return 0

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Downloads albums or images from imgur.com.")
	parser.add_argument("arg", metavar="url-or-filename", nargs="?", help="""An
	imgur url (for an album or image), or a filename if the --file argument is
	present. If absent, the script reads URLs from stdin, one url per line.""")
	parser.add_argument("-o", "--output", default=".", help="""Output directory. It is created
	if it does not exist. (default: same as album name)""")
	parser.add_argument("-p", "--prefix", help="""Image prefix. If present,
	each image is saved with the given prefix, follwed by a hyphen, a unique
	digit, and the extension. (e.g. prefix-%%u.ext)""")
	parser.add_argument("--file", action="store_true", help="""Treat the argument
	as a file name. The file should contain imgur URLs, one url per line.""")
	parser.add_argument("--flatten", action="store_true", help="""Output all 
	downloaded files in the same directory""")
	args = parser.parse_args()
	try:
		main(args)
	except KeyboardInterrupt:
		exit(0)

