#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""
pypfi.datagenerator
====================

Installation::

    pip install arrow factory-boy

Usage::

    python datagenerator.py -t
    python datagenerator.py -c 20

Documentation:

* https://arrow.readthedocs.org/en/latest/
* https://factoryboy.readthedocs.org/en/latest/
* http://docs.scipy.org/doc/


"""
import datetime
import sys
import unittest

import arrow
import factory.fuzzy as fuzzy
import numpy as np
#import pandas as pd


class DateTimeGenerator(object):
    """
    Generate a series of sequential arrow.Arrow datetimes
    """
    def __init__(self, start_date=None, wake=6, sleep=22, payday=5):
        """
        Args:
            start_date (arrow.Arrow): starting date (if None, ``.now()``)
            wake (int): usual wake time
            sleep (int): usual sleep time
            payday (int): isoweekday (1-7, 7 is Sunday)
        """
        self.start_date = (
            start_date or arrow.now().replace(second=0, microsecond=0))
        self.wake = wake
        self.sleep = sleep
        self.payday = payday
        self.current_date = self.start_date
        self.count = 0

    def next(self):
        """
        Returns:
            arrow.Arrow: next datetime
        """
        self.count += 1
        if self.count:
            next_date = self.current_date.replace(hours=+2)
            self.current_date = next_date
        return self.current_date

    def shift(self, **kwargs):
        """
        Args:
            kwargs (dict): arguments for arrow.Arrow.replace
        """
        self.current_date = self.current_date.replace(**kwargs)
        return self.current_date


EXPENSE_PREFIXES = [
    "ABC",
    "XYZ",
    "example.com",
]

INCOME_PREFIXES = [
    "Paycheck",
]

def get_prefix(prefixes, date=None, amount=None):
    """
    Get a random prefix and append " " as the suffix
    Args:
        prefixes (list): list of string prefixes
        date (arrow.Arrow): (currently unused)
        amount (numeric): (currently unused)
    """
    n = np.random.randint(0, len(prefixes))
    return u"%s " % prefixes[n]


class DataGenerator(object):
    def __init__(self, output=None,
                    initial_balance=1001,
                    date_start=None,
                    date_end=None,
                    max_count=None,
                    count=0):
        self.output = sys.stdout if output is None else output
        self.initial_balance = initial_balance
        self.balance = self.initial_balance
        if date_start is None:
            date_start = arrow.now().replace(second=0, microsecond=0)
        self.date_start = date_start
        self.date_end = date_end
        self.max_count = max_count
        self.count = count
        self.dtg = DateTimeGenerator(self.date_start)
        self.current_date = self.dtg.next()

    def generate(self):
        """
        Generate a transactions CSV

        date,desc,amount,balance

        Args:
            output (file-like): output to ``.write()`` to
        Returns:
            file-like: output
        """
        yield (
            self.current_date.isoformat(sep=' '),
            u"Account Statement",
            0,
            self.balance)
        self.count += 1

        while True:
            debit_or_credit = np.random.randint(0, 100)
            if debit_or_credit < 95:
                # debit
                desc = fuzzy.FuzzyText(
                    length=10,
                    prefix=get_prefix(EXPENSE_PREFIXES, date=self.current_date)
                ).fuzz()
                amount = fuzzy.FuzzyDecimal(-100, -0.50).fuzz()
            else:
                # credit
                desc = fuzzy.FuzzyText(
                    length=4,
                    prefix=get_prefix(INCOME_PREFIXES, date=self.current_date)
                ).fuzz()
                amount = fuzzy.FuzzyDecimal(10, 2002).fuzz()

            self.balance += amount

            yield (
                self.current_date.isoformat(sep=' '),
                desc,
                str(amount),
                str(self.balance))
            self.count += 1

            if self.max_count and self.count >= self.max_count:
                break
            if self.date_end and self.current_date < self.date_end:
                break
            if self.balance <= 0:
                # overdraft
                # TODO: self.dtg.shift_to_payday()
                break
            self.current_date = self.dtg.next()


def datagenerator2do():
    """
    Recurring events:
        - [ ] paid on fridays
        - [ ] monthly bills
    Constraints:
        - [ ] sleep/wake
        - [ ] no overdrafts (if balance < 0, not until payday)

    """


class Test_datagenerator(unittest.TestCase):
    def test_010_get_prefix(self):
        PREFIXES = EXPENSE_PREFIXES
        output = get_prefix(PREFIXES)
        self.assertIn(output[:-1], PREFIXES)

    def test_100_DateTimeGenerator(self):
        dtg = DateTimeGenerator()
        self.assertTrue(dtg.start_date)
        self.assertTrue(dtg.wake)
        self.assertTrue(dtg.sleep)
        self.assertTrue(dtg.payday)
        self.assertTrue(dtg.current_date)
        self.assertEqual(dtg.count, 0)
        for n in range(10):
            output = dtg.next()
            self.assertTrue(output)
            self.assertTrue(isinstance(output, arrow.Arrow))
            print(n, output)

        current_date = dtg.current_date
        output = dtg.shift(hours=+2)
        expected = datetime.timedelta(0, 7200)
        self.assertEqual(output - current_date, expected)


    def test_200_DataGenerator(self):
        MAX_COUNT = 20
        dg = DataGenerator(max_count=MAX_COUNT)
        self.assertTrue(dg.output)
        self.assertTrue(dg.date_start)
        self.assertFalse(dg.date_end)
        self.assertTrue(dg.current_date)
        self.assertTrue(dg.initial_balance)
        self.assertTrue(dg.balance)
        self.assertEqual(dg.max_count, MAX_COUNT)
        self.assertEqual(dg.count, 0)

        output = dg.generate()
        self.assertTrue(hasattr(output, '__iter__'))
        tuples = list(output)
        self.assertLessEqual(dg.count, MAX_COUNT)

        for l in tuples:
            print(l)

        self.assertLessEqual(len(tuples), MAX_COUNT)
        if (dg.balance >= 0 and
            (not dg.date_end or dg.date_end and dg.current_date <= dg.date_end)):
            self.assertEqual(len(tuples), MAX_COUNT)
            self.assertEqual(dg.count, MAX_COUNT) # +1


def main(*args):
    import logging
    import optparse
    import sys

    prs = optparse.OptionParser(
        usage="%prog -o <output.csv>")

    prs.add_option('-o', '--output-file',
                   dest='output_file')

    prs.add_option('-c', '--count',
                   dest='count',
                   type=int,
                   default=None)

    prs.add_option('-v', '--verbose',
                    dest='verbose',
                    action='store_true',)
    prs.add_option('-q', '--quiet',
                    dest='quiet',
                    action='store_true',)
    prs.add_option('-t', '--test',
                    dest='run_tests',
                    action='store_true',)

    args = args and list(args) or sys.argv[1:]
    (opts, args) = prs.parse_args(args)

    if not opts.quiet:
        logging.basicConfig()

        if opts.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

    if opts.run_tests:
        import sys
        sys.argv = [sys.argv[0]] + args
        import unittest
        exit(unittest.main())

    kwargs = {
        'max_count': opts.count
    }

    if opts.output_file:
        with codecs.open(opts.output_file, 'w', encoding='utf-8') as f:
            for row in DataGenerator(output=f, **kwargs).generate():
                print(row, file=f)
    else:
        for row in DataGenerator(output=sys.stdout, **kwargs).generate():
            print(row)

    return 0


if __name__ == "__main__":
    sys.exit(main())
