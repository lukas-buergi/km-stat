# work on WA-ML list in txt format exported from openoffice to structure
# it so that in the end it can go into the database
import re
from pprint import pprint
class indentedStructure():
  """ Aids in restoring structure to lines of text. """

  firstLevel = re.compile('^ML').search
  letterLevel = re.compile('^([a-z])\.').search
  digitLevel = re.compile('^([0-9]+)\.').search
  note = re.compile('^(Technical )?Note').search
  nb = re.compile('^N\.B\.').search
  referenceString = 'ML[0-9]+\.\s*([a-z]\.\s*[0-9]+\.\s*)*([a-z]\.)?'
  reference = re.compile(referenceString).search # find strings of the form of a wa-ml code
  beginsWithReference = re.compile('^\s*' + referenceString).search
  endsWithColon = re.compile(':$').search

  def __init__(self):    
    self.level = 0 # level of the last added line
    self.levels = [] # the last number/letter in each level
    self.openNote = False # if last line was a note with : at the end
    self.openNoteLastLetter = None
    self.resultLines = []


  
  def follows(self, a, b):
    """Returns if b follows a in lists with either single-char or numeric numbering. """
    if("" in [a, b]):
      raise(ValueError("a,b=" + a + "," + b))
    if(None in [a, b]):
      return(False)
    try:
      return(ord(b)==ord(a)+1)
    except TypeError:
      return(b == int(a) + 1)

  def closeNote(self, line):
    if(self.openNote):
      if(self.openNoteLastLetter==chr(ord("a")-1)):
        print("Warning: No subpoints for note that was supposed to have some at line: " + line)
      else:
        self.level -= 1
      self.level -= 1
      self.openNote = False

  def getParts(self, reference):
    parts = reference.split('.')
    strippedParts = []
    for part in parts:
      strippedParts.append(part.strip())
    return(strippedParts)

  def makeEnoughLevels(self):
    diff = self.level-len(self.levels)+1
    if(diff>0):
      self.levels += [None] * diff
    
  def findAndSetLevels(self, char, line):
    if("" == char):
      raise(ValueError)
    self.makeEnoughLevels()
    if(char in ["a", "1"]):
      self.level += 1
    elif(chr(ord(char)-1) in self.levels[0:self.level+1]):
        while(not self.follows(self.levels[self.level], char)):
          self.level -= 1
    else:
      print("Error: Preceding point not found for line: " + line)
      return()
    self.makeEnoughLevels()
    pprint(self.levels)
    self.levels[self.level] = char
  
  def addLine(self, line):
    if(self.note(line) or self.nb(line)):
      self.closeNote(line)
      
      if(self.reference(line)):
        # get sublevel of reference(line).group(0)
        # level = that level + 1
        self.level = len(self.getParts(self.reference(line).group(0)))
      else:
        # increment level
        self.level += 1
        print("Warning: Guessed indentation of line: " + line)
      self.addIndentedLine(line)
      
      if(self.endsWithColon(line)):
        self.openNote=True
        self.openNoteLastLetter=chr(ord("a")-1)
    elif(self.letterLevel(line)):
      letter = self.letterLevel(line).group(1)
      if(self.openNote and self.follows(self.openNoteLastLetter, letter)):
        #append to note
        if(letter == "a"):
          self.level += 1
        self.openNoteLastLetter = letter
        self.addIndentedLine(line)
      else:
        self.closeNote(line)
        self.findAndSetLevels(letter, line)
        self.addIndentedLine(line)
    elif(self.digitLevel(line)):
      self.closeNote(line)
      digit = self.digitLevel(line).group(1)
      self.findAndSetLevels(digit, line)
      self.addIndentedLine(line)
    elif(self.beginsWithReference(line)):
      self.closeNote(line)
      #set first levels to the parts of the reference, closing all deeper lists
      self.levels=self.getParts(self.beginsWithReference(line).group(0))
      print("beginsWithReference")
      pprint(self.levels)

  def addIndentedLine(self, line):
    """ Add a line with regular indentation as per level. """
    self.resultLines.append(" " * self.level + line)

  def addAll(self):
    textFilePath = '/home/t4b/km-stat/kriegsmaterialch/utils/wassenaar-lists/2018/15 - WA-LIST (18) 1 - ML - Without header, footer and notes 1 and 2.txt'
    with open(textFilePath, 'r') as f:
      waml1 = f.readlines()
  
    waml2 = []
    for line in waml1:
      stripped = line.strip()
      if(stripped != ""):
        waml2.append(stripped)
    for line in waml2:
      self.addLine(line)