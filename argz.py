''' argz
\'\'\'
========

Argument parsing for the lazy.

Core Concepts
-------------
- Simplicity over robustness
- Your script _requires_ arguments
- "Consumers" of scripts using this are devlopers themselves

Usage
-----
```python
# $ cat example.py
import json

def func(jsondict, dbg=False):
    """
    put descriptive docstring here
    """
    pass  # use jsondict

if __name__ == '__main__':
    import argz
    f = argz.route(func)
    f.jsondict.adapter = [open, json.load]    # will be chained
    argz.go()                                 # will use sys.argv as input
```
Running:
```console
$ example.py

Usage:
example.py jsondict [-dbg]

for detailed help, use any of (-h, /h, -?, /?, /help, --help)
```
```console
$ example.py -h
|> jsondict [-dbg]
|
|    jsondict
|        adapter         |  [<built-in function open>, <function load at 0x0336B1B0>]
|    dbg
|        default         |  False
|        adapter         |  <type 'bool'>
|
|- - doc - -
|
|    put descriptive docstring here
|_ _ _ _ _ _
```


Installation
------------
Download the file or use pip:
```
pip install argz
```


Passing Arguments: Named vs Positional
--------------------------------------
You can pass any argument by name or by position.
An argument will be treated as named if it starts with a double dash `--`, otherwise* as positional.

You can pass a mishmash of positional and named arguments, because `argz` will keep track of which arguments are left to parse according to the order in the function's definition.

\* except for [switches](#Switches)

Arguments From File
-------------------
To pass arguments from a file to your script you can prefix its path with `@`. This must be the first argument passed to the script. If there are multiple routes the route name must be included in the file as the first argument.

Currently `argz` does not allow a mixture of file input and command line input.


Adapter
-------
A callable object that accepts the string argument and returns the 'adapted' value, which will passed later to the routed function.

If the adapter is instead a sequence, each will be chained so that the return value of the former is passed to the latter, using the last returned value as input to the routed function.

To abort the parsing process, you may raise any exception. The `message` property will be printed to the user.


Validator
---------
Used to validate the input before any adapting is done. Can be one of the following types:
- regex string: will be used to match against the input
- callable object: will be called with the input string. Any exception or non-truthy value will abort the parsing process and display a message to the user.
- Any object that implements  `__contains__`
```python
def func(alphanum, filepath, key, novalidation):
    """
    put descriptive docstring here
    """
    pass

# ...
f = argz.route(func)

f.alphanum.validator = '[a-zA-Z0-9]{2,}'
f.filepath.validator = os.path.isfile
f.key.validator = {'option1': 1, 'option2': 2}

argz.go()
```

Min / Max
---------
You can set a minimum and/or maximum value for an argument:

```python
def func(count):
    """
    put descriptive docstring here
    """
    pass

# ...
f = argz.route(func)
f.count.min = 1  # same for max
argz.go()

```
These constraints will be checked after validation and adapters have run.
Both values are inclusive. For example, `unsigned char` range would be:
`min = 0; max = 0xFF`


Fallback vs Default
-------------------
Setting either one will deem an argument optional, however, they have one major difference:

> Default is any value that will be passed to the called route **without any** parsing or validation.

> Fallback is a **string** value that will pass all validations and parsing, as if it was specified via the commandline.


If the argument was not provieded via the commandline, `argz` will use either `fallback` or `default`. The `fallback` value takes precedence.

If a default value is specified in the function definition, `argz` will use it as the argument's default and infer a default adapter in some cases (see `SUPPORTED_INFERRED_ADAPTERS`).


Switches
--------
Function arguments that have a default **boolean** value will be inferred as a switch. This means this argument can also be passed using a single dash without a value following it (e.g. `-dbg`). Doing so will 'switch' the default value (`False` to `True`, and vice versa)

The `dbg` argument from the `example.py` code above demonstrates this.

Using Split
-------------------
Setting the `split` member of an argument changes a few things:

- the input will be split using that string
- if set, `min` \ `max` value(s) will be checked against the length of the list
- the validator and parser(s) will be called for each item in the list **separately**


Varargs and Kwargs:
-------------------
If the function accepts them, any additional positional and named arguments will be passed in varargs/kwargs respectively.

Adapter(s) and validator will be called with the entire list/dictionary, and they must return a value of the same type.

Accessing function arguments
----------------------------
Setting arguments properties can be done in two ways:

- by name:
```python
f = argz.route(func)
f.myvar.min = 1
```

- by index:
```python
f = argz.route(func)
f[0].min = 1
```
 > Note: argument names are case sensitive


Parsing Flow
--------------
The following graph illustrates the flow for parsing an argument (varargs\kwargs do not support splitting the input):
```
 +------------+  +-----------+          +-----------+
 |  fallback  |  |   input   |          |  default  |
 +-----+------+  +-----+-----+          +-----+-----+
       |               |                      |
       +-------+-------+                      |
               |                              |
               v                              |
          +----+-----+                        |
          |  split?  |                        |
          +---+-+----+                        |
              | |                             |
              | | Yes                         |
   +----------+ v                             |
   |   +--------+--------+                    |
No |   |  min / max len  |                    |
   |   +--------+--------+                    |
   +-------+    |                             |
           |    |    +-----------+            |
           V    v    v           |            |
       +--------+----+---+       |            |
       |                 |       |            |
       |    validator    |       |            |
       |        +        |       |            |
       |        v        |       |            |
       |  adapter chain  |       |            |
       |                 |       |            |
       +--------+----+---+       |            |
                |    |           |            |
                |    | split?    |            |
                |    |           |            |
                |    +-----------+            |
       +--------+---------+                   |
       |  min / max check | (if not split)    |
       +--------+---------+                   |
                |                             |
                v                             |
        +-------+--------+                    |
        |  return value  | <------------------+
        +----------------+

```

Using Multiple Routes
-----------
You can 'export' several different routes using `argz`.
This means that the user must choose which one they want to run:
```python
# $ cat example_routes.py
from os.path import isfile

def entry1(filepath, dbg=False):
    pass

def entry2(count):
    pass

# ...

if __name__ == '__main__':
    import argz
    argz.route(entry1).validator = isfile
    argz.route(entry2).count.min = 1
    argz.go()
```
Running:
```console
$ example_routes.py

Available routes:
> 'entry1' filepath [-dbg]
> 'entry2' count

for detailed help, use any of (-h, /h, -?, /?, /help, --help)
you can specify the route name (e.g. -h MY_ROUTE)
```
```console
$ example_routes.py -h
|> 'entry1' filepath [-dbg]
|
|    filepath
|    dbg
|        default         |  False
|        adapter         |  <type 'bool'>
|_ _ _ _ _ _

|> 'entry2' count
|
|    count
|        1 <= X
|_ _ _ _ _ _
```
> Note: routes are allowed to run without arguments, so long as there is more than one route available.


Overriding Defaults
-------------------
You can specify custom doc string to print when verbose help is shown by passing `doc` argument to `route`. To completely suppress it pass an empty string.

If you use a single route that accepts an argument whose name is in `HELP_OPTIONS`, you can replace those by specifying a `custom_help_options` list when calling `go`.


Tested on
---------
- Python 2.7.15, windows 10
- Python 3.7.2, windows 10


Troubleshooting
---------------

To enable logging:
```bash
set ARGZ_LOG=<LOG_LEVEL>
```
`LOG_LEVEL` will be passed to `Logger.setLevel`

Testing
-------
added some unit-tests, run `runtests.bat`

License
----
MIT

TODO
----
- Allow mixture of file input and command-line input
- Normalize/strip underscores ( `_` ) in argument names
- Handle name collisions with `Route` object properties
- Infer from type annotaitons/hints (py3 signature?)

Take a look at the code:
------------------------
```python
'''  # #  '''
from __future__ import print_function
import warnings
import inspect

