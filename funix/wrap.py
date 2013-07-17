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

import sys
import textwrap
import argparse

DEFAULT_WIDTH = 80

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	readable = argparse.FileType('r')
	parser.add_argument("-w", "--width", help="Width to wrap lines to (default %d)" % DEFAULT_WIDTH, type=int, default=DEFAULT_WIDTH)
	parser.add_argument("-p", "--prefix", help="Prefix to add at the beginning of parsed lines", default="")
	parser.add_argument("file", type=readable, help="File to read from (default: stdin)", nargs='?', default=sys.stdin)
	args = parser.parse_args()
	width = args.width
	prefix = args.prefix
	in_file = args.file
	if width < 0:
		sys.stderr.write("Width may not be negative\n")
		sys.exit(1)
	wrapper = textwrap.TextWrapper()
	wrapper.width = width
	wrapper.subsequent_indent = prefix
	for line in in_file:
		print wrapper.fill(line)
	in_file.close()

