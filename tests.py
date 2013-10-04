# -*- coding: utf-8 -*-
import unittest
import tests
from werkzeug.utils import import_string


def run_tests():
    for module_test in tests.__all__:
        module = import_string('tests.{0}'.format(module_test))
        suite = unittest.TestLoader().loadTestsFromModule(module)
        unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    run_tests()