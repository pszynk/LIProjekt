# -*- coding: utf-8 -*-
'''
Created on 17-03-2013

@author: pawel

Moduł definiuje klasy reprezentujące formuły logiczne. 
Formuła logiczna to struktura hierarchiczna złożona z operacji
logicznych i operandów

operacjie logiczne := NOT, AND, OR, EQU, IMP
operandy           := TRUE, FALSE, <zmienna logiczna>, <formula logiczna>
<formula logiczna> :=  <operand> <operacja logiczna> <operand> albo NOT <operand>
'''


from copy import copy, deepcopy
import logging

class FormulaFactory(object):
    '''
    Fabryka formuł logicznych
    
    klasa pomocnicza do tworzenia formuł logicznych z parsowanych stringów
    '''
    
    def __listToTree(self, BinOperation, formulas, leftAssoc=True):
        
        if not issubclass(BinOperation, BinaryOperation):
            raise TypeError("BinOperation must be subclass of BinaryOperation class")
        
        if leftAssoc:
            formula = BinOperation(formulas[0], formulas[1])
            for subf in formulas[2:]:
                formula = BinOperation(formula, subf)
            return formula
        
        formulas.reverse()     
        formula = BinOperation(formulas[1], formulas[0])
        for subf in formulas[2:]:
            formula = BinOperation(subf, formula)
        return formula
            
        
        
        
### 
    def createLogicTruth(self, tokens):
        return LogicTruth()
    
    def createLogicFalse(self, tokens):
        return LogicFalse()
    
    def createLogicVariable(self, tokens):
        logging.debug("Tworzę zmienną losową o nazwie: %s", tokens[0])
        return LogicVariable(tokens[0])

### 
    def createNotOperation(self, tokens):
        return NotOperation(tokens[0][1])

    def createAndOperation(self, tokens):
        return self.__listToTree(AndOperation, tokens[0][0::2])
    
    def createOrOperation(self, tokens):
        return self.__listToTree(OrOperation, tokens[0][0::2])
    
    def createImpicationOperation(self, tokens):
        return self.__listToTree(ImplicationOperation, tokens[0][0::2], False)
       
    def createEquvalenceOperation(self, tokens):
        return self.__listToTree(EquivalenceOperation, tokens[0][0::2])

class Formula(object):
    '''
    Formuła logiczna, klasa wirtualna
    '''


    def __init__(self, subformulas=[]):
        '''
        Formuła logiczna powstałe z podformuł logicznych (klasy Formula)
        '''
        self._subformulas = map(deepcopy, subformulas)

        

    def __str__(self):
        return "BASE FORMULA"
    
    @property
    def subformulas(self):
        '''
        zwraca listę podformuł
        '''
        return self._subformulas

    
    def negate(self):
        '''
        metoda virtualna
        
        Zwróć zaprzeczenie formuły (jezeli to możliwe, uproszczonej)
        '''
        # TODO zmusic do implementacji
        pass
###
    def makeSimple(self):
        '''
        metoda virtualna
        
        Zwróć uproszczoną formułę. To znaczy jeżeli najwyższy w hierarchi operator to coś innego niż
        AND, OR, przekształć formułę tak, że operator zamieniany jest na operacje NOT, AND, OR
        
        Jeżeli pierwszy w hierarchi jest NOT, próbujemy zepchnąć NOT niżej
        '''
        return self

    
  

###   TODO
#    def __deepcopy__(self):
#        pass 

###########################################################################################

class LogicConst(Formula):
    '''
    Stała logiczna
    '''
    def __init__(self):
        super(LogicConst, self).__init__()

    
    def makeSimple(self):
        '''
        Już w najprostrzej postaci
        '''
        return self
    

class LogicTruth(LogicConst):
    '''
    classdocs
    '''
    
    def __str__(self):
        return "<TRUE>"
   
    def negate(self):
        '''
        zwróć FAŁSZ
        '''
        return LogicFalse()

    
class LogicFalse(LogicConst):
    '''
    classdocs
    '''
    
    def __str__(self):
        return "<FALSE>"
    

    def negate(self):
        '''
        zwróć PRAWDA
        '''
        return LogicTruth()

    

