# -*- coding: utf-8 -*-
'''
Created on 11-04-2013

@author: pawel

moduł zawiera klasy reprezentujące klauzule. Uwaga, są to półprodukty.
Oznacza to że mają one formę (a v b v c) dla kl. dysjunkcyjnych lub 
(a ^ b ^ c) dla kl. konjunkcyjnych. Jednakże a, b, c nie muszą być
literałami. Mogą to być dowolne formuły logiczne. Klasy Clause mają metody
aby dobrowadzić półprodukt to poprawnej postaci Klauzuli składającej się wyłącznie
z literałów.
'''

import sys
import logging
from collections import deque
from copy import deepcopy
from sets import Set

from liprojekt.conversion.formulas import AndOperation, OrOperation, LogicVariable, LogicTruth, LogicFalse, NotOperation


class ClauseState(object):
    '''
    stan półproduktu Clause
    
    Clause może mieć trzy stany:
    * ClauseState.UNKNOWN -> nie wiadomo czy decyduje o spełnialności czy tautologi
    * ClauseState.SUCCESS -> klauzula powastała z formuły, która jest spełnialna, albo jest tautologią
    * ClauseState.FAILURE -> klauzula powstała z formuły, która nie jest spełnialan, albo nie jest tautologią
    '''
    UNKNOWN, SUCCESS, FAILURE = range(3)
    
class ClauseStatus(object):
    '''
    status półproduktu Clause
    
    opisuje stan w jakim znajduje się półproduk Clasue. Stan może wskazywać
    na fakt, że formuła z której powstało Clause jest / nie jest spełnialana, 
    albo jest / nie jest tautologią
    '''
    
    def __init__(self, state, effect, cause = ""):
        self.state = state
        self.effect = effect
        self.cause = cause
        
        if cause:
            self.msg = effect + " CAUSE: " + cause
        else:
            self.msg = effect
    
       
    def getState(self):
        return self.state
    
    def status2str(self, fformatter):
        '''
        zwraca słowny opis statusu Clause
        '''
        pass
    
    def __str__(self):
        '''
        zwraca string informujący o sytyacji jaka wynika z bycia w stanie ClauseStatus
        '''
        return self.msg
    

class ClauseUnresolved(ClauseStatus):
    '''
    status nierozstrzygnięty
    
    nie wiadomo jeszcze nic konkretnego o półprodukcie Clause
    '''
    def __init__(self):
        super(ClauseUnresolved, self).__init__(ClauseState.UNKNOWN,
                                                "Wyniki klauzuli jest nieznany")
    def status2str(self, fformatter):
        return str(self)
    
class ClauseHasTruth(ClauseStatus):
    '''
    status `ma w sobie prawdę logiczną`
    
    Clause ma prawdę logiczą, czyli jest postaci (T, a, b, ...)
    '''
    def __init__(self, state, effect):
        super(ClauseHasTruth, self).__init__(state, effect,
                                                "Klauzula zawiera prawde <T>")
    
    def status2str(self, fformatter):
        return self.effect+ " ponieważ klauzula zawiera prawdę "+ \
            fformatter.formula2str(LogicTruth())
    

class ClauseHasFalse(ClauseStatus):
    '''
    status `ma w sobie fałsz logiczny`
    
    Clause ma fałsz logiczy, czyli jest postaci (F, a, b, ...)
    '''
    def __init__(self, state, effect):
        super(ClauseHasFalse, self).__init__(state, effect,
                                                "Klauzula zawiera fałsz <F>")

    def status2str(self, fformatter):
        return self.effect+ " ponieważ klauzula zawiera fałsz "+ \
            fformatter.formula2str(LogicFalse())
    

class ClauseResolved(ClauseStatus):
    '''
    status `klauzula w pełni rozwinięta`
    
    Clause składa się wyłącznie z literałów, czyli jest postaci (a, b, c, ...) a, b, c to lit.
    (może też mieć stałe logiczne)
    '''
    def __init__(self, state, effect):
        super(ClauseResolved, self).__init__(
                state, effect, 
                "Klauzula nie zawiera zmiennej logicznej i jej zaprzeczenia")
    
    def status2str(self, fformatter):
        return self.effect + " ponieważ klauzula nie zawiera zmiennej logicznej i jej zaprzeczenia" 
    