import sys
import os
import logging
import re
from collections import OrderedDict
    
version = (0, 1, 4)

if sys.version_info.major > 2:
    unicode = str
    basestring = (str, bytes)

def _get_handler(stream=sys.stdout):
    handler = logging.StreamHandler(stream)
    formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)-9s | %(lineno)4d | %(message)s', '%Y%m%d %H:%M:%S')
    handler.setFormatter(formatter)
    return handler

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
default_log_handler = _get_handler()

try:
    _loglevel = int(os.getenv('ARGZ_LOG', 0))
except:
    _loglevel = 0

if _loglevel:
    logger.addHandler(default_log_handler)
    logger.setLevel(_loglevel)
    logger.info('logging level set to: %d' % _loglevel)


class ArgzError(Exception):
    def __init__(self, message='', extras='', route=''):
        self.message = message
        self.extras = extras
        self.route = route


class ArgumentRejectedError(ArgzError):
    pass


class ArgumentMissingError(ArgzError):
    pass


class MissingRouteError(ArgzError):
    pass


class RequestHelpError(ArgzError):
    pass


ARG_SPLIT = ' '
HELP_OPTIONS = ('-h', '/h', '-?', '/?', '/help', '--help')
INFER_DEFAULTS = True
FILE_INPUT_MARKER = '@'
SUPPORTED_INFERRED_ADAPTERS = (bool, str, unicode, bytes, int, float, )


