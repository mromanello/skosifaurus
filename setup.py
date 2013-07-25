import os
from setuptools import setup, find_packages
import skosifaurus

VERSION = ".".join([str(x) for x in skosifaurus.__version__])

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='skosifaurus',
	author='Matteo Romanello',
	author_email='matteo.romanello@gmail.com',
	url='http://github.com/mromanello/skosifaurus',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    long_description=read('README.md'),
    zip_safe=False,
)
