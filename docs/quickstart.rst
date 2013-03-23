==========
Quickstart
==========

To just get started you first need to install and then configure MiniBlog but
first a little heads-up. This software relies on the Pyramid Framework and 
uses some libraries and has dependencies to improve performance or recduce
the need for own code. This includes caching through :mod:`dogpile.cache`
which introduces the requirement for `Memcached <http://memcached.org/>`_.
Take a look at the `Prerequisites`_ first.

Prerequisites
=============
Some dependencies are outside of Python and can thus not be automatically
installed by a script. Refer to your distributions documentation and the
individual projects documentation for help on how to install them.

The following libraries & programs need to be installed for MiniBlog:

    * `Memcached <http://memcached.org/>`_
    * `libmemcached <http://libmemcached.org/libMemcached.html>`_

Once these libraries are installed, you are ready to start with the
`Installation`_.

Installation
============
The installation depends on your desired setup. Generally speaking, you should
check out the `Deployment <http://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/deployment/index.html>`_
chapter in the Pyramid Cookbook for some instructions. The instructions here
refer to an installation with `Nginx <http://wiki.nginx.org/Main>`_,
`Paste <http://pythonpaste.org/>`_ and supervisord.

Install the application
-----------------------
Download the application from [...]. Create a folder to hold your complete web
application setup, e.g. ``mkdir /var/www/miniblog``. Then switch into it with
``cd /var/www/miniblog`` and install a virtual environment here (use
``virtualenv env`` or ``virtualenv-2.7 env`` or a similar command (check your
distribution). Next activate it with ``. env/bin/activate``. Now run
``python setup.py build`` and ``python setup.py install``. This will install
the application in ``env``.

.. code-block:: console

    $ cd /var/www
    $ git clone https://github.com/Javex/miniblog.git
    $ cd miniblog
    $ virtualenv env
    $ . env/bin/activate
    $ python setup.py build
    $ python setup.py develop
    $ cp production.ini.sample production.ini

This creates your application with a sample configuration. Don't worry about
the ``develop`` setup; we use it to install dependencies but keep our
application code locally. Now we move on to the `Configuration`_.

Configuration
=============

Configure the application
-------------------------
Open up your "production.ini" with your favorite file editor (e.g. ``vim``).
At least adjust the following settings in the ``[app:miniblog]`` section:

    * title = My new fancy Blog
    * admin_email = my.mail@example.com
    * disqus_shortname = mydisqusname

Also enter the following settings in ``[filter:weberror]``:

    * error_email = my.mail@example.com
    * from_address = my.mail@example.com

For a complete documentation of the configuration process see [...]. There
you will find all settings explained.

The next step is very relevant for your applications *security*!
You need to generate *two* keys: One for authentication and one
for session. You can easily generate them from python with
something like

.. code-block:: python

    import os
    os.urandom(20).encode("hex")

Be sure to generate two _distinct_ keys and enter them into the ``auth_secret``
and ``session.secret`` in the ``[app:miniblog]`` section.

Now you have configured your application completely. Once you start the
application for the first time, the database will be created if the schema
doesn't already exist. But before we are there, we need to configure actually
serving the application to the internet.

Configure nginx
---------------

The ``Nginx`` configuration is mostly taken from the Pyramid Cookbook but is 
modified to force ssl (you may alter that if you do not want/need HTTPS).

.. literalinclude:: ../samples/nginx.conf.sample
    :language: nginx
    :linenos:

Of course, you need to adjust all paths and possibly create or request a
certificate (or remove all SSL settings). 

After installing the configuration, restart Nginx.

Quick-Test with paster
----------------------

You now need to install `Paste Script <http://pythonpaste.org/script/>`_
because we will be using it behind nginx to actually serve our application.

.. code-block:: text

   pip install pastescript
   paster serve --pid-file=paster_5000.pid production.ini http_port=5000

.. note::
    
    We don't daemonize here on purpose: We wan't to see how the application
    launches and fix any errors that might occur.

Check the output of running the command. It should be serving the application.
If it doesn't fix the errors displayed. Once all errors are fixed, head to
your configured location from the Nginx configuration file (e.g. exmaple.com)
and the page should load. Check again if the console running ``paster`` has any
error output and if not, you now have a working installation.

But you might not want to run ``paster`` from the console all the time, so you
should check out the next section.

Using Supervisord to Manager Paster
-----------------------------------

[...]