class Arg(object):
    __slots__ = (
        # inferred from definition
        'name',
        'required',
        '_isswitch',
        '_isvararg',
        '_iskwarg',

        # user supplied
        'description',
        'validator',
        'adapter',
        'split',
        'min',
        'max',


        '_fallback',
        '_default',
    )

    def __init__(self, name):
        self.name = name
        self.description = ''

        self.required = True

        self._fallback = None

        self.split = None

        self.validator = None
        self.adapter = None

        self.min = None
        self.max = None

        self._default = None

        self.init()

    def init(self):
        pass

    @property
    def fallback(self):
        return self._fallback

    @fallback.setter
    def fallback(self, v):
        if not isinstance(v, basestring):
            raise Exception('unsupported fallback type: {}'.format(type(v)))

        self._fallback = v
        self.required = False

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, v):
        self._default = v
        self.required = False

    @property
    def isvararg(self):
        return False

    @property
    def iskwarg(self):
        return False

    @property
    def isswitch(self):
        return False

    def __str__(self):

        if self.required:
            return self.name

        return '[{}]'.format(self.name)

    def __repr__(self):
        parts = ['']

        if not self.required:
            if self.fallback is not None:
                parts.append('{:<15} |  {}'.format('fallback', self.fallback))
            else:
                parts.append('{:<15} |  {}'.format('default', self.default))

        if self.validator:
            parts.append('{:<15} |  {}'.format('validator', self.validator))
        else:
            mimax = 'X'
            if self.min is not None:
                mimax = '{} <= {}'.format(self.min, mimax)
            if self.max is not None:
                mimax = '{} <= {}'.format(mimax, self.max)
            if mimax != 'X':
                parts.append(mimax)

        if self.adapter:
            parts.append('{:<15} |  {}'.format('adapter', self.adapter))

        return '{:<15} {}'.format(self.name, self.description) + '\n|        '.join(parts)

    def _get_validator(self):
        val = None
        if self.validator:
            logger.info('%s has validator', self.name)
            if callable(self.validator):
                logger.info('validtor is callable')
                val = self.validator
            elif isinstance(self.validator, basestring):
                logger.info('validtor should be regex')
                pattern = re.compile(self.validator)
                val = pattern.match
            else:  # default assume list
                logger.info('validtor is choice list')
                # using lambda just in case the class is iterable and did not implement __contains__
                # VSCode's formatter does not like it without parenthesis
                val = (lambda x: x in self.validator)

        return val

    def _get_adapters(self):
        return [self.adapter] if callable(self.adapter) else self.adapter or []

    def _try_parsing(self, parts):
        """
        _try_parsing always returns list, even with 1 value
        """
        val = self._get_validator()
        adapters = self._get_adapters()
        oparts = []
        for p in parts:
            fail = ''
            if val:
                try:
                    r = val(p)
                except Exception as e:
                    logger.debug('validator for "%s" raised: %s',
                                 p, e.message or "")
                    fail = e.message

                if fail or not r:
                    logger.info('"%s" failed validation: %s', p, val)
                    raise ArgumentRejectedError(
                        '"{}" failed validation for "{}" using {}'.format(self.name, p, val), fail, route=self)

            logger.info('"%s" is valid', p)
            try:
                for i, a in enumerate(adapters):
                    p = a(p)
                    logger.info('"%s" adapted successfully using %s', p, a)

            except Exception as e:
                logger.debug(
                    'adapter %d: %s rasied error for "%s": %s', i, a, p, e.message)
                raise ArgumentRejectedError(
                    '"{}" failed adapter {} for "{}"'.format(self.name, a, p), e.message)

            oparts.append(p)

        return oparts

    def _check_min_max(self, v):
        if self.max:
            logger.debug('max:{}, v:{}'.format(self.max, v))

        if self.min:
            logger.debug('min:{}, v:{}'.format(self.min, v))

        if self.min is not None and v < self.min:
            raise ArgumentRejectedError(
                '"{}" must be greater than or equal to {}, {} was provided'.format(self.name, self.min, v))
        if self.max is not None and v > self.max:
            raise ArgumentRejectedError(
                '"{}" must be less than or equal to {}, {} was provided'.format(self.name, self.max, v))

    def parse(self, argv):
        assert isinstance(
            argv, basestring), 'argv (for "%s") value must be string for parsing instead of  %s' % (self.name, argv)
        parts = argv.split(self.split) if self.split else [argv]
        if self.split:
            self._check_min_max(len(parts))

        v = self._try_parsing(parts)
        if not self.split:
            # if not using split, min/max are checked against the value itself. 
            v = v[0]  # unpack list of 1 item
            self._check_min_max(v)

        return v


