#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yfinance as yf
import argparse
import pandas as pd
from pprint import pprint
import sys, io, os
import json

## switch stdio by platform
if os.name == 'nt':
    ## on windows
    sys.stdin  = io.TextIOWrapper(sys.stdin.buffer,  encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
elif os.name == 'posix':
    ## on linux
    sys.stdin  = open('/dev/stdin',  'r', encoding='utf-8')

def get_stock_data(ticker_symbol, args):
    """
    Fetches and displays or saves stock data for a given ticker symbol.

    Args:
        ticker_symbol (str): The company's ticker symbol.
        args (argparse.Namespace): An object containing command-line arguments.
    """
    # Create a Ticker object from yfinance
    try:
        ticker = yf.Ticker(ticker_symbol)
        if not ticker.info or 'symbol' not in ticker.info:
            print(f"Error: Could not find information for ticker symbol '{ticker_symbol}'. It may be invalid.", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred while processing ticker '{ticker_symbol}'.", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)

    if args.debug:
        print(f"--- Processing data for {ticker.info.get('longName', ticker_symbol)} ({ticker_symbol}) ---")
    if args.outdir:
        print(f"Output files will be saved in the '{args.outdir}/' directory.")

    # If no specific options are provided, fetch all information.
    no_options_specified = not any([
        args.info, args.history, args.financials, args.balance_sheet,
        args.cashflow, args.actions, args.recommendations, args.news
    ])
    if args.all or no_options_specified:
        fetch_all = True
    else:
        fetch_all = False

    # Helper function to handle output
    def handle_output(data, data_name, unit=""):
        if data is None or (isinstance(data, (pd.DataFrame, pd.Series)) and data.empty) or (isinstance(data, (dict, list)) and not data):
            if args.output == 'text' or args.outdir:
                print(f"No data available for {data_name}.")
            return

        # Handle file output if outdir is specified
        if args.outdir and args.output in ['csv', 'json']:
            if not os.path.exists(args.outdir):
                os.makedirs(args.outdir)
            filename = os.path.join(args.outdir, f"{data_name}.{args.output}")
            print(f"Saving {data_name} to {filename}...")
            try:
                if args.output == 'csv':
                    if isinstance(data, dict):
                        pd.DataFrame.from_dict(data, orient='index', columns=['Value']).to_csv(filename)
                    elif isinstance(data, list):
                         pd.DataFrame(data).to_csv(filename, index=False)
                    else: # DataFrame
                        data.to_csv(filename)
                elif args.output == 'json':
                    with open(filename, 'w', encoding='utf-8') as f:
                        if isinstance(data, (pd.DataFrame, pd.Series)):
                            data.to_json(f, orient='split', indent=4)
                        else: # dict or list
                            json.dump(data, f, ensure_ascii=False, indent=4)
            except Exception as e:
                 print(f"Could not save file {filename}: {e}", file=sys.stderr)
            return

        # Handle standard output for all other cases
        if args.output == 'text':
            print(f"\n--- {data_name} {unit} ---")
            if isinstance(data, (dict)):
                 pprint(data)
            else:
                 print(data)
        elif args.output == 'csv':
            if args.debug:
                print(f"\n--- START {data_name}.csv {unit} ---")
            if isinstance(data, dict):
                print(pd.DataFrame.from_dict(data, orient='index', columns=['Value']).to_csv(sys.stdout))
            elif isinstance(data, list):
                 print(pd.DataFrame(data).to_csv(sys.stdout, index=False))
            else: # DataFrame
                print(data.to_csv(sys.stdout))
            if args.debug:
                print(f"--- END {data_name}.csv ---")
        elif args.output == 'json':
            if args.debug:
                print(f"\n--- START {data_name}.json {unit} ---")
            if isinstance(data, (pd.DataFrame, pd.Series)):
                print(data.to_json(orient='split', indent=4))
            else: # dict or list
                print(json.dumps(data, ensure_ascii=False, indent=4))
            if args.debug:
                print(f"--- END {data_name}.json ---")

    # --- Fetch and process data for each section ---
    financial_unit_string = ""
    if args.divisor != 1:
        financial_unit_string = f"(values divided by {int(args.divisor):,})"

    if fetch_all or args.info:
        handle_output(ticker.info, "info")

    if fetch_all or args.history:
        handle_output(ticker.history(period="1mo"), "history")

    if fetch_all or args.financials:
        data = ticker.financials
        if not data.empty and args.divisor != 1:
            data = data / args.divisor
        handle_output(data, "financials", unit=financial_unit_string)

    if fetch_all or args.balance_sheet:
        data = ticker.balance_sheet
        if not data.empty and args.divisor != 1:
            data = data / args.divisor
        handle_output(data, "balance_sheet", unit=financial_unit_string)

    if fetch_all or args.cashflow:
        data = ticker.cashflow
        if not data.empty and args.divisor != 1:
            data = data / args.divisor
        handle_output(data, "cashflow", unit=financial_unit_string)

    if fetch_all or args.actions:
        handle_output(ticker.actions, "actions")

    if fetch_all or args.recommendations:
        handle_output(ticker.recommendations, "recommendations")

    if fetch_all or args.news:
        #handle_output(ticker.news, "news")
        pass


def main():
    """
    Parses command-line arguments and calls the main function.
    """
    parser = argparse.ArgumentParser(
        description=(
            "A script to fetch company financial data using yfinance.\n"
            "If no options are specified, all available information will be fetched.\n"
            "\n"
            "    references:\n"
            "        https://ranaroussi.github.io/yfinance/\n"
            "        https://github.com/ranaroussi/yfinance\n"
            "\n"
            "    example:\n"
            "        python Get-YFinance.py AAPL -div 1000000000 -f -o csv\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("ticker", nargs='?', default=None, type=str, help="Company ticker symbol (e.g., AAPL, 7203.T)")

    # Options to select which information to retrieve
    parser.add_argument("-info", "--info", action="store_true", help="Get company information")
    parser.add_argument("-hist", "--history", action="store_true", help="Get price history (last 1 month)")
    parser.add_argument("-f", "--financials", action="store_true", help="Get income statement")
    parser.add_argument("-balance", "--balance-sheet", action="store_true", help="Get balance sheet")
    parser.add_argument("-cash", "--cashflow", action="store_true", help="Get cash flow statement")
    parser.add_argument("-act", "--actions", action="store_true", help="Get history of dividends and stock splits")
    parser.add_argument("-rec", "--recommendations", action="store_true", help="Get analyst recommendations")
    parser.add_argument("-news", "--news", action="store_true", help="Get related news")
    parser.add_argument("-all", "--all", action="store_true", help="Get all available information (default)")
    parser.add_argument("--debug", action="store_true", help="debug")

    # Option to choose output format
    parser.add_argument(
        "-o", "--output",
        choices=['text', 'csv', 'json'],
        default='text',
        help="Output format."
    )
    # Option to specify output directory
    parser.add_argument(
        "-dir", "--outdir",
        type=str,
        default=None,
        help="Directory to save output files. If not provided for csv/json, output is sent to stdout."
    )
    # Option to specify a divisor for financial data
    parser.add_argument(
        "-div", "--divisor",
        type=float,
        default=1.0,
        help="Divisor for financial figures to make them readable (e.g., 1000 for thousands). Default: 1. Set to 1 to disable."
    )

    args = parser.parse_args()

    # If no ticker is provided, print the help message and exit.
    if args.ticker is None:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Set display options for Pandas DataFrame for text output
    if args.output == 'text':
        pd.set_option('display.max_columns', None) # Display all columns
        pd.set_option('display.width', 150)       # Increase display width
        # Adjust float format based on divisor
        if args.divisor > 1:
             pd.set_option('display.float_format', '{:,.2f}'.format)
        else:
             pd.set_option('display.float_format', '{:,.0f}'.format)


    get_stock_data(args.ticker, args)

if __name__ == "__main__":
    main()
    sys.exit(0)
