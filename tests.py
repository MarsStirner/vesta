# -*- coding: utf-8 -*-
import unittest
import tests


def run_tests():
    suite = unittest.TestLoader().loadTestsFromModule(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    run_tests()