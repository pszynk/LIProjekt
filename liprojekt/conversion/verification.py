# -*- coding: utf-8 -*-
'''
Created on 20-03-2013

@author: pawel


Moduł zawiera klasy weryfikujące spełnialność formuły i
czy formuła jest tautologią.
'''

import logging
from collections import deque

from liprojekt.conversion.clauses import ConjunctionClause, DisjunctionClause
from liprojekt.conversion.recording import ClauseBinTree, ClauseBinTreeNode

class FormulaVerifier(object):    
    '''
    Klasa bazowa do weryfikacji formuł logicznych.
    
    Dziedziczą z niej klasy:
    * SatisfiabilityVerifier -> do weryfikacji spełnilaności
    * ValidityVerifier       -> do weryfikacji czy formuła jest tautologią
    '''
     
    def __init__(self, formula):
        '''
        jako argument brana jest formuła logiczna, czyli klasa formulas.Formula.
        
        Z formuły logicznej tworzony jest półprodukt Clause i umieszczany w korzeniu drzewa
        recording.ClauseBinTree.
        '''
        
        self.formula = formula
        self.tree = ClauseBinTree(
                        ClauseBinTreeNode(
                            self._createClause(formula)))
        self.succClauseNodes = []
        self.failClauseNodes = []
        
        self.resultStr = ""
        
        self.__isVerified = False
        self.__success = None
        
    def _ifVerifiedAssert(self, state):
        if self.__isVerified is not state:
            if self.__isVerified:
                raise Exception("Formula jest już zweryfikowana")
            else:
                raise Exception("Formula nie zostala jeszcze zweryfikowana")
        

    @property
    def success(self):
        '''
        Czy udało się potwierdzić weryfikowaną tezę (spełnialność/tałtologia)
        '''
        self._ifVerifiedAssert(True)
        return self.__success
    
    def _setResult(self, isSuccess):
        '''
        Ustaw wynik weryfikacji
        '''
        
        self.__success = isSuccess
        self.__isVerified = True
        return self.success
    
    def verifyFormula(self):
        '''
        Weryfikuj formułę
        
        Zaczynamy od formuły pierwotnej przetworzonej na półprodukt Clause.
        Odkładamy ją na stosie S.
        Algorytm wygląda następująco:
        1) Dopóki S nie jest puste:
        2)    s = S.pop()
        3)    (c) = konwertuj(s) lub (l, p) = konwertuj(s)
        4)    IF sprawdź czy c, (lub l, p) daje warunek STOP
        5)        zwróć SUKCES lub PORAŻKA
        6)    ELSE wrzuc c (lub l, p) na S
        
        UWAGA!! z Clause przy wykonywaniu Clause.convertStep() mogą powstać
        dwa nowe obiekty Clause
        '''
        self._ifVerifiedAssert(False)
        
        queue = deque()
        
        queue.append(self.tree.root)
     
        # 1)
        while queue:
            # 2)
            parent = queue.popleft()
            # 3)
            newClauses = parent.clause.convertStep()
            for c in newClauses:
                node  = ClauseBinTreeNode(c)

                self.tree.addLeaf(node, parent)
                
                # 4)
                if not c.isResolved():
                    # 6)
                    queue.append(node)
                # 5)
                else:
                    if c.isSuccess():
                        logging.debug("Znaleziono klauzulę weryfikującą")
                        self.succClauseNodes.append(node)
                        if self.endOnSuccess():
                            logging.debug("Znaleziono klauzulę weryfikującą -> "+
                                          "koniec weryfikacji")
                            return self._setResult(True)
                    else:
                        logging.debug("Znaleziono klauzulę dyskredytującą")
                        self.failClauseNodes.append(node)
                        if self.endOnFailure():
                            logging.debug("Znaleziono klauzulę dyskredytującą -> "+
                                          "koniec weryfikacji")
                            return self._setResult(False)
        
        logging.debug("Przeanalizowano wszystkie klauzuly")
        
        return self.analyze()
    
    def generateRaport(self, fformatter, raportFormat, treeNodeFromat=None):
        '''
        Generuje słowy raport z veryfikacji
        
        Raport można generować z wybranymi opcjami
        {result}    -> wynik weryfikacji
        {proof}     -> dowód na wynik weryfikacji
        {valuation} -> wartościowanie przy którym potwierdza się wynik walidacji
        {tree}      -> przebieg konwersji
        '''
        self._ifVerifiedAssert(True)
        
        attars = {
            'result':           self._result2str(),
            'proof':            self._proof2str(fformatter),
            'valuation':        self._valuatoin2str(fformatter),
        }
        while True:
            try:
                raport = raportFormat.format(**attars)
            except KeyError as e:
                if e.args[0] == 'tree':
                    attars['tree'] = self.__tree2str(fformatter, treeNodeFromat)
                else:
                    raise Exception('Raport nie ma atrubutu `'+e.args[0]+'`')
            else:
                return raport
        
    
       
    def __tree2str(self, fformatter, treeNodeFromat):
        return self.tree.tree2str(fformatter, treeNodeFromat)
       
    def _result2str(self):
        pass
    
    def _valuatoin2str(self, fformatter):
        pass 
    
    def _proof2str(self, fformatter):
        pass 
    
 
    
    def _createClause(self, formula):
        '''
        funkcja implementowana przez klasy SatisfiabilityVerifier, ValidityVerifier
        
        każda operuje na inncyh typach półproduktuw Clause (ConjunctionClause, DisjunctionClause)
        '''
        pass
    
    def endOnSuccess(self):
        '''
        funkcja implementowana przez klasy SatisfiabilityVerifier, ValidityVerifier
        
        czy odkrycie Clause potwierdzającej tezę kończy walidację?
        '''
        pass
    
    def endOnFailure(self):
        '''
        funkcja implementowana przez klasy SatisfiabilityVerifier, ValidityVerifier
        
        czy odkrycie Clause niepotwierdzającej tezy kończy walidację?
        '''
        pass
    
    def analyze(self):
        '''
        funkcja implementowana przez klasy SatisfiabilityVerifier, ValidityVerifier
        
        analizuj wynik przy doprowadzeniu formuły pierwotnej do postaci CNF / DNF
        '''
        pass

                                  
