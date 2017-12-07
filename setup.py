# -*- coding=utf-8 -*-
import sys
import chemfiles
from skbuild import setup

with open('requirements.txt', 'r') as fp:
    requirements = list(filter(bool, (line.strip() for line in fp)))

LONG_DESCRIPTION = """Chemfiles is a library for reading and writing molecular
trajectory files. These files are created by your favorite theoretical chemistry
program, and contains informations about atomic or residues names and positions.
Chemfiles offers abstraction on top of these formats, and a consistent interface
for loading and saving data to these files."""

setup(
    name="chemfiles",
    long_description=LONG_DESCRIPTION,
    version=chemfiles.__version__,
    author="Guillaume Fraux",
    author_email="luthaf@luthaf.fr",
    description="Read and write chemistry trajectory files",
    license="BSD",
    keywords="chemistry computational cheminformatics files formats",
    url="http://github.com/chemfiles/chemfiles.py",
    packages=['chemfiles'],
    zip_safe=False,
    install_requires=requirements,
    setup_requires=["scikit-build"],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities"
    ],
    cmake_install_dir="chemfiles"
)