class LogicVariable(Formula):
    '''
    Zmienna logiczna
    
    Właściwie jest to literał, bo może być to zmienna zanegowana.
    '''
    
    
    MAGIC_TRUE  = 't'
    MAGIC_FALSE = 'f'
    def __init__(self, name, isNegated=False):
        '''
        Przy towrzniu zmiennej podawana jest jej nazwa w postaci łańcucha znaków
        
        Zmienna rozpoznawana jest po hashu. Przy czym hash(~~p) = hash(p)
        '''
        super(LogicVariable, self).__init__()
        self.name = name
        self.isNegated = isNegated
        self.__hash = self.__computeHash()
    
    def __computeHash(self):
        if self.isNegated:
            return hash(LogicVariable.MAGIC_FALSE+self.name)
        else:
            return hash(LogicVariable.MAGIC_TRUE+self.name)
    
    def __negate(self):
        self.isNegated = not self.isNegated
        self.__hash = self.__computeHash()
        return self
        
    def negate(self):      
        return copy(self).__negate()
          
    def makeSimple(self):
        '''
        Już w najprostrzej postaci
        '''
        return self
    
    def __hash__(self):
        return self.__hash
    
    def __eq__(self, other):
        return isinstance(other, self.__class__) and hash(self) == hash(other)
        
    def __str__(self):
        if self.isNegated:
            return "<~"+self.name+"[id"+str(id(self))+"hash"+str(hash(self))+"]>" 
        return "<"+self.name+"[id"+str(id(self))+"hash"+str(hash(self))+"]>" #TODO
                
###########################################################################################

class UnaryOperation(Formula):
    '''
    Operacja jednoargumentowa
    '''
    
    def __init__(self, subformula):
        '''
        Constructor
        '''
        super(UnaryOperation, self).__init__([subformula])
    
    @property
    def subformula(self):
        '''
        posiada tylko jedną podformułę
        '''
        return self.subformulas[0]
        

class NotOperation(UnaryOperation):
    '''
    Operacja negacji
    '''

    def negate(self):
        '''
        Podwójna negacja, zwracana jest podformuła
        '''
        return self.subformula
    

    def makeSimple(self):
        '''
        Negacja przesuwana jest w dół.
        '''
        return self.subformula.negate()
    
    
    def __str__(self):
        return "<NOT "+ str(self.subformula)+">"




###########################################################################################

class BinaryOperation(Formula):
    '''
    Operacja dwuargumentowa
    '''
    def __init__(self, leftSubformula, rightSubformula):
        '''
        Constructor
        '''
        super(BinaryOperation, self).__init__([leftSubformula, rightSubformula])
        
    def getLeftSubformula(self):
        '''
        lewa podformuła
        '''
        return self._subformulas[0]
    
    def getRightSubformula(self):
        '''
        prawa podformuła
        '''
        return self._subformulas[1]
    
class AndOperation(BinaryOperation):
    '''
    Operacja koniunkcji
    '''
    
    def negate(self):
        '''
        ~(a & b) = ~a | ~b
        
        prawo De Morgana
        '''
        return OrOperation(
                    self.getLeftSubformula().negate()
                    ,
                    self.getRightSubformula().negate()
                )
        
    def makeSimple(self):
        '''
        Już w najprostrzej postaci
        '''
        return self
    

    def __str__(self):
        return "("+" AND ".join(map(str, self.subformulas))+")"


class OrOperation(BinaryOperation):
    '''
    Operacja dysjunkcji
    '''

    def negate(self):
        '''
        ~(a | b) = ~a & ~b
        
        prawo De Morgana
        '''
        return AndOperation(
                    self.getLeftSubformula().negate()
                    ,
                    self.getRightSubformula().negate()
                )
    
    def makeSimple(self):
        '''
        Już w najprostrzej postaci
        '''
        return self
    

    def __str__(self):
        return "("+" OR ".join(map(str, self.subformulas))+")"


class EquivalenceOperation(BinaryOperation):
    '''
    Operacja równoważności
    '''

    def negate(self):
        return self.makeSimple().negate()
    
    def makeSimple(self):
        '''
        (a <=> b) = (a & b) | (~a & ~b)
        '''
        return OrOperation(
                    AndOperation(
                        self.getLeftSubformula(),
                        self.getRightSubformula()
                    ),
                    AndOperation(
                        self.getLeftSubformula().negate(),
                        self.getRightSubformula().negate()
                    )
                )
    

    def __str__(self):
        return "("+" EQL ".join(map(str, self.subformulas))+")"


    
class ImplicationOperation(BinaryOperation):
    '''
    Operacja implikacj
    '''

    def negate(self):
        return self.makeSimple().negate()
    
    def makeSimple(self):
        '''
        (a => b) = ~a | b
        '''
        return OrOperation(
                    self.getLeftSubformula().negate(),
                    self.getRightSubformula()
                )


    def __str__(self):
        return "("+" IMP ".join(map(str, self.subformulas))+")"

###########################################
