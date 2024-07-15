#!/usr/bin/env python3

import enum
import readline

contextBeforeAmount = 3
contextAfterAmount = 3

contextBefore = contextBeforeAmount * [""]
contextAfter = contextAfterAmount * [""]
current = "No file loaded yet."

class Screen(enum.Enum):
  Choices = enum.auto()
  Custom = enum.auto()

def prefillCurrentLine():
  readline.insert_text(current)
  readline.redisplay()
  
 def prefillA():
  readline.insert_text("a")
  readline.redisplay()


# read work file and set up context
# TODO

# skip lines until we reach the first one that doesn't begin with a valid code followed by a single tab and no more whitespace
# TODO

# read collection of correct files and for each code contained within assign knownCodes[newCode] = codeOnNextLine
knownCodes = dict()
correctFiles = [] # paths
# TODO

state = Screen.Choices

while True:
  match state:
    case Screen.Choices:
      pass
      # strip any prefix of current line that could be a code (including whitespace interspersed with possible code parts)
      # if code of previous line is in knownCodes, iterate over the successors generating a possibility for each
      possibilites = 2 * ["line with code"]
      
      if(len(possibilities) == 1):
        readline.set_pre_input_hook(prefillA)
        
      for p in possibilites:
        print(p)
      
      userChoice = input("Enter a letter to choose or leave blank to edit line: ")

      # if it's a letter: modify work file, set up context for next line and erase appropriate amount of lines on the screen
      
      # if it's blank: erase single line on the screen and set state to Custom
      
    case Screen.Custom:
      readline.set_pre_input_hook(prefillCurrentLine)
      current = input("Enter line: ")
      # erase lines on screen, set up context for next line, set state to Choices