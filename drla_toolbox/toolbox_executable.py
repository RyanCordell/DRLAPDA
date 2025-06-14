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
  arsData = {}
  data = ''
  debug = 0
  loadedJson = dict('')
  separatorToken = ':'

  def clearResults(self):
    self.textbox.configure(state='normal')
    self.textbox.delete('0.0', 'end')
    self.textbox.configure(state='disabled')
  def printLine(self, msg):
    self.textbox.configure(state='normal')
    self.textbox.insert('0.0', msg)
    if (self.debug):
      print(msg)
    self.textbox.configure(state='disabled')

  def stuff(event):
    print(event)

  def changeSeparatorToken(token):
    separatorToken = token

  def __init__(self, *args, **kw):
    super().__init__(*args, **kw)

    # Window
    self.title('DoomRL Arsenal Toolbox')
    # self.minsize(1280, 640)
    self.geometry("1280x800+12+12")

    # Grid (4x4)
    self.grid_columnconfigure(     1, weight=1)
    self.grid_columnconfigure( (2,3), weight=0)
    self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

    from sbarinfo import Sbarinfo
    from arsenal import Arsenal

    # Left sidebar
    self.left_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
    self.left_frame.grid(row=0, column=0, rowspan=6, sticky='nsew')
    self.left_frame.grid_rowconfigure(10, weight=1)

    self.frame_label = customtkinter.CTkLabel(self.left_frame, text='SBARINFO Merger', font=('CTkFont', 20))
    self.frame_label.grid(row=0, column=0, padx=20, pady=(10, 20))

    self.openInput = customtkinter.CTkButton(self.left_frame, text='Open input file', command=partial(Sbarinfo.sbarinfo_doInput, self))
    self.openInput.grid(row=2, column=0, padx=40, pady=0)


    self.simulateSbarinfoCompile = customtkinter.CTkButton(self.left_frame, text='Build (no output)', command=partial(Sbarinfo.sbarinfo_doQuasiCompile, self))
    self.simulateSbarinfoCompile.grid(row=5, column=0, padx=40, pady=20)

    self.compileSbarinfo = customtkinter.CTkButton(self.left_frame, text='Compile', command=partial(Sbarinfo.sbarinfo_doCompile, self))
    self.compileSbarinfo.grid(row=6, column=0, padx=40, pady=20)
    self.compileSbarinfo.configure(state='disabled')
    self.clearOutput = customtkinter.CTkButton(self.left_frame, text='Clear output window', command=partial(Arsenal.arsenal_clearWindow, self))
    self.clearOutput.grid(row=7, column=0, padx=40, pady=20)

    # Middle
    self.textboxLabel = customtkinter.CTkLabel(self, text='Progress report', font=('CTkFont', 20))
    self.textboxLabel.grid(row=0, column=1, padx=0, pady=0, sticky='ew')
    self.textbox = customtkinter.CTkTextbox(self, width=250, height=900, font=('Arial', 16))
    self.textbox.grid(row=1, column=1, padx=20, pady=0, sticky='nsew')
    self.textbox.configure(state='disabled')

    # Right
    self.right_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
    self.right_frame.grid(row=0, column=2, rowspan=6, sticky='nsew')
    self.right_frame.grid_rowconfigure(10, weight=1)

    self.frame_label = customtkinter.CTkLabel(self.right_frame, text='Arsenal Builder', font=('CTkFont', 20))
    self.frame_label.grid(row=0, column=2, padx=20, pady=(10, 40))

    self.openJSON = customtkinter.CTkButton(self.right_frame, text='Open JSON files', command=partial(Arsenal.arsenal_doInput, self))
    self.openJSON.grid(row=2, column=2, padx=40, pady=(0, 20))

    # self.files_label = customtkinter.CTkLabel(self.right_frame, text='Selected files:')
    # self.files_label.grid(row=3, column=2, padx=20, pady=(10, 20))

    # self.selected_files = customtkinter.CTkLabel(self.right_frame, text='...')
    # self.selected_files.grid(row=4, column=2, padx=20, pady=(0, 20))

    # self.openFillers = customtkinter.CTkButton(self.right_frame, text='Open Filler files', command=partial(Arsenal.arsenal_doFillerInputs, self))
    # self.openFillers.grid(row=3, column=2, padx=40, pady=(10,0))

    self.separatorTokenLabel = customtkinter.CTkLabel(self.right_frame, text='Separator token')
    self.separatorTokenLabel.grid(row=4, column=2, padx=0, pady=0, sticky='ew')
    self.separatorTokenFrame = customtkinter.CTkTextbox(self.right_frame, height=30, activate_scrollbars=False)
    self.separatorTokenFrame.grid(row=5, column=2, padx=40, pady=0)
    self.separatorTokenFrame.insert("0.0", self.separatorToken)
    self.separatorTokenFrame.bind(sequence=None, command=self.changeSeparatorToken)

    self.simulateCompile = customtkinter.CTkButton(self.right_frame, text='Build (no output)', command=partial(Arsenal.arsenal_doQuasiCompile, self))
    self.simulateCompile.grid(row=6, column=2, padx=40, pady=20)

    self.compileArsenal = customtkinter.CTkButton(self.right_frame, text='Compile', command=partial(Arsenal.arsenal_doCompile, self))
    self.compileArsenal.grid(row=7, column=2, padx=40, pady=20)

if __name__ == '__main__':
  app = Combiner()
  app.mainloop()

