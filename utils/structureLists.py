#######################################################################
# Copyright Lukas Bürgi 2019
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

class MatchingError(RuntimeError):
  pass

class indentedLine():
  def __init__(self, indentation, line):
    self.indentation = indentation
    self.line = line.lstrip()

  def get(self):
    return(" " * self.indentation + self.line)
    
class numberedList():
  mandatoryChild = False # next line needs to match one of innerClasses
  irrelevantParent = False # usually it makes a difference if a class matches as inner of one class or another

  prefix = '^\s*' # no capturing groups allowed
  enumerationSymbol = None # regex to detect this level. The actual symbol needs to be the only capturing group in the regex
  suffix = '\.' # no capturing groups allowed

  innerClasses = []

  def __init__(self, tail=None, lines=None, outer=None):
    self.inner = None # Link to adjacent inner level
    lastEnumSymbol = self.intToEnumSymbol(0) # the last enumeration symbol that was encountered on this level
    if(self.enumerationSymbol == None):
        raise(RuntimeError("Usage error, enumerationSymbol not defined in " + self.__class__.__name__))
    self.regex = re.compile(self.prefix + self.enumerationSymbol + self.suffix)
    
    if(tail == None):
      self.depth = 0 # Depth of this level
      self.outer = None # Link to adjacent outer level
      self.tail = self # Link to outermost level (that saves some shared state)

      # The following are shared among instances in the same hierarchy
      self.indentedLines = [] # array of instances of indentedLine()
      self.untreatedLines = lines # array of strings, constant
      self.currentLine = 0 # the index into untreatedLines
      self.head = self
    else:
      self.depth = outer.depth + 1 # Depth of this level
      self.outer = outer # Link to adjacent outer level
      self.tail = tail # Link to outermost level (that saves some shared state)


  def copy(self):
    if(self.tail == self):
      copy = self.__class__(lines=self.untreatedLines)
      copy.indentedLines = self.indentedLines
      copy.currentLine = self.currentLine
      return(copy)
    else:
      raise(NotImplementedError())
 
  def getInnerClasses(self):
    """ Classes of which one is chosen to instantiate and assign to "inner" if inner == None and we need to go deeper. """
    return(self.innerClasses)

  def enumSymbolToInt(self, a):
    """ Enumeration symbols are int by default. """
    return(a)

  def intToEnumSymbol(self, a):
    """ Enumeration symbols are int by default. """
    return(a)
    
  def incrementedEnumSymbol(self, a):
    """ Returns incremented enumeration symbol a."""
    return(self.intToEnumSymbol(self.enumSymbolToInt(a)+1))

  def follows(self, a, b):
    """ Returns true if b directly follows a in the enumeration. """
    return(self.incrementedEnumSymbol(a) == b)

  def isEnumSymbol(self, a):
    """ Checks whether something is an enumSymbol. Assumes there are less than 100 enum symbols, change the value if necessary. """
    n=self.enumSymbolToInt(a)
    return(1<n and n<100)
  
  def getLine(self):
    return(self.tail.untreatedLines[self.tail.currentLine])

  def match(self):
    """ Returns whether the current line matches. """
    return(self.regex.search(self.getLine()))

  def getEnumSymbol(self):
    return(self.match().group(1))
  
  def check(self):
    try:
      enumSymbol = self.getEnumSymbol()
    except AttributeError:
      return(False)
    return(self.follows(self.lastEnumSymbol, enumSymbol))

  def call(self):
    """ Adds next line to this level, including all the book keeping. """
    self.lastEnumSymbol = self.getEnumSymbol()
    self.tail.indentedLines.append(indentedLine(self.depth, self.getLine()))
    self.tail.currentLine += 1
    self.tail.head = self
    self.outer.inner = self

  def callNextLevel(self):
    """ Find level of next line, add it. """
    # find all levels that match
    candidateLevels = []
    currentLevel = self.tail
    if(not self.mandatoryChild):
      while(currentLevel != self):
        candidateLevels.append(currentLevel)
        currentLevel = currentLevel.inner
    candidateLevels.append(self)
    
    matchingLevels = []
    for level in candidateLevels:  
      if(level.check()):
        matchingLevels.append(level)
      for ilevel in level.getInnerClasses():
        instance = ilevel(tail=self.tail, outer=level)
        if(type(instance) != type(level.inner) and instance.check()): # cond. for all elements of level.inner
          matchingLevels.append(instance)
    
    
    if(len(matchingLevels) == 0):
      raise(MatchingError(
        "No matching level found for line " + str(self.tail.currentLine) + " which is as follows:\n"
        + self.getLine()
        + "Previous lines were:\n" + self.get(10)
        + "Previous line was of type " + self.__class__.__name__ + ".\n"
        + "Candidates would have been: " + str(candidateLevels)
      ))
    elif(len(matchingLevels) == 1):
      nextLevel = matchingLevels[0]
    else:
      # eliminate duplicates
      # sort matchingLevels by type(matchingLevels)
      matchingLevels.sort(key=lambda x : type(x).__name__)
      # go through matchingLevels and delete each level if the previous level has same type and the type has irrelevantParent==True
      pre = matchingLevels[0]
      for nex in matchingLevels[1:]:
        if(type(pre) == type(nex)):
          matchingLevels.remove(nex)
        else:
          pre = nex
      if(len(matchingLevels) == 1):
        nextLevel = matchingLevels[0]
      else:
        print("There are " + str(len(matchingLevels)) + " matching levels:")
        for i, level in enumerate(matchingLevels):
          print(str(i) + ": " + level.outer.__class__.__name__ + "->" + level.__class__.__name__)
        print("Previous lines:")
        print(self.get(10))
        print("Next line:")
        print(self.getLine())
        i = int(input("Enter number to choose: "))
        assert(0<=i)
        assert(i<len(matchingLevels))
        nextLevel = matchingLevels[i]
    # add current line
    nextLevel.call() 

  def parse(self):
    """ Do the work, without outputting it. """
    if(self.tail.currentLine < len(self.tail.untreatedLines)):
      self.tail.head.callNextLevel()
      self.tail.head.parse()
    else:
      print("Done. Quitting.")

  def get(self, amount=None):
    """ Return the indented lines as a string."""
    if(amount == None):
      amount = len(self.tail.indentedLines)
    maxi = len(self.tail.indentedLines)
    result = ""
    for l in self.tail.indentedLines[-min(amount, maxi):]:
      result += l.get() + "\n"
    return(result)

