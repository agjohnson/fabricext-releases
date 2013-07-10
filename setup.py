'''
Fabric Release Deployment
'''

from setuptools import setup


setup(
    name='fabricext-deploy',
    version='0.1',
    url='http://github.com/agjohnson/fabricext-deploy',
    license='MIT',
    author='Anthony Johnson',
    author_email='aj@ohess.org',
    description='Fabric transaction and release wrapper',
    long_description=__doc__,
    namespace_packages = ['fabricext'],
    install_requires=[
        'fabric'
    ]
)
