#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""
pypfi.budget
=============

"""
import sys

class Budget(object):
    monthly_expense_attrs = (
        'monthly_electric',
        'monthly_garbage',
        'monthly_gas',
        'monthly_water',
        'monthly_internet',
        'monthly_phone',
        'monthly_tv',
        'monthly_learning_books',
        'monthly_learning_tuition',
        'monthly_recreation',
        'monthly_entertainment',
        'monthly_groceries',
        'monthly_restaurants',
        'monthly_clothing',
        'monthly_auto_fuel',
        'monthly_auto_maint',
        'monthly_auto_insurance',
        'monthly_health_insurance',
        'monthly_health_prescriptions',
        'monthly_home_rent',
        'monthly_home_mortgage',
        'monthly_pet_food',
        'monthly_pet_health',
    )
    monthly_income_attrs = (
        'monthly_salary',
    )
    def __init__(self,
                 monthly_salary=None,

                 monthly_electric=None,
                 monthly_garbage=None,
                 monthly_gas=None,
                 monthly_water=None,
                 monthly_internet=None,
                 monthly_phone=None,
                 monthly_tv=None,
                 monthly_learning_books=None,
                 monthly_learning_tuition=None,
                 monthly_recreation=None,
                 monthly_entertainment=None,
                 monthly_groceries=None,
                 monthly_restaurants=None,
                 monthly_clothing=None,
                 monthly_auto_fuel=None,
                 monthly_auto_maint=None,
                 monthly_auto_insurance=None,
                 monthly_health_insurance=None,
                 monthly_health_prescriptions=None,
                 monthly_home_rent=None,
                 monthly_home_mortgage=None,
                 monthly_home_insurance=None,
                 monthly_pet_food=None,
                 monthly_pet_health=None,
                 ):
        self.monthly_salary = monthly_salary

        self.monthly_electric = monthly_electric
        self.monthly_garbage = monthly_garbage
        self.monthly_gas = monthly_gas
        self.monthly_water = monthly_water
        self.monthly_internet = monthly_internet
        self.monthly_phone = monthly_phone
        self.monthly_tv = monthly_tv
        self.monthly_learning_books = monthly_learning_books
        self.monthly_learning_tuition = monthly_learning_tuition
        self.monthly_recreation = monthly_recreation
        self.monthly_entertainment = monthly_entertainment
        self.monthly_groceries = monthly_groceries
        self.monthly_restaurants = monthly_restaurants
        self.monthly_clothing = monthly_clothing
        self.monthly_auto_fuel = monthly_auto_fuel
        self.monthly_auto_maint = monthly_auto_maint
        self.monthly_auto_insurance = monthly_auto_insurance
        self.monthly_health_insurance = monthly_health_insurance
        self.monthly_health_prescriptions = monthly_health_prescriptions
        self.monthly_home_rent = monthly_home_rent
        self.monthly_home_mortgage = monthly_home_mortgage
        self.monthly_home_insurance = monthly_home_insurance
        self.monthly_pet_food = monthly_pet_food
        self.monthly_pet_health = monthly_pet_health

    @property
    def total_monthly_income(self):
        return sum(
            getattr(self, attr) or 0 for attr in self.monthly_income_attrs)

    @property
    def total_monthly_expenses(self):
        return sum(
            getattr(self, attr) or 0 for attr in self.monthly_expense_attrs)

    @property
    def monthly_gross(self):
        return self.total_monthly_income

    @property
    def monthly_net(self):
        """
        Returns:
            float: difference between income and expenses
        """
        return self.total_monthly_income - self.total_monthly_expenses

    @property
    def is_balanced(self):
        """
        Returns:
            bool: whether the net (income-expenses) is >= 0
        """
        return (self.monthly_net >= 0)


import unittest
class Test_Budget(unittest.TestCase):
    def test_001_Budget(self):
        b = Budget()
        self.assertTrue(isinstance(b, Budget))
        self.assertEqual(b.total_monthly_income, 0)
        self.assertEqual(b.total_monthly_expenses, 0)
        self.assertEqual(b.monthly_gross, 0)
        self.assertEqual(b.monthly_net, 0)
        self.assertTrue(b.is_balanced)


def main():
    import optparse
    import logging

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
    sys.exit(main())
