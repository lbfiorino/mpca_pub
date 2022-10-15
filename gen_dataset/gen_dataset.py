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
parser.add_argument("-t", "--tool", dest='tool', choices=['argus', 'cfm'], help="Ferramenta utilizada para gerar o csv.", required=True)
parser.add_argument("-n", "--dataset-name", dest='dataset_name', choices=['train', 'test'], help="Nome do dataset gerado.", required=True)

if len(sys.argv)==1:
     parser.print_help(sys.stderr)
     print("\n")
     exit(1)
args = parser.parse_args()


if args.tool.lower() == "argus":
    SORT_COLUMN = "StartTime"
elif args.tool.lower() == "cfm":
    SORT_COLUMN = "Flow Start Time"

# print(f"CSV_DIR: {args.csv_dir}")   
# print(f"TOOL: {args.tool}")
# print(f"COLUMN TO SORT: {SORT_COLUMN}")

CSV_DIR = os.path.realpath(args.csv_dir)
OUTFILE = os.path.join(CSV_DIR, "dataset_"+args.dataset_name+"_"+args.tool+".csv")

print(f"\n[INFO] {bcolors.BOLD}Generating {args.dataset_name} dataset ({args.tool})...{bcolors.ENDC}\n")

## Create dataset 
DATASET_DF = pd.DataFrame()

# Enter csv dir
os.chdir(CSV_DIR)
cwd = os.getcwd()

# Delete old dataset file if exists
if os.path.exists(OUTFILE):
    os.remove(OUTFILE)

# Merge and sort CSVs
tool_filter="*"+args.tool+".csv"
for csv in glob.glob(tool_filter):
    print(f"Merging CSV: {csv}...")
    df = pd.read_csv(csv, dtype=str)
    DATASET_DF = pd.concat([DATASET_DF, df])

DATASET_DF.sort_values(by=SORT_COLUMN, inplace=True)

# Leave csv dir
os.chdir(script_dir)

# Save dataset file
print("\nSaving dataset file....")
DATASET_DF.to_csv(OUTFILE, index=False)

print ("")
print(f"{bcolors.BOLD}************************************************************************************************{bcolors.ENDC}")
print(f"{'TOOL:':>16} {args.tool}")
print(f"{'CSV_DIR:':>16} {CSV_DIR}")
print(f"{'COLUMN TO SORT:':>16} {SORT_COLUMN}")
print ("")
print(f"{bcolors.OKGREEN}{args.dataset_name.upper()+' DATASET FILE:'} {bcolors.HEADER+bcolors.BOLD}{os.path.realpath(OUTFILE)}{bcolors.ENDC}")
print(f"{bcolors.BOLD}************************************************************************************************{bcolors.ENDC}")
print ("")