class ClauseHasOppositeLVars(ClauseStatus):
    '''
    status `klauzula ma zmienną logiczną i jej negację`
    
    w skład Clause wchodzi zmienna logiczna i jej negacja, czyli jest postaci (p, ~p, ...)
    '''
    def __init__(self, state, lit, neglit, effect):
        self.lit = lit
        self.neglist = neglit
        cause = "Klauzula zawiera zmienną "+str(lit)+ \
                " i jej negacje "+str(neglit)
        super(ClauseHasOppositeLVars, self).__init__(
                state, effect, cause)

    def status2str(self, fformatter):
        return self.effect+ " ponieważ klauzula zawiera zmienną logiczną "+ \
            fformatter.formula2str(self.lit)+ " i jej negację "+ \
            fformatter.formula2str(self.neglist)
    
    
#==============================================================================
#================================= CLAUSE =====================================
#==============================================================================
class Clause(object):
    '''
    Półprodukt, którego celem jest stać się klauzulą
    
    Klasa Clause stanowi etap w procesie konwersji formuły logicznej na klauzuly
    '''

########## CONSTRUCTOR #########################################################  
    def __init__(self, formula, conSymbol = ","):
        '''
        Konstuktor klasy Clause
        
        Clause tworzone jest z formuły logicznej. Argument formula jest klasy formulas.Formula.
        formula staje się pierwszą nieprzerobioną podformułą w półprodukcie Clause. Konwersja
        półproduktu Clause polaga na upraszczaniu kolenych podformuł z listy jeszcze nieprzerobionych
        podformuł.
        '''
        self.cFormulas = deque()
        self.uncFormulas = deque()
        self.uncFormulas.append(formula)
        self.lvars = Set()
        self.hasLogicTruth = False
        self.hasLogicFalse = False
        self.status = ClauseUnresolved()
        
        
        self.conSymbol = conSymbol
        
        self.handlerMap = {}
        self.handlerMap[LogicTruth] = self.__handleLogicTruth
        self.handlerMap[LogicFalse] = self.__handleLogicFalse
        self.handlerMap[LogicVariable] = self.__handleLogicVariable
        
        self.handlerMap[NotOperation] = self.__handleNotOperation
        self.handlerMap[AndOperation] = self._handleAndOperation
        self.handlerMap[OrOperation] = self._handleOrOperation
        
        self.__correctMap = {}
        self.__correctMap[LogicTruth] = self.__handleLogicTruth
        self.__correctMap[LogicFalse] = self.__handleLogicFalse
        self.__correctMap[LogicVariable] = self.__handleLogicVariable        

########## STATE #############################################################  
    def isResolved(self):
        '''
        Czy Clause określa sytuację
        
        Znaczy, czy wiadomo cos o formule z której powstało Clause, na podstawie danej
        Clause. (czy owa formuła jest / nie jest spełnialna, jest / nie jest tautologią)
        '''
        return self.status.state in (ClauseState.SUCCESS, ClauseState.FAILURE)
    
    def isSuccess(self):
        '''
        Clause potwierdza tezę
        
        Clause potwierdza tezę, że formuła z której powstała jest spełnialna / jest tautologią
        '''
        return self.status.state is ClauseState.SUCCESS
    
    def isFailure(self):
        '''
        Clause podważa tezę
        
        Clause podważa tezę, że formuła z której powstała jest spełnialna / jest tautologią
        '''
        return self.status.state is ClauseState.FAILURE

