.. _quickstart:

==========
Quickstart
==========

To just get started you first need to install and then configure MiniBlog but
first a little heads-up. This software relies on the Pyramid Framework and
uses some libraries and has dependencies to improve performance or recduce
the need for own code. For a more thorough explanation see [...]

.. todo::
    Write & link exmplanation for libraries...


Preface
=======
Before you start installing MiniBlog there are some things you might want to
consider. If you are already sure you want to install MiniBlog, you can
skip this part and start directly with the `Installation`_.

You may not like some of the ways in which MiniBlog works. Some of these are
actually easily customizable, so you can adjust these after initial setup.
Others are builtin and require working on the actual source code.

The following libraries and elements are used with MiniBlog:

    * `SQLAlchemy <http://www.sqlalchemy.org/>`_
    * `dogpile.cache <https://bitbucket.org/zzzeek/dogpile.cache>`_
    * `Pyramid <http://www.pylonsproject.org/>`_
    * `WTForms <http://wtforms.simplecodes.com/>`_
    * `Markdown <http://daringfireball.net/projects/markdown/>`_
    * `Persona Login <https://login.persona.org/>`_

None of these requirements can actually be removed easily, but some can be
modified, especially SQLAlchemy and dogpile.cache. The others you will just
have to acceppt. The only ones that may get in your way while blogging are
Markdown and Persona.

Why choose Markdown?
--------------------
Markdown allows you to write text in a nice and structured way without
thinking too much about HTML. It also provides an additional layer of
security as it limits the ability to input HTML & other code.

The main reason to use Markdown came from the requirement to write blog
entries in an easy and quick way without risking any security
problems (i.e. writing HTML by yourself). You might argue that since this
is a blogging software for one person only, it might not be problematic in this
case and you are probably right. The added security is considered a bonus
feature among the ease of writing Markdown.

However, if you *really* don't want Markdown, you can replace it. There is
nothing that prevents you from replacing or removing it. See [...] for 
detailed instructions.

.. todo::
    Write & link Markdown replacement instructions


Why choose Persona?
-------------------
As a proof of concept for myself. When I started building this software I had
recently seen a talk about Persona and now I wanted to try it. This seemed like
the perfect opportunity because the site would not have any requirement for
user management and thus the implementation would only require to hard code an
email address to the configuration and let Persona do the rest.

I tried it and I liked it. But you might not and so you should keep this in
in mind: Persona is hardwired into the software and while replacing it is
possible, it is neither easy nor supported. If, however, you want to go that
way, you can take a look at [...].

.. todo::
    Write & link something that describes where Persona is used and what might
    need replacement then.


Summary
-------
If none of the above scares you (or you are willing to work out some
modifications) then you are invited to start with MiniBlog's `Installation`_.
Should you build something as a modification (e.g. replace Markdown or
Persona), please let me know so I can think about intergrating it to
this project.

Installation
============
The installation depends on your desired setup. Generally speaking, you should
check out the `Deployment <http://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/deployment/index.html>`_
chapter in the Pyramid Cookbook for some instructions. The instructions here
refer to an installation with `Nginx <http://wiki.nginx.org/Main>`_,
`Paste <http://pythonpaste.org/>`_ and `supervisord <http://supervisord.org/>`_.

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
    $ mkdir cache
    $ virtualenv env
    $ . env/bin/activate
    $ python setup.py develop
    $ cp samples/production.ini.sample production.ini

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

The next step is very relevant for your applications **security**!
You need to generate **two** keys: One for authentication and one
for session. You can easily generate them from python with
something like

.. code-block:: python

    import os
    os.urandom(20).encode("hex")

Be sure to generate two *distinct* keys and enter them into the ``auth_secret``
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

   pip install pastescript cherrypy weberror
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

Using Supervisord to Manage Paster
-----------------------------------
So you have tested the application and verified it is running and working?
Good, because now everything is set for the final step: Installing the
application as a service so it is run automatically.

The process described here uses Supervisor on an ArchLinux system with a
systemd unit file for the service. Depending on your system you might need a
different setup (e.g. if no systemd is present). Some examples of how to run
Supervisor on any of these systems can be found on `GitHub <https://github.com/Supervisor/initscripts>`_.

First of all, you need to create some directories and install Supervisor:

.. code-block:: console

    $ mkdir log tmp
    $ pacman -S supervisor
    $ chown -R http:http /var/www/miniblog

The last commands sets the permission for the folder to the webserver's
user. You could also create a user just for this application, the webserver
only needs the ability to serve the static files.

Now we create our `supervisord.conf`:

.. literalinclude:: ../samples/supervisord.conf.sample
    :language: ini
    :linenos:

Change the username ``user=http`` to your webserver's username (or whatever you
chose aboe). That should be the only change required to get the server running.
However, to improve performance or adjust behavior, you might want to finetune
some settings.

To make this startable by systemd we take ArchLinux's usual systemd file and
modify it slightly:

.. literalinclude:: ../samples/miniblog.service.sample
    :language: ini
    :linenos:

For ArchLinux now do:

.. code-block:: console

    $ cd /etc/systemd/system
    $ # Insert miniblog.service file here
    $ systemctl enable miniblog
    $ systemctl start miniblog

If everything went alright, you should now be able to access your site.
That's it, the software is installed. Browse it a bit to make sure everything
worked, add some entries and get used to the site. For usage guidance on how
to use this software see `Usage`_.

However, if you have trouble, look no further and head to the
`Troubleshooting`_ section.

Troubleshooting
---------------
If you have issues with reaching the installed site after having followed this
tutorial, you first have to figure out where the problem lies. If it was
before `Quick-Test with paster`_ you should try to launch a single,
non-daemonized session there and try to trace the error. Also make sure to
check the Nginx log file (``/var/log/nginx/miniblog_error.log``).

If your problems start with using Supervisor then you should take a look at
the files in ``/var/www/miniblog/log``. There you might find some information.
If these files do not exists (there should be one for supervisord and as many
application logs as you have processes configured) then you might have a
permission issue.


Usage
=====
To get started blogging, only one minor step is needed. MiniBlog uses
`Persona <https://login.persona.org/>`_ for login, thus you need to
create a Persona login. This is actually extremely simple: Hover over
the grey menubar in the right corner. You will see a "Login" entry appear.
Click it and a Persona window will appear. Follow the instructions and
create an account for the email address you entered in your ``production.ini``.
It is vital that these addresses match as they will allow you to log in.

After completing the process, you should now see new entries in the menu, e.g.
"Add Entry". Hover over to the right: It should now display "Logout". You are
now all set. Play around in the menu and start blogging.

MiniBlog provides a high level of customization as it exposes the configuration
possibilities of its underlying libraries, especially :mod:`dogpile.cache` and
:mod:`sqlalchemy`.

Finally, you might want to create the about page: On this page you can talk a
bit about yourself and why this blog exists & what it's about. For this, copy
the sample file:

.. code-block:: console

    $ cd miniblog/templates
    $ cp about.mako.sample about.mako

Now oben the file and edit the ``body`` block:

.. code-block:: html

    <%block name="body">
    Your content here...
    </%block>

You can use any HTML you like within that block and you also have access to
some variables available to a Mako template, especially Pyramids request
via ``view.request``. No probably won't need that so just use plain HTML and
start rambling.

