#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='ragde',
    version='0.0.1',
    description=(
        'A Python Package for Textual Analysis of Financial Disclosures'
    ),
    author='Reginald Edwards',
    author_email='reginald.edwards@gmail.com',
    maintainer='Reginald Edwards',
    license='MIT License',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/196sigma/ragde',
    classifiers=[
        'Development Status :: 1 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'numpy',
        'matplotlib',
    ],
    entry_points = {'console_scripts':['filing-readability=ragde.filing_readability:main',
                                       'filing-named-entities=ragde.filing_named_entities:main']}
)
