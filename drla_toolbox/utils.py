
def current_time() -> datetime:
    """
    Returns the current time as a string in the format "HH:MM:SS"
    """

    return datetime.now().strftime("%H:%M:%S")

def is_invoked_by_combiner(self) -> bool:
    return "Combiner" in self.__class__.__name__
      
def attempt_print(self, line: str) -> None:
    if is_invoked_by_combiner(self) and hasattr(self, "printline"):
        self.printLine(line)
    else:
        print(line)