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
import re, pdb
from pprint import pprint
from anytree import NodeMixin

class MatchingError(RuntimeError):
  pass

class Possibility(NodeMixin):
  def __init__(self, parent, previousLines, nextLines):
    super().__init__()
    self.parent=parent
    self.prev = previousLines
    self.next = nextLines
    # sanitize lines
    for index, line in enumerate(self.prev):
      self.prev[index] = line.strip()
    for index, line in enumerate(self.next):
      self.next[index] = line.strip()
  
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
      if(len(leaf.prev) > 0):
        enum = self.enumeration(leaf.prev[-1])
      else:
        enum = self.enumeration()
      
      possibilities = enum.getReferencePossibilities(leaf.next[0])

      for p in possibilities:
        Possibility(leaf, leaf.prev+[p], leaf.next[1:])
      
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

  def parse(self):
    while(self.parseStep()):
      pass
    
  def get(self):
    return(str(self.possibilityRoot))

class enumerationBase():
  """
  
  """
  mandatoryChild = False # if True, only matches if some child also matches TODO NOT IMPLEMENTED
  childClasses = [] # classes of enumeration that could be children of this enumeration
  
  # canonical versions for output
  symbolPrefix = ''
  symbolSuffix = '.'

  referencePrefix = ''
  referenceSeparator = ''
  referenceSuffix = ': '

  # regex versions for matching
  symbolPrefixRegex = r''
  symbolRegex = r'[0-9]*'
  symbolSuffixRegex = r'\.'
  
  standardLinePrefixRegex = r'^\s*'
  standardLineSuffixRegex = r'\s*:?\s*(?P<content>.*)$' # content captures the actual content of the line
  
  referenceLinePrefixRegex = r'^\s*'
  referenceSeparatorRegex = r'\s*'
  referenceLineSuffixRegex = r'\s*:\s*(?P<content>.*)$' # content captures the actual content of the line  
  
  # range of symbols
  first = 1
  last = 100
  
  def __init__(self, line=None, parent=None):
    """
    Initializes the structure given a line which is parsed as a reference or single enumeration symbol.
    """
    # doesn't depend on arguments to init ##############################
    self.current = self.first - 1
    self.content = None
    
    self.referenceAfterEnumerationRegex = "(?:" + self.referenceSeparatorRegex + "|" + self.referenceLineSuffixRegex + ")"
    
    self.child = None
    
    # actual instance-specific stuff ###################################
    self.parent = parent
    self.line = line
    if(not line is None):
      self.setFromLine()

  def getStandardLineRegex(self):
    return( self.standardLinePrefixRegex
          + r'(?P<enumeration>'
          + self.symbolPrefixRegex
          + r'(?P<symbol>'
          + self.symbolRegex
          + r')'
          + self.symbolSuffixRegex
          + r')'
          + self.standardLineSuffixRegex
    )
  
  def getStandardLineMatch(self, line):
    """
    Return None or a dict-like object with entries enumeration, symbol and content.
    """
    match = re.search(self.getStandardLineRegex(), line)
    return(match)

  def increment(self, line):
    match = self.getStandardLineMatch(line)
    if(match):
      number = self.enumerationSymbolToInt(match['symbol'])
      if(number == self.current + 1):
        self.current += 1
        self.content = match['content']
        self.line = line
      else:
        raise(MatchingError("Could match line (" + number + "th, " + line + "), but isn't successor to this one (" + self.current + "th)."))
    else:
      raise(MatchingError("Couldn't match line: " + line))

  def getReferenceStartRegex(self):
    return( self.referenceLinePrefixRegex
          + r'(?P<enumeration>'
          + self.symbolPrefixRegex
          + r'(?P<symbol>'
          + self.symbolRegex
          + r')'
          + self.symbolSuffixRegex
          + r')(?P<restOfLine>'
          + self.referenceAfterEnumerationRegex
          + r')'
    )

  def getReferenceStartMatch(self, line):
    """
    Return None or a dict-like object with entries enumeration, symbol, content, restOfLine.
    """
    match = re.search(self.getReferenceStartRegex(), line)
    return(match)
  
  def getReferenceRecursiveRegex(self):
    return( self.referenceSeparatorRegex
          + r'(?P<enumeration>'
          + self.symbolPrefixRegex
          + r'(?P<symbol>'
          + self.symbolRegex
          + r')'
          + self.symbolSuffixRegex
          + r')(?P<restOfLine>'
          + self.referenceAfterEnumerationRegex
          + r')'
    )
  
  def getReferenceRecursiveMatch(self, line):
    """
    Return None or a dict-like object with entries enumeration, symbol, content, restOfLine.
    """
    match = re.search(self.getReferenceRecursiveRegex(), line)
    return(match)

  def __str__(self):
    """
    The string representation of an enumeration structure is the line it represents in canonical (nicely formatted) form.
    """
    return(self.getReference() + self.getContent())


  def getContent(self):
    if(self.line is None):
      raise(RuntimeError("Not initialized, can't get content."))
    return(self.content)
  
  def enumerationSymbolToInt(self, a):
    """ Enumeration symbols are int by default so this is the identity function. """
    return(int(a))

  def intToEnumerationSymbol(self, a):
    """ Enumeration symbols are int by default so this is the identity function. """
    return(str(a))
    
  def incrementedEnumerationSymbol(self, a):
    """ Returns incremented enumeration symbol a."""
    numeric = self.enumerationSymbolToInt(a)+1
    return(self.intToEnumerationSymbol(numeric))
    
  def decrementedEnumerationSymbol(self, a):
    """ Returns decremented enumeration symbol a."""
    numeric = self.enumerationSymbolToInt(a)-1
    return(self.intToEnumerationSymbol(numeric))
    
  def follows(self, a, b):
    """ Returns true if b directly follows a in the enumeration. """
    return(self.incrementedEnumerationSymbol(a) == b)
  
  def getCurrentEnumerationSymbol(self):
    return(self.intToEnumerationSymbol(self.current))
  
  def getCurrentEnumeration(self):
    return(self.getCurrentEnumerationSymbol() + self.symbolSuffix)
  
  def getReferenceNoSuffix(self):
    """
    Return the reference of this enumeration structure.
    """
    if(self.parent==None):
      return(self.referencePrefix + self.getCurrentEnumeration())
    else:
      return(self.parent.getReferenceNoSuffix() + self.referenceSeparator + self.getCurrentEnumeration())

  def getReference(self):
    """
    Return the full reference of this enumeration structure.
    """
    return(self.getReferenceNoSuffix() + self.referenceSuffix)
  
  def getEnumerationFromReference(self, restOfLine):
    possibilities = []
    for child in self.childClasses:
      try:
        c = child(restOfLine, self)
      except(MatchingError):
        pass
      else:
        possibilities.append(c)
    if(len(possibilities) > 1):
      raise(MatchingError("Parsing invalid (ambiguous) reference failed."))
    if(possibilities==[]):
      raise(MatchingError("Parsing invalid (no way to parse correctly) reference failed."))
    else:
      return(possibilities[0])
  
  def setFromReference(self):
    if(self.parent):
      # continue matching partially matched line
      match = self.getReferenceRecursiveMatch(self.line)
    else:
      # match beginning of line
      match = self.getReferenceStartMatch(self.line)
    
    if(match):
      self.current = self.enumerationSymbolToInt(match['symbol'])
      self.content = match['content']
      
      # either we are done or we need to continue parsing
      try:
        self.child = self.getEnumerationFromReference(match['restOfLine'])
      except(MatchingError):
        pass
    else:
      if(self.parent):
        raise(MatchingError("Couldn't match reference (at second or later step)"))
      else:
        raise(MatchingError("Couldn't match reference (at beginning)."))
  
  def setFromLine(self):
    """
    Try to match a line without context.
    """
    if( self.line is None):
      raise(RuntimeError("No line given to match, self.line is None."))
    
    if( self.parent ):
      raise(RuntimeError("Doesn't make sense to match without context given a parent. Does it?"))
    
    # try to parse as reference
    try:
      self.setFromReference()
    except(MatchingError):
      # fall back to parsing as ordinary line (with empty/zero context)
      self.increment(self.line)

  def getReferencePossibilities(self, line, checkChildren=True):
    """
    Take a line which follows the one this object was initialized with, match this line against possible successors and return all possibilities of the line including  a full reference.
    """
    possibilities = []
    
    # children are possibilities
    if(checkChildren and not self.line is None):
      # check all children
      for child in self.childClasses:
        # see if the line matches the first enumeration symbol of the child class
        # TODO: This also allows reference matches. Problem?
        try:
          child = child(line, self)
        except(MatchingError):
          continue
        possibility = str(child)
        possibilities.append(possibility)
    
    # one possibility on this level

    try:
      self.increment(line)
    except(MatchingError):
      pass
    else:
      possibility = self.getReference() + self.getContent()
      possibilities.append(possibility)
    # call self.parent.possibilities
    if(not self.parent is None):
      possibilities += self.parent.getReferencePossibilities(line, False)
    return(possibilities)
    