########## CONVERSION #########################################################  
    def __convertStep(self):
        if self.isResolved():
            return (self,)
        
        try:
            formula = self.uncFormulas.popleft()
            return self.__handleFormula(formula)                            
        except IndexError:
            # wszystkie formuly 
            return self.__handleResolved()
    
    def __correctStep(self):
        if self.isResolved():
            return self
        try:
            formula = self.uncFormulas.popleft()
            return self.__correctFormula(formula)
        except IndexError:
            return self.__handleResolved()[0]
        
    def __correctFormula(self, formula):
        # TODO sprawdz czy to formula
        try:
            correctedClause = self.__correctMap[formula.__class__](formula)[0]
            correctedClause = correctedClause.__correctStep()
            return correctedClause
        except KeyError:
            # nie można poprawić, wstaw spowrotem na kolejkę nieprzerobionych
            self.uncFormulas.appendleft(formula)
            return self
        except:
            print "nieprzewidziany blad", sys.exc_info()[0]
            raise


    def __analyseLVariables(self, lvar = None):
        logging.debug("Analiza zmiennych, nowa zmienna to [%s]\n"+
                      "pozostałe zmienne to %s", lvar, map(str, self.lvars))
        if lvar:
            opp = lvar.negate()
            if opp in self.lvars:
                logging.debug("Znaleziono negację zmiennej")
                self._oppositeLVarsDetected(lvar, opp)
        else:
            oppSet = Set(map((lambda x: x.negate()), self.lvars))
            pairs = oppSet.intersection(self.lvars)
            if pairs:
                lvar = pairs.pop()
                self._oppositeLVarsDetected(lvar, lvar.negate())

    def __handleFormula(self, formula):
        # TODO sprawdz czy to formula
        f = formula.makeSimple()
        try:
            newClauses = self.handlerMap[f.__class__](f)
        except KeyError:
            print "Nieobslugiwana formula", f
            raise

        except:
            print "nieprzewidziany blad", sys.exc_info()[0]
            raise
        
        return map((lambda x: x.__correctStep()), newClauses)

    
    def __handleResolved(self):
        self._resolvedClauseDetected()
        return (self,)            
               
                                  
    def convertStep(self):
        '''
        kolejny krok konwersji
        
        brana jest kolejna nieurposzczona podformuła z której składa sie Clause. 
        Podformuła poddawana jest przekształceniom opartym na prawach DeMorgana,
        powstaje nowy obiekt Clause, albo para nowych obiektów Clause.
        '''
        if self.isResolved():
            return (self,)
        
        clauseCopy = deepcopy(self)
        return clauseCopy.__convertStep()
       
            
# HANDLERS ####################################################################
## ALWAYS THE SAME ##
    def __handleLogicVariable(self, lvar):
        self.cFormulas.append(lvar)
        self.lvars.add(lvar)
        self.__analyseLVariables(lvar)
        return (self,)
    
    def __handleNotOperation(self, formula):
        self.uncFormulas.appendleft(formula)
        return (self,)
    
## CLAUSE TYPE SPEC BEHAV ##    
    def __handleLogicTruth(self, formula=None):
        self.cFormulas.append(LogicTruth())
        self._logicTruthDetected()
        return (self,)
        
    def __handleLogicFalse(self, formula=None):
        self.cFormulas.append(LogicFalse())
        self._logicFalseDetected()
        return (self,)


## DIFF OUTCOME ##       
    def _handleAndOperation(self, formula):
        '''
        Jak obsługiwać operację AND przy upraszczaniu podformuły
        
        Zachowanie zależy od tego czy mamy doczynienia, z Klauzulą dysjunkcyjną. czy koniunkcyjną.
        Implementowane w klasach DisjunctionClause i ConjunctionClause
        '''
        #TODO zmus do impl
        pass
    
    def _handleOrOperation(self, formula):
        '''
        Jak obsługiwać operację OR przy upraszczaniu podformuły
        
        Zachowanie zależy od tego czy mamy doczynienia, z Klauzulą dysjunkcyjną. czy koniunkcyjną.
        Implementowane w klasach DisjunctionClause i ConjunctionClause
        '''
        #TODO zmus do impl
        pass
        

