#! /usr/bin/env python

from __future__ import print_function
import sys
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
            if key in i2f and not i2f[key]:
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
                m2 = re.search('^calls=', record[i - 1])
                if not m2:
                    if rid in i2c:
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
                m2 = re.search(' (\d+)$', record[i + 1])
                if m2:
                    if rid in i2c:
                        i2c[rid] += int(m2.group(1))
                    else:
                        i2c[rid] = int(m2.group(1))

    return i2c


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        'input', nargs='?', default=sys.stdin,
        metavar='input_file', type=argparse.FileType('r'),
        help='path to the input file (use stdin if omitted)')

    parser.add_argument(
        'output', nargs='?', default=sys.stdout,
        metavar='output_file', type=argparse.FileType('w'),
        help='path to the output file (use stdout if omitted)')

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

    lst = []
    for i in i2f:
        sc = i2sc[i]
        if i not in  i2oc:
            i2oc[i] = 0
        oc = i2oc[i]
        # print(i, sc, oc, sc + oc, i2f[i])
        line = '{0}, {1}, {2}, {3}, {4}\n'.format(i, sc, oc, sc + oc, i2f[i])
        lst.append([sc,oc, i2f[i]])
        #args.output.write(line)

    lst.sort(key=lambda x: x[0], reverse=True)
    total_self = sum( [ x[0] for x in lst ] ) * 1.0
    total_other = sum( [ x[1] for x in lst ] ) * 1.0
    
    for x in lst[0:20]:
        s = x[2]
        s = re.sub('[(].*','',s);        
        args.output.write('{0:5.2f}   (+{1:5.2f}) {2:20} {3}\n'.format(x[0]/total_self*100, x[1]/total_other*100, x[0] , s ))
                   

if __name__ == "__main__":
    main()
