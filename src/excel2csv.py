#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
excel2csv - A robust, pipeline-friendly Excel (.xlsx) to CSV converter.
Consolidates advanced data processing features with smart formatting.

Features integrated from legacy tool:
- Multiple input files concatenation
- Custom delimiters (CSV, TSV, SSV)
- Row skipping and duplicate removal
- Output to file or stdout
"""

import io
import sys
import os
import argparse
from datetime import datetime

# Attempt to load external dependencies.
try:
    import pandas as pd
except ImportError:
    sys.stderr.write("Dependency Error: 'pandas' is required.\n")
    sys.stderr.write("Install via: pip install pandas \n")
    sys.exit(1)

_version = "2.0.0"

# -----------------------------------------------------------------------------
# Platform-Specific I/O Configuration
# Ensures UTF-8 consistency across Windows (nt) and Unix-like (posix) systems.
# -----------------------------------------------------------------------------
if os.name == 'nt':
    sys.stdin  = io.TextIOWrapper(sys.stdin.buffer,  encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
elif os.name == 'posix':
    sys.stdin  = open('/dev/stdin',  'r', encoding='utf-8')


def raise_error(msg, *args):
    """Prints a clear error message to stderr and exits with status 1."""
    script_name = os.path.basename(__file__)
    print(f"Error[{script_name}]: {msg.format(*args)}", file=sys.stderr)
    sys.exit(1)


def get_args():
    """
    Defines command-line interface with detailed help, synopsis, and examples.
    """
    synopsis = r"""excel2csv - Advanced .xlsx converter with data processing.

    Synopsis:
        Converts one or more Excel files to a delimited text format (CSV/TSV).
        Supports smart date detection, data trimming, and duplicate removal.
    """

    examples = r"""EXAMPLES:
    # 1. Standard conversion of multiple files
    python excel2csv.py file1.xlsx file2.xlsx > combined.csv

    # 2. Output as TSV and skip the first 2 metadata rows
    python excel2csv.py data.xlsx --tsv --skip 2

    # 3. List sheets in a workbook
    python excel2csv.py data.xlsx --list-sheets

    # 4. Smart date formatting with custom delimiter and duplicate removal
    python excel2csv.py log.xlsx --date-format "%Y/%m/%d" --drop-duplicates --trim
    """

    parser = argparse.ArgumentParser(
        description=synopsis,
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Positional arguments: One or more files
    parser.add_argument("input_files", nargs="+", help="One or more .xlsx files to process.")
    
    # Selection & Metadata
    parser.add_argument("-s", "--sheet", default=0,
                        help="Sheet name or 0-based index (default: 0).")
    parser.add_argument("-l", "--list-sheets", action="store_true",
                        help="List all sheet names in the FIRST workbook and exit.")
    
    # Data Processing (Integrated from legacy)
    parser.add_argument("--skip", type=int, default=0,
                        help="Number of rows to skip at the start of each sheet.")
    parser.add_argument("--drop-duplicates", action="store_true",
                        help="Remove duplicate rows after merging all files.")
    parser.add_argument("-n", "--no-header", action="store_true",
                        help="Treat the first row as data, not as a header.")
    parser.add_argument("-t", "--trim", action="store_true",
                        help="Strip leading/trailing whitespace from all cells.")
    
    # Formatting
    parser.add_argument("-d", "--date-format", 
                        help="Explicit strftime format for dates (e.g., '%%Y-%%m-%%d').")
    
    # Output Control (Integrated from legacy)
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--csv", action="store_true", help="Output as CSV (default).")
    output_group.add_argument("--tsv", action="store_true", help="Output as TSV.")
    output_group.add_argument("--ssv", action="store_true", help="Output as Space-Separated Values.")
    
    parser.add_argument("-o", "--output", help="Output file path (default: stdout).")
    parser.add_argument("-V", "--version", action="version", version=_version)

    return parser.parse_args()


def format_dates_smartly(df, explicit_format=None):
    """
    Identifies datetime columns and applies formatting logic.
    Strips time if all values are 00:00:00, or applies user's format.
    """
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            if explicit_format:
                df[col] = df[col].dt.strftime(explicit_format)
            else:
                # Check if time component is zero for all rows
                times = df[col].dt.time.dropna().unique()
                if len(times) == 1 and list(times)[0] == datetime.min.time():
                    df[col] = df[col].dt.strftime('%Y-%m-%d')
                else:
                    df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
    return df


def main():
    args = get_args()
    
    # Mode: List Sheets (Process first file only)
    if args.list_sheets:
        target = args.input_files[0]
        if not os.path.exists(target): raise_error("File not found: {}", target)
        try:
            xl = pd.ExcelFile(target, engine='openpyxl')
            for name in xl.sheet_names: print(name)
            sys.exit(0)
        except Exception as e:
            raise_error("Could not read sheet names: {}", e)

    # Mode: Data Aggregation
    dfs = []
    sheet_id = args.sheet
    if isinstance(sheet_id, str) and sheet_id.isdigit():
        sheet_id = int(sheet_id)

    header_param = None if args.no_header else 0

    for fpath in args.input_files:
        if not os.path.exists(fpath):
            print(f"Warning: File not found, skipping: '{fpath}'", file=sys.stderr)
            continue
        
        try:
            temp_df = pd.read_excel(
                fpath,
                sheet_name=sheet_id,
                header=header_param,
                skiprows=args.skip,
                engine='openpyxl'
            )
            dfs.append(temp_df)
        except Exception as e:
            print(f"Warning: Failed to read '{fpath}': {e}", file=sys.stderr)

    if not dfs:
        raise_error("No valid data loaded from the provided files.")

    # Merge all DataFrames
    # ignore_index=True is safer when concatenating disparate files without a shared index
    combined_df = pd.concat(dfs, ignore_index=True)

    # Post-processing: Remove duplicates
    if args.drop_duplicates:
        combined_df = combined_df.drop_duplicates().reset_index(drop=True)

    # Post-processing: Trim whitespace
    if args.trim:
        combined_df = combined_df.map(lambda x: x.strip() if isinstance(x, str) else x)

    # Post-processing: Date formatting
    combined_df = format_dates_smartly(combined_df, args.date_format)

    # Determine output stream and separator
    out_stream = args.output if args.output else sys.stdout
    separator = ","
    if args.tsv: separator = "\t"
    elif args.ssv: separator = " "

    try:
        combined_df.to_csv(
            out_stream,
            sep=separator,
            index=False,
            header=(not args.no_header),
            lineterminator='\n'
        )
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)


if __name__ == "__main__":
    main()