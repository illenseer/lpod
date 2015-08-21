import codecs
import os
import re
import sys

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *parts), "rb", "utf-8") as f:
        return f.read()


def find_version(*file_paths):
    """
    Build a path from *file_paths* and search for a ``__version__``
    string inside.
    """
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='traod',
    version=find_version('traod', '__init__.py'),
    description="Parse and translate ordered disjunctions in LPODs.",
    license='GPLv3',
    author='Nils Pascal Illenseer',
    author_email='ni@np.cx',
    packages=find_packages(exclude=['tests*']),
    entry_points={
        'console_scripts': [
            'traod = traod.__main__:main',
        ],
    },
    install_requires=[
        "click==5.1",
        "grako==3.6.3",
    ],
)
