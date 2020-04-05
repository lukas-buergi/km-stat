#!/usr/bin/env python3
# coding=utf-8
#######################################################################
# Copyright Lukas Bürgi 2019, 2020
#
# This file is part of km-stat.
#
# km-stat is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# km-stat is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with km-stat.  If not, see
# <https://www.gnu.org/licenses/>.
########################################################################
# work on WA-ML list in txt format exported from openoffice to structure
# it so that in the end it can go into the database
import re
from pprint import pprint
from anytree import NodeMixin
import pdb

DEBUG=True

class MatchingError(RuntimeError):
  pass

class Possibility(NodeMixin):
  def __init__(self, parent, previousLines, nextLines):
    super().__init__()
    self.parent=parent
    self.prev = previousLines
    self.next = nextLines
    if(DEBUG):
      print(self.getContext(5,5))
  
  def __str__(self):
    if(self.next != []):
      raise(RuntimeError("String representation only available when there are no unparsed lines remaining."))
    return(self.getParsed())
  
  def getContext(self, prev=1, next=5):
    """
    Returns the last line added to prev and some following lines from next.
    """
    out="----- Begin context -----\n"
    for l in self.prev[-prev:]:
      out += l + "\n"
    out += "----- Current position -----\n"
    for l in self.next[:next]:
      out += l + "\n"
    out += "----- End context -----\n"
    return(out)
  
  def getParsed(self):
    """
    Return the part of the  list that has been parsed so far.
    """
    out=""
    for l in self.prev:
      out += l + "\n"
    return(out)

class structuredList():
  maxPossibilityTreeHeight = 100
  finalNode = None
  
  def __init__(self, lines, enumeration):
    self.possibilityRoot = Possibility(None, [], lines)
    self.resetFirstLeaves()
    self.enumeration = enumeration
  
  def updateFirstLeaves(self):
    """
    Keep list of leaves to work on non-empty.
    """
    while( len(self.firstLeaves) == 0):
      if( len(self.nonLeaves) == 0):
        self.interactiveEliminate()
        if(self.possibilityRoot.is_leaf):
          self.firstLeaves = [self.possibilityRoot]
        else:
          self.nonLeaves = [self.possibilityRoot]
      else:
        nonLeaves=self.nonLeaves
        self.nonLeaves=[]
        for nonLeaf in nonLeaves:
          for node in nonLeaf.children:
            if(node.is_leaf):
              self.firstLeaves.append(node)
            else:
              self.nonLeaves.append(node)
    
  def resetFirstLeaves(self):
    """
    If list of leaves to work on might be out of date or empty, this functions rectifies the problem.
    """
    self.firstLeaves = []
    self.nonLeaves = []
    self.updateFirstLeaves()
    
  def interactiveEliminate(self):
    # ask user about the first line with multiple possibilities.
    cur = self.possibilityRoot
    while(len(cur.children) == 1):
      cur = cur.children[0]
    if(len(cur.children) > 1):
      print("Context: Previous lines:")
      for l in cur.prev[-5:]:
        print(l)
      print("-------------------------------------------------------")
      print("Multiple possibilities, please choose:")
      for i, c in enumerate(cur.children):
        print(str(i) + ":")
        print()
        print(c.getContext())
        print("-------------------------------------------------------")
      chosenChild = int(input("Enter the number of the right interpretation: "))
      self.possibilityRoot = cur.children[chosenChild]
      self.resetFirstLeaves()
    else:
      pass
  
  def extendPossibilityTree(self):
    """
    Extend probability tree on a best effort basis (might not change tree at all).
    """
    self.updateFirstLeaves()
    leaf = self.firstLeaves.pop()
    if(len(leaf.next)>0):
      previousLineArg = [leaf.prev[-1]] if len(leaf.prev) > 0 else []
      possibilities = self.enumeration(*previousLineArg).possibilities(leaf.next[0])
      for p in possibilities:
        Possibility(leaf, leaf.prev.append(p), leaf.next[1:])
      
      # delete leaf and go up the tree and delete all of its parents that would be leaves after the deletion of this child
      if(len(possibilities)==0):
        curNode=leaf
        while(curNode.is_leaf):
          p=curNode.parent
          if(p==None):
            #self.finalNode = leaf # delete line?
            raise(MatchingError("Failed, eliminated all possibilties. Final eliminated possibility is:\n" + leaf.getContext(5,5)))
          curNode.parent=None
          curNode=p
  
  def parseStep(self):
    if(len(self.possibilityRoot.next) == 0):
      # we are done, no use calling this method again
      return(False)
    else:
      if( self.possibilityRoot.height < self.maxPossibilityTreeHeight ):
        # continue in the hope that some can be eliminated
        self.extendPossibilityTree()
      else:
        self.interactiveEliminate()
      # shorten tree if possible, if the root has just one child, make that child the new root
      while(len(self.possibilityRoot.children) == 1):
        self.possibilityRoot = self.possibilityRoot.children[0]
      return(True)

