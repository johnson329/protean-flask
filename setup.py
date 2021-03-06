#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""Setup Module for Protean Flask Extension"""

from __future__ import absolute_import
from __future__ import print_function

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    """Helper method to read files"""
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
    name='protean-flask',
    version='0.0.11',
    license='BSD 3-Clause License',
    description='Protean Flask Extension',
    long_description='%s\n%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst')),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    author='Subhash Bhushan C',
    author_email='subhash@team8solutions.com',
    url='https://github.com/proteanhq/protean-flask',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Operating System :: POSIX :: Linux',
        'Operating System :: OS/2',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    install_requires=[
        'click==7.0',
        'flask==1.1.1',
        'inflect==1.0.1',
        'protean==0.0.11',
        'marshmallow==2.16.1',
        # eg: 'aspectlib==1.1.1', 'six>=1.7',
    ],
    extras_require={
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
    },
    entry_points={
        'console_scripts': [
            'protean-flask = protean_flask.cli:main',
        ]
    },
)
