=======================
defpage.com Google Docs
=======================

Deploy
======

Create virtual environment::

  $ git clone git@spacta.com:defpage/gd.git
  $ cd gd
  $ virtualenv --no-site-packages --distribute .

Install shared python library for defpage (take it here: git@spacta.com:defpage/pylib.git)::

  $ bin/pip install -e [ path_to_pylib ]

Install site::

  $ bin/pip install -e .

Run tests::

  $ bin/python setup.py test

Run site for development::

  $ bin/pserve development.ini --reload

Run site in production::

  $ bin/pserve production.ini --daemon