class enumerationBase():
  """
  
  """
  mandatoryChild = False # if True, only matches if some child also matches NOT IMPLEMENTED
  childClasses = [] # classes of enumeration that could be children of this enumeration
  
  prefix = '^\s*' # no capturing groups allowed
  enumerationSymbol = '(?P<enumeration>(?P<symbol>[0-9]*)\.)\s*' # symbol capures enumeration symbol alone, enumeration captures the whole
  suffix = '(?P<content>.*)$' # content captures the actual content of the line
  
  referencePrefix = '^\s*'
  referenceSeparator = ''
  referenceSuffixPattern = ':\s*(?P<content>.*)$' # content captures the actual content of the line
  
  referenceSuffix = ': '
  
  
  firstEnumerationSymbol = 1
  lastEnumerationSymbol = 100
  
  def __str__(self):
    """
    The string representation of an enumeration structure is the line it represents, i.e. the line its oldest ancestor was initialized with.
    """
    if(self.parent):
      return(str(self.parent))
    else:
      return(self.line)
  
  def enumerationSymbolToInt(self, a):
    """ Enumeration symbols are int by default so this is the identity function. """
    assert(a>=self.firstEnumerationSymbol and a<=self.lastEnumerationSymbol)
    return(int(a))

  def intToEnumerationSymbol(self, a):
    """ Enumeration symbols are int by default so this is the identity function. """
    assert(a>=self.firstEnumerationSymbol and a<=self.lastEnumerationSymbol)
    return(int(a))
    
  def incrementedEnumerationSymbol(self, a):
    """ Returns incremented enumeration symbol a."""
    numeric = self.enumerationSymbolToInt(a)+1
    assert(numeric <= self.enumerationSymbolToInt(self.lastEnumerationSymbol))
    return(self.intToEnumerationSymbol(numeric))
    
  def decrementedEnumerationSymbol(self, a):
    """ Returns decremented enumeration symbol a."""
    numeric = self.enumerationSymbolToInt(a)-1
    assert(numeric >= self.enumerationSymbolToInt(self.firstEnumerationSymbol))
    return(self.intToEnumerationSymbol(numeric))
    
  def follows(self, a, b):
    """ Returns true if b directly follows a in the enumeration. """
    return(self.incrementedEnumerationSymbol(a) == b)
  
  def matchSingle(self, line):
    """
    Return False if no match, matched enumeration symbol otherwise.
    """
    regex = self.prefix + self.enumerationSymbol + self.suffix
    match = re.search(regex, line)
    pdb.set_trace()
    return(match)
  
  def matchReferenceStart(self, line):
    """
    Return False if no match, matched enumeration symbol and rest of line otherwise.
    """
    regex = self.referencePrefix + self.enumerationSymbol + self.referenceAfterEnumerationSymbol
    match = re.search(regex, line)
    pdb.set_trace()
    return(match)
    
  def matchReferenceRecursive(self, line):
    """
    Return False if no match, matched enumeration symbol and rest of line otherwise.
    """
    regex = self.referenceSeparator + self.enumerationSymbol + self.referenceAfterEnumerationSymbol
    match = re.search(regex, line)
    pdb.set_trace()
    return(match)

  def referenceWithoutSuffix(self):
    """
    Return the reference of this enumeration structure.
    """
    
    if(parent==None):
      return(self.referencePrefix + self.currentEnumeration)
    else:
      return(self.parent.referenceWithoutSuffix() + self.referenceSeparator + self.currentEnumeration)
  
  def referenceParseStep(self, restOfLine):
    possibilities = []
    for child in self.childClasses:
      try:
        possibilities.append(child(restOfLine, self))
      except(MatchingError):
        pass
    if(len(possibilities) > 1):
      raise(MatchingError("Initialization with invalid (ambiguous) reference failed."))
    if(possibilities==[]):
      return(None)
    else:
      return(possibilities[0])
  
  def __init__(self, line=None, parent=None):
    """
    Initializes the structure given a line which is parsed as a reference or single enumeration symbol.
    """
    # doesn't depend on arguments to init ##############################
    
    self.referenceAfterEnumerationSymbol = "(?:" + self.referenceSeparator + "|" + self.referenceSuffixPattern + ")"
    
    self.parentEnumerator = None
    self.childEnumerator = None
    
    self.currentEnumerationSymbol = None
    self.currentEnumeration = None
    
    # actual instance-specific stuff ###################################
    self.parent = parent
    self.line = line
    
    if(self.line):
      if(not self.parent):
        if(match := self.matchSingle(line)):
          self.currentEnumerationSymbol = match['symbol']
          self.currentEnumeration = match['enumeration']
        elif(match := self.matchReferenceStart(line)):
          self.currentEnumerationSymbol = match['symbol']
          self.currentEnumeration = match['enumeration']
          child=self.referenceParseStep(line[match.end('enumeration'):])
          if(child):
            self.child=child
          else:
            raise(MatchingError("Initialization with invalid reference failed (reference parses up to but excluding \"" + line[match.end('enumeration'):] + "\")."))
      elif(match := self.matchReferenceRecursive(line)):
        self.currentEnumerationSymbol = match['symbol']
        self.currentEnumeration = match['enumeration']
        self.child = self.referenceParseStep(line[match.end('enumeration'):])
      else:
        raise(MatchingError("Couldn't parse line \"" + line + "\" at all."))
  
  def possibilities(self, line, checkChildren=True):
    """
    Take a line which follows the one this object was initialized with, match this line against possible successors and return all possibilities of the line including  a full reference.
    """
    successors = []
    if(checkChildren):
      # check all children
      for child in self.childClasses:
        # see if the line matches the first enumeration symbol of the child class
        child = child()
        match = child.matchSingle(line)
        if(match and match['symbol'] == child.firstEnumerationSymbol):
          successor = self.referenceWithoutSuffix + self.referenceSeparator + match['symbol'] + self.referenceSuffix + match['content']
          successors.append(successor)
    # one possibility on this level
    if(self.line):
      # see if the line matches the next enumeration symbol of this class
      match = self.matchSingle(line)
      if(match and match['symbol'] == self.incrementedEnumerationSymbol(self.currentEnumerationSymbol)):
          successor = self.referenceWithoutSuffix + self.referenceSeparator + match['symbol'] + self.referenceSuffix + match['content']
          successors.append(successor)
    # call self.parent.possibilities
    if(self.parent):
      successors += self.parent.possibilities(line, False)
    return(successors)
    
