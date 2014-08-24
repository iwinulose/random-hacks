#!/usr/bin/env python
# Copyright (c) 2014, Charles Duyk
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

"""A script to list all the (unique) urls posted by a given reddit user"""

import argparse
import requests
import sys
import webbrowser

_headers = {
	"User-Agent" : "submitted.py/0.1 by iwinulose"
}

#TODO:
# - option for more than just submission (comment, all)

POST_TYPES = ("submitted", "comments", "all")

def make_url(username, post_type=POST_TYPES[0]):
	"""Create the API url for submissions"""
	return "http://api.reddit.com/user/{user}/{type}".format(user=username, type=post_type)

def submitted_urls(username, after=None, post_type=POST_TYPES[0], num_left=None):
	"""Returns a set of all URLs submitted by the given user."""
	num_to_fetch = 100
	if num_left is not None:
		if num_left > 100:
			num_to_fetch = 100
		else:
			num_to_fetch = num_left
	params = dict()
	params["limit"] = num_to_fetch 
	if after:
		params["after"] = after
	base_url = make_url(username, post_type=post_type)
	resp = requests.get(base_url, params=params, headers=_headers)
	if resp.status_code != 200:
		sys.stderr.write("Got a bad response ({})\n".format(resp))
		return set()
	json = resp.json()["data"]
	after = json["after"]
	children = json["children"]
	urls = set([post["data"]["url"] for post in children])
	if num_left is not None:
		num_left -= len(children)
		if num_left <= 0:
			return urls
	if after:
		next = submitted_urls(username, after=after, post_type=post_type, num_left=num_left)
		urls = urls.union(next)
	return urls
	
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Lists all the (unique) urls of posts by a given reddit user")
	parser.add_argument("username", help="The username")
	parser.add_argument("--open", action="store_true", help="Open the links in a browser")
#	parser.add_argument("-t", "--post-type", help="User submissions, comments, or all posts", choices=POST_TYPES, default=POST_TYPES[0])
	parser.add_argument("-n", "--number", type=int, default=None, help="Number of results to return (most recent.)")
	args = parser.parse_args()
	urls = submitted_urls(args.username, post_type=args.post_type, num_left=args.number)
	if urls:
		urls = map(lambda url: url.encode('utf-8'), urls)
		print "\n".join(urls)
		if args.open:
			for url in urls:
				webbrowser.open(url)

