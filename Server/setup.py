#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(name='AndroidRAT',
	version='1.1',
	author='EquipoAndroid',
	packages=find_packages(),
	#Para poder ocupar androidrat como comando
	entry_points={
		'console_scripts': ['androidrat = app.app:main']
	},
	#se instalaran los paquetes que esten en requisitos.txt
	install_requires=open('requisitos.txt').readlines()
)
