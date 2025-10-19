#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import re
import subprocess
import sys, os, io
import webbrowser
from pathlib import Path

## switch stdio by platform
if os.name == 'nt':
    ## on windows
    sys.stdin  = io.TextIOWrapper(sys.stdin.buffer,  encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
elif os.name == 'posix':
    ## on linux
    sys.stdin  = open('/dev/stdin',  'r', encoding='utf-8')

def is_utility_line(line: str) -> bool:
    """
    Checks if a line is a comment, empty, a tag, or a label.
    These lines should not be treated as executable links.
    
    Args:
        line: The line to check.
    
    Returns:
        True if the line is a utility line, False otherwise.
    """
    stripped_line = line.strip()
    if not stripped_line:
        return True  # Empty line
    if stripped_line.startswith('#'):
        return True  # Comment line
    if stripped_line.lower().startswith('tag:'):
        return True  # Tag line
    if stripped_line.startswith('@'):
        return True  # Label definition line
    return False

def show_labels(lines: list[str]):
    """
    Parses and prints all labels and their comments from the file content.
    
    Args:
        lines: A list of strings representing the lines of the file.
    """
    print(f"{'Label':<20} | {'Synopsis'}")
    print(f"{'-'*20}-+--{'-'*30}")
    
    # Regex to capture the label name and an optional comment after a colon.
    # e.g., @news : Major news sites
    label_pattern = re.compile(r'^@\s*([^\s:]+)\s*(?::\s*(.*))?$')
    
    for line in lines:
        match = label_pattern.match(line.strip())
        if match:
            label_name, comment = match.groups()
            print(f"{label_name:<20} | {comment or ''}")

def extract_links(lines: list[str], label: str | None = None) -> list[str]:
    """
    Extracts relevant links from the file content.
    If a label is provided, only links within that block are returned.
    
    Args:
        lines: A list of strings representing the lines of the file.
        label: The specific label block to extract links from.
    
    Returns:
        A list of cleaned, executable link strings.
    """
    links_to_process = []

    if label:
        # --- Label Mode ---
        # Find the first block where the label name contains the provided `label` text.
        in_label_block = False
        # Regex to capture just the name part of a label line, e.g. "news" from "@news : ..."
        label_name_pattern = re.compile(r'^@\s*([^\s:]+)')
        
        for line in lines:
            stripped_line = line.strip()
            
            is_label_line = stripped_line.startswith('@')

            if in_label_block:
                if is_label_line:
                    # We were in a matching block, and hit a new label, so we're done.
                    break
                # Process line inside the block
                if not is_utility_line(line):
                    links_to_process.append(stripped_line)
            elif is_label_line:
                # We are not in a block yet, check if this label is a partial match
                match = label_name_pattern.match(stripped_line)
                if match:
                    current_label_name = match.group(1)
                    # Use partial matching: 'in' operator checks for substring
                    if label in current_label_name:
                        in_label_block = True
                        # Now that we are in the block, we continue to the next line
    else:
        # --- Default Mode ---
        # No label was specified, so process the entire file content.
        for line in lines:
            if not is_utility_line(line):
                links_to_process.append(line.strip())
                
    return links_to_process

def main():
    """Main function to parse arguments and execute links."""
    parser = argparse.ArgumentParser(
        description="Invoke-Link Python Port: Open file or web links from a text file.",
        epilog="Example: python link_invoker.py my_links.txt news --all"
    )
    
    parser.add_argument(
        'filepath',
        type=str,
        help="Path to the link file."
    )
    parser.add_argument(
        'label',
        type=str,
        nargs='?', # Makes the argument optional
        default=None,
        help="Specifies a label block (e.g., 'news') to process."
    )
    parser.add_argument(
        '-s', '--show-labels',
        action='store_true',
        help="Displays all labels and their comments in the file."
    )
    parser.add_argument(
        '-a', '--all',
        action='store_true',
        help="Opens all links in the target block (or the entire file)."
    )
    parser.add_argument(
        '-d', '--doc',
        action='store_true',
        help="Opens the second and subsequent links (skips the first link)."
    )
    parser.add_argument(
        '-f', '--first',
        type=int,
        default=1,
        help="Opens the first 'n' links. Default is 1."
    )
    parser.add_argument(
        '--app',
        type=str,
        help="Specifies an application to open the links with."
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Outputs the commands that would be executed without running them."
    )

    args = parser.parse_args()

    link_file = Path(args.filepath)
    if not link_file.is_file():
        print(f"Error: File not found at '{args.filepath}'", file=sys.stderr)
        sys.exit(1)

    try:
        with open(link_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error: Could not read file '{args.filepath}': {e}", file=sys.stderr)
        sys.exit(1)

    if args.show_labels:
        show_labels(lines)
        return

    # 1. Extract links based on label (or lack thereof)
    clean_links = extract_links(lines, args.label)

    if not clean_links:
        print("No executable links found.", file=sys.stderr)
        return

    # 2. Filter the list of links based on user flags
    final_links = []
    if args.all:
        final_links = clean_links
    elif args.doc:
        final_links = clean_links[args.first:]
    else:
        final_links = clean_links[:args.first]

    # 3. Execute the final list of links
    for link in final_links:
        # Sanitize link by removing potential surrounding quotes
        link = link.strip('\'"')

        if args.dry_run:
            if args.app:
                print(f"Would run: {args.app} \"{link}\"")
            else:
                print(f"Would open: {link}")
            continue
        
        try:
            print(f"Opening: {link}")
            if args.app:
                subprocess.run([args.app, link], check=True)
            else:
                # webbrowser.open is a convenient, cross-platform way to open URLs and files
                webbrowser.open(link)
        except FileNotFoundError:
            print(f"Error: Application '{args.app}' not found.", file=sys.stderr)
        except Exception as e:
            print(f"Error opening '{link}': {e}", file=sys.stderr)

if __name__ == '__main__':
    main()

