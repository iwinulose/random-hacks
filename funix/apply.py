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

import subprocess
import argparse
import os
import sys

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("command", help="The command to run on each element in the folder")
	parser.add_argument("folder", help="The folder over which to iterate", nargs="?", default=".")
	parser.add_argument("-v", "--verbose", help="Verbose output to stderr", action="store_true")
	args = parser.parse_args()
	command = args.command
	folder = args.folder
	verbose = args.verbose
	commandList = command.split()
	for dirName, subDirs, files in os.walk(folder):
		for file in files:
			path = os.path.join(dirName, file)
			if verbose:
				sys.stderr.write("%s %s\n" % (command, path))
			invocation = commandList[:]
			invocation.append(path)
			subprocess.call(invocation)

