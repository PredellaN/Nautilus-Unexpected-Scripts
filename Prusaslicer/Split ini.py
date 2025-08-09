#!/usr/bin/env python3

import argparse
import os
import sys
from configparser import ConfigParser

def split_ini_file(path):
    # Read without interpolation so % values are preserved
    cfg = ConfigParser(interpolation=None)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            cfg.read_file(f)
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr)
        return

    for section in cfg.sections():
        if ':' not in section:
            print(f"Skipping section without prefix:name format: [{section}]", file=sys.stderr)
            continue

        prefix, name = section.split(':', 1)
        prefix_dir = prefix.strip()
        fname = f"{name.strip()}.ini"
        out_dir = os.path.join(os.getcwd(), prefix_dir)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, fname)

        # Create a new ConfigParser to write only this section
        out_cfg = ConfigParser(interpolation=None)
        out_cfg.add_section(section)
        for key, val in cfg.items(section):
            out_cfg.set(section, key, val)

        with open(out_path, 'w', encoding='utf-8') as out_f:
            out_cfg.write(out_f)

        print(f"Wrote section [{section}] to {out_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Split PrusaSlicer .ini files into one-file-per-[prefix:name] sections."
    )
    parser.add_argument(
        'ini_files',
        metavar='INI',
        nargs='+',
        help='path to a .ini file to process'
    )
    args = parser.parse_args()

    for ini in args.ini_files:
        split_ini_file(ini)

if __name__ == '__main__':
    main()

