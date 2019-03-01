import os
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

import unittest
from sys import version_info, stdout
import argz
from tests import test_routes
import warnings

py_v = version_info
print ('\n{0} {1} {0}'.format(20*'=', '.'.join(map(str, py_v))))

argz.logger.addHandler(argz.default_log_handler)
argz.logger.setLevel(10)
argz.logger.disabled = True  # change for logging, can be done per unittest


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


class Basic(ArgzTest):

    def test_route_default_found(self):
        r = argz.route(test_routes.route_allow_all)
        argvalue = 'arg'

        ret = argz.parse(argvalue, stderr=self.argzerr)
        f, al, kw = self.check_res(ret)
        self.assertIs(test_routes.route_allow_all, f,
                      'wrong function returned for default route')

    def test_route_default_arg_passed_str(self):
        r = argz.route(test_routes.route_allow_all)
        argvalue = 'arg'

        ret = argz.parse(argvalue, stderr=self.argzerr)
        f, al, kw = self.check_res(ret)

        self.assertIs(f, test_routes.route_allow_all, 'wrong route')
        self.assertTrue(len(al) == 1, 'wrong number of args passed to route')
        self.assertEqual(
            al[0], argvalue, 'wrong arg value passed')
        self.assertFalse(kw, 'kwargs is not empty')

    def test_route_arg_default_split_str(self):
        r = argz.route(test_routes.route_allow_all)
        argvalue = 'arg1 arg2'

        ret = argz.parse(argvalue, stderr=self.argzerr)
        f, al, kw = self.check_res(ret)
        self.assertIs(f, test_routes.route_allow_all, 'wrong route')
        self.assertTrue(len(al) == 2, 'wrong number of args passed to route')
        self.assertEqual(
            al, argvalue.split(' '), 'wrong split output')
        self.assertFalse(kw, 'kwargs is not empty')

    def test_route_arg_list(self):
        r = argz.route(test_routes.route_allow_all)
        argvalue = ['arg1', 'arg2']

        ret = argz.parse(argvalue, stderr=self.argzerr)
        f, al, kw = self.check_res(ret)
        self.assertIs(f, test_routes.route_allow_all, 'wrong route')

        self.assertEqual(
            al, argvalue, 'wrong split output')
        self.assertFalse(kw, 'kwargs is not empty')

    def test_route_no_args_shows_help(self):
        r = argz.route(test_routes.route_allow_all)
        # so won't take args from sys.argv
        ret = argz.parse('', stderr=self.argzerr)
        self.assertFalse(ret, 'running without arguments should print usage')
        self.assertRE(self.argzerr.getvalue(), 'Usage:',
                      'failed showing usage when called without arguments')


class More(ArgzTest):
    def test_route_with_default(self):
        r = argz.route(test_routes.route_defarg)
        argval = 'required'
        ret = argz.parse(argval, stderr=self.argzerr)
        f, al, kw = self.check_res(ret)
        self.assertFalse(kw, 'kwargs is not empty')

        self.assertEqual(al[0], argval, 'required arg is wrong')
        self.assertEqual(al[1], 1, 'default arg is wrong')


