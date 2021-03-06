import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid >= 1.4',
    'SQLAlchemy >= 0.8',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'Markdown',
    'Requests',
    'MarkupSafe',
    'webhelpers',
    'dogpile.cache',
    'wtforms',
    ]

setup(name='miniblog',
      version='0.0',
      description='miniblog',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='miniblog',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = miniblog:main
      [console_scripts]
      initialize_miniblog_db = miniblog.scripts.initializedb:main
      """,
      )
