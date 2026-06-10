from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from errors import SmallCError


WELCOME = """Small-C Interactive Interpreter v1.0
Type HELP for commands.
"""


HELP = """
Commands:
  NEW                         Clear current source buffer.
  LOAD <file>                  Load a Small-C source file.
  SAVE <file>                  Save current source buffer.
  LIST                         Show current source with line numbers.
  APPEND                       Enter multi-line source; finish with a single line: END
  INSERT <line> <code>          Insert code before line number.
  DELETE <line>                Delete one line.
  CHECK                        Lex and parse current source.
  RUN                          Parse and run main().
  TRACE ON | TRACE OFF          Show executed statement types.
  VARS                         Show global variables after run/load.
  FUNCS                        Show functions after CHECK/RUN.
  HELP                         Show this help.
  EXIT | QUIT                  Leave interpreter.

Tip:
  You can also type a one-line Small-C statement/declaration, and it will be appended.
"""


class SmallCRepl:
    def __init__(self):
        self.lines = []
        self.interpreter = Interpreter()
        self.last_program = None

    def source(self):
        return "\n".join(self.lines) + ("\n" if self.lines else "")

    def parse_current(self):
        tokens = Lexer(self.source()).tokenize()
        program = Parser(tokens).parse()
        self.last_program = program
        self.interpreter.load_program(program)
        return program

    def cmd_new(self):
        self.lines = []
        self.last_program = None
        self.interpreter = Interpreter()
        print("All cleared.")

    def cmd_load(self, path):
        with open(path, "r", encoding="utf-8") as f:
            self.lines = f.read().splitlines()
        self.last_program = None
        print(f"Loaded {len(self.lines)} lines from {path!r}.")

    def cmd_save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.source())
        print(f"Saved {len(self.lines)} lines to {path!r}.")

    def cmd_list(self):
        if not self.lines:
            print("(empty)")
            return
        for i, line in enumerate(self.lines, start=1):
            print(f"{i:>4}: {line}")

    def cmd_append(self):
        print("Enter source lines. Finish with a single line: END")
        while True:
            line = input("... ")
            if line.strip() == ".":
                break
            self.lines.append(line)
        print("Appended.")

    def cmd_insert(self, rest):
        parts = rest.split(maxsplit=1)
        if len(parts) != 2:
            print("Usage: INSERT <line> <code>")
            return
        line_no = int(parts[0])
        code = parts[1]
        line_no = max(1, min(line_no, len(self.lines) + 1))
        self.lines.insert(line_no - 1, code)
        print(f"Inserted at line {line_no}.")

    def cmd_delete(self, rest):
        line_no = int(rest.strip())
        if line_no < 1 or line_no > len(self.lines):
            print("Line out of range.")
            return
        removed = self.lines.pop(line_no - 1)
        print(f"Deleted line {line_no}: {removed}")

    def cmd_check(self):
        self.parse_current()
        print("No errors found.")
        print(f"Functions: {', '.join(self.interpreter.funcs_snapshot()) or '(none)'}")

    def cmd_run(self):
        program = self.parse_current()
        result = self.interpreter.run(program)
        print(f"\nProgram exited with return value {result}.")

    def cmd_vars(self):
        data = self.interpreter.vars_snapshot()
        if not data:
            print("(no global variables)")
            return
        for k, v in data.items():
            print(f"{k} = {v}")

    def cmd_funcs(self):
        funcs = self.interpreter.funcs_snapshot()
        if not funcs:
            try:
                self.parse_current()
                funcs = self.interpreter.funcs_snapshot()
            except SmallCError:
                pass
        if not funcs:
            print("(no functions)")
            return
        for name in funcs:
            print(name)

    def cmd_direct_exec(self, code_line):
        temp_source = f"""
    int main() {{
        {code_line}
        return 0;
    }}
    """
        tokens = Lexer(temp_source).tokenize()
        program = Parser(tokens).parse()
        result = self.interpreter.run(program)
        print(f"\nProgram exited with return value {result}.")
        tokens = Lexer(temp_source).tokenize()
        program = Parser(tokens).parse()
        result = self.interpreter.run(program)
        print(f"\nProgram exited with return value {result}.")

    def run(self):
        print(WELCOME)
        while True:
            try:
                raw = input("SC> ")
            except EOFError:
                print()
                break

            line = raw.strip()
            if not line:
                continue

            upper = line.upper()
            parts = line.split(maxsplit=1)
            cmd = parts[0].upper()
            rest = parts[1] if len(parts) > 1 else ""

            try:
                if cmd in ("EXIT", "QUIT"):
                    print("Goodbye.")
                    break
                elif cmd == "HELP":
                    print(HELP)
                elif cmd == "NEW":
                    self.cmd_new()
                elif cmd == "LOAD":
                    self.cmd_load(rest.strip())
                elif cmd == "SAVE":
                    self.cmd_save(rest.strip())
                elif cmd == "LIST":
                    self.cmd_list()
                elif cmd == "APPEND":
                    self.cmd_append()
                elif cmd == "INSERT":
                    self.cmd_insert(rest)
                elif cmd == "DELETE":
                    self.cmd_delete(rest)
                elif cmd == "CHECK":
                    self.cmd_check()
                elif cmd == "RUN":
                    self.cmd_run()
                elif cmd == "VARS":
                    self.cmd_vars()
                elif cmd == "FUNCS":
                    self.cmd_funcs()
                elif cmd == "TRACE":
                    value = rest.strip().upper()
                    if value == "ON":
                        self.interpreter.trace = True
                        print("Trace enabled.")
                    elif value == "OFF":
                        self.interpreter.trace = False
                        print("Trace disabled.")
                    else:
                        print("Usage: TRACE ON or TRACE OFF")
                else:
                    if line.startswith("printf("):
                        self.cmd_direct_exec(raw)
                    else:
                        self.lines.append(raw)
                        print(f"Appended line {len(self.lines)}. Use RUN or CHECK.")
            except Exception as e:
                print(f"Error: {e}")
