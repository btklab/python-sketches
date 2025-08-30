#!/usr/bin/env python3
#coding: utf-8

#
# Get-Dataset - A command-line tool to fetch datasets from the Seaborn library.
#

import argparse
import sys, io, os
import seaborn as sns
import pandas as pd # Import pandas to work with DataFrames

## switch stdio by platform
if os.name == 'nt':
    ## on windows
    sys.stdin  = io.TextIOWrapper(sys.stdin.buffer,  encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
elif os.name == 'posix':
    ## on linux
    sys.stdin  = open('/dev/stdin',  'r', encoding='utf-8')

def main():
    """
    Main function to parse arguments and trigger corresponding actions.
    This acts as the central controller for the script.
    """
    # --- Argument Parser Setup ---
    # We use argparse to create a user-friendly command-line interface.
    # This makes the script's options discoverable and easy to use.
    help_desc_msg = """Get-Dataset - Fetch and display datasets from the Seaborn library.
    
If no arguments are given, it lists all available datasets.
    """
    
    help_epi_msg = r"""EXAMPLES:
    
    # List available datasets (simple, fast)
    python Get-Dataset.py

    # List available datasets (detail, slow)
    python Get-Dataset.py --detail

    # Output iris dataset as csv
    python Get-Dataset.py -n iris
    python Get-Dataset.py --name iris

    # Output iris dataset with specified delimiter
    python Get-Dataset.py -n iris -d ';'
    """
    
    parser = argparse.ArgumentParser(description=help_desc_msg,
                    epilog=help_epi_msg,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    
    # A mutually exclusive group ensures that the user can perform only one
    # of the main actions at a time (e.g., either list datasets or get one).
    action_group = parser.add_mutually_exclusive_group()

    # --- Define Command-Line Arguments ---
    # Argument to list all available dataset names.
    # `action="store_true"` makes it a simple flag (it's either present or not).
    action_group.add_argument(
        "-l", "--list",
        action="store_true",
        help="List all available dataset names with details (default action)."
    )

    action_group.add_argument(
        "--detail",
        action="store_true",
        help="List all available dataset names with details (default action)."
    )
    # Argument to specify the name of the dataset to be fetched.
    # `metavar` provides a placeholder name in the help message for clarity.
    action_group.add_argument(
        "-n", "--name",
        type=str,
        metavar="DATASET_NAME",
        help="Specify the name of the dataset to output as CSV."
    )

    # Argument to specify a custom delimiter for the output.
    # This is independent of the main action (list vs. get name).
    parser.add_argument(
        "-d", "--delimiter",
        type=str,
        default=",",
        metavar="CHAR",
        help="Specify the delimiter for the CSV output. Default is a comma."
    )

    # Parse the arguments provided by the user.
    args = parser.parse_args()

    # --- Execute Logic Based on Arguments ---
    # Direct the flow of the program based on the parsed arguments.
    if args.name:
        # If a specific dataset name is provided, output it as CSV
        # using the specified or default delimiter.
        output_dataset_as_csv(args.name, args.delimiter)
    else:
        # Default behavior: If --name is not specified, list the datasets.
        # This covers both the --list flag and the case with no arguments.
        list_available_datasets(args.detail)

def list_available_datasets(detail=False):
    """
    Fetches and prints the list of all available dataset names from Seaborn,
    including details like number of rows, columns, and data types.
    """
    try:
        # Retrieve the list of dataset names from the Seaborn library.
        dataset_names = sns.get_dataset_names()
        if not detail:
            for name in dataset_names:
                print("- " + name )
        else:
            print("Available datasets:")
            print("-" * 70) # Separator for better readability
            print(f"{'Dataset Name':<20} | {'Rows':<8} | {'Cols':<8} | {'Data Types':<25}")
            print("-" * 70)

            # Iterate through each dataset name to load and extract details
            for name in dataset_names:
                try:
                    # Load the dataset. This might take some time for larger datasets.
                    df = sns.load_dataset(name)
                    rows = df.shape[0]
                    cols = df.shape[1]
                    # Get unique data types present in the DataFrame's columns
                    data_types = ", ".join(sorted(df.dtypes.astype(str).unique()))
                    # Truncate data_types if too long to fit the column
                    if len(data_types) > 25:
                        data_types = data_types[:22] + "..."

                    print(f"{name:<20} | {rows:<8} | {cols:<8} | {data_types:<25}")
                except Exception as e:
                    # If a specific dataset fails to load, print an error for that dataset
                    # but continue with the rest.
                    print(f"{name:<20} | {'Error':<8} | {'Error':<8} | {f'Could not load: {e}':<25}")
            print("-" * 70)

    except Exception as e:
        # If fetching the initial list of names fails (e.g., network issues),
        # inform the user via standard error and exit.
        print(f"Error: Could not retrieve the dataset list. Details: {e}", file=sys.stderr)
        sys.exit(1) # Exit with a non-zero status code to indicate failure.

def output_dataset_as_csv(dataset_name, delimiter):
    """
    Loads a specified dataset and prints it to standard output in CSV format
    without a trailing newline, using a custom delimiter.

    Args:
        dataset_name (str): The name of the dataset to load.
        delimiter (str): The character to use for separating values.
    """
    try:
        # Attempt to load the dataset using the provided name.
        # This function might raise a ValueError if the dataset is not found
        # or other exceptions for network-related issues.
        #print(f"Loading dataset '{dataset_name}'...", file=sys.stderr)
        df = sns.load_dataset(dataset_name)
        #print("Load complete. Outputting CSV data.", file=sys.stderr)

        # To prevent extra blank lines at the end of the output,
        # we first write the CSV to an in-memory buffer.
        buffer = io.StringIO()

        # Write the DataFrame to the buffer using the specified delimiter.
        # `index=False` is crucial to prevent writing the DataFrame's row numbers.
        df.to_csv(buffer, index=False, lineterminator='\n', sep=delimiter)

        # Get the CSV content from the buffer and remove any trailing newline characters.
        csv_text = buffer.getvalue().rstrip('\r\n')

        # Write the cleaned string directly to standard output.
        # Using sys.stdout.write() avoids the extra newline that print() would add.
        sys.stdout.write(csv_text)

    except ValueError:
        # This is a specific, expected error when the dataset name is invalid.
        # We provide a helpful message to guide the user.
        print(f"Error: Dataset '{dataset_name}' not found.", file=sys.stderr)
        print("Use the --list option to see all available dataset names.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Catch any other unexpected exceptions (e.g., network problems)
        # to prevent the script from crashing without a clear message.
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

# --- Script Entry Point ---
# This standard Python construct ensures that the `main()` function is called
# only when the script is executed directly (e.g., `python Get-Dataset.py`).
# It prevents the code from running if the script is imported as a module.
if __name__ == "__main__":
    main()
    sys.exit(0)