class ReadmeExample(ArgzTest):
    def test_json_adapter(self):
        import json
        r = argz.route(test_routes.route_json_dict)
        argval = 'tests/json_data.json'
        r.jsondict.adapter = [open, json.load]    # will be chained

        with warnings.catch_warnings():
            # py3 json.load warns about not closing file
            warnings.simplefilter("ignore")
            ret = argz.parse(argval, stderr=self.argzerr)

            f, al, kw = self.check_res(ret)
            self.assertIsInstance(al[0], dict, 'json not parsed into dict')
            self.assertEqual(al[0],  json.load(open(argval)))

    def test_validator_regex(self):

        argval = ['ABC123', 'tests/json_data.json', 'option1', 'someval']
        r = argz.route(test_routes.route_validator)
        r.alphanum.validator = '[A-Z0-9]{2,}'
        ret = argz.parse(argval, stderr=self.argzerr)
        f, al, kw = self.check_res(ret)

        argval_notalphanum = ['_ABC[123']+argval[1:]
        ret = argz.parse(argval_notalphanum, stderr=self.argzerr)
        self.assertEqual(ret, None, 'should have failed validation')

    def test_validator_callable(self):
        import os
        argval = ['ABC123', 'tests/json_data.json', 'option1', 'someval']
        r = argz.route(test_routes.route_validator)
        r.filepath.validator = os.path.isfile
        ret = argz.parse(argval, stderr=self.argzerr)
        f, al, kw = self.check_res(ret)

        argval = argval[:1] + [argval[1]+".not_a_file"] + argval[2:]
        ret = argz.parse(argval, stderr=self.argzerr)
        self.assertEqual(ret, None, 'should have failed validation')

    def test_validator_contains(self):
        argval = ['ABC123', 'tests/json_data.json', 'option1', 'someval']
        r = argz.route(test_routes.route_validator)
        r.key.validator = {'option1': 1, 'option2': 2}

        ret = argz.parse(argval, stderr=self.argzerr)
        f, al, kw = self.check_res(ret)

        argval = argval[:-2] + [argval[-2]+'3'] + argval[-1:]
        ret = argz.parse(argval, stderr=self.argzerr)
        self.assertEqual(ret, None, 'should have failed validation')

    def test_min_int(self):
        r = argz.route(test_routes.route_min)
        r.count.min = 1
        r.count.adapter = [int]

        ret = argz.parse('3', stderr=self.argzerr)
        f, al, kw = self.check_res(ret)

        ret = argz.parse('0', stderr=self.argzerr)
        self.assertEqual(ret, None, 'should have failed validation')

        ret = argz.parse('-1', stderr=self.argzerr)
        self.assertEqual(ret, None, 'should have failed validation')

    def test_min_list(self):
        r = argz.route(test_routes.route_min)
        r.count.min = 2
        r.count.split = ','

        ret = argz.parse('3,2,1', stderr=self.argzerr)
        f, al, kw = self.check_res(ret)

        ret = argz.parse('0', stderr=self.argzerr)
        self.assertEqual(ret, None, 'should have failed validation')

    def test_split(self):
        r = argz.route(test_routes.route_min)
        r.count.min = 2
        r.count.split = ','

        ret = argz.parse('3,2,1', stderr=self.argzerr)
        f, al, kw = self.check_res(ret)
        self.assertEqual(al[0], ['3', '2', '1'])

    def test_adapter_on_split(self):
        r = argz.route(test_routes.route_min)
        r.count.min = 2
        r.count.split = ','
        r.count.adapter = [int]

        ret = argz.parse('3,2,1', stderr=self.argzerr)
        f, al, kw = self.check_res(ret)
        self.assertEqual(al[0], [3, 2, 1])

    def test_switch_basic(self):
        import json
        r = argz.route(test_routes.route_json_dict)
        argval = 'tests/json_data.json -dbg'
        r.jsondict.adapter = [open, json.load]    # will be chained

        with warnings.catch_warnings():
            # py3 json.load warns about not closing file
            warnings.simplefilter("ignore")
            ret = argz.parse(argval, stderr=self.argzerr)

            f, al, kw = self.check_res(ret)
            self.assertEqual(al[1], True)

    def test_switch_with_optional(self):
        r = argz.route(test_routes.test_switch)
        pos_arg_val = 'some_string'
        opt_arg_val = 'opt'
        argval = '{} -dbg'.format(pos_arg_val)

        ret = argz.parse(pos_arg_val, stderr=self.argzerr)

        f, al, kw = self.check_res(ret)
        self.assertEqual(al[0], pos_arg_val)
        self.assertEqual(al[1], None)
        self.assertEqual(al[2], False)


        ret = argz.parse(argval, stderr=self.argzerr)

        f, al, kw = self.check_res(ret)
        self.assertEqual(al[0], pos_arg_val)
        self.assertEqual(al[1], None)
        self.assertEqual(al[2], True)

        argval = '{} {}'.format(pos_arg_val, opt_arg_val)
        ret = argz.parse(argval, stderr=self.argzerr)

        f, al, kw = self.check_res(ret)
        self.assertEqual(al[0], pos_arg_val)
        self.assertEqual(al[1], opt_arg_val)
        self.assertEqual(al[2], False)


    def test_fallback(self):
        argval = ['ABC123', 'tests/json_data.json', 'option1']
        r = argz.route(test_routes.route_validator)
        
        ret = argz.parse(argval, stderr=self.argzerr)
        self.assertEqual(ret, None, 'should have failed validation')
        r.novalidation.fallback = '123'
        ret = argz.parse(argval, stderr=self.argzerr)
        f, al, kw = self.check_res(ret)
        self.assertEqual(al[-1], r.novalidation.fallback)


if __name__ == '__main__':
    unittest.main()
