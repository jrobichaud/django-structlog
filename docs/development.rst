Development
===========

Prerequisites
-------------

- `docker <https://docs.docker.com/>`_


Installation
------------

.. code-block:: bash

    $ git clone https://github.com/jrobichaud/django-structlog.git
    $ cd django-structlog
    $ pip install -r requirements.txt
    $ pre-commit install


Start Demo App
--------------

.. code-block:: bash

   $ docker-compose up --build


Testing the Documentation Locally
---------------------------------

Building the doc
^^^^^^^^^^^^^^^^

.. code-block:: bash

   $ cd docs
   $ make html && make doctest


Serving the doc
^^^^^^^^^^^^^^^

.. code-block:: bash

   $ cd docs/_build/html
   $ python -m http.server
   Serving HTTP on 0.0.0.0 port 5000 (http://0.0.0.0:5000/) ...