class SatisfiabilityVerifier(FormulaVerifier):
    # podac wartosciowanie
    
    def _createClause(self, formula):
        '''
        Operuje na ConjunctionClause
        '''
        
        return ConjunctionClause(formula)

    def endOnSuccess(self):
        '''
        Odkrycie Clause potwierdzającej tezę kończy walidacji!
        '''
        return True
    
    def endOnFailure(self):
        '''
        Odkrycie Clause NIEpotwierdzającej tezy NIE kończy walidacji!
        '''
        return False
    
    def analyze(self):
        '''
        Formuła jest spełnialna o ile udało się znaleźć chociaż jedną Clause
        potwierdzajacą tezę.
        '''
        return self._setResult(self.succClauseNodes != [])

    def _result2str(self):
        if self.success:
            return "Udowodniono spełnialność formuły"
        else:
            return "Udowodniono NIEspełnialność formuły"
    
    def _valuatoin2str(self, fformatter):
        if self.success:
            return "Formuła jest spełnialna przy wartościowaniu takim, że wszystkie literały i stałe: " +\
                   self.succClauseNodes[0].clause2str(
                      fformatter, "{clauseConvertedFormulas}\n") + \
                   "    są prawdziwe" 
        else:
            return "Formuła nie jest spełnialna ponieważ niemożliwe jest wartościowanie, takie że wszystkie literały i stałe: " +\
                   self.failClauseNodes[0].clause2str(
                      fformatter, "{clauseConvertedFormulas},\n") + \
                   "    są prawdziwe"
              
    
    def _proof2str(self, fformatter):
        if self.success:
            return self.succClauseNodes[0].clause2str(
                    fformatter, "{nodeId}: {clauseStatus} -> {clauseVars}, , {clauseConsts}")
            
        else:
            return "Wszystkie klauzule koniunkcyjne zawierają zmienną i jej negację"
       
class ValidityVerifier(FormulaVerifier):
    
    def _createClause(self, formula):
        '''
        Operuje na DisjunctionClause
        '''
        return DisjunctionClause(formula)
        
    def endOnSuccess(self):
        '''
        Odkrycie Clause potwierdzającej tezę NIE kończy walidacji!
        '''
        return False
    
    def endOnFailure(self):
        '''
        Odkrycie Clause NIEpotwierdzającej tezę kończy walidacji!
        '''
        return True
        
    def analyze(self):
        '''
        Formuła jest tautologią o ile nie znaleziono ANI JEDNEJ Clause
        zaprzeczającej tezie.
        '''
        logging.debug("""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Analiza walidacji czy formuła jest TAUTOLOGIĄ:
> znaleziono %d klauzul weryfikujących:
%s
> znaleziono %d klauzul dyskredytujących:
%s
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
""",
        len(self.succClauseNodes), "\n".join(map(str, self.succClauseNodes)), 
        len(self.failClauseNodes), "\n".join(map(str, self.failClauseNodes)))
        return self._setResult(self.failClauseNodes == [])

    def _result2str(self):
        if self.success:
            return "Udowodniono, że formuła jest tautologią"
        else:
            return "Udowodniono, że formuła NIE jest tautologią"
 
    def _valuatoin2str(self, fformatter):
        if self.success:
            return "Formuła jest tautologią więc jest prawdziwa dla każdego wartościowania"
        else:
            return "Formuła nie jest tautologią\n" +\
                   "    nie jest prawdziwa dla wartościowania takiego że wszystkie literały i stałe: " +\
                   self.failClauseNodes[0].clause2str(
                       fformatter, "{clauseConvertedFormulas}") + '\n' +\
                   "    są fałszywe"
    
    def _proof2str(self, fformatter):
        if self.success:
            return "Wszystkie klauzule dysjunkcyjne zawierają zmienną i jej negację"
        else:
            return self.failClauseNodes[0].clause2str(
                    fformatter, "{nodeId}: {clauseStatus} -> {clauseVars}, {clauseConsts}")
 
    