#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(name='trojandroid_server',
	packages=find_packages(),
	entry_points={
		'console_scripts': ['androidtrojan = app.app:main']
	},
	install_requires=open('requerimientos.txt').readlines()
)
