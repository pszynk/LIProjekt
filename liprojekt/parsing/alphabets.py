# -*- coding: utf-8 -*-

'''
Created on 02-03-2013

@author: pawel

Moduł zawoerakący klasy reprezentujące możliwe alfabety
w jakimi zapisane są formuły logiczne podawane przez urzytkownika
'''

class AlphabetMap(object):
    '''
    Wirtualna klasa reorezentująca alfabet, składnię formuł logicznych
    '''
       
    def getOperators(self):
        '''
        zwraca mapę symboli operatorów logicznych
        '''
        return self.OPERATORS
    
    def getOperatorSymbol(self, key):
        '''
        zwraca rządany symbol operatora, jeżeli nie ma takiego operatora
        w alfabecie, rzucany jest wyjątek
        '''
        try:
            return self.getOperators()[key]
        except KeyError:
            raise Exception("Alfabet nie ma symbolu operatora o kodzie `"+key+"`")
        
    def getConstants(self):
        '''
        zwraca mapę symboli stałych logicznych
        '''
        return self.CONSTANTS
    
    def getConstantSymbol(self, key):
        '''
        zwraca rządany symbol operatora, jeżeli nie ma takiego symbolu stałej logicznej
        w alfabecie, rzucany jest wyjątek
        '''
        try:
            return self.getConstants()[key]
        except KeyError:
            raise Exception("Alfabet nie ma symbolu stałej o kodzie `"+key+"`")
            
    def getParenthesis(self):
        '''
        zwraca mapę symboli nawiasów
        '''
        return self.PARENTHESIS
    
    def getParenthesisSymbol(self, key):
        '''
        zwraca rządany symbol nawiasu, jeżeli nie ma takiego symbolu nawiasu
        w alfabecie, rzucany jest wyjątek
        '''
        try:
            return self.getParenthesis()[key]
        except KeyError:
            raise Exception("Alfabet nie ma symbolu nawiasu o kodzie `"+key+"`")
        
    def getNotFormat(self):
        '''
        zwraca format operatora zaprzeczenia
        '''
        return self.NOT_FORMAT
    
    def notNeedSpace(self):
        return self.NOT_NEED_SPACE
    
    
    
    def getLegend(self):
        '''
        Zwraca legende alfabetu w postaci łańcycha znaków
        '''
        legend = "*"*5 + " " + self.NAME + " " + "*"*5 + "\n"
        legend += "-"*20 + "\n"
        legend += "Operatory:\n"
        for name, symbol in self.OPERATORS.items():
            legend += " "*3+name.ljust(6)+" ".rjust(10, '-')+symbol+"\n"
        
        legend+= "\n"
        legend += "-"*20 + "\n"
        legend += "Stałe:\n"
        for name, symbol in self.CONSTANTS.items():
            legend += " "*3+name.ljust(6)+" ".rjust(10, '-')+symbol+"\n"
        legend+= "\n"

        legend += "-"*20 + "\n"
        legend += "Nawiasy:\n"
        for name, symbol in self.PARENTHESIS.items():
            legend += " "*3+name.ljust(6)+" ".rjust(10, '-')+symbol+"\n"
        return legend;
        
        def __str__(self):
            return self.NAME
    
class SymbolicAlphabetMap(AlphabetMap):
    '''
    Składnia oparta na symbolach
    '''
    NAME = "Składnia znakowa"
    OPERATORS = {
        'and':      '&',
        'or':       '|',
        'impL':     '=>',
        'equ':      '<=>',
        'not':      '~'
    }
    
    CONSTANTS = {
        'false':    'F',
        'true':     'T'
    }

    PARENTHESIS = {
        '(':        '(',
        ')':        ')'
    }
    
    NOT_FORMAT = "{not}{subformula}"
    NOT_NEED_SPACE = False
    
class WordAlphabetMap(AlphabetMap):
    '''
    Składnia oparta na słowach
    '''
    
    NAME = "Składnia słowna"
    OPERATORS = {
        'and':      'and',
        'or':       'or',
        'impL':     'imp',
        'equ':      'equ',
        'not':      'not'
    }
    
    CONSTANTS = {
        'false':    'false',
        'true':     'true'
    }
    
    PARENTHESIS = {
        '(':        '(',
        ')':        ')'
    }
    
    NOT_FORMAT = "{not} {subformula}"
    NOT_NEED_SPACE = True