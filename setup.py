import os
import re

from setuptools import setup


HERE = os.path.dirname(os.path.abspath(__file__))


def get_version():
    filename = os.path.join(HERE, 'transfluent.py')
    contents = open(filename).read()
    pattern = r"^__version__ = '(.*?)'$"
    return re.search(pattern, contents, re.MULTILINE).group(1)


setup(
    name='transfluent',
    version=get_version(),
    description='A Python wrapper for Transfluent API',
    long_description=(
        open('README.rst').read() + '\n' +
        open('CHANGES.rst').read()
    ),
    author='Janne Vanhala',
    author_email='janne.vanhala@gmail.com',
    url='http://github.com/jpvanhal/python-transfluent',
    py_modules=['transfluent'],
    license=open('LICENSE').read(),
    platforms='any',
    install_requires=[
        'requests>=1.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
