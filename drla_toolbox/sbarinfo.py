"""
sbarinfo

This module provides functions for the sbarinfo toolchain.

The main class is `Sbarinfo`, which contains methods for processing 'skeleton'
Sbarinfo data, such as combining multiple files and variable replacement, before
outputting it into the expected format that ZDoom supports.

The `current_time` function returns a string representing the current time in
the format "HH:MM:SS", used only for logging purposes.

The constants `INPUT_FOLDER_ARG` and `OUTPUT_FOLDER_ARG` are used to
indicate the indices of the input and output folder arguments.

"""
import sys
import os.path

from tkinter import filedialog as fd
from datetime import datetime

from typing import Any, IO


def current_time() -> datetime:
    """
    Returns the current time as a string in the format "HH:MM:SS"
    """

    return datetime.now().strftime("%H:%M:%S")


INPUT_FOLDER_ARG: int = 1
OUTPUT_FOLDER_ARG: int = 2


class Sbarinfo:
    """
    The primary class.

    The main points of the class have already been outlined above. The nitty gritty
    is as follows:

    Available methods include:
        - `is_invoked_by_combiner`: Returns True if the class is invoked by the
          Combiner, and False otherwise.
        - `empty_memory_variables`: Empties the list of variables in the class' 
          'memory'.
        - `attempt_print`: Prints a line to the console if the class is not
          invoked by the Combiner, otherwise it calls the `printLine` method.
        - `main`: Calls the `process_input` method and then the `perform_compile`
          method, only called when invoked via terminal.
        - `process_merge`: Processes any "#MERGE" directives found in the input file.

    The class also contains two class variables:
        - `variables_in_memory`: A list of variables in memory.
        - `data`: The data that is being processed.

    """
    variables_in_memory: list[str | list[str]]
    data: Any

    def __init__(self):
        self.output_file: IO | None | str = None
        self.input_file: str = ""

    def is_invoked_by_combiner(self) -> bool:
        return "Combiner" in self.__class__.__name__

    def empty_memory_variables(self) -> None:
        self.variables_in_memory = []

    def attempt_print(self, line: str) -> None:
        if Sbarinfo.is_invoked_by_combiner(self) and hasattr(self, "printline"):
            self.printLine(line)
        else:
            print(line)

    def main(self):
        self.process_input()

        if sys.argv[OUTPUT_FOLDER_ARG]:
            self.output_file = sys.argv[OUTPUT_FOLDER_ARG]

        self.perform_compile()

    def process_merge(self, index: int, line: str) -> None:
        if self.input_file != "":
            # print("line: %s" % line)
            if "#MERGE" in line:
                Sbarinfo.variables_in_memory = []
                file_to_load: str = line.split('"')[1]
                load_file_path: str = os.path.normpath(
                    os.path.join(os.path.dirname(self.input_file), "", file_to_load)
                )
                file_exists: bool = os.path.exists(load_file_path)

                if file_exists:
                    Sbarinfo.attempt_print(
                        self,
                        f'{current_time()} MERGE @ {index} and {load_file_path} found. Executing\n'
                    )

                    with open(load_file_path, mode="r", encoding="utf-8") as merge_buffer:
                        Sbarinfo.data[index] = merge_buffer.read() + "\n"
                        Sbarinfo.data[index] = Sbarinfo.variable_handler(
                            self, Sbarinfo.data[index]
                        )

                else:
                    Sbarinfo.attempt_print(
                        self,
                        f'{current_time()} {load_file_path} not found. Skipping directive\n',
                    )
                    Sbarinfo.data[index] = ""

    def variable_handler(self, data: str | list[str]) -> str:
        variable_line: list[str] = []

        data_lines: list[str] = data.splitlines(keepends=True)

        for i, line in enumerate(data_lines):
            if "$" in line:
                if line.lstrip().startswith("$"):
                    temp: list[str] = line.split(
                        "="
                    )  # This should yield $VARIABLE_NAME, AMOUNT;

                    variable_line.append(temp[0].strip())
                    variable_line.append(temp[1].strip())

                    Sbarinfo.attempt_print(
                        self,
                        f'{current_time()} Variable {variable_line[0]} declared \n'
                    )

                    if len(variable_line) > 0:
                        variable_line[0] = variable_line[0].replace("$", "")
                        variable_line[1] = variable_line[1].replace(";", "")

                    self.variables_in_memory.append(variable_line)

                    variable_line = []
                    data_lines[i] = ""
                else:
                    if len(self.variables_in_memory) > 0:
                        for variable in self.variables_in_memory:
                            if f'${variable[0]}' in line:
                                line = line.replace(f'${variable[0]}', variable[1])
                                data_lines[i] = line

                    Sbarinfo.attempt_print(
                        self, f'{current_time()} Line changed: {line}\n'
                    )

        return "".join(data_lines)

    def perform_compile(self) -> None:
        if not sys.argv[1:]:
            Sbarinfo.process_output(self)

        if self.output_file:
            with open(self.input_file, mode="r", encoding="utf-8") as fullscreen_sbarinfo:
                Sbarinfo.data = fullscreen_sbarinfo.readlines()

            for index, line in enumerate(Sbarinfo.data):
                Sbarinfo.process_merge(self, index, line)

            file_path: str = ""

            if hasattr(self.output_file, "name"):
                file_path = self.output_file.name
            else:
                file_path = self.output_file

            if len(file_path) > 0:
                with open(file_path, mode="w+", encoding="utf-8") as file:
                    file.writelines("".join(Sbarinfo.data))

                Sbarinfo.attempt_print(
                    self,
                    f'''{current_time()} Finished {file_path} [{os.path.getsize(os.path.normpath(file_path))} bytes]\n''',
                )

            Sbarinfo.empty_memory_variables(self)

        if sys.argv[1:]:
            Sbarinfo.process_output(self)
        
        Sbarinfo.data = ""

    def do_fake_compile(self) -> None:
        if self.input_file:
            with open(self.input_file, mode="r", encoding="utf-8") as fullscreen_sbarinfo:
                Sbarinfo.data = fullscreen_sbarinfo.readlines()

            for index, line in enumerate(Sbarinfo.data):
                Sbarinfo.process_merge(self, index, line)

            Sbarinfo.attempt_print(
                self, f'{current_time()} Data: {Sbarinfo.data}'
            )

    def process_output(self) -> None:
        # We have to ignore some of these types as 'self' comes from the Combiner class
        if self.is_invoked_by_combiner() \
            and hasattr(self, "currentPath") \
            and self.currentPath:
            self.output_file = fd.asksaveasfile(
                title="Save file as..",
                initialdir=self.currentPath,  # type: ignore
                filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
            )
            if not self.output_file:
                self.clearResults()
                Sbarinfo.attempt_print(self, f'{current_time()} No file chosen\n')
                self.compileSbarinfo.configure(state="disabled")
        else:
            with open(sys.argv[OUTPUT_FOLDER_ARG], mode="w", encoding="utf-8") as file:
                file.write("".join(Sbarinfo.data))

    def process_input(self) -> None:
        if (
            Sbarinfo.is_invoked_by_combiner(self)
            and hasattr(self, "currentPath")
            and self.currentPath
        ):
            self.input_file = fd.askopenfilename(
                title="Open a file",
                initialdir=self.currentPath,
                filetypes=(
                    ("Text files", "*.skeleton"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*"),
                ),
                defaultextension=".skeleton",
            )

            if Sbarinfo.is_invoked_by_combiner(self):
                self.clearResults()
            if self.input_file:
                if Sbarinfo.is_invoked_by_combiner(self):
                    self.compileSbarinfo.configure(state="normal")
                Sbarinfo.attempt_print(
                    self,
                    f'{current_time()} File selected: {os.path.normpath(self.input_file)}\n'
                )
            else:
                Sbarinfo.attempt_print(self, f'{current_time()} No file selected\n')
        else:
            if sys.argv[INPUT_FOLDER_ARG]:
                self.input_file = sys.argv[INPUT_FOLDER_ARG]


if __name__ == "__main__":
    # print("sys args: %s" % sys.argv[1:])
    if len(sys.argv) < 2:
        print("Usage: python sbarinfo.py input_file output_file")
    else:
        self = Sbarinfo()
        self.main()
