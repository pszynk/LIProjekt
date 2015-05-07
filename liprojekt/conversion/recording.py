# -*- coding: utf-8 -*-
'''
Created on 20-03-2013

@author: pawel

Moduł zawiera klasy zapisujące dane o procesie walidacji
formuły logicznej (sprawdzania czy jest spełnialna / jest tautologią)
'''
from array import array
from collections import deque
from sets import Set
from cStringIO import StringIO

import logging

class ClauseBinTreeNode(object):
    '''
    Węzeł drzewa binarnego ClauseBinTree
    
    Odpowiada jednemu obiektowi clauses.Clause
    '''
    
    class NodeID():
        '''
        Identyfikator węzła ClauseBinTree
        
        Format indetyfikatora to np: 
        * C00010 -> jego ojciec ma ID C0001
        * C0101  -> jego synowi mają ID: C01010 i C01011
        '''
        LEFT, RIGHT = range(2)
        SYMBOL = 'C'
        def __init__(self, parentID = None, direct = None):
            '''
            Należy podać ID ojca, oraz informację, czy jesteśmy lewym, czy prawym dzieckiem
            '''
            if parentID is None:
                self.code = array('B')
            elif direct is None:
                raise ValueError("direct nie moze byc None jezeli podano parentID")
            elif direct not in (self.LEFT, self.RIGHT):
                raise ValueError("direct musi przyjmowac wartosci NodeID.LEFT "+self.LEFT + 
                                 " albo NodeID.RIGHT "+self.RIGHT)
            else:
                self.code = array('B', parentID.code)
                self.code.append(direct)
        
        def __str__(self):
            return self.SYMBOL + "".join(map(str, self.code.tolist()))
                    
        
    def __init__(self, clause):
        '''
        ClauseBinTree tworzony jest z obiektu clauses.Clause
        '''
        self.__clause = clause
        self._parent = None
        self._leftChild = None
        self._rightChild = None       
        self._ID = ClauseBinTreeNode.NodeID()
    
    @property
    def clause(self):
        '''
        obiekt clauses.Clause który odpowiada temu węzłowi
        '''
        return self.__clause
    
    @property
    def parent(self):
        '''
        ojciec węzła
        '''
        return self._parent
    
    @parent.setter
    def parent(self, node):
        '''
        ustaw za ojca węzeł node
        '''
        if node is not None:
            self._parent = node

    
    def getChildren(self):
        '''
        pobierz listę dzieci węzła
        '''
        return [x for x in [self._leftChild, self._rightChild] if x is not None]
    
    
    def setChildren(self, left=None, right=None):
        """
        ustaw węzły lest, right jako dzieci węzła
        """
        self._leftChild = left
        self._rightChild = right

    
    def addChild(self, node):
        '''
        dodaj węzły jako dzieci węzła, zaczynajac od lewego
        '''
        if self._leftChild is None:
            self._leftChild = node
            self._leftChild.ID = ClauseBinTreeNode.NodeID(self._ID, 
                ClauseBinTreeNode.NodeID.LEFT)
        elif self._rightChild is None:
            self._rightChild = node
            self._rightChild.ID = ClauseBinTreeNode.NodeID(self._ID, 
                ClauseBinTreeNode.NodeID.RIGHT)
        else:
            raise Exception("Nie mozna dodac wiecej dzieci")
            
                
    @property
    def ID(self):
        '''
        ID węzła (NodeID)
        '''
        return self._ID
    
    @ID.setter
    def ID(self, ID):
        '''
        ustaw ID węzła (NodeID)
        '''
        self._ID = ID
      
    
    def isLeaf(self):
        '''
        czy węzeł jest liściem?
        '''
        return self._children == []
    
    def isRoot(self):
        '''
        czy węzeł jest korzeniem?
        '''
        return self.parent == None

    def clause2str(self, fformatter, treeNodeFormat, statusPrefix="", onlyResolved=False):
        '''
        Formatowana informacja o clauses.Clause w danym węźle
        
        Zwraca formatowaną wiadomość zawierającą informacje o półprodukcie clauses.Clause
        znajdującym się w węźle. Możliwe info. to:
        * {nodeId}                    : ID węzła
        * {clauseVars}                : zmienne logiczne w klauzuli
        * {clauseConsts}              : stałe logiczne w klauzuli
        * {clauseConvertedFormulas}   : uproszczeone podformuły w klauzuli
        * {clauseUnconvertedFomrulas} : NIEuproszczeone podformuły w klauzuli
        * {clauseAllFormulas}         : wszystkie podformuły klauzuli
        * {clauseStatus}              : status klauzuli
        '''
        attars = {
            'nodeId':                       str(self._ID),
            'clauseVars':                   self.clause.lvars2str(fformatter),
            'clauseConsts':                 self.clause.lconsts2str(fformatter),
            'clauseConvertedFormulas':      self.clause.convertedFormulas2str(fformatter),
            'clauseUnconvertedFomrulas':    self.clause.unconvertedFormulas2str(fformatter),
            'clauseAllFormulas':            self.clause.allFormulas2str(fformatter),
            'clauseStatus':                 self.clause.status2str(fformatter, 
                                                statusPrefix, onlyResolved)
        }
        try:
            rtrn = treeNodeFormat.format(**attars)
        except KeyError as e:
            raise Exception(str(self.__class__)+'nie ma atrubutu do wypisywanie`'+
                            e.args[0]+'`')
        else:
            return rtrn
        
    def __str__(self):
        return str(self._ID) + ": " + str(self.clause)
    
              
