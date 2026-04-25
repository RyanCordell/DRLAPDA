import os.path
import customtkinter
from tkinter import filedialog as fd

from arsenal import Arsenal
from sbarinfo import Sbarinfo

print('Starting combiner')

customtkinter.set_appearance_mode('dark')
customtkinter.set_default_color_theme('dark-blue')


class Combiner(customtkinter.CTk):
    def clearResults(self):
        self.textbox.configure(state='normal')
        self.textbox.delete('0.0', 'end')
        self.textbox.configure(state='disabled')

    def printLine(self, msg):
        self.textbox.configure(state='normal')
        self.textbox.insert('0.0', msg)
        if self.debug:
            print(msg)
        self.textbox.configure(state='disabled')

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.currentPath: str = os.path.dirname(os.path.abspath(__file__))
        self.debug: bool = False

        self.arsenal = Arsenal(
            on_log=self.printLine,
            on_clear=self.clearResults,
            pick_input_dir=lambda: fd.askdirectory(
                title="Open folder of JSON files",
                initialdir=self.currentPath
            ),
            pick_output_file=lambda name: fd.asksaveasfile(
                title="Save file as..",
                initialfile=name,
                initialdir=self.currentPath,
                filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
            )
        )

        self.sbarinfo = Sbarinfo(
            on_log=self.printLine,
            on_clear=self.clearResults,
            pick_input_file=lambda: fd.askopenfilename(
                title="Open a file",
                initialdir=self.currentPath,
                filetypes=(
                    ("Skeleton files", "*.skeleton"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*"),
                ),
                defaultextension=".skeleton",
            ),
            pick_output_file=lambda: fd.asksaveasfile(
                title="Save file as..",
                initialdir=self.currentPath,
                filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
            )
        )

        # Window
        self.title('DoomRL Arsenal Toolbox')
        self.geometry("1280x800+12+12")

        # Grid (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        # Left sidebar — SBARINFO
        self.left_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.left_frame.grid(row=0, column=0, rowspan=6, sticky='nsew')
        self.left_frame.grid_rowconfigure(10, weight=1)

        self.frame_label = customtkinter.CTkLabel(self.left_frame, text='SBARINFO Merger', font=('CTkFont', 20))
        self.frame_label.grid(row=0, column=0, padx=20, pady=(10, 20))

        self.openInput = customtkinter.CTkButton(
            self.left_frame, text='Open input file',
            command=self._sbarinfo_open_input
        )
        self.openInput.grid(row=2, column=0, padx=40, pady=0)

        self.simulateSbarinfoCompile = customtkinter.CTkButton(
            self.left_frame, text='Build (no output)',
            command=self.sbarinfo.do_fake_compile
        )
        self.simulateSbarinfoCompile.grid(row=5, column=0, padx=40, pady=20)

        self.compileSbarinfo = customtkinter.CTkButton(
            self.left_frame, text='Compile',
            command=self.sbarinfo.perform_compile
        )
        self.compileSbarinfo.grid(row=6, column=0, padx=40, pady=20)
        self.compileSbarinfo.configure(state='disabled')

        self.clearOutput = customtkinter.CTkButton(
            self.left_frame, text='Clear output window',
            command=self.arsenal.clearWindow
        )
        self.clearOutput.grid(row=7, column=0, padx=40, pady=20)

        # Middle — progress log
        self.textboxLabel = customtkinter.CTkLabel(self, text='Progress report', font=('CTkFont', 20))
        self.textboxLabel.grid(row=0, column=1, padx=0, pady=0, sticky='ew')
        self.textbox = customtkinter.CTkTextbox(self, width=250, height=900, font=('Arial', 16))
        self.textbox.grid(row=1, column=1, padx=20, pady=0, sticky='nsew')
        self.textbox.configure(state='disabled')

        # Right sidebar — Arsenal
        self.right_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.right_frame.grid(row=0, column=2, rowspan=6, sticky='nsew')
        self.right_frame.grid_rowconfigure(10, weight=1)

        self.frame_label_right = customtkinter.CTkLabel(self.right_frame, text='Arsenal Builder', font=('CTkFont', 20))
        self.frame_label_right.grid(row=0, column=2, padx=20, pady=(10, 40))

        self.openJSON = customtkinter.CTkButton(
            self.right_frame, text='Open JSON folder',
            command=self.arsenal.do_input
        )
        self.openJSON.grid(row=2, column=2, padx=40, pady=(0, 20))

        self.separatorTokenLabel = customtkinter.CTkLabel(self.right_frame, text='Separator token')
        self.separatorTokenLabel.grid(row=4, column=2, padx=0, pady=0, sticky='ew')
        self.separatorTokenFrame = customtkinter.CTkTextbox(self.right_frame, height=30, activate_scrollbars=False)
        self.separatorTokenFrame.grid(row=5, column=2, padx=40, pady=0)
        self.separatorTokenFrame.insert("0.0", self.arsenal.separator_token)
        self.separatorTokenFrame.bind(sequence='<KeyRelease>', command=self._update_separator_token)

        self.simulateCompile = customtkinter.CTkButton(
            self.right_frame, text='Build (no output)',
            command=lambda: self.arsenal.do_compile(do_output=False)
        )
        self.simulateCompile.grid(row=6, column=2, padx=40, pady=20)

        self.compileArsenal = customtkinter.CTkButton(
            self.right_frame, text='Compile',
            command=lambda: self.arsenal.do_compile(do_output=True)
        )
        self.compileArsenal.grid(row=7, column=2, padx=40, pady=20)

    def _sbarinfo_open_input(self):
        self.sbarinfo.process_input()
        self.compileSbarinfo.configure(
            state='normal' if self.sbarinfo.input_file else 'disabled'
        )

    def _update_separator_token(self, event=None):
        self.arsenal.separator_token = self.separatorTokenFrame.get("0.0", "end").strip()


if __name__ == '__main__':
    app = Combiner()
    app.mainloop()
