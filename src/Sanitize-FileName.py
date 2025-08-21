#!/usr/bin/env python3
#coding: utf-8

#
# Sanitize-FileName.py (with stdin support)
#

import re, sys
import argparse

def sanitize_filename(filename, replacement='_'):
    """
    Replaces characters in a string that are unsuitable for Windows filenames.

    This function identifies and replaces characters that are invalid in Windows filenames,
    including control characters (ASCII 0-31) and the set of reserved characters:
    < > : " / \\ | ? *

    Args:
        filename (str): The filename string to sanitize.
        replacement (str, optional): The character to use for replacing invalid
                                     characters. Defaults to '_'.

    Returns:
        str: The sanitized filename string.
    """
    invalid_chars_pattern = r'[\x00-\x1f<>:"/\\|?*]'
    sanitized_name = re.sub(invalid_chars_pattern, replacement, filename)
    return sanitized_name

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sanitizes filenames by replacing invalid Windows characters.",
        epilog='Example: python %(prog)s "My*File:Name?.txt" -r "-"'
    )

    parser.add_argument(
        'filenames',
        metavar='FILENAME',
        type=str,
        nargs='*',  # make optional to allow stdin usage
        help='One or more filename strings to sanitize.'
    )

    parser.add_argument(
        '-r', '--replacement',
        type=str,
        default='_',
        help="The character to use for replacing invalid characters. Defaults to '_'."
    )

    args = parser.parse_args()

    # If no filenames are passed, read from stdin
    if not args.filenames:
        for line in sys.stdin:
            line = line.strip()
            if line:
                sanitized = sanitize_filename(line, args.replacement)
                print(sanitized)
    else:
        for filename in args.filenames:
            sanitized = sanitize_filename(filename, args.replacement)
            print(sanitized)

    sys.exit(0)