class Switcharg(Arg):
    __slots__ = ()

    @property
    def isswitch(self):
        return True

    def __str__(self):
        return '[-{}]'.format(self.name)


class Varargs(Arg):
    __slots__ = (
        '_args'
    )

    def init(self):
        self._args = []

    @property
    def isvararg(self):
        return True

    def __str__(self):
        return '[*{}1 ...]'.format(self.name)

    def add(self, argv, name=None):
        self._args.append(argv)

    def parse(self):
        r = self._try_parsing([self._args])[0]

        assert isinstance(r, list), '{} is not a list'.format(r)
        return r

    def __len__(self):
        return len(self._args)


class Kwargs(Arg):
    __slots__ = (
        '_kwargs'
    )

    @property
    def iskwarg(self):
        return True

    def __str__(self):
        return '[--{}1 value1 ...]'.format(self.name)

    def add(self, argv, name):
        if name in self._kwargs:
            raise ArgumentRejectedError(
                'kwarg "{}" already exists. can\'t set it to "{}"'.format(name, argv))
        self._kwargs[name] = argv

    def init(self):
        self._kwargs = {}

    def parse(self):
        r = self._try_parsing([self._kwargs])[0]

        assert isinstance(r, dict), '{} is not a dict'.format(r)
        return r

    def __len__(self):
        return len(self._kwargs)


