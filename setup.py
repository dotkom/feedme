import os
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='feedme',
    version='1.8.4',
    author='dotkom',
    author_email='dotkom@online.ntnu.no',
    packages=['feedme'],
    license='BSD License',  # example license
    description='Food ordering management system',
    long_description='A food ordering management system for Django.\n\n\
    This project was initially started to help \'dotKom\' with organizing the ordering of food for their work nights.\n\n\
    Check out the github repo for installation instructions.',
    url='https://github.com/dotKom/feedme',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    include_package_data=True,
)
