# -*- coding: utf-8 -*-

'''
Paczka z kodem aplikacji LIProjekt, do weryfikowania
spełnialności formuły logicznej i sprawdzania, czy formuła
logicznja jest tautologią

1) Spis plików z kodem
2) Instrukcja obsługi
3) Opis działania
4) Testy

Ad 1.
    liprojekt/
    ├── conversion
    │   ├── clauses.py
    │   ├── formatting.py
    │   ├── formulas.py
    │   ├── recording.py
    │   └── verification.py
    ├── interface
    │   └── interface.py
    ├── parsing
    │   ├── alphabets.py
    │   ├── myparsing.py
    │   └── parsers.py
    └── tests
        └── tests.py

Ad 2.
    * Program pozwala na wczytanie formuły logicznej z wjeści lub z pliku.
    
    * W celu poznania składni w jakiej powinny być pisane formuły
      należy uruchomić program z opcją -l [nazwa wybranej składni]
      (obecnie program obługije dwie składnie WORD i SYMBOLIC)
      `liprojekt -l WORD`
    
    * Aby przetestować program dostępną paczką testów, należy uruchomić program
      z parametrem test
      `liprojekt test` 
      
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

3) Opis działania
- Wejściowa formuła logiczna to F

- Aby sprawdzić czy F jest spełnialna, należy doprowadzić F do postaci DNF,
  jeżeli podczas tworzenia klauzul koniunkcyjnych nie natrafimy w jednej z nich
  na zmienną logiczną i jej zaprzeczenie, to formuła jest spełnialna
  
- Aby sprawdzić czy F jest tautologią, należy doprowadzić F do postaci CNF,
  jeżeli podczas tworzenia klauzul dysjunkcujnych w każdej z nich natrafimy
  na zmienną logiczną i jej zaprzeczenie, to formuła jest tautologią
  
  Do tworzenia klauzul:
    (koniunkcyjnej / dysjunkcujnej)
  wykorzystywana jest klasa:
    (conversion.clauses.ConjunctionClause / conversion.clauses.DisjunctionClause)
    (CC / DC)
    
  Są to półprodukty z kótrych powstają właściwe klauzule.
  Obie klasy mają metode convertStep która upraszcza znajdującą się w niej 
  formułę i zwraca klauzule lub parę klauzul
  Przykład:
  
  F = (p & ~p) => q
  CC(F).convertStep = [CC(~p | p), CC(q)] <- rozbicie na dwie klauzule
  DC(F).convertStep = [DC(q, (~p | p))]   <- powstanie jednej klauzuli 

  Tworzone jest drzewo konwersji T
  Za korzeń drzewa brane jest C(T)  (CC dla DNF, DC dla CNF)
  
  algorytm jest następujący:
  1) weź liść drzewa L
  2) Czy L spełnia warunek STOP
  3) NIE:
  4)     wykonaj L.convertStep = [a, b]
  5)     ustaw a, b jako synów L
  6) TAK:
  7)    czy L decyduje o wyniku?
  8)    TAK
  9)        Podaj wynik zgodny z L, przerwij iteracje
  10)   NIE
  11)       Kontynuj algorytm
  
  warunki STOP dla DNF (spełnialność):
      1. klauzula zawiera zmienną i jej negacje (nie istjeje spełniające ją wartościowanie)
      2. klauzula NIE zawiera zmiennej i jej negacji (istnieje spełniające ją wartościowanie)
      
    * w przypadku warunku 2. algorytm jest przerywany, formuła jest spełnialna
    * Jeżeli nie ma więcej liści do sprawdzenia, znaczy że wszystkie spełniają 1.
      czyli, klauzula jest niespełnialna
      
   warunki STOP dla CNF (spełnialność):
      1. klauzula zawiera zmienną i jej negacje (jest tautologią)
      2. klauzula NIE zawiera zmiennej i jej negacji (nie jest tautologią)
      
    * w przypadku warunku 2. algorytm jest przerywany, formuła jest tautologią
    * Jeżeli nie ma więcej liści do sprawdzenia, znaczy że wszystkie spełniają 1.
      czyli, klauzula jest tautologią

4) testy 

    testy uruchamiane są poleceniem `liprojekt test`
    wyniki zapisane są do pliku test_output.txt
    
    szczegóły o testach znajdują sie w dokumentacji modułu liprojekt.tests.tests
'''