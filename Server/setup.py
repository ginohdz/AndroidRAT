#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(name='AndroidRAT',
	version='1.1',
	author='EquipoAndroid',
	packages=find_packages(),
	entry_points={
		'console_scripts': ['androidrat = app.app:main']
	},
	install_requires=open('requisitos.txt').readlines()
)
