#! /usr/bin/env python

from __future__ import print_function
import argparse
import re

def is_empty(line):
    m = re.search('^\s*$', line)
    if m:
        return True

    return False


def id2fname(profile):
    i2f = {}

    for line in profile:
        m = re.search('^fn=\((\d+)\) (.*)', line)
        if m:
            i2f[m.group(1)] = m.group(2)

    return i2f


def id2record(profile):
    i2r = {}
    records = []
    current_record = []

    for line in profile:
        if not is_empty(line):
            current_record.append(line)
        else:
            if len(current_record) == 0:
                continue
            else:
                records.append(current_record)
                current_record = []

    for r in records:
        shouldDiscard = True
        rid = 0

        for line in r:
            m = re.search('^fn=\((\d+)\) (.*)', line)
            if m:
                rid = m.group(1)
                shouldDiscard = False
                break

        if shouldDiscard:
            records.remove(r)
        else:
            i2r[rid] = r

    return i2r


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "input", nargs="?", default="-",
        metavar="INPUT_FILE", type=argparse.FileType("r"),
        help="path to the input file (read from stdin if omitted)")

    parser.add_argument(
        "output", nargs="?", default="-",
        metavar="OUTPUT_FILE", type=argparse.FileType("w"),
        help="path to the output file (write to stdout if omitted)")

    args = parser.parse_args()
    profile = args.input.readlines()

    i2f = id2fname(profile)

    # for i in i2f:
        # print(i, i2f[i])

    i2r = id2record(profile)

    for r in i2r:
        print(r, i2r[r][0])



if __name__ == "__main__":
    main()
