#!/usr/bin/env python

def make_struct(i):
	c = chr(i)
	s = ""
	if c.isalnum():
		s = c
	else:
		s = "%%%02x" % i
	return '{%d, "%s"}' % (len(s), s)

def main():
	structs = [make_struct(i) for i in xrange(128)]
	table = "const translation_s lookup[] = {\n\t" + ",\n\t".join(structs) + "\n}"
	print table
	
if __name__ == "__main__":
	main()
