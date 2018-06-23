#!/usr/bin/python
# -*- encoding: utf-8; -*-
# flake8: noqa

from setuptools import setup, find_packages
from os import path
import versioneer

here = path.abspath(path.dirname(__file__))

long_description = """
# Ry's Markdown implementation #

rydown is a formal lexer/parser for Markdown. It uses PLY to lex
tokens and parse them into an abstract syntax tree, which can then be
serialized into HTML.

It's not a full Markdown implementation, but  it's everything I need to keep
RyPress.com running.

Due to its PLY implementation, the codebase is smaller than many other Markdown
libraries. If you're familiar with formal grammars, this makes it easier to
grok. If you're not, check out my tutorials.

See https://rypress.com/rydown for more information.
"""

setup(
    name='rydown',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='A formal Markdown lexer/parser',
    long_description=long_description,

    url='https://rypress.com/rydown',
    author='Ryan Hodson',
    author_email='ry@rypress.com',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup',
        'Topic :: Text Processing :: Markup :: HTML',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords='markdown',
    packages=['rydown', 'rydown.codesyntax'],
    install_requires=['ply', 'pygments'],
)
