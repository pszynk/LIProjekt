# -*- coding: utf-8 -*-

'''
Created on 11-04-2013

@author: pawel

Moduł z testami. Testy są podielone na:

Testy reprezentatywne formuł NIEspełnialnych
Testy reprezentatywne formuł spełnialnych, NIE tautologii
Testy reprezentatywne tautologii
Testy dodatkowe       tautologii
Testy reprezentatywne formuł niespełnialnych
'''
import unittest


from liprojekt.interface.interface import Interface


TEST_FILE_NAME = "test_output.txt"
'''
plik w którym zapisywane są wyniki testów
'''

class FromInputTestCase(unittest.TestCase):
    '''
    Bazowa klasa testów, gdzie działanie aplikacji sprawdzane jest
    poprzez zadanie argumentów na linii komend (tak jak robiłby to użytkownik)
    '''

    def setUp(self):
        '''
        tworzenie testu -> nowa klasa interface.Interface
        '''
        self.interface = Interface()
        self.args = []
        with open(TEST_FILE_NAME, 'a') as f:
            f.write('\n'+'>'*80+'\n')
            f.write(self.__doc__)
            f.write('\n')


    def tearDown(self):
        '''
        burzenie testu, nic nie trzeba robić
        '''
        pass


    def _executeInterface(self):
        '''
        uruchom aplikacje w trybie testowym
        '''
        self.interface.testRun(self.args)
    
    def _checkValidity(self):
        '''
        True  -> jeżeli formuła okazała się być tautologią
        False -> wpp.
        '''
        return self.interface.validVerif is not None and self.interface.valid
    
    def _checkSatisfiability(self):
        '''
        True  -> jeżeli formuła okazała się być spełnialna
        False -> wpp.
        '''
        return self.interface.satisVerif is not None and self.interface.satisfiable
    
    def _assertIsTautology(self, isTautology):
        '''
        asercja 'Jest tautologią'
        '''
        self.assertTrue(isTautology, 'Formula ['+self.interface.getFormattedFormula()+ \
                        '] jest tautologią!!!')
    
    def _assertIsNotTautology(self, isNotTautology):
        '''
        asercja 'NIE Jest tautologią'
        '''
        self.assertFalse(isNotTautology, 'Formula ['+self.interface.getFormattedFormula()+ \
                        '] NIE jest tautologią!!!')
    
    def _assertIsSatisfiable(self, isSatisfiable):
        '''
        asercja 'Jest spełnialna'
        '''
        self.assertTrue(isSatisfiable, 'Formula ['+self.interface.getFormattedFormula()+ \
                        '] jest spełnialna!!!')
    
    def _assertIsNotSatisfiable(self, isNotSatisfiable):
        '''
        asercja 'NIE Jest spełnialna'
        '''
        self.assertFalse(isNotSatisfiable, 'Formula ['+self.interface.getFormattedFormula()+ \
                        '] jest NIEspełnialna!!!')


class RepresentativeTestCase(FromInputTestCase):
    '''
    Paczka testów reprezentatywnych
    
    Argumenty podawane z linii komend, wyniki dopisywane dp pliku testowego.
    Dla zadanej formuły sprawdzane jest czy program rozpoznał w niej formułę
    spełnialną / tautologię
    '''
    
    def _setArgs(self, formula, name):
        '''
        ustaw parametry wykonania na 
        -f -> wczytanie formuły z wejścia
        -O -> dopisanie wyników do pliku
        '''
        self.formulaString = formula
        self.args = ['-f', formula, '-O', TEST_FILE_NAME, '-t']
    
    def _testForTautology(self, tautology, name):
        '''
        Przetestuj dla formuły która jest tautologią
        '''
        self._setArgs(tautology, name)
        self._executeInterface()
        self._assertIsTautology(self._checkValidity())
        self._assertIsSatisfiable(self._checkSatisfiability())
    
    def _testForSatisfiableOnly(self, satisfiableOnly, name):
        '''
        Przetestuj dla formuły która jest TYLKO spełnialna
        '''
        self._setArgs(satisfiableOnly, name)
        self._executeInterface()
        self._assertIsNotTautology(self._checkValidity())
        self._assertIsSatisfiable(self._checkSatisfiability())
        
    def _testForNotSatisfiable(self, notSatisfiable, name):
        '''
        Przetestuj dla formuły która NIE jest spełnialna
        '''
        self._setArgs(notSatisfiable, name)
        self._executeInterface()
        self._assertIsNotTautology(self._checkValidity())
        self._assertIsNotSatisfiable(self._checkSatisfiability())
        