# DETECTED EVENTS ###############################################################

    def _resolvedClauseDetected(self):
        '''
        Jak reagować w przypadku urposzczenia wszystkich podformuł w Clause
        
        Zachowanie zależy od tego czy mamy doczynienia, z Klauzulą dysjunkcyjną. czy koniunkcyjną.
        Implementowane w klasach DisjunctionClause i ConjunctionClause
        '''
        pass
    
    def _oppositeLVarsDetected(self, lvar, notLvar):
        '''
        Jak reagować w przypadku napotkania zmiennej losowej i jej negacji w Clause
        
        Zachowanie zależy od tego czy mamy doczynienia, z Klauzulą dysjunkcyjną. czy koniunkcyjną.
        Implementowane w klasach DisjunctionClause i ConjunctionClause
        '''
        pass
    
    def _logicTruthDetected(self):
        '''
        Jak reagować w przypadku napotkania prawdy logicznej w Clause
        
        Zachowanie zależy od tego czy mamy doczynienia, z Klauzulą dysjunkcyjną. czy koniunkcyjną.
        Implementowane w klasach DisjunctionClause i ConjunctionClause
        '''
        pass
    
    def _logicFalseDetected(self):
        '''
        Jak reagować w przypadku napotkania nieprawdy logicznej w Clause
        
        Zachowanie zależy od tego czy mamy doczynienia, z Klauzulą dysjunkcyjną. czy koniunkcyjną.
        Implementowane w klasach DisjunctionClause i ConjunctionClause
        '''
        pass
    
############# OUTPUT STRING #####################################################
    def __str__(self):
        return "Vars and Consts: " + (" " + self.conSymbol + " ").join(map(str, self.cFormulas)) + "\n" + \
                "Unconverted subformulas: " + (" " + self.conSymbol + " ").join(map(str, self.uncFormulas)) + "\n" + \
                "Status: " + str(self.status)

    def lvars2str(self, fformatter):
        '''
        wypisuje zmienne logicznie w Clause
        '''
        return ", ".join(map(fformatter.formula2str, self.lvars))
    
    def lconsts2str(self, fformatter):
        '''
        wypisuje stałe logicznie w Clause
        '''
        consts = []
        if self.hasLogicTruth:
            consts.append(fformatter.formula2str(LogicTruth()))
        if self.hasLogicFalse:
            consts.append(fformatter.formula2str(LogicFalse()))
        return ", ".join(consts)
    
    def convertedFormulas2str(self, fformatter):
        '''
        wypisuje podformuły uproszczone (zmienne i stałe logiczne) logicznie w Clause
        '''
        return (" "+self.conSymbol+" ").join(map(fformatter.formula2str, self.cFormulas))
    
    def unconvertedFormulas2str(self, fformatter):
        '''
        wypisuje podformuły nieuproszczone w Clause
        '''
        return (" "+self.conSymbol+" ").join(map(fformatter.formula2str, self.uncFormulas))
    
    def allFormulas2str(self, fformatter):
        '''
        wypisuje wszystkie podformuły w Clause
        '''
        return self.convertedFormulas2str(fformatter)+" "+self.conSymbol+" "+ \
                self.unconvertedFormulas2str(fformatter)
    
    def status2str(self, fformatter, statusPrefix="", onlyResolved=False):
        '''
        wypisuje status Clause
        '''
        if (onlyResolved and self.status.state != ClauseState.UNKNOWN) or not onlyResolved:
            return statusPrefix+self.status.status2str(fformatter)
        return ""

