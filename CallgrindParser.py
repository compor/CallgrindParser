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
        m = re.search('^fn=\((\d+)\)\s*(.*)?', line)
        if m:
            i2f[int(m.group(1))] = m.group(2)

    for line in profile:
        m = re.search('^cfn=\((\d+)\)\s*(.*)?', line)
        if m:
            key = int(m.group(1))
            if i2f.has_key(key) and not i2f[key]:
                i2f[key] = m.group(2)

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
            m = re.search('^fn=\((\d+)\)\s*(.*)?', line)
            if m:
                rid = m.group(1)
                shouldDiscard = False
                break

        if shouldDiscard:
            records.remove(r)
        else:
            i2r[int(rid)] = r

    return i2r


def calc_self_cost(i2r):
    i2c = {}

    for rid, record in i2r.items():
        for i in range(len(record)):
            m1 = re.search('^[-+*]?\d+.*\s(\d+)$', record[i])
            if m1:
                m2 = re.search('^calls=', record[i-1])
                if not m2:
                    if i2c.has_key(rid):
                        i2c[rid] += int(m1.group(1))
                    else:
                        i2c[rid] = int(m1.group(1))

    return i2c


def calc_other_cost(i2r):
    i2c = {}

    for rid, record in i2r.items():
        for i in range(len(record)):
            m1 = re.search('^calls=', record[i])
            if m1:
                m2 = re.search(' (\d+)$', record[i+1])
                if m2:
                    if i2c.has_key(rid):
                        i2c[rid] += int(m2.group(1))
                    else:
                        i2c[rid] = int(m2.group(1))

    return i2c


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

    # for r in i2r:
        # print(r, i2r[r])

    i2sc = calc_self_cost(i2r)

    # for i in i2sc:
        # print(i, i2sc[i])

    i2oc = calc_other_cost(i2r)

    # for i in i2oc:
        # print(i, i2oc[i])

    for i in i2f:
        sc = i2sc[i]
        if not i2oc.has_key(i):
            i2oc[i] = 0
        oc = i2oc[i]
        print(i, sc, oc, sc + oc, i2f[i])



if __name__ == "__main__":
    main()