class enumerationEmpty(enumerationBase):
  """
  Empty lines that are ignored (or any other ignored lines). For other ignored lines, match them using prefix exclusively.
  TODO: Actually ignore them, currently produces blank lines.
  """
  prefix = '^\s*'
  enumerationSymbol = '(?P<enumeration>)(?P<symbol>)'
  suffix = '(?P<content>)$'
  
  # canonical versions for output
  symbolPrefix = ''
  symbolSuffix = ''

  referencePrefix = ''
  referenceSeparator = ''
  referenceSuffix = ''

  # regex versions for matching
  symbolPrefixRegex = r''
  symbolRegex = r''
  symbolSuffixRegex = r''
  
  standardLinePrefixRegex = r'^\s*'
  standardLineSuffixRegex = r'(?P<content>)$' # content captures the actual content of the line
  
  referenceLinePrefixRegex = r'^\s*'
  referenceSeparatorRegex = r''
  referenceLineSuffixRegex = r'(?P<content>)$' # content captures the actual content of the line  

class enumerationArabic(enumerationBase):
  pass

class enumerationChar(enumerationBase):
  # canonical versions for output
  symbolPrefix = ''
  symbolSuffix = '.'

  referencePrefix = ''
  referenceSeparator = ''
  referenceSuffix = ': '

  # regex versions for matching
  symbolPrefixRegex = r''
  symbolRegex = r'[a-z]*'
  symbolSuffixRegex = r'\.'
  
  standardLinePrefixRegex = r'^\s*'
  standardLineSuffixRegex = r'\s*:?\s*(?P<content>.*)$' # content captures the actual content of the line
  
  referenceLinePrefixRegex = r'^\s*'
  referenceSeparatorRegex = r'\s*'
  referenceLineSuffixRegex = r'\s*:\s*(?P<content>.*)$' # content captures the actual content of the line  
  
  # range of symbols
  first = 1
  last = 26
  
  def enumerationSymbolToInt(self, a):
    return(ord(a)-96)

  def intToEnumerationSymbol(self, a):
    return(chr(a+96))

