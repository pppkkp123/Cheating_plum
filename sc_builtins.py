import random
from errors import RuntimeSmallCError


def _format_c(fmt, args):
    """Very small printf-style formatter: supports %d, %c, %s and %%."""
    out = []
    arg_i = 0
    i = 0
    while i < len(fmt):
        if fmt[i] == "%" and i + 1 < len(fmt):
            spec = fmt[i + 1]
            if spec == "%":
                out.append("%")
            elif spec in ("d", "i"):
                out.append(str(int(args[arg_i])))
                arg_i += 1
            elif spec == "c":
                v = args[arg_i]
                out.append(chr(v) if isinstance(v, int) else str(v)[0])
                arg_i += 1
            elif spec == "s":
                out.append(str(args[arg_i]))
                arg_i += 1
            else:
                # keep unknown specifier readable
                out.append("%" + spec)
            i += 2
            continue
        out.append(fmt[i])
        i += 1

    # Append extra arguments like many teaching interpreters do for convenience.
    while arg_i < len(args):
        out.append(" " + str(args[arg_i]))
        arg_i += 1
    return "".join(out)


class Builtins:
    def __init__(self, input_provider=input, output_writer=print):
        self.input_provider = input_provider
        self.output_writer = output_writer

    def call(self, name, args):
        if name in ("printf", "print"):
            if not args:
                return 0
            if isinstance(args[0], str):
                text = _format_c(args[0], args[1:])
            else:
                text = " ".join(str(a) for a in args)
            print(text, end="")
            return len(text)

        if name == "putchar":
            v = args[0]
            ch = chr(v) if isinstance(v, int) else str(v)[0]
            print(ch, end="")
            return ord(ch)

        if name == "getchar":
            s = self.input_provider()
            return ord(s[0]) if s else 0

        if name == "strlen":
            return len(str(args[0]))

        if name == "strcpy":
            # Teaching simplification: Python strings are immutable, so return copied value.
            return str(args[1])

        if name == "strcmp":
            a, b = str(args[0]), str(args[1])
            return 0 if a == b else (-1 if a < b else 1)

        if name == "strcat":
            return str(args[0]) + str(args[1])

        if name == "abs":
            return abs(int(args[0]))

        if name == "max":
            return max(int(args[0]), int(args[1]))

        if name == "min":
            return min(int(args[0]), int(args[1]))

        if name == "pow":
            return int(args[0]) ** int(args[1])

        if name == "rand":
            return random.randint(0, 32767)

        if name == "srand":
            random.seed(int(args[0]))
            return 0

        raise RuntimeSmallCError(f"unknown function {name!r}")
