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



def lbs_to_kgs(lbs):
	return .453592 * lbs


def kgs_to_lbs(kgs):
	return kgs/.453592


def in_to_m(inches):
	return .0254 * inches


def bmi(kg, m):
	kg = float(kg)
	m = float(m)
	return kg/pow(m, 2)


def bmi_imperial(lbs, ft, inches):
	kgs = lbs_to_kgs(lbs)
	meters = in_to_m(12*ft + inches)
	return bmi(kgs, meters)


def weight_for_bmi(height, bmi):
	return bmi*pow(height, 2)


class Calculator(object):
	def __init__(self, ft=0.0, inches=0.0, m=0.0, lbs=0.0, kgs=0.0) :
		if not any((ft, inches, m)):
			raise ValueError("Must specify height")
		self.height = m + in_to_m(12*ft + inches)
		self.weight = kgs + lbs_to_kgs(lbs)
	
	def bmi(self):
		return bmi
	
	def set_weight_lbs(self, lbs):
		self.weight = lbs_to_kgs(lbs)
	
	def set_weight(self, kgs):
		self.weight = weight
	
	def set_height_imperial(self, ft, inches):
		self.height = in_to_m(12*ft + inches)
	
	def bmi(self):
		return bmi(self.weight, self.height)
	
	def weight_for_bmi(self, bmi):
		return weight_for_bmi(self.height, bmi)
		
	def weight_for_bmi_imperial(self, bmi):
		kgs = self.weight_for_bmi(bmi)
		return kgs_to_lbs(kgs)


if __name__ == "__main__":
	import argparse
	import sys
	parser = argparse.ArgumentParser(description="Calculates BMI and/or requisite weight for target BMI.")
	parser.add_argument("--feet", type=float, default=0.0)
	parser.add_argument("--inches", type=float, default=0.0)
	parser.add_argument("--meters", type=float, default=0.0)
	parser.add_argument("--lbs", type=float, default=0.0)
	parser.add_argument("--kgs", type=float, default=0.0)
	parser.add_argument("--target", type=float, default=0.0, help="If a target BMI is supplied, prints the requisite weight")
	group = parser.add_mutually_exclusive_group()
	group.add_argument("--metric", action="store_true", help="Print values in metric units")
	group.add_argument("--imperial", action="store_true", help="Print values in imperial units")
	args = parser.parse_args()
	ft = args.feet
	inches = args.inches
	meters = args.meters
	lbs = args.lbs
	kgs = args.kgs
	target = args.target
	use_metric = (meters or kgs or args.metric) if not args.imperial else False
	if not any((ft, inches, meters)):
		sys.stderr.write("Must provide a height.\n")
		parser.print_help(sys.stderr)
		sys.exit(1)
	calc = Calculator(ft=ft, inches=inches, m=meters, lbs=lbs, kgs=kgs)
	if lbs or kgs:
		bmi = calc.bmi()
		print "Your BMI is %.01f" % (bmi)
	if target:
		unit = "undef"
		target_weight = calc.weight_for_bmi(target)
		if use_metric:
			unit = "kgs"
		else:
			target_weight = kgs_to_lbs(target_weight)
			unit = "lbs"
		print "You want to be %.01f %s to have a BMI of %.01f" % (target_weight, unit, target)

