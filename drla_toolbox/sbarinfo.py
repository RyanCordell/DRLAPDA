import sys
import os.path

from typing import Any, IO

from utils import current_time
from dataclasses import dataclass

INPUT_FOLDER_ARG: int = 1
OUTPUT_FOLDER_ARG: int = 2


@dataclass
class SbarinfoVariable:
    name: str
    value: str


class Sbarinfo:
    def __init__(self, on_log=print, on_clear=None, pick_input_file=None, pick_output_file=None):
        self.data: Any = None
        self.output_file: IO | None | str = None
        self.input_file: str = ""
        self.variables_in_memory: list[SbarinfoVariable] = []
        self.on_log = on_log
        self.on_clear = on_clear
        self.pick_input_file = pick_input_file
        self.pick_output_file = pick_output_file

    def empty_memory_variables(self) -> None:
        self.variables_in_memory = []

    def main(self):
        self.process_input()

        if sys.argv[OUTPUT_FOLDER_ARG]:
            self.output_file = sys.argv[OUTPUT_FOLDER_ARG]

        self.perform_compile()

    # I suppose there should be a ruleset def that checks active line and fires off the appropriate function..
    def process_merge(self, index: int, line: str) -> None:
        if self.input_file == "":
            return

        if "#MERGE" not in line:
            return

        self.variables_in_memory = []
        file_to_load: str = line.split('"')[1]
        load_file_path: str = os.path.normpath(
            os.path.join(os.path.dirname(self.input_file), "", file_to_load)
        )
        file_exists: bool = os.path.exists(load_file_path)

        if file_exists:
            self.on_log(f'{current_time()} MERGE @ {index} and {load_file_path} found. Executing\n')

            with open(load_file_path, mode="r", encoding="utf-8") as merge_buffer:
                self.data[index] = merge_buffer.read() + "\n"
                self.data[index] = self.variable_handler(self.data[index])
        else:
            self.on_log(f'{current_time()} {load_file_path} not found. Skipping directive\n')
            self.data[index] = ""

    def variable_handler(self, data: str | list[str]) -> str:
        data_lines: list[str] = data.splitlines(keepends=True)

        for i, line in enumerate(data_lines):
            if "$" not in line:
                continue

            if line.lstrip().startswith("$"):
                temp: list[str] = line.split("=")  # yields $VARIABLE_NAME, AMOUNT;

                var = SbarinfoVariable(
                    name=temp[0].strip().replace("$", ""),
                    value=temp[1].strip().replace(";", "")
                )

                self.on_log(f'{current_time()} Variable {var.name} declared \n')
                self.variables_in_memory.append(var)
                data_lines[i] = ""
            else:
                for var in self.variables_in_memory:
                    if f'${var.name}' in line:
                        line = line.replace(f'${var.name}', var.value)
                        data_lines[i] = line
                self.on_log(f'{current_time()} Line changed: {line}\n')

        return "".join(data_lines)

    def perform_compile(self) -> None:
        if not sys.argv[1:]:
            self.process_output()

        if self.output_file:
            with open(self.input_file, mode="r", encoding="utf-8") as fullscreen_sbarinfo:
                self.data = fullscreen_sbarinfo.readlines()

            for index, line in enumerate(self.data):
                self.process_merge(index, line)

            file_path: str = ""

            if hasattr(self.output_file, "name"):
                file_path = self.output_file.name
            else:
                file_path = self.output_file

            if len(file_path) > 0:
                with open(file_path, mode="w+", encoding="utf-8") as file:
                    file.writelines("".join(self.data))

                self.on_log(
                    f'''{current_time()} Finished {file_path} [{os.path.getsize(os.path.normpath(file_path))} bytes]\n'''
                )

            self.empty_memory_variables()

        if sys.argv[1:]:
            self.process_output()

        self.data = None

    def do_fake_compile(self) -> None:
        if self.input_file:
            with open(self.input_file, mode="r", encoding="utf-8") as fullscreen_sbarinfo:
                self.data = fullscreen_sbarinfo.readlines()

            for index, line in enumerate(self.data):
                self.process_merge(index, line)

            self.on_log(f'{current_time()} Data: {self.data}')

    def process_output(self) -> None:
        if self.pick_output_file:
            self.output_file = self.pick_output_file()
            if not self.output_file:
                if self.on_clear:
                    self.on_clear()
                self.on_log(f'{current_time()} No file chosen\n')
        else:
            with open(sys.argv[OUTPUT_FOLDER_ARG], mode="w", encoding="utf-8") as file:
                file.write("".join(self.data))

    def process_input(self) -> None:
        if self.pick_input_file:
            self.input_file = self.pick_input_file() or ""
            if self.on_clear:
                self.on_clear()
            if self.input_file:
                self.on_log(
                    f'{current_time()} File selected: {os.path.normpath(self.input_file)}\n'
                )
            else:
                self.on_log(f'{current_time()} No file selected\n')
        else:
            if sys.argv[INPUT_FOLDER_ARG]:
                self.input_file = sys.argv[INPUT_FOLDER_ARG]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sbarinfo.py input_file output_file")
    else:
        s = Sbarinfo()
        s.main()
