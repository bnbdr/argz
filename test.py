import os
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

import unittest
from sys import version_info, stdout
import argz


py_v = version_info
print ('\n{0} {1} {0}'.format(20*'=', '.'.join(map(str, py_v))))

argz.logger.addHandler(argz.default_log_handler)
# argz.logger.setLevel(10)  # enable for logging, could be changed per unittest


# @unittest.skipIf(py_v.major > 2, "not supported in this python version")
# with self.assertRaises(BadAccessorName) as cm:
#  bad code

class ArgzTest(unittest.TestCase):
    def check_res(self, ret):
        self.assertTrue(ret, 'return value is Falsy')
        self.assertTrue(len(ret) == 3, 'return value is not a set')
        return ret

    def assertRE(self, *args, **kwargs):
        if py_v.major < 3:
            return self.assertRegexpMatches(*args, **kwargs)
        else:
            return self.assertRegex(*args, **kwargs)

    def setUp(self):
        print ('\r > ' + self.id())
        argz.clear()
        self.argzerr = StringIO()

    def tearDown(self):
        pass


def route_allow_all(*args, **kwargs):
    return args, kwargs


def route_defarg(reqarg, defarg=1):
    return defarg


class Basic(ArgzTest):

    def test_route_default_found(self):
        r = argz.route(route_allow_all)
        argvalue = 'arg'

        ret = argz.parse(argvalue, stderr=self.argzerr)
        f, al, kw = self.check_res(ret)
        self.assertIs(route_allow_all, f,
                      'wrong function returned for default route')

    def test_route_default_arg_passed_str(self):
        r = argz.route(route_allow_all)
        argvalue = 'arg'

        ret = argz.parse(argvalue, stderr=self.argzerr)
        f, al, kw = self.check_res(ret)

        self.assertIs(f, route_allow_all, 'wrong route')
        self.assertTrue(len(al) == 1, 'wrong number of args passed to route')
        self.assertEqual(
            al[0], argvalue, 'wrong arg value passed')
        self.assertFalse(kw, 'kwargs is not empty')

    def test_route_arg_default_split_str(self):
        r = argz.route(route_allow_all)
        argvalue = 'arg1 arg2'

        ret = argz.parse(argvalue, stderr=self.argzerr)
        f, al, kw = self.check_res(ret)
        self.assertIs(f, route_allow_all, 'wrong route')
        self.assertTrue(len(al) == 2, 'wrong number of args passed to route')
        self.assertEqual(
            al, argvalue.split(' '), 'wrong split output')
        self.assertFalse(kw, 'kwargs is not empty')

    def test_route_arg_list(self):
        r = argz.route(route_allow_all)
        argvalue = ['arg1', 'arg2']

        ret = argz.parse(argvalue, stderr=self.argzerr)
        f, al, kw = self.check_res(ret)
        self.assertIs(f, route_allow_all, 'wrong route')

        self.assertEqual(
            al, argvalue, 'wrong split output')
        self.assertFalse(kw, 'kwargs is not empty')

    def test_route_no_args_shows_help(self):
        r = argz.route(route_allow_all)
        # so won't take args from sys.argv
        ret = argz.parse('', stderr=self.argzerr)
        self.assertFalse(ret, 'running without arguments should print usage')
        self.assertRE(self.argzerr.getvalue(), 'Usage:',
                      'failed showing usage when called without arguments')


class More(ArgzTest):
    def test_route_with_default(self):
        r = argz.route(route_defarg)
        argval = 'required'
        ret = argz.parse(argval, stderr=self.argzerr)
        f, al, kw = self.check_res(ret)
        self.assertFalse(kw, 'kwargs is not empty')

        self.assertEqual(al[0], argval, 'required arg is wrong')
        self.assertEqual(al[1], 1, 'default arg is wrong')


if __name__ == '__main__':
    unittest.main()
