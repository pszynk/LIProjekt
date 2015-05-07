# -*- coding: utf-8 -*-

'''
Created on 02-03-2013

@author: pawel

Moduł zawiera narzędzia do parsowania łańcuchów znaków na
formuły logiczne klasy fomulas.Formula
'''


from pyparsing import Literal, Keyword, Word, ParserElement, \
    opAssoc, StringEnd, alphas, alphanums

from liprojekt.conversion.formulas import FormulaFactory
import liprojekt.parsing.myparsing as myparsing

class LogicExprParser(object):
    '''
    Klasa wirtualna, bazowa dla parserów formuł logicznych 
    '''
    pass

class DefaultLogicExprParser(LogicExprParser):
    '''
    Domyślny parser formuł logicznych
    
    Parser wykorzystuje bibliotekę pyparsing.
    
    Gramatyka z godnie z którą parsowane są łańcych zawierające
    formuły logiczne jest następująca:
    
    ======== BNF: boolean exporession ========
    
    order of precedence
    1) NOT    (-)    negation
    2) AND    (&)    conjunction
    3) OR     (|)    disjunction
    4) IMP    (=>)   implication
    5) EQU    (<=>)  equivalence
    
    BNF
    
    <expression> ::= <imp-term> [EQL <imp-term>]*
    <imp-term>   ::= <or-term> [EQL <or-term>]*
    <or-term>    ::= <and-term> [EQL <and-term>]*
    <and-term>   ::= <not-factor> [EQL <not-factor>]*
    <not-factor> ::= [NOT] <factor> 
    <factor>     ::= <literal> | <variable> | <expression>
    <literal>    ::= 0 | 1
    <variable>   ::= <alpha>+[<alpha> | <uscore> | <digit>]*
    -------------------------------------------------------------
    <alpha>      ::= 'A'..'Z' 'a'..'z'
    <uscore>     ::= '_'
    <digit>      ::= '0'..'9'
    '''
    
    def __init__(self, alphabet):
        self.operators = alphabet.getOperators()
        self.constants = alphabet.getConstants()
        self.notNeedSpace = alphabet.notNeedSpace()
        
        self.ffactory = FormulaFactory()
        self.__createGram()
        ParserElement.enablePackrat()
        
        
    def __createGram(self):

        if self.notNeedSpace:
            lNot = Keyword(self.operators['not'])
        else:
            lNot = Literal(self.operators['not'])
        
        lAnd = Literal(self.operators['and'])
        lOr = Literal(self.operators['or'])
        lImp = Literal(self.operators['impL'])
        lEqu = Literal(self.operators['equ'])
        
        lTrue = Keyword(self.constants['true'])
        lFalse = Keyword(self.constants['false'])
        
        lVar = Word(alphas, alphanums+'_')
        
        lVar.setParseAction(self.ffactory.createLogicVariable)
        lTrue.setParseAction(self.ffactory.createLogicTruth)
        lFalse.setParseAction(self.ffactory.createLogicFalse)

        factor = lTrue | lFalse | lVar
        
        expression = myparsing.operatorPrecedence(factor,
        [
         (lNot, 1, opAssoc.RIGHT, self.ffactory.createNotOperation),
         (lAnd, 2, opAssoc.LEFT, self.ffactory.createAndOperation),
         (lOr,  2, opAssoc.LEFT, self.ffactory.createOrOperation),
         (lImp, 2, opAssoc.LEFT, self.ffactory.createImpicationOperation),
         (lEqu, 2, opAssoc.LEFT, self.ffactory.createEquvalenceOperation)
        ],
        [('(', ')'), ('[', ']'), ('{', '}')])
    

        self.final = expression + StringEnd()
        
    def parseString(self, logicExprStr):
        '''
        Zwraca formułę logiczną klasy formulas.Formula,
        po sparsowaniu łańcucha logicExprStr
        '''
        return self.final.parseString(logicExprStr)[0]
    
    def parseFile(self, logicExprFileName):
        '''
        Zwraca formułę logiczną klasy formulas.Formula,
        po sparsowaniu łańcucha znajdującego się w pliku o nazwie
        logicExprFileName
        '''
        return self.final.parseFile(logicExprFileName)[0]
    
    

    
    