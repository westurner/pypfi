#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

install_requires = [
    # 'numpy',
    # 'pandas',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='pypfi',
    version='0.1.0',
    description='pypfi',
    long_description=readme + '\n\n' + history,
    author='Wes Turner',
    author_email='wes.turner@gmail.com',
    url='https://github.com/westurner/pypfi',
    packages=[
        'pypfi',
    ],
    package_dir={'pypfi':
                 'pypfi'},
    include_package_data=True,
    install_requires=install_requires,
    license="BSD",
    zip_safe=False,
    keywords='pypfi personalfinance',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points="""
    [console_scripts]
    pypfi = pypfi.pypfi:main
    """,
    test_suite='tests',
    tests_require=test_requirements
)