class RepresentativeTautologyTestCase(RepresentativeTestCase):
    '''
    Testy dla formuł będących tautologiami:
    
    * T1  =  (p => q) => ((q => r) => (p => r))
    * T2  =   p => (p | q)
    * T3  =   p => (q => p)
    * T4  =  (p => r) => ((q => r) => ((p | q) => r))
    * T5  =  (p & q) => q
    * T6  =  (p & q) => p
    * T7  =  (r => p) => ((r => q) => (r => p & q))
    * T8  = ((p & q) => r) => (p => (q => r))
    * T9  =  (p => (q => r)) => ((p & q) => r)
    * T10 =  (p & ~p) => q
    * T11 =  (p => (p & ~p)) => ~p
    * T12 =   p | ~p
    '''
            
    def test_T1(self):
        '''
        (p => q) => ((q => r) => (p => r))
        '''
        self._testForTautology('(p => q) => ((q => r) => (p => r))', 'T1')
    
    def test_T2(self):
        '''
        p => (p | q)
        '''
        self._testForTautology('p => (p | q)', 'T2')
    
    def test_T3(self):
        '''
        p => (q => p)
        '''
        self._testForTautology('p => (q => p)', 'T3')
    
    def test_T4(self):
        '''
        (p => r) => ((q => r) => ((p | q) => r))
        '''
        self._testForTautology('(p => r) => ((q => r) => ((p | q) => r))', 'T4')
    
    def test_T5(self):
        '''
        (p & q) => q
        '''
        self._testForTautology('(p & q) => q', 'T5')
    
    def test_T6(self):
        '''
        (p & q) => p
        '''
        self._testForTautology('(p & q) => p', 'T6')
    
    def test_T7(self):
        '''
        (r => p) => ((r => q) => (r => p & q))
        '''
        self._testForTautology('(r => p) => ((r => q) => (r => p & q))', 'T7')
    
    def test_T8(self):
        '''
        ((p & q) => r) => (p => (q => r))
        '''
        self._testForTautology('((p & q) => r) => (p => (q => r))', 'T8')
    
    def test_T9(self):
        '''
        (p => (q => r)) => ((p & q) => r)
        '''
        self._testForTautology('(p => (q => r)) => ((p & q) => r)', 'T9')
    
    def test_T10(self):
        '''
        (p & ~p) => q
        '''
        self._testForTautology('(p & ~p) => q', 'T10')
    
    def test_T11(self):
        '''
        (p => (p & ~p)) => ~p
        '''
        self._testForTautology('(p => (p & ~p)) => ~p', 'T11')
    
    def test_T12(self):
        '''
        p | ~p
        '''
        self._testForTautology('p | ~p', 'T12')
    
class RepresentativeAdditionalTautologyTestCase(RepresentativeTestCase):
    '''
    Dodatkowe testy dla formuł będących tautologiami:

    * AT13 =   p => ~~p
    * AT14 =  (p => q) <=> (~p | q)
    * AT15 =  (p & q) <=> (~p | ~q)
    * AT16 = ((p <=> q) <=> r) <=> (p <=> (q <=> r))
    * AT17 =   F => p
    * AT18 =   p => T
    * AT19 =  (p | F) <=> p
    * AT20 =  (p & T) <=> p
    
    '''
    def test_AT13(self):
        '''
        p => ~~p
        '''
        self._testForTautology('p => ~~p', 'AT13')
    
    def test_AT14(self):
        '''
        (p => q) <=> (~p | q)
        '''
        self._testForTautology('(p => q) <=> (~p | q)', 'AT14')
    
    def test_AT15(self):
        '''
        (p & q) <=> (~p | ~q)
        '''
        self._testForTautology('~(p & q) <=> (~p | ~q)', 'AT15')   
    
    def test_AT16(self):
        '''
        ((p <=> q) <=> r) <=> (p <=> (q <=> r))
        '''
        self._testForTautology('((p <=> q) <=> r) <=> (p <=> (q <=> r))', 'AT16')   
    
    def test_AT17(self):
        '''
        F => p
        '''
        self._testForTautology('F => p', 'AT17')   
    
    def test_AT18(self):
        '''
        p => T
        '''
        self._testForTautology('p => T', 'AT18')   
    
    def test_AT19(self):
        '''
        (p | F) <=> p
        '''
        self._testForTautology('(p | F) <=> p', 'AT19')   
    
    def test_AT20(self):
        '''
        (p & T) <=> p
        '''
        self._testForTautology('(p & T) <=> p', 'AT20')   
      