class Route(object):

    def __init__(self, fref, doc=None):

        if not inspect.isfunction(fref):
            if not fref.im_self:  # not bound
                raise Exception('{} is not a function'.format(fref))

        self.__fref = fref
        self.__doc = doc if doc is not None else fref.__doc__
        try:
            self.__filename = os.path.basename(inspect.getsourcefile(self.__fref))
        except TypeError:
            self.__filename = '__interpreter__'
        with warnings.catch_warnings():
            # python 3 changed getargspec to deprecated so it will print warnings.  Python 3.6 reversed that decision so will be ignored: https://docs.python.org/3/library/inspect.html#inspect.getfullargspec
            warnings.simplefilter("ignore")
            argspec = inspect.getargspec(fref) 
        self.__kwargs = None
        self.__varargs = None

        if argspec.keywords:
            logger.info("kwargs allowed as: '%s'", argspec.keywords)
            self.__kwargs = Kwargs(argspec.keywords)

        if argspec.varargs:
            logger.info("varargs allowed as: '%s'", argspec.varargs)
            self.__varargs = Varargs(argspec.varargs)

        defaults = argspec.defaults or []
        defaults_start = len(argspec.args) - len(defaults)
        self.__args = OrderedDict()
        for i, an in enumerate(argspec.args):
            logger.info("discovered argument: '%s'", an)

            if '_' in an:
                logger.warn("'%s' contains underscores", an)

            arg = Arg(an)

            if i >= defaults_start:
                # means not required
                arg.default = argspec.defaults[i-defaults_start]
                logger.debug("'%s' has default value of %s",
                             an, str(arg.default))
                if INFER_DEFAULTS and isinstance(arg.default, SUPPORTED_INFERRED_ADAPTERS):
                    arg.adapter = type(arg.default)
                    logger.debug("'%s' has infered adapter: %s",
                                 an, arg.adapter)

                    if arg.adapter == bool:  # if the param is a boolean, use it as switch in commandline
                        logger.debug("'%s' inferred as switch", an)

                        swarg = Switcharg(an)
                        swarg.default = arg.default
                        swarg.adapter = arg.adapter
                        arg = swarg

            self.__args[an] = arg

        bad_names = set(self.__dict__) & set(self.__args)
        if bad_names:
            logger.error('name collision for: %s', bad_names)
            raise Exception(
                '{} will shadow Arg class properties'.format(bad_names))

    def __call__(self, parts):
        logger.info("'%s' route called with %s", self.__fref.__name__, parts)

        leftover = list(self.__args.values())  # should not change the dict values
        parsed_dict = {}
        while parts:
            argv = None
            supplied_switch = False
            positional = False
            p = parts.pop(0)
            logger.debug("processing '%s'", p)
            if p.startswith('--'):
                argn = p[2:]
                logger.debug('%s is named', p)
            elif p.startswith('-'):
                # switches are only allowed with kwargs
                argn = p[1:]
                supplied_switch = True
                logger.debug('%s is a switch', p)
            else:
                logger.debug('%s is positional', p)
                positional = True
                argn = None

            if not argn and not positional:
                raise ArgumentRejectedError(
                    'positional arguments cannot begin with "--" or "-", pass them as named', route=self)

            if argn and argn not in self.__args and self.__kwargs is None:
                logger.info(
                    "'%s' not allowed and %s does not support kwargs", argn, self.__fref.__name__)
                raise ArgumentRejectedError("unsupported argument name: '{}', {} does not support kwargs".format(
                    argn,  self.__fref.__name__), route=self)

            if positional:
                argv = p
                if not leftover and self.__varargs is None:
                    raise ArgumentRejectedError(
                        "positional value '{}' provided with no vararg support".format(argv), route=self)

                if not leftover:
                    self.__varargs.add(argv)
                    logger.debug(
                        "'%s' was provided to varargs, will be parsed later", argv)
                    continue

                t_arg = leftover.pop(0)
                argn = t_arg.name
                logger.debug(
                    "'%s' was provided as positional to %s", argv, argn)
            else:
                logger.debug(
                    "'%s' discovered as named", argn)

                if argn not in self.__args:
                    logger.debug(
                        "'%s' not found in args, will be put in kwargs, will be parsed later", argn)
                    if self.__kwargs is None:
                        raise ArgumentRejectedError(
                            "'{}' not accepted, and no kwargs support".format(argn), route=self)

                    if supplied_switch:
                        logger.info(
                            "kwargs does not support switches: '%s'", p)
                        raise ArgumentRejectedError(
                            "switches are not supported in kwargs ('{}')".format(p), route=self)

                    try:
                        argv = parts.pop(0)
                    except IndexError:
                        logger.info(
                            "no value specified for '%s' for kwargs", p)
                        raise ArgumentMissingError(
                            'Missing value for kwarg argument: {}'.format(p), route=self)

                    self.__kwargs.add(argv, argn)  # could throw Rejected
                    continue

                logger.debug("'%s' found in func", argn)
                t_arg = self.__args[argn]
                if t_arg not in leftover:
                    logger.info('"%s" was already set', argn)
                    raise ArgumentRejectedError('"%s" was already set' % argn)
                leftover.remove(t_arg)

                if supplied_switch and not t_arg.isswitch:
                    logger.info(
                        "'%s' provided as switch despite not inferred as one", p)
                    raise ArgumentRejectedError(
                        "'{}' is not a switch (provided: '{}'),".format(argn, p))

                if t_arg.isswitch and supplied_switch:
                    # no value needed from commandline since this is a switch
                    parsed_dict[t_arg.name] = not t_arg.default
                    continue
                try:
                    argv = parts.pop(0)
                except IndexError:
                    logger.info("no value specified for '%s'", p)
                    raise ArgumentMissingError(
                        'Missing value for named argument: {}'.format(p), route=self)

            logger.info("calling parse on '%s' for '%s'", argv, argn)
            parsed_arg = t_arg.parse(argv)
            logger.debug('"%s" set to %s', t_arg.name, parsed_arg)

            assert argn not in parsed_dict, '{} already in {}'.format(
                argn, parsed_dict)
            parsed_dict[argn] = parsed_arg

        for leftover_arg in leftover:
            logger.debug(
                'setting up leftovers with default/fallback values (%d left over)', len(leftover))
            if leftover_arg.required:
                logger.info(
                    "no value specified for '%s', it is required", leftover_arg.name)
                raise ArgumentMissingError(
                    "argument '{}' is required".format(leftover_arg.name), route=self)

            if leftover_arg.fallback is not None:
                logger.debug(
                    "calling parse using fallback: '%s' on '%s' ", leftover_arg.fallback, leftover_arg.name)
                parsed_arg = leftover_arg.parse(leftover_arg.fallback)
                parsed_dict[leftover_arg.name] = parsed_arg
            else:
                logger.debug(
                    "skipping parse using default: '%s' on '%s' ", leftover_arg.default, leftover_arg.name)
                parsed_dict[leftover_arg.name] = leftover_arg.default

        names = list(self.__args.keys())
        out_args = {}
        for argn in parsed_dict:
            out_args[names.index(argn)] = parsed_dict[argn]

        arglist = [out_args[key]
                   for key in sorted(out_args.keys(), reverse=False)]

        if self.__varargs is not None and len(self.__varargs):
            logger.debug('going to parse varargs (len: %d)',
                         len(self.__varargs))
            arglist.extend(self.__varargs.parse())

        argkw = {}
        if self.__kwargs and len(self.__kwargs):
            bad_names = set(parsed_dict) & set(self.__kwargs._kwargs)

            if bad_names:
                raise ArgzError(
                    '{} will shadow other input to func'.format(bad_names), route=self)

            logger.debug('going to parse kwrargs (len: %d)',
                         len(self.__kwargs))
            argkw = self.__kwargs.parse()

        return self.__fref, arglist, argkw

    def __getitem__(self, i):
        return self.__args[self.__args.keys()[i]]

    def __getattr__(self, n):
        return self.__args[n]

    def __dir__(self):
        return self.__args.keys()

    def __iter__(self):
        return iter(self.__args)

    def __str__(self):
        """
        return usage of target
        """
        s = []
        for an in self.__args:
            a = self.__args[an]
            s.append(str(a))
        for a in [self.__kwargs, self.__varargs]:
            if a is not None:  # checks None because kwargs/varargs implement __len__
                s.append(str(a))
        return "'"+self.__fref.__name__+"'" + ' ' + ' '.join(s)

    def __repr__(self):

        s = [str(self), '\n|']
        for an in self.__args:
            a = self.__args[an]
            s.append('\n|    '+repr(a))

        for a in [self.__kwargs, self.__varargs]:
            if a:
                s.append('\n|    '+repr(a))

        s.append('\n')

        if self.__doc:
            doc = self.__doc
            if doc.rstrip('\t').rstrip(' ')[-1] != '\n':
                doc += '\n'
            s.append('|\n|'+'- '*2 + 'doc' + ' -'*2)
            s.append('\n|')
            if doc[0] not in ['\t', ' ', '\n']:
                doc = '\n'+' ' * 4 + doc
            s.append(doc.rstrip(' ').replace('\n', '\n|'))
        else:
            s.append('|')

        s.append('_ '*6)

        return ''.join(s) + '\n'



