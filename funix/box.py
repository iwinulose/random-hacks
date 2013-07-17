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
import argparse

prog_description = """
Pretty prints boxes around strings. Input is read from a file or stdin.
The input should be formatted as groups of lines, separated by lines of
whitespace. Each group of lines is printed into its own box. 

Adjacent whitespace-only lines are collapsed.
"""

def max_line_len(groups):
	max_len = 0
	for linegroup in groups:
		for line in linegroup:
			line_len = len(line)
			max_len = max(max_len, line_len)
	return max_len

def repeated_chars_from_string(string, num):
	str_len = len(string)
	repeats = num/str_len
	remain = num % str_len
	return repeats*string + string[:remain]

class BoxFormatter(object):
	def __init__(self, groups=None, h_padding=2, v_padding=1, h_sep="|", v_sep="_", fill=" "):
		self.groups = groups
		self.h_padding = h_padding
		self.v_padding = v_padding
		self.h_sep = h_sep
		self.v_sep = v_sep
		self.fill = fill

	def _gen_rule(self, add_h_sep=True):
		"""Returns a horizontal rule of the box width, using the horizontal separator provided"""
		h_sep = self.h_sep
		if not add_h_sep:
			h_sep = ""
		rule_len = self.box_width - 2*len(h_sep)
		rule_fill = repeated_chars_from_string(self.v_sep, rule_len)
		return h_sep + rule_fill + h_sep
	
	def _gen_blank(self):
		"""Returns a blank line with the horizontal separators"""
		blank_fill = repeated_chars_from_string(self.fill, self.inner_width)
		return self.h_sep + blank_fill + self.h_sep
	
	def _preflight(self):
		"""Sets up the BoxFormatter for the current lines"""
		longest_line = max_line_len(self.groups)
		self.inner_width = longest_line + 2*self.h_padding
		self.box_width = self.inner_width + 2*len(self.h_sep) 
		self._rule = self._gen_rule()
		self._blank = self._gen_blank()
	
	def _format_line(self, line):
		padding_amount = self.inner_width - len(line)
		num_padding_before = num_padding_after = padding_amount/2
		if padding_amount % 2:
			num_padding_after += 1
		padding_before = repeated_chars_from_string(self.fill, num_padding_before)
		padding_after = repeated_chars_from_string(self.fill, num_padding_after)
		return self.h_sep + padding_before + line + padding_after + self.h_sep
		
	def format(self, groups=None):
		if groups:
			self.groups = groups
		if not self.groups:
			return ""
		self._preflight()
		output = []
		output.append(self._gen_rule(add_h_sep=False))
		for group in self.groups:
			#add padding
			for i in xrange(self.v_padding):
				output.append(self._blank)
			#the lines
			for line in group:
				output.append(self._format_line(line))
			#padding
			for i in xrange(max(self.v_padding - 1, 0)):
				output.append(self._blank)
			output.append(self._rule)
		return "\n".join(output)

def parse_input(in_file):
	"""Returns an iterable of iterables. Each element of the outer 
	iterable is a set of lines to be put in each box"""
	ret = []
	current = []
	for line in in_file:
		line = line.strip()
		if line:
			current.append(line)
		else:
			if current:
				ret.append(current)
				current = []
	if current:
		ret.append(current)
	return ret

def main():
	parser = argparse.ArgumentParser(description=prog_description)
	readable = argparse.FileType('r')
	parser.add_argument("file", type=readable, help="File to read from (default: stdin)", nargs='?', default=sys.stdin)
	args = parser.parse_args()
	in_file = args.file
	groups = parse_input(in_file)
	in_file.close()
	formatter = BoxFormatter(groups=groups)
	print formatter.format()

if __name__ == "__main__":
	main()

