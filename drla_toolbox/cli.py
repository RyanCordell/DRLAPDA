import sys
import os.path
from arsenal import Arsenal
from sbarinfo import Sbarinfo


def run_arsenal():
    if len(sys.argv) < 3:
        print("Usage: cli.py arsenal <input_folder> <output_folder> [separator]")
        return

    input_dir = sys.argv[2]
    output_dir = sys.argv[3]

    if not os.path.isdir(input_dir):
        print(f"Input folder not found: {input_dir}")
        return

    separator = sys.argv[4] if len(sys.argv) > 4 else ":"

    a = Arsenal(pick_input_dir=lambda: input_dir)
    a.separator_token = separator
    a.do_input()

    if not a.loaded_json:
        print("No JSON data loaded. Check input folder.")
        return

    a.do_compile(do_output=True)


def run_sbarinfo():
    if len(sys.argv) < 4:
        print("Usage: cli.py sbarinfo <input_file> <output_file>")
        return

    s = Sbarinfo()
    s.input_file = sys.argv[2]
    s.output_file = sys.argv[3]
    s.perform_compile()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: cli.py <arsenal|sbarinfo> [args...]")
        sys.exit(1)

    match sys.argv[1]:
        case "arsenal":  run_arsenal()
        case "sbarinfo": run_sbarinfo()
        case _:          print(f"Unknown tool: {sys.argv[1]}")
