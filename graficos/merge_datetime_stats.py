#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, glob, sys
import argparse
import pandas as pd


script_realpath = os.path.realpath(__file__)
script_dir = os.path.dirname(script_realpath)

# print(script_realpath)
# print(script_dir)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Parser command-line options
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--csv-dir", dest='csv_dir', help="Diretório com os arquivos CSV.", required=True)
parser.add_argument("-o", "--output-file", dest='output_file', help="Nome do arquivo CSV gerado.", required=True)

if len(sys.argv)==1:
     parser.print_help(sys.stderr)
     print("\n")
     exit(1)
args = parser.parse_args()


CSV_DIR = os.path.realpath(args.csv_dir)
OUTFILE = os.path.join(CSV_DIR, args.output_file+".stats_merged.csv")

## CSV merged dataframe
CSV_DF = pd.DataFrame()

# Enter csv dir
os.chdir(CSV_DIR)
cwd = os.getcwd()


# Merge CSVs
tool_filter="*.stats.csv"
for csv in glob.glob(tool_filter):
    print(f"Merging CSV: {csv}...")
    df = pd.read_csv(csv)
    CSV_DF = pd.concat([CSV_DF, df]).groupby(['Datetime']).sum().reset_index()

# Leave csv dir
os.chdir(script_dir)

# Save dataset file
CSV_DF.to_csv(OUTFILE, index=False)

print ("")
print(f"{bcolors.BOLD}************************************************************************************************{bcolors.ENDC}")
print(f"{'CSV_DIR:':>16} {CSV_DIR}")
print ("")
print(f"{bcolors.OKGREEN} MERGED CSV: {bcolors.HEADER+bcolors.BOLD}{os.path.realpath(OUTFILE)}{bcolors.ENDC}")
print(f"{bcolors.BOLD}************************************************************************************************{bcolors.ENDC}")
print ("")
