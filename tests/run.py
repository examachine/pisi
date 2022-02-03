#!/usr/bin/env python 
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Author:  Eray Ozkural <eray@pardus.org.tr>

import unittest
import sys
import os
import locale

sys.path.insert(0, '.')
sys.path.insert(0, '..')

import pisi.api
import pisi.context as ctx

def run_test_suite(testsuite):
    unittest.TextTestRunner(verbosity=2).run(testsuite)
    if ctx.initialized:
        pisi.api.finalize()

def run_all():

    print('** Running all tests')
    #testsuite = unittest.TestSuite()
    for root, dirs, files in os.walk('tests'):
        testsources = [x for x in files if x.endswith('tests.py')]
        for testsource in testsources:
            module = __import__(testsource[:len(testsource)-3])
            print('\n* Running tests in', testsource)
            run_test_suite(module.suite)

if __name__ == "__main__":

    locale.setlocale(locale.LC_ALL, '')
    args = sys.argv
    if len(args) > 1: # run modules given from the command line
        tests = sys.argv[1:]
        for test in tests:
            test += 'tests'
            module = __import__(test)
            print("* Running tests in", test)
            run_test_suite(module.suite)
    else: # run all tests
        run_all()
