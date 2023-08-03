import os.path
import sys
import customtkinter
from functools import partial

print('Starting combiner')

customtkinter.set_appearance_mode('dark')
customtkinter.set_default_color_theme('dark-blue')

class Combiner(customtkinter.CTk):
  inputFile = ''
  outputFile = ''
  currentPath = os.path.dirname(os.path.abspath(__file__))
  data = ''
  debug = 0

  def clearResults(self):
    self.textbox.delete('0.0', 'end')
  def printLine(self, msg):
    self.textbox.configure(state='normal')
    self.textbox.insert('0.0', msg)
    if (self.debug):
      print(msg)
    self.textbox.configure(state='disabled')

  def __init__(self):
    super().__init__()

    # Window
    self.title('DoomRL Arsenal Toolbox')
    self.minsize(1280, 480)

    # Grid (4x4)
    self.grid_columnconfigure(     1, weight=1)
    self.grid_columnconfigure( (2,3), weight=0)
    self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

    from sbarinfo import Sbarinfo
    from arsenal import Arsenal

    # Left sidebar
    self.left_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
    self.left_frame.grid(row=0, column=0, rowspan=5, sticky='nsew')
    self.left_frame.grid_rowconfigure(4, weight=1)

    self.frame_label = customtkinter.CTkLabel(self.left_frame, text='SBARINFO Merger')
    self.frame_label.grid(row=0, column=0, padx=20, pady=(10, 20))

    # self.inputLabel = customtkinter.CTkLabel(self.sidebar_frame, text='Input file')
    # self.inputLabel.grid(row=1, column=0, padx=20, pady=(20, 10))
    self.openInput = customtkinter.CTkButton(self.left_frame, text='Open input file', command=partial(Sbarinfo.sbarinfo_doInput, self))
    self.openInput.grid(row=2, column=0, padx=40, pady=0)

    self.compileSbarinfo = customtkinter.CTkButton(self.left_frame, text='Compile', command=partial(Sbarinfo.sbarinfo_doCompile, self))
    self.compileSbarinfo.grid(row=5, column=0, padx=40, pady=20)
    self.compileSbarinfo.configure(state='disabled')

    # Middle
    self.textboxLabel = customtkinter.CTkLabel(self, text='Progress report')
    self.textboxLabel.grid(row=0, column=1, padx=0, pady=0, sticky='nsew')
    self.textbox = customtkinter.CTkTextbox(self, width=250)
    self.textbox.grid(row=1, column=1, padx=20, pady=0, sticky='nsew')
    self.textbox.configure(state='disabled')

    # Right
    self.right_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
    self.right_frame.grid(row=0, column=2, rowspan=5, sticky='nsew')
    self.right_frame.grid_rowconfigure(4, weight=1)

    self.frame_label = customtkinter.CTkLabel(self.right_frame, text='Arsenal Builder')
    self.frame_label.grid(row=0, column=2, padx=20, pady=(10, 20))

    self.openJSON = customtkinter.CTkButton(self.right_frame, text='Open JSON file', command=partial(Arsenal.arsenal_doInput, self))
    self.openJSON.grid(row=2, column=2, padx=40, pady=0)

    self.openFillers = customtkinter.CTkButton(self.right_frame, text='Open Filler files', command=partial(Arsenal.arsenal_doFillerInputs, self))
    self.openFillers.grid(row=3, column=2, padx=40, pady=(10,0))

    self.compileArsenal = customtkinter.CTkButton(self.right_frame, text='Compile', command=partial(Arsenal.arsenal_doCompile, self))
    self.compileArsenal.grid(row=5, column=2, padx=40, pady=20)

if __name__ == '__main__':
  app = Combiner()
  app.mainloop()

