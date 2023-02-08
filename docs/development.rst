.. _development:

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

   $ docker compose up --build


- WSGI server: Open ``http://127.0.0.1:8000/`` in your browser.
- ASGI server: Open ``http://127.0.0.1:8001/`` in your browser.


Building, Serving and Testing the Documentation Locally
-------------------------------------------------------

.. code-block:: bash

   $ docker compose -p django-structlog-docs -f docker-compose.docs.yml up --build
   Serving on http://127.0.0.1:5000
