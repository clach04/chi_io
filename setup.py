import os
import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if len(sys.argv) <= 1:
    print("""
Suggested setup.py parameters:

    * build
    * install
    * sdist  --formats=zip
    * sdist  # NOTE requires tar/gzip commands

    python -m pip install -e .

PyPi:

    python -m pip install setuptools twine
    twine upload dist/*
    ./setup.py  sdist ; twine upload dist/* --verbose

""")

readme_filename = 'README.md'
if os.path.exists(readme_filename):
    f = open(readme_filename)
    long_description = f.read()
    f.close()
else:
    long_description = None

#exec(open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'chi_io', '_version.py')).read())
__version__ = '1.0.2'

setup(
    name='chi_io',
    version=__version__,
    author='clach04',
    url='https://github.com/clach04/chi_io',
    description='Pure Python read/write encryption/decryption of encrypted Tombo chi files ',
    long_description=long_description,
    long_description_content_type='text/markdown',
    #packages=['chi_io'],  # not implemented yet
    py_modules=['chi_io', 'pyblowfish'],
    #data_files=[('.', [readme_filename])],  # does not work :-( ALso tried setup.cfg [metadata]\ndescription-file = README.md # Maybe try include_package_data = True and a MANIFEST.in?
    classifiers=[  # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        # FIXME TODO more
        ],
    platforms='any',  # or distutils.util.get_platform()
    #install_requires=['pycryptodome'],  # pycryptodome (and/or PyCrypto) are optional and not required, but will be so much faster if used!
)
