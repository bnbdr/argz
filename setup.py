from setuptools import setup
import argz


author = 'bnbdr'
setup(
    name='argz',
    version='.'.join(map(str, argz.version)),
    author=author,
    author_email='bad.32@outlook.com',
    url='https://github.com/{}/argz'.format(author),
    description="Argument parsing for the lazy",
    long_description=argz.__doc__,
    long_description_content_type="text/markdown",
    license='MIT',
    keywords='argument parse args',
    py_modules=['argz'],
    classifiers=(
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
