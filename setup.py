# -*- coding=utf-8 -*-
import os
import sys
import glob
import shutil
import inspect

from ctypes.util import find_library

from setuptools import setup, Extension
from setuptools.command.build_py import build_py
from setuptools.command.build_ext import build_ext
from setuptools.command.install_lib import install_lib
from subprocess import Popen, PIPE, call

CMAKE_OPTS = [("BUILD_SHARED_LIBS", "ON")]

# Get current file even when using execfile
__file__ = inspect.getfile(inspect.currentframe())
CHEMFILES_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "native"
)

VERSION = open(os.path.join(CHEMFILES_DIR, "VERSION")).read().strip()
VERSION = VERSION.replace("-", "_")

READ_THE_DOCS_BUILD = os.environ.get('READTHEDOCS', None) == 'True'


def check_cmake():
    try:
        cmd = Popen(["cmake"], stdout=PIPE, stderr=PIPE)
        cmd.wait()
    except OSError:
        raise EnvironmentError("CMake is not available!")


def write_version(path):
    with open(os.path.join(path, "_version.py"), "w") as fd:
        fd.write('__version__ = "{}"\n'.format(VERSION))


class custom_build_py(build_py):
    def run(self):
        build_py.run(self)
        # honor the --dry-run flag
        if not self.dry_run:
            ROOT = os.path.join(self.build_lib, 'chemfiles')
            write_version(ROOT)


class custom_build_ext(build_ext):
    def build_extension(self, ext):
        if ext.name != 'chemfiles':
            return build_ext.build_extension(self, ext)

        # Create the temporary build directory
        try:
            os.makedirs(self.build_temp)
        except OSError:
            pass

        if READ_THE_DOCS_BUILD:
            # Create a dummy shared library
            open(os.path.join(self.build_temp, "_chemfiles.so"), 'a').close()
            return
        if find_library("chemfiles"):
            print("Found library at {}. Not building the integrated one"
                  .format(find_library("chemfiles")))
            return
        else:
            print("Chemfiles library not found. Building it with CMake")
        check_cmake()

        cwd = os.getcwd()
        os.chdir(self.build_temp)

        configure = ["cmake", CHEMFILES_DIR]
        cmake_opts = ['-D' + '='.join(opt) for opt in CMAKE_OPTS]
        configure.extend(cmake_opts)
        print("running {}".format(" ".join(configure)))
        if call(configure) != 0:
            raise EnvironmentError("Error in CMake configuration")

        build = ["cmake", "--build", "."]
        if call(build) != 0:
            raise EnvironmentError("Error while building chemfiles")

        filename = glob.glob(os.path.join("*chemfiles*.*.*"))[0]
        shutil.copy(filename, "_chemfiles.so")
        os.chdir(cwd)

    def get_ext_filename(self, ext_name):
        return os.path.join(self.build_temp, "_chemfiles.so")


class custom_install_lib(install_lib):
    def run(self):
        TEMP_DIR = self.distribution.get_command_obj('build_ext').build_temp
        install_lib.run(self)
        self.copy_file(
            os.path.join(TEMP_DIR, "_chemfiles.so"),
            os.path.join(self.install_dir, "chemfiles", "_chemfiles.so")
        )

        MOLFILES_ROOT = os.path.join(self.install_dir, "chemfiles", "molfiles")
        os.mkdir(MOLFILES_ROOT)
        for path in glob.iglob(os.path.join(TEMP_DIR, "lib", "*plugin.so")):
            self.copy_file(
                os.path.join(path),
                os.path.join(MOLFILES_ROOT, os.path.basename(path))
            )

LONG_DESCRIPTION = """Chemfiles is a library for reading and writing molecular
trajectory files. These files are created by your favorite theoretical
chemistry program, and contains informations about atomic or residues names
and positions. Chemfiles offers abstraction on top of these formats, and a
consistent interface for loading and saving data to these files."""

options = {
    "name": "chemfiles",
    "version": VERSION,
    "author": "Guillaume Fraux",
    "author_email": "luthaf@luthaf.fr",
    "description": ("An efficient library for chemistry files IO"),
    "license": "MPL-v2.0",
    "keywords": "chemistry computational cheminformatics files formats",
    "url": "http://github.com/chemfiles/chemfiles.py",
    "packages": ['chemfiles'],
    "ext_modules": [Extension('chemfiles', [])],
    "long_description": LONG_DESCRIPTION,
    "install_requires": ["numpy"],
    "classifiers": [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix",
        "Programming Language :: C++",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities"
    ],
    "cmdclass": {
        'build_ext': custom_build_ext,
        'install_lib': custom_install_lib,
        'build_py': custom_build_py,
    }
}

if sys.hexversion < 0x03040000:
    options["install_requires"].append("enum34")

setup(**options)
