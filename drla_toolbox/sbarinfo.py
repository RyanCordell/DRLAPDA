import os.path
from tkinter import filedialog as fd
from datetime import datetime

#TODO: Introduce 'variables'

class Sbarinfo:
  def sbarinfo_directive_MERGE(self, index: any, line: any):
    if self.inputFile != '': 
      if "#MERGE" in line:
        fileToLoad = line.split('"')[1]
        loadFilePath = os.path.normpath(os.path.join(os.path.dirname(self.inputFile), '', fileToLoad))
        fileExists = os.path.exists(loadFilePath)

        if fileExists:
          self.printLine("[%s] MERGE directive and %s found. Executing\n" % (datetime.now().strftime("%H:%M:%S"), loadFilePath))
          with open(loadFilePath, mode='r', encoding='utf-8') as mergeBuffer:
            self.data[index] = mergeBuffer.read() + '\n'
            Sbarinfo.sbarinfo_variable_handler(self, self.data[index])
            #Eventually include parsing of variables here

        else:
          self.printLine("[%s] %s not found. Skipping directive\n" % (datetime.now().strftime("%H:%M:%S"), loadFilePath))
          self.data[index] = ''
  
  def sbarinfo_variable_handler(self, line: any):
    if self.inputFile != '': 
      if "$VAR" in line:
        self.printLine("[%s] Variables replaced \n" % (datetime.now().strftime("%H:%M:%S")))
  

  def sbarinfo_doCompile(self):
    Sbarinfo.sbarinfo_doOutput(self)

    if (self.outputFile): 
      with open(self.inputFile, mode='r', encoding='utf-8') as fullscreenSbarinfo:
        self.data = fullscreenSbarinfo.readlines()

      for index, line in enumerate(self.data):
        Sbarinfo.sbarinfo_directive_MERGE(self, index, line)
      
      with open(self.outputFile.name, mode='w', encoding='utf-8') as file:
        file.writelines(self.data)
        
        self.printLine("[%s] Combiner finished successfully! Resulting file size is: %s bytes\n" % (datetime.now().strftime("%H:%M:%S"), os.path.getsize(self.outputFile.name)))

  def sbarinfo_doQuasiCompile(self):
    if (self.inputFile): 
      with open(self.inputFile, mode='r', encoding='utf-8') as fullscreenSbarinfo:
        self.data = fullscreenSbarinfo.readlines()

      for index, line in enumerate(self.data):
        Sbarinfo.sbarinfo_directive_MERGE(self, index, line)
      
      self.printLine("[%s] Data: %s" % (datetime.now().strftime("%H:%M:%S"), self.data))
        

  def sbarinfo_doOutput(self):
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
      self.printLine('[%s] No file chosen\n' % datetime.now().strftime("%H:%M:%S"))
      self.compileSbarinfo.configure(state='disabled')
      return 0

  def sbarinfo_doInput(self):
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
      self.printLine('[%s] File selected: %s\n' % (datetime.now().strftime("%H:%M:%S"), os.path.normpath(self.inputFile)))
    else:
      self.printLine('[%s] No file selected\n' % datetime.now().strftime("%H:%M:%S"))
