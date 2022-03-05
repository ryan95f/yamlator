#!/usr/bin/env python

import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='yamler',
    version='0.1.0',
    description='A tool to validate that a YAML file conforms to a given schema',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Ryan Flynn',
    packages=setuptools.find_packages(include=['yamler']),
    install_requires=[
        'lark==1.0.0',
        'PyYAML==6.0'
    ],
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': ['yamler=yamler.cmd:main']
    },
    package_data={'yamler': ['grammer/grammer.lark']}
)
