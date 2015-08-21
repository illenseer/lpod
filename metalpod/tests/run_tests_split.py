#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""Description."""

from __future__ import absolute_import, division, print_function


import glob
import re
import subprocess


class Test(object):
    def __init__(self, filename):
        self.filename = filename
        self.strategy = ''
        self.given_as = []
        self.test_as = []
        with open(filename) as test:
            indata = test.readlines()
        for line in indata:
            opt = re.match(r'^% OPT: (pareto|incl|card)', line)
            if opt:
                self.strategy = opt.group(1)
            given_as = re.match(r'^% AS: (.*)$', line)
            if given_as:
                self.given_as.append(set(given_as.group(1).split(' ')))

    def run_tests(self):
        cmd = (
            'traod -b metalpod -g split -s {st} {fi} | '
            'clingo --pre | '
            'reify | '
            'clingo -Wno-atom-undefined meta.lp metaD.lp metaO.lp - 0 | '
            'cat -'
        ).format(st=self.strategy, fi=self.filename)
        output = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            shell=True
        ).split('\n')
        not_as = True
        for line in output:
            if not_as:
                test_as = re.match(r'.*Answer:', line)
                if test_as:
                    not_as = False
            else:
                j = set()
                for i in line.split(' '):
                    res = re.match(r'^(hold\(atom\(_.*|)$', i)
                    if not res:
                        j.add(i.strip())
                self.test_as.append(j)
                not_as = True

    def compare(self):
        equal = True
        if len(self.given_as) != len(self.test_as):
            equal = False
        else:
            for i in self.given_as:
                if not i in self.test_as:
                    equal = False
                    break
            for i in self.test_as:
                if not i in self.given_as:
                    equal = False
                    break
        if equal:
            result = '[PASS]'
            print('{}: {}'.format(self.filename, result))
            return 0
        else:
            result = '[ERROR]'
            print('{}: {}'.format(self.filename, result))
            return 1


def main():
    s = 0
    e = 0
    for filename in glob.glob('./tests/*.lp'):
        s += 1
        test = Test(filename)
        test.run_tests()
        e += test.compare()

    print('\n{} passed tests.'.format(s - e))
    print('{} failed tests.'.format(e))


if __name__ == '__main__':
    main()
