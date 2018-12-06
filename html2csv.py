#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Richard's html2csv converter
#rbarnes@umn.edu
#


from bs4 import BeautifulSoup
import os
import sys
import csv
import argparse

parser = argparse.ArgumentParser(description='Reads in an HTML and attempts to convert all tables into CSV files.')
parser.add_argument('--delimiter', '-d', action='store', default=',',help="Character with which to separate CSV columns")
parser.add_argument('--quotechar', '-q', action='store', default='"',help="Character within which to nest CSV text")
parser.add_argument('--ignoreempty', '-e', action='store_true', help="Ignore empty tables. Helps reduce output on table-layout html pages.")
parser.add_argument('filename',nargs="?",help="HTML file from which to extract tables")
args = parser.parse_args()


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
  tableisempty = True
  print("Processing Table #%d" % (tablecount))
  outfilename = sys.argv[1]+str(tablecount)+'.csv'
  with open(outfilename, 'w', newline='') as csvfile:
    fout = csv.writer(csvfile, delimiter=args.delimiter, quotechar=args.quotechar, quoting=csv.QUOTE_MINIMAL)
    rowcount = 1
    #Removes nested tables. for handling the sins of 1990's web pages.
    [t.extract() for t in table.findAll("table")]
    #This would grab all TRs regardless of depth without the above line removing nested tables
    for row in table.findAll('tr'):
      print(f"Processing row number {rowcount}")
      rowcount += 1
      cols = row.findAll(['td','th'])
      print(f"Found {len(cols)} columns.")
      if cols:
        cols = [str(x.text).strip() for x in cols]
        if (len(cols) > 1) or len(cols[0]) > 0 :
          tableisempty = False
        if not tableisempty:
          fout.writerow(cols)
  if args.ignoreempty and tableisempty:
    print(f"Removing {outfilename} because it is empty and `-e` flag was activated.")
    os.remove(outfilename)
