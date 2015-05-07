# -*- coding: utf-8 -*-
'''
Created on 12-04-2013

@author: pawel

Moduł zawiera klasę Interface, która stanowi interfejs aplikacji
'''

import sys
from datetime import datetime
import argparse as argp
import logging

from pyparsing import ParseException

from liprojekt.parsing.parsers import DefaultLogicExprParser
from liprojekt.conversion.verification import SatisfiabilityVerifier, ValidityVerifier
from liprojekt.conversion.formatting import FormulaFormatter
from liprojekt.parsing.alphabets import SymbolicAlphabetMap, WordAlphabetMap

    

class Interface(object):
    '''
    Klasa wczytuje polecenia z klini komend i prezentuje wyniki
    weryfikacji spełnialności i czy formuła jest tautologią w rządany sposób
    
    usage: LIProjekt [-h] (-f FORMULA | -i INPUT | -l [{DEFAULT,WORD,SYMBOLIC}])
                 [-a {DEFAULT,WORD,SYMBOLIC}] [-o OUTPUT | -O OUTPUT]
                 [-g GRAPH | -t] [-v] [-d] [--log LOG]

    optional arguments:
      -h, --help            show this help message and exit
      -f FORMULA, --formula FORMULA
                            formuła do weryfikacji (jezeli zawiera spacje nalezy
                            umiescic ja w "") (default: None)
      -i INPUT, --input INPUT
                            nazwa pliku z formula do weryfikacji (default: None)
      -l [{DEFAULT,WORD,SYMBOLIC}], --legend [{DEFAULT,WORD,SYMBOLIC}]
                            legenda znakow alfabetu (default: None)
      -o OUTPUT, --output OUTPUT
                            nazwa pliku do ktorego zapisany bedzie wynik
                            weryfikacji domyslnie na standardowe wyjscie (default:
                            None)
      -O OUTPUT, --Output OUTPUT
                            nazwa pliku do ktorego zapisany bedzie wynik
                            weryfikacji domyslnie na standardowe wyjscie (default:
                            None)
      -g GRAPH, --graph GRAPH
                            nazwa pliku w formacie .png z drzewem przetwarzania
                            [NIE ZAIMPL. W TEJ WERSJI] (default: None)
      -t, --text            czy zapisywac kroki przetwarzania w postaci teksowej
                            (default: False)
    
      -a {DEFAULT,WORD,SYMBOLIC}, --alphabet {DEFAULT,WORD,SYMBOLIC}
                            zestaw znaków na do reprezentowania formuł
                            logicznych (default: DEFAULT)
    
      -v, --verbose         czy wypisywac dodatkowe informacje podczas dzialania
                            programu (default: False)
      -d, --debug           czy wypisywac dodatkowe komunikaty DEBUG (default:
                            False)
      --log LOG             nazwa pliku do którego wypisane zostana komunikaty
                            (default: None)
    '''
    PROGRAM_NAME = "LIProjekt"
    LINELENGTH = 120
    ALPHABETS = { 
     'SYMBOLIC':    SymbolicAlphabetMap(),
     'WORD':        WordAlphabetMap(),
     'DEFAULT':     SymbolicAlphabetMap()
    }
    
    ARGS = dict(           
        # czy wczytywac formule ze standardowego wejscia, czy z pliku?             
        tasks = 
        [
         (("-f", "--formula"), 
          dict(
            help="formuła do weryfikacji "+ 
                "(jezeli zawiera spacje nalezy umiescic ja w \"\")",
            type=str
          )
         ),
         (("-i", "--input"),
          dict(
            help="nazwa pliku z formula do weryfikacji",
            type=str,
          )
         ),
                  (("-l", "--legend"),
          dict(
            help="legenda znakow alfabetu",
            type=str,
            nargs='?',
            const='DEFAULT',
            choices=ALPHABETS.keys()
          )
         ),
        ],
                
        info = 
        [
         (("-a", "--alphabet"),
          dict(
            help="zestaw znaków na do reprezentowania formuł logicznych",
            type=str,
            default='DEFAULT',
            choices=ALPHABETS.keys()
          )
         )
        ],
                
        output_file =
        [
         (("-o", "--output"), 
          dict(
            help="nazwa pliku do ktorego zapisany bedzie wynik weryfikacji "+
                "domyslnie na standardowe wyjscie",
            type=str
          )
         ),
        (("-O", "--Output"), 
          dict(
            help="nazwa pliku do ktorego zapisany bedzie wynik weryfikacji "+
                "domyslnie na standardowe wyjscie",
            type=str
          )
         ),
        ],
                
                
        output_type = [
         (("-g", "--graph"),
          dict(
            help="nazwa pliku w formacie .png z drzewem przetwarzania [NIE ZAIMPL. W TEJ WERSJI]",
            type=str
          )
         ),
         (("-t", "--text"),
          dict(
            help="czy zapisywac kroki przetwarzania w postaci teksowej",
            action="store_true"
          )
         ) 
        ],
        
        # logi z dzialania programu
        logging =
        [
         (("-v", "--verbose"), 
          dict(
            help="czy wypisywac dodatkowe informacje podczas dzialania programu",
            action="store_true"
          )
         ),
         (("-d", "--debug"),
          dict(
            help="czy wypisywac dodatkowe komunikaty DEBUG",
            action="store_true"
          )
         ),
         (("--log",),
          dict(
            help="nazwa pliku do którego wypisane zostana komunikaty",
            type=str
          )
         ) 
        ]
    )
    
    
    
    def __init__(self):
        self.__createArgParser()
        self.validVerif = None
        self.satisVerif = None
        

    
    def __setAlphabet(self, key):
        logging.info("Wybrano składnię: %s - %s", key, self.ALPHABETS[key])
        self.alphabet = self.ALPHABETS[key]
    
    def __createArgParser(self):
        self.parser = argp.ArgumentParser(
                        prog=self.PROGRAM_NAME, 
                        formatter_class=argp.ArgumentDefaultsHelpFormatter)
        
        
        # tworze grupe arg. input wykluczających się
        task_group = self.parser.add_mutually_exclusive_group(required=True)
        self.__loadArguments(task_group, "tasks")
        
        # tworze grupe arg. input pozostałych
        info_group = self.parser.add_argument_group()
        self.__loadArguments(info_group, "info")
        
        # tworze grupe arg. output
        output_file_group = self.parser.add_mutually_exclusive_group(required=False)
        self.__loadArguments(output_file_group, "output_file")

        # tworze grupe arg. output
        output_type_group = self.parser.add_mutually_exclusive_group(required=False)
        self.__loadArguments(output_type_group, "output_type")

        # tworze grupe arg. loging
        logging_group = self.parser.add_argument_group()
        self.__loadArguments(logging_group, "logging")
    
        
        
    def __handleLogging(self):

        _level = logging.WARNING
        _format = "%(levelname)s: %(message)s"
        if self.sessionArgs.verbose:
            _level = logging.INFO
        if self.sessionArgs.debug:
            _level = logging.DEBUG
            _format = "[%(module)s->%(funcName)s] %(levelname)s: %(message)s"
        if self.sessionArgs.log:
            logging.basicConfig(filename=self.sessionArgs.log, format=_format, level=_level)
        else:
            logging.basicConfig(format=_format, level=_level)
            
        logging.debug("""
%s
%s DEBUG %s
%s
""", "*"*self.LINELENGTH, '*'*36, '*'*37, "*"*self.LINELENGTH)

    def __handleInput(self):
        
        
        # wybiera składnię
        self.__setAlphabet(self.sessionArgs.alphabet)
           
        # wybiera formater formul 
        self.formulaFomratter = FormulaFormatter(self.alphabet)
        
        # wybiera parser formul
        self.formulaParser = DefaultLogicExprParser(self.alphabet)
        
        self.formula = None
        try:
            # czy podano formule
            if self.sessionArgs.formula is not None:
                if self.sessionArgs.formula is "":
                    raise Exception("Podano pustą formułę")
                else:
                    logging.info("formuła wczytana z wejścia")
                    self.formula = self.formulaParser.parseString(self.sessionArgs.formula)
            # czy podano plik
            elif self.sessionArgs.input:
                logging.info("formula wyczytwana z `pliku` %s", self.sessionArgs.input)
                self.formula = self.formulaParser.parseFile(self.sessionArgs.input)
            elif self.sessionArgs.legend:
                print self.ALPHABETS[self.sessionArgs.legend].getLegend();
                sys.exit(0);
            else:
                print self.sessionArgs
                raise Exception("Program nie ma nic do zrobienia")
                
        # blad skladni w formuli    
        except ParseException, err:
            logging.error("formula ma niepoprawną składnię"+"\n"
                          + '='*self.LINELENGTH+"\n"
                          + str(err.line) +"\n"
                          + " "*(err.column-1) + "^" +"\n"
                          + '='*self.LINELENGTH+"\n"
                          + str(err)+"\n")
            
            raise Exception("Niepoprawna składnia formuły")
        
        # nie da sie otworzyc pliku z formula
        except IOError, err:
            logging.error("nie można otworzyć pliku z formułą"+"\n"
                          + "Errno=" + str(err.errno)+"\n"
                          + "Komunikat: " + str(err.strerror)+"\n")
            
            raise Exception("Nie udało się otworzyć pliku zawierającego formułę")
    
        logging.info("Wyczytwana formula to:\n\t`%s`", 
                 self.formulaFomratter.formula2str(self.formula))
        logging.debug("[%s] => \n\t[%s]\n\t(%s)", self.sessionArgs.formula, 
                  self.formulaFomratter.formula2str(self.formula),
                  str(self.formula))

        
    def __verifyFormula(self):
        
        self.satisfiable = False;
        self.valid = False;
        
        # sprawdz czy formuła jest spełnialna
        self.satisVerif = SatisfiabilityVerifier(self.formula)
        if self.satisVerif.verifyFormula():
            self.satisfiable = True;
            logging.info("Formuła jest spełnialna")

            # formuła jest spełnialna, sprawdz więc czy jest tautologią
            self.validVerif = ValidityVerifier(self.formula)
            if self.validVerif.verifyFormula():
                self.valid = True;
                logging.info("Formuła jest tautologią")
            else:
                logging.info("Formuła nie jest tautologią")
        else:
            logging.info("Formuła jest NIEspełnialna, a więc nie jest też tautologią")
            
            
        logging.debug("""
========================================================
Drzewo spelnialnosci:
%s
========================================================
""", str(self.satisVerif.tree))
        
        if self.validVerif:
            logging.debug("""
========================================================
Drzewo pełności:
%s
========================================================
""", str(self.validVerif.tree))



    def __encapsRaport(self, raport):
        llength = self.LINELENGTH
        hline = ('='*llength) + '\n'
        bline = ('-'*llength) + '\n'
        
        stitle = hline + \
                " LIPROJEKT RAPORT ".center(self.LINELENGTH, '-') + '\n' + \
                hline
        sdt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sformula = self.getFormattedFormula()
        
        ssatis = "Spełnialna: " + \
            ("TAK" if self.satisfiable else "NIE") + '\n'
        svalid = "Tautologia: " + \
            ("TAK" if self.valid else "NIE") + '\n'
        
        encraport =         \
            stitle +        \
            sdt + '\n\n' +    \
            sformula + '\n\n' + \
            ssatis + \
            svalid + \
            bline + \
            raport + '\n' + \
            bline
        return encraport
        
     
    def __generateRaport(self, withTree=True):
        bline = ("_"*50).center(self.LINELENGTH) + '\n';
        tab = " "*4
        conversionFormat =                                                \
            "ID [{nodeId}]\n"                                           + \
            tab + "[STAŁE / ZMIENNE]: [{clauseConsts} / {clauseVars}]\n"+ \
            tab + "[DO KONWERSJI]: [{clauseUnconvertedFomrulas}]\n"     + \
            tab + "[STATUS]: [{clauseStatus}]\n"

        raportFormat =                            \
            "Wynik := {result}\n"               + \
            "Dowód := {proof}\n"                + \
            "Wartościowanie := {valuation}\n"
        
        if withTree:
            raportFormat +=                               \
            bline                                       + \
            "KONWERSJA".center(self.LINELENGTH) +'\n'   + \
            bline                                       + \
            "{tree}"                                    + \
            bline


        raport = \