class TargetList(object):
    """
    When this object is called with a function reference it will be added as a route. 
    Pass `doc` argument to override the docstring printing on verbose help
    """

    def __init__(self):
        self.__name__ = 'route'
        self._targets = OrderedDict()

    def __call__(self, fref, doc=None):
        logger.info("adding route to: '%s'", fref.__name__)

        if fref.__name__ in self._targets:
            raise ArgzError('{} already exists'.format(fref.__name__))

        # TODO: replace assert with exception
        assert fref.__name__ not in self.__dict__, 'same name as member'

        r = self._targets[fref.__name__] = Route(fref, doc=doc)
        return r

    def __contains__(self, item):
        return item in self._targets

    def __len__(self):
        return len(self._targets)

    def __getattr__(self, n):
        return self._targets[n]

    def __getitem__(self, i):
        return self._targets[i]

    def getDefaultRoute(self):  # TODO: what if shadows name?
        return list(self._targets.values())[0] if len(self._targets) == 1 else None

    def __dir__(self):
        return self._targets.keys()

    def __str__(self):
        """
        return usage of all targets
        """
        if len(self._targets) == 1:
            return _get_route_argshelp(self.getDefaultRoute())
            # return ' '.join(str(self.getDefaultRoute()).split(' ')[1:])
        ss = ['']
        mxln = len(max(self._targets.keys(), key=len)) + 3
        for rn in self._targets:
            r = self._targets[rn]
            ss.append(str(r))
        return '\nAvailable routes:' + '\n> '.join(ss)

    def __repr__(self):
        ss = []
        if len(self._targets) == 1:
            return  '|> ' +_get_route_argshelp(self.getDefaultRoute(),f=repr)
            # return '|> ' + ' '.join(repr(self.getDefaultRoute()).split(' ')[1:])

        for rn in self._targets:
            r = self._targets[rn]
            ss.append("|> {}".format(repr(r)))
        return '\n'.join(ss)

    __nonzero__ = __len__
    def __bool__(self):
        return self.__len__() > 0


