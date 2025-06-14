import sys
import os.path

from tkinter import filedialog as fd
from datetime import datetime

from typing import Dict, List, Optional, Union, Any

def currentTime() -> datetime:
  return datetime.now().strftime("%H:%M:%S")

INPUT_FOLDER_ARG : int = 1
OUTPUT_FOLDER_ARG: int = 2

class Sbarinfo:
  variables_in_memory: list[str]
  data: Any
  
  def isInvokedByCombiner(self) -> bool:
    return 'Combiner' in self.__class__.__name__
  
  def empty_memory_variables(self) -> None:
    self.variables_in_memory = list()
    
  def attemptPrint(self, line: str) -> None:
    if (Sbarinfo.isInvokedByCombiner(self) and hasattr(self, 'printline')): self.printLine(line)
    else: print(line)

  def main(self):
    self.doInput()
    
    if (sys.argv[OUTPUT_FOLDER_ARG]):
        self.outputFile = sys.argv[OUTPUT_FOLDER_ARG]
        
    self.doCompile()

  def directive_MERGE(self, index: int, line: str):
    if (self.inputFile != ''): 
      # print("line: %s" % line)
      if ("#MERGE" in line):
        self.variables_in_memory = list()
        fileToLoad: str = line.split('"')[1]
        loadFilePath: str = os.path.normpath(os.path.join(os.path.dirname(self.inputFile), '', fileToLoad))
        fileExists: bool = os.path.exists(loadFilePath)

        if (fileExists):
          Sbarinfo.attemptPrint(self, "[%s] MERGE @ %s and %s found. Executing\n" % (currentTime(), index, loadFilePath))
          
          with open(loadFilePath, mode='r', encoding='utf-8') as mergeBuffer:
            Sbarinfo.data[index] = mergeBuffer.read() + '\n'
            Sbarinfo.data[index] = Sbarinfo.variable_handler(self, Sbarinfo.data[index], index)

        else:
          Sbarinfo.attemptPrint(self, "[%s] %s not found. Skipping directive\n" % (currentTime(), loadFilePath))
          Sbarinfo.data[index] = ''
  
  def variable_handler(self, data: str | list[str], index: int):
    variable_line: list[str] = list()
    dataLines: list[str] = data.splitlines(keepends=True)
    
    for i, line in enumerate(dataLines):
      if ("$" in line):
        if (line.lstrip().startswith("$")):
          temp: list[str] = line.split('=') # This should yield $VARIABLE_NAME, AMOUNT;
          
          variable_line.append(temp[0].strip())
          variable_line.append(temp[1].strip())
          
          Sbarinfo.attemptPrint(self, "[%s] Variable %s declared \n" % (currentTime(), variable_line[0]))
          
          if (len(variable_line) > 0):
            variable_line[0] = variable_line[0].replace('$', '')
            variable_line[1] = variable_line[1].replace(';', '')

          self.variables_in_memory.append(variable_line)
          
          variable_line = list()
          dataLines[i] = ''
        else:
          if (len(self.variables_in_memory) > 0):
            for index, variable in enumerate(self.variables_in_memory):
              if (f'${variable[0]}' in line):
                line = line.replace(f'${variable[0]}', variable[1])
                dataLines[i] = line
                
          Sbarinfo.attemptPrint(self, "[%s] Line changed: %s\n" % (currentTime(), line))
    
    return ''.join(dataLines)

  def doCompile(self):
    if (not sys.argv[1:]):
      Sbarinfo.doOutput(self)

    if (self.outputFile): 
      with open(self.inputFile, mode='r', encoding='utf-8') as fullscreenSbarinfo:
        Sbarinfo.data = fullscreenSbarinfo.readlines()

      for index, line in enumerate(Sbarinfo.data):
        Sbarinfo.directive_MERGE(self, index, line)
        
      filePath: str = ''
      
      if (hasattr(self.outputFile, 'name')):
        filePath = self.outputFile.name
      else:
        filePath = self.outputFile
      
      if (len(filePath) > 0):
        with open(filePath, mode='w', encoding='utf-8') as file:
          file.writelines(''.join(Sbarinfo.data))
          Sbarinfo.data = ''
          
          Sbarinfo.attemptPrint(self, "[%s] Combiner finished successfully! Resulting file size is: %s bytes\n" % (currentTime(), os.path.getsize(self.outputFile)))
      
      Sbarinfo.empty_memory_variables(self)
      
    if (sys.argv[1:]):
      Sbarinfo.doOutput(self)

  def doQuasiCompile(self):
    if (self.inputFile): 
      with open(self.inputFile, mode='r', encoding='utf-8') as fullscreenSbarinfo:
        Sbarinfo.data = fullscreenSbarinfo.readlines()

      for index, line in enumerate(Sbarinfo.data):
        Sbarinfo.directive_MERGE(self, index, line)
      
      Sbarinfo.attemptPrint(self, "[%s] Data: %s" % (currentTime(), Sbarinfo.data))

  def doOutput(self):
    if (hasattr(self, 'currentPath') and self.currentPath):
      self.outputFile = fd.asksaveasfile(
        title='Save file as..',
        initialdir=self.currentPath,
        filetypes=(
          ('Text files', '*.txt'),
          ('All files', '*.*')
        )
      )
      if (not self.outputFile): 
        self.clearResults()
        Sbarinfo.attemptPrint(self, '[%s] No file chosen\n' % currentTime())
        self.compileSbarinfo.configure(state='disabled')
        return 0
    else:
      with open(sys.argv[OUTPUT_FOLDER_ARG], mode='w', encoding='utf-8') as file:
        file.write(''.join(Sbarinfo.data))

  def doInput(self):
    if (Sbarinfo.isInvokedByCombiner(self) and hasattr(self, 'currentPath') and self.currentPath):
      self.inputFile = fd.askopenfilename(
        title='Open a file',
        initialdir=self.currentPath,
        filetypes=(
          ('Text files', '*.skeleton'),
          ('Text files', '*.txt'),
          ('All files', '*.*')
        ),
        defaultextension='.skeleton'
      )

      if (Sbarinfo.isInvokedByCombiner(self)): self.clearResults()
      if (self.inputFile):
        if (Sbarinfo.isInvokedByCombiner(self)): self.compileSbarinfo.configure(state='normal')
        Sbarinfo.attemptPrint(self, '[%s] File selected: %s\n' % (currentTime(), os.path.normpath(self.inputFile)))
      else:
        Sbarinfo.attemptPrint(self, '[%s] No file selected\n' % currentTime())
    else:
      if (sys.argv[INPUT_FOLDER_ARG]):
        self.inputFile = sys.argv[INPUT_FOLDER_ARG]
        # with open(sys.argv[INPUT_FOLDER_ARG], mode='r', encoding='utf-8') as file:
        #   self.inputFile = file
        #   Sbarinfo.data = file.read(file)

if (__name__ == '__main__'): 
  # print("sys args: %s" % sys.argv[1:])
  if (len(sys.argv) < 2):
    print("Usage: python sbarinfo.py input_file output_file")
  else:
    self = Sbarinfo()
    self.main()