class numberedListReference(numberedList):
  """ A class for references containing the whole hierarchy instead of just the least significant symbol of it. It matches lines as follows: The numberedListReference.prefix string is a prefix, then any legal sequence of enumeration symbols separated by numberedListReference.separator which defaults to whitespace and ended by numberedListReference.suffix which defaults to .*. """
  prefix = '^ML\s*' #([0-9]+)\.\s*(?:([a-z])\.\s*([0-9]+)\.\s*)*(?:([a-z])\.)?'
  separator = '\s*'
  suffix = '\s*:.+$'
  
  enumerationSymbol = '' # shut up problem, TODO: solve properly
  
  tailClass = None # In case this is the first class called, need another class to use as tail

  def __init__(self, tail=None, lines=None, outer=None):
    super().__init__(tail, lines, outer)
    if(tail==None):
      self.tail = self.tailClass(tail, lines, outer)

  def getMatch(self, array):
    regexString = ""
    for r in array:
      regexString += r
    compiled = re.compile(regexString)
    match = compiled.search(self.getLine())
    return(match)

  def check(self):
    regex = [self.prefix, self.tail.enumerationSymbol, self.suffix]
    if(self.getMatch(regex)):
      newTail = self.tail.copy()
      newTail.lastEnumSymbol = self.getMatch(regex).groups()[-1]
      while(self.getMatch(regex).end() < len(self.getLine()) - 1):
        addedNew = False
        for c in newTail.tail.head.getInnerClasses():
          newRegex = regex.copy()
          newRegex.insert(-2, self.separator)
          newRegex.insert(-2, c.enumerationSymbol)
          if(self.getMatch(newRegex)):
            regex = newRegex
            head = c(tail=newTail, outer=newTail.head)
            head.lastEnumSymbol = self.getMatch(regex).groups()[-1]
            newTail.head.outer = head
            newTail.tail.head = head
        if(not addedNew):
          break
      return(newTail)
    else:
      return(False)


  def call(self):
    newTail = self.check()
    assert(newTail)
    # TODO: check the following works
    self.tail.head = newTail
    self.tail = newTail
    self.tail.indentedLines.append(indentedLine(0, self.tail.untreatedLines[self.tail.currentLine]))
    self.tail.currentLine += 1

