import os.path
from tkinter import filedialog as fd
from datetime import datetime

def currentTime() -> datetime:
  return datetime.now().strftime("%H:%M:%S")

class Sbarinfo:
  variables_in_memory: list[str]
  
  def empty_memory_variables(self):
    self.variables_in_memory = list()

  def directive_MERGE(self, index: int, line: str):
    if (self.inputFile != ''): 
      if ("#MERGE" in line):
        self.variables_in_memory = list()
        fileToLoad: str = line.split('"')[1]
        loadFilePath: str = os.path.normpath(os.path.join(os.path.dirname(self.inputFile), '', fileToLoad))
        fileExists: bool = os.path.exists(loadFilePath)

        if (fileExists):
          self.printLine("[%s] MERGE directive and %s found. Executing\n" % (currentTime(), loadFilePath))
          
          with open(loadFilePath, mode='r', encoding='utf-8') as mergeBuffer:
            self.data[index] = mergeBuffer.read() + '\n'
            Sbarinfo.variable_handler(self, self.data[index])

        else:
          self.printLine("[%s] %s not found. Skipping directive\n" % (currentTime(), loadFilePath))
          self.data[index] = ''
  
  def variable_handler(self, line: str):
    variable_line: list[str] = list()

    if (self.inputFile != ''): 
      if ("$" in line):
        if (line.startswith("$")):
          self.printLine("[%s] Variable declared \n" % (currentTime()))
          temp: list[str] = line.split('=') # This should yield $VARIABLE_NAME, AMOUNT;
          variable_line.append(temp[0].strip())
          variable_line.append(temp[1].strip())
          
          if (len(variable_line) > 0):
            variable_line[0].replace('$', '')
            variable_line[1].replace(';', '')
            

          self.variables_in_memory.append(variable_line)
          print("variables_in_memory:", self.variables_in_memory)
          variable_line = list()
        else:
          if (len(self.variables_in_memory) > 0):
            for index, variable in enumerate(self.variables_in_memory):
              if (f'${variable}' in line):
                line.replace(f'${variable}', variable_line)

  def doCompile(self):
    Sbarinfo.doOutput(self)

    if (self.outputFile): 
      with open(self.inputFile, mode='r', encoding='utf-8') as fullscreenSbarinfo:
        self.data = fullscreenSbarinfo.readlines()

      for index, line in enumerate(self.data):
        Sbarinfo.directive_MERGE(self, index, line)
      
      with open(self.outputFile.name, mode='w', encoding='utf-8') as file:
        file.writelines(self.data)
        self.data = ''
        
        self.printLine("[%s] Combiner finished successfully! Resulting file size is: %s bytes\n" % (currentTime(), os.path.getsize(self.outputFile.name)))

      Sbarinfo.empty_memory_variables(self)

  def doQuasiCompile(self):
    if (self.inputFile): 
      with open(self.inputFile, mode='r', encoding='utf-8') as fullscreenSbarinfo:
        self.data = fullscreenSbarinfo.readlines()

      for index, line in enumerate(self.data):
        Sbarinfo.directive_MERGE(self, index, line)
      
      self.printLine("[%s] Data: %s" % (currentTime(), self.data))
        

  def doOutput(self):
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

  def doInput(self):
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
