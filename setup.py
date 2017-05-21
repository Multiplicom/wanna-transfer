import re
import codecs
import os.path
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


requires = [
    'docopt==0.6.2',
    'boto3==1.4.4',
    'softlayer==5.2.5',
    'configparser==3.5.0'
]

setup_options = dict(
    name='wanna-transfer',
    version=find_version("wanna", "__init__.py"),
    description='High level transfer to the cloud',
    long_description=open('README.md').read(),
    author='Piotr Pawlaczek',
    url='http://github.com/piotrpawlaczek/wanna',
    scripts=['bin/wanna', ],
    packages=find_packages(exclude=['tests*']),
    install_requires=requires,
    license="BSD",
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy'
    ),
)

setup(**setup_options)
