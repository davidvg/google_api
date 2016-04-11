#!/usr/bin/env python

from setuptools import setup, find_packages
from os import path
from codecs import open

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='google_api',
    version='0.1',
    description='Basic implementation of some of the Google APIs.',
    long_description=long_description,

    url='https://github.com/davidvg/google_api',

    author='David Vazquez Garcia',
    author_email='davidvazquez.gijon@gmail.com',

    license='MIT',

    classifiers=[
        # List of classifiers:
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        
        # *** Development status
        #'Development Status :: 1 - Planning'
        'Development Status :: 2 - Pre-Alpha',
        #'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        #'Development Status :: 6 - Mature',
        #'Development Status :: 7 - Inactive',
        
        'License :: OSI Approved :: MIT License',

        # *** Intended Audience
        'Intended Audience :: Developers',
        # *** Topic
        'Topic :: Software Development :: Build Tools',

        'Operating System :: OS Independent',
        'Environment :: Console',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    
    keywords='api google gmail',

    packages=['gmail_api'],
    #packages=find_packages(exclude=[]),

    install_requires=['httplib2', 'oauthclient', 'apiclient', 'email'],

    platforms='any',

    #package_files=[],

    #data_files=[],

    entry_points={
        'console_scripts': [
            # main() function called in __init__.py
            #'gmail_api=gmail_api:main',
        ],
    },
)