#==============================================================================
#=========================== CONJUNCTION CLAUSE ===============================
#==============================================================================
class  ConjunctionClause(Clause):
    '''
    Klasa reprezentująca półprodukt dążący do postaci klauzuli koniunkcyjnej
    '''
    
    def _handleAndOperation(self, formula):
        '''
        obsługa operacji AND przy dążeniu do postaci klauzuli koniunkcyjnej
        
        Po prostu weź dwie strony operacji i ustaw je na początku podformuł nieprzerobionych
        '''
        self.uncFormulas.extendleft(formula.subformulas)
        return (self,)
    
    def _handleOrOperation(self, formula):
        '''
        obsługa operacji OR przy dążeniu do postaci klauzuli koniunkcyjnej
        
        Rozbij się na dwie klauzule ConjunctionClause, jedna zawiera lewy operand
        operacji OR, druga prawy.
        '''
        myCopy = deepcopy(self)
        self.uncFormulas.appendleft(formula.getLeftSubformula())
        myCopy.uncFormulas.appendleft(formula.getRightSubformula())
        return (self, myCopy)
        
    
    # DETECTED EVENTS ###############################################################
    
    def _resolvedClauseDetected(self):
        '''
        Uproszczono klauzule do postaci klauzuli koniunkcyjnej? 
        
        To znaczy, że ta klauzula jest spełnialna
        '''
        self.status = ClauseResolved(ClauseState.SUCCESS, 
                         "Klauzula jest spelnialna")
        
    def _oppositeLVarsDetected(self, lvar, notLvar):
        '''
        W klauzuli wykryto zmienną logiczną i jej negację.
        
        To znaczy, że klauzlua nie jest spełnialna.
        '''
        self.status = ClauseHasOppositeLVars(ClauseState.FAILURE, lvar, notLvar, 
                                             "Klauzula jest zawsze fałszywa")
    
    def _logicTruthDetected(self):
        '''
        W klauzuli wykryto prawdę logiczną.
        
        Nic nam to nie daje.
        '''
        self.hasLogicTruth = True;
    
    def _logicFalseDetected(self):
        '''
        W klauzuli wykryto nieprawdę logiczną.
        
        To znaczy, że jest zawsze fauszywa (niespełnialna)
        '''
        self.hasLogicFalse = True;
        self.status = ClauseHasFalse(ClauseState.FAILURE, 
                                     "Klauzula jest zawsze fauszywa")


#==============================================================================
#=========================== DISJUNCTION CLAUSE ===============================
#==============================================================================   
class  DisjunctionClause(Clause):
    '''
    Klasa reprezentująca półprodukt dążący do postaci klauzuli dysjunkcyjnej
    '''
    def _handleAndOperation(self, formula):
        '''
        obsługa operacji AND przy dążeniu do postaci klauzuli koniunkcyjnej

        Rozbij się na dwie klauzule DisjunctionClause, jedna zawiera lewy operand
        operacji AND, druga prawy.       
        '''
        myCopy = deepcopy(self)
        self.uncFormulas.appendleft(formula.getLeftSubformula())
        myCopy.uncFormulas.appendleft(formula.getRightSubformula())
        return (self, myCopy)
    
 
    def _handleOrOperation(self, formula):
        '''
        obsługa operacji AND przy dążeniu do postaci klauzuli koniunkcyjnej
        
        Po prostu weź dwie strony operacji i ustaw je na początku podformuł nieprzerobionych
        '''
        self.uncFormulas.extendleft(formula.subformulas)
        return (self,)
        
# DETECTED EVENTS ###############################################################

    def _resolvedClauseDetected(self):
        '''
        Uproszczono klauzule do postaci klauzuli koniunkcyjnej? 
        
        To znaczy, że ta klauzula jest jest tautologią.
        '''
        self.status = ClauseResolved(ClauseState.FAILURE, 
                         "Klauzula nie jest zawsze prawdziwa")
                   
    def _oppositeLVarsDetected(self, lvar, notLvar):
        '''
        W klauzuli wykryto zmienną logiczną i jej negację.
        
        To znaczy, że klauzlua jest tautologią.
        '''
        self.status = ClauseHasOppositeLVars(ClauseState.SUCCESS, lvar, notLvar, 
                                             "Klauzula jest zawsze prawdziwa")
    
    def _logicTruthDetected(self):
        '''
        W klauzuli wykryto prawdę logiczną.
        
        To znaczy, że jest zawsze prawdziwa (tautologia)
        '''
        self.hasLogicTruth = True;
        self.status = ClauseHasTruth(ClauseState.SUCCESS, "Klauzula jest zawsze prawdziwa")
    
    def _logicFalseDetected(self):
        '''
        W klauzuli wykryto nieprawdę logiczną.
        
        Nic nam to nie daje.
        '''
        self.hasLogicFalse = True;