route = TargetList()
def _get_route_argshelp(r, f=str):
    if len(route) == 1:
        return ' '.join(f(r).split(' ')[1:])
    return f(r)

def _parse(parts, help_options):
    if not route:
        raise Exception('No targets provided')

    if not parts:
        logger.info('there are no arguments, show basic usage')
        raise RequestHelpError()

    p0 = parts[0]
    if p0.lower() in help_options:
        logger.debug('user requested help: {}'.format(p0))
        if len(parts) > 1 and parts[1] in route:
            logger.debug('showing info on specific route: {}'.format(parts[1]))
            raise RequestHelpError("> '{}' {}".format(
                parts[1], repr(route[parts[1]])))
        logger.debug('showing detailed help')
        raise RequestHelpError(p0)

    def_route = route.getDefaultRoute()
    if not def_route:  # multiple available targets
        try:
            def_route = route[p0]
            parts = parts[1:]
            logger.info("'%s' route taken", def_route)
        except KeyError:
            # will print help of all targets
            logger.debug('user requested unknown route: {}'.format(p0))
            raise MissingRouteError(p0)
    else:
        logger.info("only default route available: '%s'", def_route)

    f, parsed_args, parsed_kwargs = def_route(
        parts)  # can throw ArgumentRejectedError
    return f, parsed_args, parsed_kwargs


