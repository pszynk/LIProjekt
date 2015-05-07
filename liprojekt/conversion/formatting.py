# -*- coding: utf-8 -*-
'''
Created on 11-04-2013

@author: pawel

Moduł służy do formatowania formuł logicznych klasy
formulas.Formula na stringi
'''

from liprojekt.conversion.formulas import (AndOperation, OrOperation, NotOperation,
    EquivalenceOperation, ImplicationOperation,  
    LogicFalse, LogicTruth, LogicVariable)
 

class FormulaFormatter(object):
    '''
    classdocs
    '''


    def __init__(self, alphabet):
        '''
        Constructor
        '''
        self.alphabet = alphabet
        
        self.handleMap = \
        {
         AndOperation:          self.__formatAndFormula,
         OrOperation:           self.__formatOrFormula,
         NotOperation:          self.__formatNotFormula,
         EquivalenceOperation:  self.__formatEquFormula,
         ImplicationOperation:  self.__formatImpFormula,
         LogicTruth:            self.__formatLogicTruthFormula,
         LogicFalse:            self.__formatLogicFalseFormula,
         LogicVariable:         self.__formatLogicVariableFormula
         }
        

    def formula2str(self, formula):
        return self.handleMap[formula.__class__](formula)
    
    def __prepSymbol(self, symbol):
        return " "+symbol+" "
    
    def __putInParenths(self, strform):
        return  self.alphabet.getParenthesisSymbol("(")+ \
                strform+                                     \
                self.alphabet.getParenthesisSymbol(")")
    # Consts
    def __formatLogicTruthFormula(self, formula):
        return (self.alphabet.getConstantSymbol('true'))
    
    def __formatLogicFalseFormula(self, formula):
        return (self.alphabet.getConstantSymbol('false'))
    
    # Var
    def __formatLogicVariableFormula(self, formula):
        if formula.isNegated:
            attars = {'subformula': formula.name,
                      'not': self.alphabet.getOperatorSymbol('not')}
            return self.alphabet.getNotFormat().format(**attars)
        return formula.name
    
    # Unary
    def __formatNotFormula(self, formula):
        attars = {'subformula': self.formula2str(formula.subformula),
                  'not': self.alphabet.getOperatorSymbol('not')}
        return self.alphabet.getNotFormat().format(**attars)
    
    # Binary
    def __formatAndFormula(self, formula):
        return self.__putInParenths(
                    (self.__prepSymbol(self.alphabet.getOperatorSymbol('and'))).join(
                                  map(self.formula2str, formula.subformulas)))
    
    def __formatOrFormula(self, formula):
        return self.__putInParenths(
                    (self.__prepSymbol(self.alphabet.getOperatorSymbol('or'))).join(
                                  map(self.formula2str, formula.subformulas)))
    
    
    def __formatEquFormula(self, formula):
        return self.__putInParenths(
                    (self.__prepSymbol(self.alphabet.getOperatorSymbol('equ'))).join(
                                  map(self.formula2str, formula.subformulas)))
    
    def __formatImpFormula(self, formula):
        return self.__putInParenths(
                    (self.__prepSymbol(self.alphabet.getOperatorSymbol('impL'))).join(
                                  map(self.formula2str, formula.subformulas)))
    