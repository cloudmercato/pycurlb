#!/usr/bin/env python
from setuptools import setup, find_packages
import pycurlb


def read_file(name):
    with open(name) as fd:
        return fd.read()

keywords = ['curl', 'pycurl', 'benchmark', 'http', 'ftp']

setup(
    name='pycurlb',
    version=pycurlb.__version__,
    description=pycurlb.__doc__,
    long_description=read_file('README.rst'),
    author=pycurlb.__author__,
    author_email=pycurlb.__email__,
    install_requires=['pycurl'],
    license='BSD',
    url=pycurlb.__url__,
    keywords=keywords,
    packages=find_packages(exclude=[]),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'curlb = pycurlb.main',
        ]
    },
    # test_suite='runtests.main',
    # tests_require=read_file('requirements-tests.txt'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet',
        'Topic :: Internet :: File Transfer Protocol (FTP)',
        'Topic :: Internet :: WWW/HTTP',

    ],
)