class enumerationEmpty(enumerationBase):
  """ Empty lines that are ignored (or any other ignored lines). For other ignored lines, match them using prefix exclusively."""
  prefix = '^\s*'
  enumerationSymbol = '(?P<enumeration>)(?P<symbol>)'
  suffix = '(?P<content>)$'

class enumerationArabic(enumerationBase):
  pass

class enumerationChar(enumerationBase):
  enumerationSymbol = '(?P<enumeration>(?P<symbol>([a-z]))\.)\s*'
  firstEnumerationSymbol = 'a'
  lastEnumerationSymbol = 'z'
  
  def enumerationSymbolToInt(self, a):
    return(ord(a))

  def intToEnumerationSymbol(self, a):
    return(chr(a))

class enumerationNote(enumerationBase):
  prefix = '^\s*'
  enumerationSymbol = '(?P<enumeration>)(?P<symbol>Note)'
  suffix = '\s*(?P<content>.*[^:])$'
  
  def enumerationSymbolToInt(self, a):
    return(1)
    
  def intToEnumerationSymbol(self, a):
    return("Note")

class enumerationNoteTechnical(enumerationNote):
  enumerationSymbol = '(?P<enumeration>)(?P<symbol>Technical Note)'

  def intToEnumerationSymbol(self, a):
    return("Technical Note")

class enumerationCatchAll(enumerationBase):
  """
  Try to match a general normal list that might have been output from Microsoft Word or some such without extensive customization.
  This will ask much more questions than a custom tailored class.
  """

enumerationCatchAll.childClasses = [enumerationArabic, enumerationChar]
enumerationArabic.childClasses = [enumerationArabic, enumerationChar]
enumerationChar.childClasses = [enumerationArabic, enumerationChar]

textFilePath = 'structureListsTestGeneric.flat-in.txt'
with open(textFilePath, 'r', encoding='utf-8-sig') as f:
  test = f.readlines()

sl = structuredList(test, enumerationCatchAll)
try:
  while(sl.parseStep()):
    pass
except MatchingError as e:
  print(e)

outPath = '/tmp/out.txt'
with open(outPath, 'w') as f:
  f.writelines(sl.possibilityRoot.prev)
