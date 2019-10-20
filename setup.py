import os
import distutils.cmd
import subprocess

from setuptools import find_packages, setup


class BaseCommand(distutils.cmd.Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


def create_command(text, commands):
    """Creates a custom setup.py command."""

    class CustomCommand(BaseCommand):
        description = text

        def run(self):
            for cmd in commands:
                subprocess.check_call(cmd)

    return CustomCommand


with open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf-8') as readme:
    README = readme.read()

setup(
    name='django-localized-fields',
    version='5.4',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    license='MIT License',
    description='Implementation of localized model fields using PostgreSQL HStore fields.',
    long_description=README,
    url='https://github.com/SectorLabs/django-localized-fields',
    author='Sector Labs',
    author_email='open-source@sectorlabs.ro',
    keywords=['django', 'localized', 'language', 'models', 'fields'],
    install_requires=[
        'django-postgres-extra>=1.22,<2.0',
        'Django>=1.11',
        'deprecation==2.0.7'
    ],
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
    ],
    cmdclass={
        'lint': create_command(
            'Lints the code',
            [['flake8', 'setup.py', 'localized_fields', 'tests']],
        ),
    },
)
