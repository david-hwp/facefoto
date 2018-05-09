Install
-------

**Be sure to use the same version of the code as the version of the docs
you're reading.** You probably want the latest tagged version, but the
default Git version is the master branch. ::

    # clone the repository
    git clone https://github.com/david-hwp/facefoto.git
    cd facefoto
    # checkout the correct version
    git tag  # shows the tagged versions
    git checkout latest-tag-found-above

Create a virtualenv and activate it::

    python3 -m venv venv
    . venv/bin/activate

Or on ubantu::

    virtualenv venv --python=python3.5
    . venv/bin/activate

Or on Windows cmd::

    py -3 -m venv venv
    venv\Scripts\activate.bat

Install facefoto::

    pip install -e .


Run
---

::

    export FLASK_APP=facefoto
    export FLASK_ENV=development
    flask run

Or on Windows cmd::

    set FLASK_APP=facefoto
    set FLASK_ENV=development
    flask run

Open http://127.0.0.1:5000 in a browser.

or you want specify the host and port::

    flask run -h '0.0.0.0' -p 8080


Test
----

::

    pip install '.[test]'
    pytest

Run with coverage report::

    coverage run -m pytest
    coverage report
    coverage html  # open htmlcov/index.html in a browser