class enumerationNote(enumerationBase):
  """
  Not properly implemented.
  """
  prefix = '^\s*'
  enumerationSymbol = '(?P<enumeration>)(?P<symbol>Note)'
  suffix = '\s*(?P<content>.*[^:])$'
  
  def enumerationSymbolToInt(self, a):
    return(1)
    
  def intToEnumerationSymbol(self, a):
    return("Note")

class enumerationNoteTechnical(enumerationNote):
  """
  Not properly implemented.
  """
  enumerationSymbol = '(?P<enumeration>)(?P<symbol>Technical Note)'

  def intToEnumerationSymbol(self, a):
    return("Technical Note")

class enumerationCatchAll(enumerationBase):
  """
  Try to match a general normal list that might have been output from Microsoft Word or some such without extensive customization.
  This will ask much more questions than a custom tailored class.
  """

class enumerationCatchAllArabic(enumerationArabic):
  pass

class enumerationCatchAllChar(enumerationChar):
  pass

enumerationCatchAll.childClasses = [enumerationCatchAllArabic, enumerationCatchAllChar]
enumerationCatchAllArabic.childClasses = [enumerationCatchAllArabic, enumerationCatchAllChar]
enumerationCatchAllChar.childClasses = [enumerationCatchAllArabic, enumerationCatchAllChar]

if __name__ == '__main__':
  textFilePath = 'structureListsTestGeneric.flat-in.txt'
  with open(textFilePath, 'r', encoding='utf-8-sig') as f:
    test = f.readlines()

  sl = structuredList(test, enumerationCatchAll)
  try:
    sl.parse()
  except MatchingError as e:
    print(e)

  outPath = '/tmp/out.txt'
  with open(outPath, 'w') as f:
    f.writelines(sl.possibilityRoot.prev)