'''
*******************************
** SPRAWDZANIE SPEŁNIALNOŚCI **
*******************************

'''
        raport += self.satisVerif.generateRaport(
            self.formulaFomratter, raportFormat, conversionFormat)
        if self.satisfiable:
            rvalid = \
'''
*********************************************
** SPRAWDZANIE CZY FORMUŁA JEST TAUTOLOGIĄ **
*********************************************

'''
            rvalid += self.validVerif.generateRaport(
            self.formulaFomratter, raportFormat, conversionFormat)          
            raport += '\n' + rvalid;
            
        return self.__encapsRaport(raport)
            

    def __handleOutput(self):
        self.outputFile = None
        
        if self.sessionArgs.text:
            raport = self.__generateRaport(True)
        else:
            raport = self.__generateRaport(False)
        
        if self.sessionArgs.output:
            self.outputFile = self.sessionArgs.output
            writeMode = 'w'
        elif self.sessionArgs.Output:
            self.outputFile = self.sessionArgs.Output
            writeMode = 'a'
        
        if self.outputFile:          
            with open(self.outputFile, writeMode) as f:
                f.write(raport)
        else:
            print raport
        
        if self.sessionArgs.graph:
            raise Exception("Printing graphs not supported in this version")
        
                
    
    def __loadArguments(self, group, name):
        for arg in self.ARGS[name]:
            group.add_argument(*arg[0], **arg[1])
    
    def main(self):
        '''
        Wykonanie aplikacji
        
        1) parsuj argumenty wykonania
        2) Sprawdz czy formuła jest spełńialna
        3)  Jeżeli formuła jest spełnialna to sprawdź czy jest tautologią
        4) Prezentuj wyniki
        '''
        self.sessionArgs = self.parser.parse_args()
        self.__handleLogging()
        self.__handleInput()
        self.__verifyFormula()
        self.__handleOutput()
        
        logging.debug("""
%s
%s DEBUG END %s
%s
""", "*"*self.LINELENGTH, '*'*34, '*'*35, "*"*self.LINELENGTH)

    
    def getFormattedFormula(self):
        return self.formulaFomratter.formula2str(self.formula)

    def testRun(self, args):
        '''
        Testowe wykonanie aplikacji
        '''
        self.sessionArgs = self.parser.parse_args(args)
        self.__handleLogging()
        self.__handleInput()
        self.__verifyFormula()
        self.__handleOutput()
        
        logging.debug("""
%s
%s DEBUG END %s
%s
""", "*"*self.LINELENGTH, '*'*34, '*'*35, "*"*self.LINELENGTH)
    