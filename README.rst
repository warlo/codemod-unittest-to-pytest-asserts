**********************************
codemod-unittest-to-pytest-asserts
**********************************

A `codemod <https://pypi.org/project/codemod/>`_ to automatically refactor
unittest assertions with pytest assertions.


Installation
============

This codemod requires Python 3.8 or newer.

With pip, assuming Python 3.8 or newer is used::

   python3 -m pip install codemod-unittest-to-pytest-asserts

With pipx, assuming Python 3.8 exists on the system::

   pipx install --python $(which python3.8) codemod-unittest-to-pytest-asserts


Usage
=====

Run the installed command on the Python files or directory of files you want to refactor::

   codemod-unittest-to-pytest-asserts some-python-files.py

or::

   codemod-unittest-to-pytest-asserts some_directory/

You'll be asked to confirm all changes.

It is recommended to run an autoformatter, like Black, after the
refactoring.
