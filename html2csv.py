#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Richard's html2csv converter
#rbarnes@umn.edu
#

#TODO: Extract TODO comments into github issues

from bs4 import BeautifulSoup
import sys
import csv
import argparse

parser = argparse.ArgumentParser(description='Reads in an HTML and attempts to convert all tables into CSV files.')
parser.add_argument('--delimiter', '-d', action='store', default=',',help="Character with which to separate CSV columns")
parser.add_argument('--quotechar', '-q', action='store', default='"',help="Character within which to nest CSV text")
parser.add_argument('filename',nargs="?",help="HTML file from which to extract tables")
args = parser.parse_args()

#TODO: Add a -v/--verbose option for the excessive print statements below. Consider both `-v` `-V` (AKA: VERY VERBOSE, which is currently the default)

if sys.stdin.isatty() and not args.filename:
  parser.print_help()
  sys.exit(-1)
elif not sys.stdin.isatty():
  args.filename = sys.stdin
else:
  args.filename = open(sys.argv[1],'r')

print("Opening file")
fin  = args.filename.read()

print("Parsing file")
soup = BeautifulSoup(fin,"html.parser")

print("Preemptively removing unnecessary tags")
[s.extract() for s in soup('script')]

print("CSVing file")
tablecount = -1
for table in soup.findAll("table"):
  tablecount += 1
  print("Processing Table #%d" % (tablecount))
  with open(sys.argv[1]+str(tablecount)+'.csv', 'w', newline='') as csvfile:
    fout = csv.writer(csvfile, delimiter=args.delimiter, quotechar=args.quotechar, quoting=csv.QUOTE_MINIMAL)
    rowcount = 1
    #Removes nested tables. for handling the sins of 1990's web pages.
    #TODO: Add an argument to enable/disable table de-nesting
    [t.extract() for t in table.findAll("table")]
    #This would grab all TRs regardless of depth without the above line removing nested tables
    for row in table.findAll('tr'):
      print(f"Processing row number {rowcount}")
      rowcount += 1
      cols = row.findAll(['td','th'])
      print(f"Found {len(cols)} columns.")
      #TODO: Detect and discard empty tables (those that contain 1 row, 1 column, consisting of an empty string...I think?)
      #TODO: Add a warning for non-rectangular tables.
      if cols:
        cols = [str(x.text).strip() for x in cols]
        fout.writerow(cols)
#TODO: In HTML documents that use tables for layout (yuck!) add option to detect table titles in preceding sibling tables of size 1x1
#TODO: Add option to compress multi-line categorical headers (eg: headers with colspan>1) into concatenated-naming-style single row headers
#  EG: "Population" header spanning above sub-headers "Number" and "Percentage" produces two single-column headers of "Population - Number"
#  and "Population - Percentage". Delemiter can be configurable with a sensible default set.