class ClauseBinTree(object):
    '''
    Drzewo binarne zawierające historię walidacji(konwersji) formuły
    
    Drzewo binarne którego węzłami są obiekty ClauseBinTree.
    '''
    def __init__(self, root=None):
        '''
        Tworzenie pustego drzewa, lub drzewa z korzeniem root
        '''
        self.nodes = Set()
        self.root = root

    @property
    def root(self):
        '''
        zwróć korzeń drzewa
        '''
        return self.__root
    
    @root.setter
    def root(self, node):
        '''
        ustaw korzeń drzewa (i wyczyść wszystkie węzły)
        '''
        self.nodes.clear()
        self.__root = node
        self.nodes.add(node)
    
    def addLeaf(self, node, parent=None):
        '''
        dodaj liść do drzewa
        
        Dołącza do drzewa liść node, jeżeli nie podano wartości parent to 
        node jest ustawiany jako korzeń.
        '''
        logging.debug("Dodaję liść \n%s\n, do ojca \n%s\n", str(node), str(parent))
        if parent is None:
            if self.root is not None:
                raise ValueError("Parent can't be 'None', the tree already has its root")
            else:
                self.root = node
        elif parent in self:
            if node in self:
                raise ValueError("node already in the tree")
            else:
                node.setChildren()
                parent.addChild(node)
                self.nodes.add(node)
        else:
            raise ValueError("parent not in the tree")
    
  
    def indepthGen(self):
        '''
        generator zwracający, węzły drzewa zgodnie z algorytmem przechodznia 
        drzewa binarnego wszerz
        '''
        queue = deque()
        queue.append(self.root)
        while queue:
            node = queue.popleft()
            queue.extend(node.getChildren())
            yield node
            
    
    def tree2str(self, fformatter, treeNodeFromat):
        '''
        wypisz węzły drzewa, zgodnie z formatem treeNodeFormat,
        przechodząc drzewo wszerz
        '''
        
        rtrn = StringIO()
        for node in self.indepthGen():
            rtrn.write(node.clause2str(fformatter, treeNodeFromat)+"\n")
        return rtrn.getvalue()
    
    def __contains__(self, item):
        '''
        czy drzewo zawiera obiekt item
        '''
        
        return item in self.nodes
    
    def __len__(self):
        '''
        ilość elementów w drzewie
        '''
        
        return len(self.nodes)
    
    def __str__(self):
        rtrn = StringIO()
        for node in self.indepthGen():
            rtrn.write(str(node)+"\n")
        return rtrn.getvalue()
    
        
        
           
    
    
    