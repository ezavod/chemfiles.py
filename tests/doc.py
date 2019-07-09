# -*- coding=utf-8 -*-
import unittest
import doctest
import chemfiles
import types
import sys
import re

EXCLUDE = ["clib"]


# Allow both `u'foo'` and `'foo'` to match `'foo'` in output
# This means the doc tests are usable with both Python 2 and 3
class Py23DocChecker(doctest.OutputChecker, object):
    RE = re.compile(r"(\W|^)[uU]([rR]?[\'\"])", re.UNICODE)

    def remove_u(self, want, got):
        if sys.version_info[0] < 3:
            return (re.sub(self.RE, r'\1\2', want), re.sub(
                self.RE, r'\1\2', got))
        else:
            return want, got

    def check_output(self, want, got, optionflags):
        want, got = self.remove_u(want, got)
        return super(Py23DocChecker, self).check_output(want, got, optionflags)

    def output_difference(self, example, got, optionflags):
        example.want, got = self.remove_u(example.want, got)
        return super(Py23DocChecker, self).output_difference(example, got, optionflags)


def disable_chemfiles_warnings(*args):
    chemfiles.set_warnings_callback(lambda u: None)


def enable_chemfiles_warnings(*args):
    chemfiles.misc._set_default_warning_callback()


def load_tests(loader, tests, ignore):
    """
    Add chemfiles's doc tests to the test suite used by unittest
    """

    for key, obj in chemfiles.__dict__.items():
        if key in EXCLUDE:
            continue
        if isinstance(obj, types.ModuleType):
            tests.addTests(doctest.DocTestSuite(
                "chemfiles.{}".format(key),
                setUp=disable_chemfiles_warnings,
                tearDown=enable_chemfiles_warnings,
                checker=Py23DocChecker()
            ))

    return tests
