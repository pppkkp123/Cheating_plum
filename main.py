import sys
from repl import SmallCRepl
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter


def run_file(path: str):
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    program = Parser(Lexer(source).tokenize()).parse()
    interpreter = Interpreter()
    result = interpreter.run(program)
    print(f"\nProgram exited with return value {result}.")


def main():
    if len(sys.argv) >= 2:
        run_file(sys.argv[1])
    else:
        SmallCRepl().run()


if __name__ == "__main__":
    main()
