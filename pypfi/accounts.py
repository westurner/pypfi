#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""
pypfi.accounts
===============

"""


class Account(object):
    def __init__(self,
                 name=None,
                 subaccounts=None):
        self.name = name
        self.subaccounts = subaccounts or []


class ExpenseAccount(Account):
    pass


class IncomeAccount(Account):
    pass


FREQUENCIES = [
    'yearly',
    'monthly',
    'weekly',
    'daily',
    'onetime',
]

class Expense(object):
    def __init__(self,
                 name=None,
                 freq=None,
                 amount=None,
                 payee=None):
        self.name = name
        if freq not in FREQUENCIES:
            raise KeyError
        self.freq = freq
        self.amount = amount
        self.payee = payee


class Income(object):
    def __init__(self,
                 name=None,
                 freq=None,
                 amount=None,
                 source=None):
        self.name = name
        if freq not in FREQUENCIES:
            raise KeyError
        self.freq = freq
        self.amount = amount
        self.source = source


import unittest
class Test_Accounts(unittest.TestCase):
    def test_011_Account(self):
        NAME = 'test_account'
        a = Account(NAME)
        self.assertTrue(isinstance(a, Account))
        self.assertEqual(a.name, NAME)
        self.assertEqual(a.subaccounts, [])

    def test_021_IncomeAccount(self):
        NAME = 'test_income_account'
        a = IncomeAccount(NAME)
        self.assertTrue(isinstance(a, Account))
        self.assertTrue(isinstance(a, IncomeAccount))
        self.assertEqual(a.name, NAME)
        self.assertEqual(a.subaccounts, [])

    def test_031_ExpenseAccount(self):
        NAME = 'test_expense_account'
        a = ExpenseAccount(NAME)
        self.assertTrue(isinstance(a, Account))
        self.assertTrue(isinstance(a, ExpenseAccount))
        self.assertEqual(a.name, NAME)
        self.assertEqual(a.subaccounts, [])

    def test_041_Expense(self):
        NAME = 'test_expense'
        FREQ = 'monthly'
        AMOUNT = 100
        PAYEE = 'test_payee'
        e = Expense(NAME, FREQ, AMOUNT, PAYEE)
        self.assertTrue(isinstance(e, Expense))
        self.assertEqual(e.name, NAME)
        self.assertEqual(e.freq, FREQ)
        self.assertEqual(e.amount, AMOUNT)
        self.assertEqual(e.payee, PAYEE)

    def test_051_Income(self):
        NAME = 'test_expense'
        FREQ = 'monthly'
        AMOUNT = 100
        SOURCE = 'test_source'
        i = Income(NAME, FREQ, AMOUNT, SOURCE)
        self.assertTrue(isinstance(i, Income))
        self.assertEqual(i.name, NAME)
        self.assertEqual(i.freq, FREQ)
        self.assertEqual(i.amount, AMOUNT)
        self.assertEqual(i.source, SOURCE)


def main(*args):
    import logging
    import optparse
    import sys

    prs = optparse.OptionParser(usage="%prog -t")

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
    (opts, args) = prs.parse_args()

    if not opts.quiet:
        logging.basicConfig()

        if opts.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

    if opts.run_tests:
        import sys
        sys.argv = [sys.argv[0]] + args
        import unittest
        exit(unittest.main())

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

