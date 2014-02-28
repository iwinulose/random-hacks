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

import sys
import heapq
import pprint

class DecodeError(Exception):
	pass

class HuffmanNode(object):
	def __init__(self, obj, weight, left=None, right=None):
		self.obj = obj
		self.weight = weight
		self.left = left
		self.right = right 

	def __cmp__(self, other):
		return cmp(self.weight, other.weight)
	
	def __repr__(self):
		return u"HuffmanNode({}, {}, {}, {})".format(self.obj, self.weight, repr(self.left), repr(self.right))
	
	def is_leaf(self):
		return self.left is None and self.right is None
	
	def build_encode_table(self, table=None, prefix=""):
		if table == None:
			table = {}
		if self.left is not None:
			self.left.build_encode_table(table, prefix+"0")
		if self.right is not None:
			self.right.build_encode_table(table, prefix+"1")
		if self.is_leaf():
			table[self.obj] = prefix
		return table

class Huffman(object):
	@classmethod
	def build_for_string(cls, string):
		def get_frequencies(string):
			freqs = {}
			for char in string:
				val = 0
				if char in freqs:
					val = freqs[char]
				val += 1
				freqs[char] = val
			return freqs 

		def build_nodes(freqs):
			return [HuffmanNode(char, val) for (char, val) in freqs.iteritems()]

		freqs = get_frequencies(data) 
		nodes = build_nodes(freqs)
		heapq.heapify(nodes)
		while len(nodes) > 1:
			min1 = heapq.heappop(nodes)
			min2 = heapq.heappop(nodes)
			new = HuffmanNode(None, min1.weight + min2.weight, min1, min2)
			heapq.heappush(nodes, new)
		tree = nodes[0]
		return cls(tree)
	
	def __init__(self, tree):
		self.tree = tree
		self.table = tree.build_encode_table()
	
	def encode_to_binary_string(self, string):
		return u"".join((self.table[char] for char in string))
	
	def encode(self, string):
		def _substrings_of_length(string, n, padding):
			length = len(string)
			num_substrs = length / n
			if length % n:
				num_substrs += 1
			for i in xrange(num_substrs):
				yield string[i*n:i*n+n].ljust(n, padding)

		binstring = self.encode_to_binary_string(string)
		substr_gen = _substrings_of_length(binstring, 8, "0")
		int_gen = (int(string, 2) for string in substr_gen)
		return bytearray(int_gen)

	def _decode(self, generator):
		chars = []
		curr = self.tree
		for token in generator:
			if not token and curr.left:
				curr = curr.left
			elif token and curr.right:
				curr = curr.right
			if curr.is_leaf():
				chars.append(curr.obj)
				curr = self.tree
		return u"".join(chars)
		
	def decode_binary_string(self, binstring):
		def _binary_string_generator(binstring):
			for char in binstring:
				if char == "0":
					yield False
				elif char == "1":
					yield True
				else:
					raise DecodeError("Illegal character in binary string ({})".format(char))
		return self._decode(_binary_string_generator(binstring))
	
	def decode(self, buff):
		def _binary_generator(buff):
			for byte in buff:
				for i in reversed(xrange(8)):
					bit = byte & (1 << i)
					yield bool(bit)
		return self._decode(_binary_generator(buff))

if __name__ == "__main__":
	data =  sys.stdin.read().decode("utf-8")
	if data:
		encoder = Huffman.build_for_string(data)
		binary = encoder.encode_to_binary_string(data)
		print "In:", data.encode("utf-8")
		pprint.pprint(encoder.table)
		print encoder.decode_binary_string(binary).encode("utf-8")
		binary = encoder.encode(data)
		print binary
		print encoder.decode(binary)

