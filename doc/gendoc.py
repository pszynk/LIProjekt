#!/usr/bin/python
# -*- coding: utf-8 -*-

MODULES_LIST = [
    'liprojekt',
    'liprojekt.conversion',
    'liprojekt.conversion.clauses',
    'liprojekt.conversion.formatting',
    'liprojekt.conversion.formulas',
    'liprojekt.conversion.verification',
    'liprojekt.interface',
    'liprojekt.interface.interface',
    'liprojekt.parsing',
    'liprojekt.parsing.alphabets',
    'liprojekt.parsing.myparsing',
    'liprojekt.parsing.parsers',
    'liprojekt.tests',
    'liprojekt.tests.tests',
]
if __name__ == '__main__':
    from subprocess import call
    call(["pydoc", "-w"]+ MODULES_LIST);
