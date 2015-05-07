#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 25-04-2013

@author: pawel
'''

from distutils.core import setup

setup(name='LIProjekt',
      version='1.1',
      description='Projekt LI I - sprawdzanie spełnialności formuły i czy jest tautologią',
      author='Paweł Szynkiewicz',
      packages=['liprojekt', 'liprojekt.conversion', 'liprojekt.interface', 
                'liprojekt.parsing', 'liprojekt.tests',],
      scripts=['bin/liprojekt',],
      install_requires=['pyparsing>=1.5.2',],
     )