def _get_parts_from_args(args):
    filename = ''
    if args is None:
        logger.info('using sys.argv')
        filename = sys.argv[0]
        parts = sys.argv[1:]
        if filename == '-m':
            assert len(
                sys.argv) > 1, 'file called with "-m" but has no other arguments'
            filename = sys.argv[1]
            logger.info('%s', filename)
            parts = sys.argv[2:]
            filename = os.path.basename(filename)
    else:
        if not args:
            return [], filename

        if isinstance(args, (list,)):
            return args[:], filename # return a copy of the list

        try:
            # TODO: remove the try/except
            parts = args.split(ARG_SPLIT)
            logger.info("parsed input split using '%s'", ARG_SPLIT)
        except AttributeError:
            logger.info("using args input as is")

    # option to read parts from file
    if parts and parts[0][0] == FILE_INPUT_MARKER:
        fpath = parts[0][1:]
        logger.info('reading input from file "%s"', fpath)
        if not os.path.isfile(fpath):
            raise ArgzError('"{}" not found for argument input', fpath)
        fileparts = open(fpath, 'r').read().split(ARG_SPLIT)

        if len(parts) > 1:
            logger.warn(
                'mixed argument input not supported yet and will be ignored: %s', args[1:])
        parts = fileparts

    logger.info("arguments: %s", str(parts))
    return parts, filename

def clear():
    '''
    resets existing all routes
    '''
    global route
    route = TargetList()


def parse(args=None, custom_help_options=HELP_OPTIONS, stderr=sys.stderr):
    '''
    Parse arguments and return tuple of target function, arglist and kwargs

    :param str/list/None args: The arguments to parse. use sys.argv if None. 
    :param list custom_help_options: if first argument is in this list will show verbose help.  Use if the default help flags override an argument name. 
    '''
    
    parts, filename = _get_parts_from_args(args)
    try:
        retval = _parse(parts, custom_help_options)
    except RequestHelpError as e:
        if e.message:
            if e.message in custom_help_options:
                print(repr(route), file=stderr)  # detailed help
            else:  # is a route help string
                print(e.message, file=stderr)
        else:
            if len(route) == 1:
                print('', file=stderr)
                print('Usage:', file=stderr)
                print(filename + ' ' + str(route), file=stderr)  # basic usage
            else:
                print(route, file=stderr)  # basic usage
            print('', file=stderr)
            print('for detailed help, use any of ' +
                  str(custom_help_options).replace("'", ''), file=stderr)
            if len(route) > 1:
                print('you can specify the route name (e.g. -h MY_ROUTE)', file=stderr)
    except MissingRouteError as e:
        if e.message:
            print('route `{}` not found'.format(e.message), file=stderr)
        else:
            print('please choose a route:', file=stderr)
        print(route, file=stderr)
    except ArgumentMissingError as e:
        print(e.message, file=stderr)
        print(e.extras, file=stderr)
        if e.route:
            print('Usage:', file=stderr)
            print(filename + ' ' + _get_route_argshelp(e.route), file=stderr)

    except ArgumentRejectedError as e:
        print(e.message, file=stderr)
        print(e.extras, file=stderr)
        print(filename + ' ' + str(e.route or route), file=stderr)
    except ArgzError:
        # general error
        print(e.message, file=stderr)
        print(e.extras, file=stderr)
        print(e.route, file=stderr)
    else:
        logger.debug('arguments parsed successfully')
        return retval

    logger.warning('failed parsing args')
    return None

def go(args=None, custom_help_options=HELP_OPTIONS, stderr=sys.stderr):
    '''
    Parse arguments and call appropriate route

    :param str/list/None args: The arguments to parse. use sys.argv if None. 
    :param list custom_help_options: if first argument is in this list will show verbose help.  Use if the default help flags override an argument name. 
    '''

    parsed = parse(args, custom_help_options, stderr)
    if not parsed:
        # TODO: consider throwing exception?
        return None

    f, arglist, argdict = parsed
    logger.info('%s with %s, %s', f.__name__, arglist, argdict)
    # let target throw exceptions as they please
    return f(*arglist, **argdict)
