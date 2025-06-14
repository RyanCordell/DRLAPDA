import sys
import os.path

from tkinter import filedialog as fd
from datetime import datetime

def currentTime() -> datetime:
  return datetime.now().strftime("%H:%M:%S")

class Sbarinfo:
  variables_in_memory: list[str]
  data: any
  
  def empty_memory_variables(self):
    self.variables_in_memory = list()
    
  def doPrint(self, line):
    if (hasattr(self, 'printline')): 
      self.printLine(line)
    else:
      print(line)

  def directive_MERGE(self, index: int, line: str):
    if (self.inputFile != ''): 
      # print("line: %s" % line)
      if ("#MERGE" in line):
        self.variables_in_memory = list()
        fileToLoad: str = line.split('"')[1]
        loadFilePath: str = os.path.normpath(os.path.join(os.path.dirname(self.inputFile), '', fileToLoad))
        fileExists: bool = os.path.exists(loadFilePath)

        if (fileExists):
          self.doPrint("[%s] MERGE @ %s and %s found. Executing\n" % (currentTime(), index, loadFilePath))
          
          with open(loadFilePath, mode='r', encoding='utf-8') as mergeBuffer:
            self.data[index] = mergeBuffer.read() + '\n'
            self.data[index] = Sbarinfo.variable_handler(self, self.data[index], index)
            

        else:
          self.doPrint("[%s] %s not found. Skipping directive\n" % (currentTime(), loadFilePath))
          self.data[index] = ''
  
  def variable_handler(self, data: str | list[str], index: int):
    variable_line: list[str] = list()
    dataLines: list[str] = data.splitlines(keepends=True)
    
    for i, line in enumerate(dataLines):
      if ("$" in line):
        if (line.lstrip().startswith("$")):
          temp: list[str] = line.split('=') # This should yield $VARIABLE_NAME, AMOUNT;
          
          variable_line.append(temp[0].strip())
          variable_line.append(temp[1].strip())
          
          self.doPrint("[%s] Variable %s declared \n" % (currentTime(), variable_line[0]))
          
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
                
          self.doPrint("[%s] Line changed: %s\n" % (currentTime(), line))
    
    return ''.join(dataLines)

  def doCompile(self):
    if (not sys.argv[1:]):
      Sbarinfo.doOutput(self)

    if (self.outputFile): 
      with open(self.inputFile, mode='r', encoding='utf-8') as fullscreenSbarinfo:
        self.data = fullscreenSbarinfo.readlines()

      for index, line in enumerate(self.data):
        Sbarinfo.directive_MERGE(self, index, line)
        
      filePath: str = ''
      
      if (hasattr(self.outputFile, 'name')):
        filePath = self.outputFile.name
      else:
        filePath = self.outputFile
      
      if (len(filePath) > 0):
        with open(filePath, mode='w', encoding='utf-8') as file:
          file.writelines(''.join(self.data))
          self.data = ''
          
          self.doPrint("[%s] Combiner finished successfully! Resulting file size is: %s bytes\n" % (currentTime(), os.path.getsize(self.outputFile)))
      
      # if (hasattr(self.outputFile, 'name')):
      #   with open(self.outputFile.name, mode='w', encoding='utf-8') as file:
      #     file.writelines(self.data)
      #     self.data = ''
          
      #     self.doPrint("[%s] Combiner finished successfully! Resulting file size is: %s bytes\n" % (currentTime(), os.path.getsize(self.outputFile.name)))
      # else:
      #   with open(self.outputFile, mode='w', encoding='utf-8') as file:
      #     file.writelines(''.join(self.data))
      #     self.data = ''
          
      #     self.doPrint("[%s] Combiner finished successfully! Resulting file size is: %s bytes\n" % (currentTime(), os.path.getsize(self.outputFile)))

      Sbarinfo.empty_memory_variables(self)
      
    if (sys.argv[1:]):
      Sbarinfo.doOutput(self)

  def doQuasiCompile(self):
    if (self.inputFile): 
      with open(self.inputFile, mode='r', encoding='utf-8') as fullscreenSbarinfo:
        self.data = fullscreenSbarinfo.readlines()

      for index, line in enumerate(self.data):
        Sbarinfo.directive_MERGE(self, index, line)
      
      self.doPrint("[%s] Data: %s" % (currentTime(), self.data))
        
    
  def main(self):
    self.doInput()
    
    if (sys.argv[2]):
        self.outputFile = sys.argv[2]
        
    self.doCompile()

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
        self.printLine('[%s] No file chosen\n' % currentTime())
        self.compileSbarinfo.configure(state='disabled')
        return 0
    else:
      with open(sys.argv[2], mode='w', encoding='utf-8') as file:
        file.write(''.join(self.data))

  def doInput(self):
    if (hasattr(self, 'currentPath') and self.currentPath):
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

      self.clearResults()
      if (self.inputFile):
        self.compileSbarinfo.configure(state='normal')
        self.printLine('[%s] File selected: %s\n' % (currentTime(), os.path.normpath(self.inputFile)))
      else:
        self.printLine('[%s] No file selected\n' % currentTime())
    else:
      if (sys.argv[1]):
        self.inputFile = sys.argv[1]
        # with open(sys.argv[1], mode='r', encoding='utf-8') as file:
        #   self.inputFile = file
        #   self.data = file.read(file)

if (__name__ == '__main__'): 
  # print("sys args: %s" % sys.argv[1:])
  self = Sbarinfo()
  self.main()