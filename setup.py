import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

setup(
    name='django-localized-fields',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='Implementation of localized model fields using PostgreSQL HStore fields.',
    long_description=README,
    url='http://sectorlabs.ro/',
    author='Sector Labs',
    author_email='open-source@sectorlabs.ro',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
)
