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


Building, Serving and Testing the Documentation Locally
-------------------------------------------------------

.. code-block:: bash

   $ docker-compose -f docker-compose.docs.yml up --build
   Serving on http://0.0.0.0:5000
