import distutils.cmd
import os
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


with open(
    os.path.join(os.path.dirname(__file__), "README.rst"), encoding="utf-8"
) as readme:
    README = readme.read()


setup(
    name="django-localized-fields",
    version="6.0b1",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    license="MIT License",
    description="Implementation of localized model fields using PostgreSQL HStore fields.",
    long_description=README,
    url="https://github.com/SectorLabs/django-localized-fields",
    author="Sector Labs",
    author_email="open-source@sectorlabs.ro",
    keywords=["django", "localized", "language", "models", "fields"],
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    cmdclass={
        "lint": create_command(
            "Lints the code",
            [
                ["flake8", "setup.py", "localized_fields", "tests"],
                ["pycodestyle", "setup.py", "localized_fields", "tests"],
            ],
        ),
        "lint_fix": create_command(
            "Lints the code",
            [
                [
                    "autoflake",
                    "--remove-all-unused-imports",
                    "-i",
                    "-r",
                    "setup.py",
                    "localized_fields",
                    "tests",
                ],
                [
                    "autopep8",
                    "-i",
                    "-r",
                    "setup.py",
                    "localized_fields",
                    "tests",
                ],
            ],
        ),
        "format": create_command(
            "Formats the code",
            [["black", "setup.py", "localized_fields", "tests"]],
        ),
        "format_verify": create_command(
            "Checks if the code is auto-formatted",
            [["black", "--check", "setup.py", "localized_fields", "tests"]],
        ),
        "format_docstrings": create_command(
            "Auto-formats doc strings", [["docformatter", "-r", "-i", "."]]
        ),
        "format_docstrings_verify": create_command(
            "Verifies that doc strings are properly formatted",
            [["docformatter", "-r", "-c", "."]],
        ),
        "sort_imports": create_command(
            "Automatically sorts imports",
            [
                ["isort", "setup.py"],
                ["isort", "-rc", "localized_fields"],
                ["isort", "-rc", "tests"],
            ],
        ),
        "sort_imports_verify": create_command(
            "Verifies all imports are properly sorted.",
            [
                ["isort", "-c", "setup.py"],
                ["isort", "-c", "-rc", "localized_fields"],
                ["isort", "-c", "-rc", "tests"],
            ],
        ),
        "fix": create_command(
            "Automatically format code and fix linting errors",
            [
                ["python", "setup.py", "format"],
                ["python", "setup.py", "format_docstrings"],
                ["python", "setup.py", "sort_imports"],
                ["python", "setup.py", "lint_fix"],
            ],
        ),
        "verify": create_command(
            "Verifies whether the code is auto-formatted and has no linting errors",
            [
                [
                    ["python", "setup.py", "format_verify"],
                    ["python", "setup.py", "format_docstrings_verify"],
                    ["python", "setup.py", "sort_imports_verify"],
                    ["python", "setup.py", "lint"],
                ]
            ],
        ),
    },
)
