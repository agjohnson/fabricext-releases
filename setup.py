'''
Fabric Release Deployment
'''

from setuptools import setup, find_packages


setup(
    name='fabricext-releases',
    version='0.1',
    url='http://github.com/agjohnson/fabricext-releases',
    license='MIT',
    author='Anthony Johnson',
    author_email='aj@ohess.org',
    description='Fabric transaction and release wrapper',
    long_description=__doc__,
    packages=find_packages(),
    namespace_packages=['fabricext'],
    install_requires=[
        'fabric'
    ]
)
