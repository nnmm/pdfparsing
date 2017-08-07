# coding: utf-8

import pdfquery
import csv
import argparse

parser = argparse.ArgumentParser(description='Parses tables from pdfs.')
parser.add_argument('--header', required=True, help='A word in the table header to identify the start')
parser.add_argument('--cols', nargs='+', required=True, help='The columns in the order as they appear in the table. Can be "Anzahl", "Bezeichnung", "Preis" or "-", the last of which ignores the column.')
parser.add_argument('pdf', metavar='FILE', help='The PDF to be parsed')
args = parser.parse_args()

pdf = pdfquery.PDFQuery(args.pdf)
pdf.load()

# -------------------- y1
# |                  |
# |                  |
# |                  |
# -------------------- y0
# x0                x1
#
# points lower on the page have lower y coordinates,
# i. e. y0 < y1

# This assumes that:
# - each row is on one line
# - the entire table is on one page
# - each row (and the header) has the same number of entries (LTTextLineHorizontal elements)
# - prices are written using ',' as decimal separator
# and will fail or produce garbage for pdfs that don't meet these assumptions

class PdfTableRows(object):
	"""An iterable over the rows of a pdf table"""
	def __init__(self, pdf, header):
		super(PdfTableRows, self).__init__()
		self.pdf = pdf
		self.table = self.find_start(header)

	def find_start(self, header):
		# the bbox where the table is stretches over the whole page horizontally
		xmax = float(pdf.tree.xpath('//*/LTPage')[0].get('x1'))
		# and starts at the y-coordinate where we find the header
		el = self.pdf.pq('LTTextLineHorizontal:contains("{}")'.format(header))
		ymax = float(el[0].get('y0'))

		table = pdf.pq('LTTextLineHorizontal:overlaps_bbox("{},{},{},{}")'.format(0, 0, xmax, ymax))
		# filter to cut off the header itself
		return table.filter(lambda: float(this.get('y0')) < ymax)

	def __iter__(self):
		return self

	def __next__(self):
		if self.table.size() == 0:
			raise StopIteration

		# find the current y
		y = max(float(el.get('y0')) for el in self.table)
		# extract the line with current y
		line = self.get_line(y)
		# go to next line
		self.table = self.table.filter(lambda: float(this.get('y0')) < y)
		return line

	def get_line(self, y):
		row = self.table.filter(lambda: float(this.get('y0',0)) == y)
		ordered_row = sorted(row, key=lambda el: float(el.get('x0')))
		return [sel.text.strip() for sel in ordered_row]

class PdfTable(PdfTableRows):
	"""Filters and parses output of PdfTableRows"""
	def __init__(self, pdf, config):
		super(PdfTable, self).__init__(pdf, config.header)
		self.config = config
		self.started = False

	def __iter__(self):
		return self

	def __next__(self):
		while True:		
			row = PdfTableRows.__next__(self)
			try:
				res = self.parse_row(row)
				self.started = True
				return res
			except ValueError as e:
				# If we arrive at the first malformed row after
				# having seen correct rows before, stop
				if self.started:
					raise StopIteration

	def parse_row(self, row):
		if len(row) != len(self.config.cols):
			raise ValueError('{} does not have {} elements'.format(row, len(self.config.cols)))
		result = []
		for typ, val in zip(self.config.cols, row):
			if typ == 'Anzahl':
				result.append(int(val))
			elif typ == 'Bezeichnung':
				result.append(val)
			elif typ == 'Preis':
				result.append(PdfTable.parse_price(val))
		return result

	def parse_price(value):
		# strip '€' or 'EUR'
		if value.startswith('€'):
			value = value[1:]
		if value.startswith('EUR'):
			value = value[3:]
		if value.endswith('€'):
			value = value[:-1]
		if value.endswith('EUR'):
			value = value[:-3]

		# remove all dots, then replace comma by dot
		value.replace(".", "")
		value = value.replace(",", ".")
		return float(value)

config = args
pt = PdfTable(pdf, config)

print(list(filter(lambda x: x != '-', config.cols)))
for l in pt:
	print(l)