class RepresentativeSatisfiableNotTautologyTestCase(RepresentativeTestCase):
    '''
    Testy dla formuł spełnialnych NIE będących tautologiami:
    
    * SNT1 =   T & p
    * SNT2 = ((p & q) => (p | r)) <=> ~((F | p) => (T & q))
    * SNT3 = ( p |  q |  r |  s |  t) &
             (~p |  q | ~r |  s |  t) & 
             ( p | ~q |  r | ~s |  t) & 
             (~p | ~q | ~r | ~s |  t)
    '''

    def test_SNT1(self):
        '''
        T & p
        '''
        self._testForSatisfiableOnly('T & p', 'SNT1')
    
    def test_SNT2(self):
        '''
        ((p & q) => (p | r)) <=> ~((F | p) => (T & q))
        '''
        self._testForSatisfiableOnly('((p & q) => (p | r)) <=> ~((F | p) => (T & q))', 
                                     'SNT2')
        
    def test_SNT3(self):
        '''
        ( p |  q |  r |  s |  t) &
        (~p |  q | ~r |  s |  t) & 
        ( p | ~q |  r | ~s |  t) & 
        (~p | ~q | ~r | ~s |  t)
        '''
        self._testForSatisfiableOnly('( p |  q |  r |  s |  t) &'+
                                     '(~p |  q | ~r |  s |  t) &'+ 
                                     '( p | ~q |  r | ~s |  t) &'+ 
                                     '(~p | ~q | ~r | ~s |  t)', 'SNT3')


class RepresentativeNotSatisfiableTestCase(RepresentativeTestCase):
    '''
    Testy dla formuł spełnialnych NIE będących tautologiami:

    * NS1 =  ~(F & p) <=> ~(T | p)
    * NS2 = (((p & q) => (p | q)) & (~p | q)) <=> ~((F | p) => (T & q))
    * NS3 =  ( p |  q |  r) &
             (~p |  q |  r) & 
             ( p | ~q |  r) &
             ( p |  q | ~r) & 
             (~p | ~q |  r) &
             (~p |  q | ~r) &
             ( p | ~q | ~r) &
             (~p | ~q | ~r)
     
    '''
    def test_NS1(self):
        '''
         ~(F & p) <=> ~(T | p)
        '''
        self._testForNotSatisfiable('~(F & p) <=> ~(T | p)', 'NS1')
    
    def test_NS2(self):
        '''
        (((p & q) => (p | q)) & (~p | q)) <=> ~((F | p) => (T & q))
        '''
        self._testForNotSatisfiable('(((p & q) => (p | q)) & (~p | q)) <=> ~((F | p) => (T & q))', 
                                     'NS2')
        
    def test_NS3(self):
        '''
        ( p |  q |  r) &
        (~p |  q |  r) & 
        ( p | ~q |  r) &
        ( p |  q | ~r) & 
        (~p | ~q |  r) &
        (~p |  q | ~r) &
        ( p | ~q | ~r) &
        (~p | ~q | ~r)
        '''
        self._testForNotSatisfiable('( p |  q |  r) &'+
                                    '(~p |  q |  r) &'+ 
                                    '( p | ~q |  r) &'+
                                    '( p |  q | ~r) &'+ 
                                    '(~p | ~q |  r) &'+
                                    '(~p |  q | ~r) &'+
                                    '( p | ~q | ~r) &'+
                                    '(~p | ~q | ~r)', 'NS3')
    
def runTests():
    '''
    Uruchom pulę testów, zapisz wyniki to pliku TEST_FILE_NAME
    '''
    #unittest.main()
    with open(TEST_FILE_NAME, 'w') as f:
        f.write("Plik z wynikiami testów Liporjekt\n")
        print "Wyniki testów zapisywane do pliku: " + TEST_FILE_NAME
    
    suite_RT = unittest.TestLoader().loadTestsFromTestCase(RepresentativeTautologyTestCase)
    suite_AT = unittest.TestLoader().loadTestsFromTestCase(RepresentativeAdditionalTautologyTestCase)
    suite_RSNT = unittest.TestLoader().loadTestsFromTestCase(RepresentativeSatisfiableNotTautologyTestCase)
    suite_RNS = unittest.TestLoader().loadTestsFromTestCase(RepresentativeNotSatisfiableTestCase)
    alltests = unittest.TestSuite([suite_RT, suite_AT, suite_RSNT, suite_RNS])
    unittest.TextTestRunner(verbosity=3).run(alltests)