class numberedListEmpty(numberedList):
  """ Empty lines or other lines that are ignored. """
  prefix = '^'
  enumerationSymbol = ''
  suffix = '$'

  irrelevantParent = True
  
  def check(self):
    return(self.match())

  def call(self):
    self.tail.currentLine += 1

class numberedListArabic(numberedList):
  enumerationSymbol = '([0-9]+)'
  suffix = '\..*$'

class numberedListChar(numberedList):
  enumerationSymbol = '([a-z])'
  suffix = '\..*$'
  # TODO: Why is this in fact needed here?
  lastEnumSymbol = chr(ord('a')-1)
  
  def enumSymbolToInt(self, a):
    return(ord(a))

  def intToEnumSymbol(self, a):
    return(chr(a))

class numberedListNote(numberedList):
  enumerationSymbol = '(Technical )?Note'

  def check(self):
    return(self.match())

  def call(self):
    self.tail.indentedLines.append(indentedLine(self.depth, self.tail.untreatedLines[self.tail.currentLine]))
    self.tail.currentLine += 1

class numberedListNoteWithChildren(numberedList):
  mandatoryChild = True
    
  enumerationSymbol = '(Technical )?Note'
  suffix = '.*:$'
  def check(self):
    return(self.match())

  def getEnumSymbol(self):
    return(None)

class numberedListArabicInner(numberedListArabic):
  pass

class numberedListArabicOuter(numberedListArabic):
  pass

class numberedListCharInner(numberedListChar):
  pass

class numberedListCharOuter(numberedListChar):
  pass

class numberedListReferenceML(numberedListReference):
  prefix = '^ML\s*'
  suffix = '\..*$'
  tailClass = numberedListArabicOuter

numberedListArabicInner.innerClasses = [numberedListEmpty, numberedListCharInner]
numberedListCharInner.innerClasses = [numberedListEmpty, numberedListArabicInner]
numberedListNoteWithChildren.innerClasses = [numberedListEmpty, numberedListCharInner]

numberedListArabicOuter.innerClasses = [numberedListEmpty, numberedListReferenceML, numberedListNoteWithChildren, numberedListNote, numberedListCharOuter]
numberedListCharOuter.innerClasses = [numberedListEmpty, numberedListReferenceML, numberedListNoteWithChildren, numberedListNote, numberedListArabicOuter]

textFilePath = '/home/t4b/km-stat/kriegsmaterialch/utils/wassenaar-lists/2018/15 - WA-LIST (18) 1 - ML - Without header, footer and notes 1 and 2.txt'
with open(textFilePath, 'r', encoding='utf-8-sig') as f:
  waml1 = f.readlines()

ml = numberedListReferenceML(lines=waml1)
try:
  ml.parse()
except MatchingError as e:
  print(e)

outPath = 'out.txt'
with open(outPath, 'w') as f:
  f.writelines(ml.get())
