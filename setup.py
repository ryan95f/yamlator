#!/usr/bin/env python

import setuptools

VERSION = '0.1.2'
PACKAGE_NAME = 'yamlator'
DESCRIPTION = 'Yamlator is a CLI tool that allows a YAML file to be validated using a lightweight schema language'  # nopep8


def create_long_description():
    with open('README.md', 'r', encoding='utf-8') as fh:
        long_description = fh.read()

        # Replace the relative paths in the ReadMe.md
        # with links to the documentation in GitHub
        long_description = long_description.replace(
            './docs/schema_components.md',
            'https://github.com/ryan95f/yamlator/blob/main/docs/schema_components.md'  # nopep8
        )

        long_description = long_description.replace(
            './example/',
            'https://github.com/ryan95f/yamlator/tree/main/example'
        )

        long_description = long_description.replace(
            './docs/setting_up_the_environment.md',
            'https://github.com/ryan95f/yamlator/blob/main/docs/setting_up_the_environment.md'  # nopep8
        )
        return long_description


long_description = create_long_description()

setuptools.setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    license='MIT',
    long_description_content_type='text/markdown',
    url='https://github.com/ryan95f/yamlator',
    author='Ryan Flynn',
    packages=setuptools.find_packages(include=[
        'yamlator',
        'yamlator.validators',
        'yamlator.cmd',
        'yamlator.cmd.outputs'
    ]),
    install_requires=[
        'lark==1.0.0',
        'PyYAML==6.0'
    ],
    python_requires='>=3.7',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent'
    ],
    entry_points={
        'console_scripts': ['yamlator=yamlator.cmd:main']
    },
    package_data={'yamlator': ['grammar/grammar.lark']}
)
