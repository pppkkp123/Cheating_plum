from ast_nodes import *
from memory import Environment, ArrayValue, Cell
from sc_builtins import Builtins
from errors import RuntimeSmallCError


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


class Interpreter:
    def __init__(self):
        self.globals = Environment(name="global")
        self.env = self.globals
        self.functions = {}
        self.builtins = Builtins()
        self.trace = False
        self.last_program = None

    def load_program(self, program: Program):
        self.last_program = program
        self.functions = {}
        # Fresh global memory each LOAD/RUN.
        self.globals = Environment(name="global")
        self.env = self.globals

        for decl in program.declarations:
            if isinstance(decl, FunctionDecl):
                self.functions[decl.name] = decl
            elif isinstance(decl, VarDecl):
                self.execute_var_decl(decl)

    def run(self, program: Program = None):
        if program is not None:
            self.load_program(program)
        if "main" not in self.functions:
            raise RuntimeSmallCError("No main() function found")
        return self.call_user_function("main", [])

    def execute(self, stmt):
        if self.trace:
            print(f"[TRACE] {type(stmt).__name__}")

        if isinstance(stmt, Block):
            self.execute_block(stmt, Environment(self.env, name="block"))
        elif isinstance(stmt, VarDecl):
            self.execute_var_decl(stmt)
        elif isinstance(stmt, IfStmt):
            if self.truthy(self.eval(stmt.condition)):
                self.execute(stmt.then_branch)
            elif stmt.else_branch is not None:
                self.execute(stmt.else_branch)
        elif isinstance(stmt, WhileStmt):
            while self.truthy(self.eval(stmt.condition)):
                try:
                    self.execute(stmt.body)
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break
        elif isinstance(stmt, ForStmt):
            loop_env = Environment(self.env, name="for")
            old = self.env
            self.env = loop_env
            try:
                if stmt.init is not None:
                    if isinstance(stmt.init, VarDecl) or isinstance(stmt.init, Block):
                        self.execute(stmt.init)
                    else:
                        self.eval(stmt.init)
                while True:
                    if stmt.condition is not None and not self.truthy(self.eval(stmt.condition)):
                        break
                    try:
                        self.execute(stmt.body)
                    except ContinueSignal:
                        pass
                    except BreakSignal:
                        break
                    if stmt.update is not None:
                        self.eval(stmt.update)
            finally:
                self.env = old
        elif isinstance(stmt, BreakStmt):
            raise BreakSignal()
        elif isinstance(stmt, ContinueStmt):
            raise ContinueSignal()
        elif isinstance(stmt, ReturnStmt):
            value = self.eval(stmt.value) if stmt.value is not None else 0
            raise ReturnSignal(value)
        elif isinstance(stmt, ExprStmt):
            if stmt.expr is not None:
                self.eval(stmt.expr)
        else:
            raise RuntimeSmallCError(f"unknown statement type: {type(stmt).__name__}")

    def execute_block(self, block: Block, new_env: Environment):
        old = self.env
        self.env = new_env
        try:
            for stmt in block.statements:
                self.execute(stmt)
        finally:
            self.env = old

    def execute_var_decl(self, decl: VarDecl):
        if decl.size is not None:
            size = int(self.eval(decl.size))
            self.env.define(decl.name, ArrayValue(size))
        else:
            value = self.eval(decl.init) if decl.init is not None else 0
            self.env.define(decl.name, value)

    def eval(self, expr):
        if expr is None:
            return 0

        if isinstance(expr, Literal):
            return expr.value

        if isinstance(expr, Var):
            return self.env.get(expr.name)

        if isinstance(expr, ArrayAccess):
            return self.get_lvalue_cell(expr).value

        if isinstance(expr, Assign):
            cell = self.get_lvalue_cell(expr.target)
            right = self.eval(expr.value)
            if expr.op == "=":
                cell.value = right
            else:
                left = cell.value
                if expr.op == "+=":
                    cell.value = left + right
                elif expr.op == "-=":
                    cell.value = left - right
                elif expr.op == "*=":
                    cell.value = left * right
                elif expr.op == "/=":
                    if right == 0:
                        raise RuntimeSmallCError("division by zero")
                    cell.value = int(left / right)
                elif expr.op == "%=":
                    if right == 0:
                        raise RuntimeSmallCError("modulo by zero")
                    cell.value = left % right
                else:
                    raise RuntimeSmallCError(f"unknown assignment operator {expr.op}")
            return cell.value

        if isinstance(expr, Unary):
            if expr.op in ("++", "--"):
                cell = self.get_lvalue_cell(expr.expr)
                cell.value += 1 if expr.op == "++" else -1
                return cell.value
            v = self.eval(expr.expr)
            if expr.op == "-":
                return -int(v)
            if expr.op == "+":
                return int(v)
            if expr.op == "!":
                return 0 if self.truthy(v) else 1
            if expr.op == "~":
                return ~int(v)
            raise RuntimeSmallCError(f"unknown unary operator {expr.op}")

        if isinstance(expr, Postfix):
            cell = self.get_lvalue_cell(expr.expr)
            old = cell.value
            if expr.op == "++":
                cell.value = old + 1
            elif expr.op == "--":
                cell.value = old - 1
            else:
                raise RuntimeSmallCError(f"unknown postfix operator {expr.op}")
            return old

        if isinstance(expr, Binary):
            if expr.op == "&&":
                return 1 if self.truthy(self.eval(expr.left)) and self.truthy(self.eval(expr.right)) else 0
            if expr.op == "||":
                return 1 if self.truthy(self.eval(expr.left)) or self.truthy(self.eval(expr.right)) else 0

            left = self.eval(expr.left)
            right = self.eval(expr.right)
            return self.apply_binary(expr.op, left, right)

        if isinstance(expr, Call):
            args = [self.eval(a) for a in expr.args]
            if expr.name in self.functions:
                return self.call_user_function(expr.name, args)
            return self.builtins.call(expr.name, args)

        raise RuntimeSmallCError(f"unknown expression type: {type(expr).__name__}")

    def get_lvalue_cell(self, expr) -> Cell:
        if isinstance(expr, Var):
            return self.env.resolve_cell(expr.name)

        if isinstance(expr, ArrayAccess):
            array_obj = self.eval(expr.array)
            idx = int(self.eval(expr.index))
            if not isinstance(array_obj, ArrayValue):
                raise RuntimeSmallCError("subscripted value is not an array")
            return array_obj.get_cell(idx)

        raise RuntimeSmallCError("left side of assignment must be a variable or array element")

    def apply_binary(self, op, left, right):
        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            if right == 0:
                raise RuntimeSmallCError("division by zero")
            return int(left / right)
        if op == "%":
            if right == 0:
                raise RuntimeSmallCError("modulo by zero")
            return left % right
        if op == "<":
            return 1 if left < right else 0
        if op == "<=":
            return 1 if left <= right else 0
        if op == ">":
            return 1 if left > right else 0
        if op == ">=":
            return 1 if left >= right else 0
        if op == "==":
            return 1 if left == right else 0
        if op == "!=":
            return 1 if left != right else 0
        if op == "&":
            return int(left) & int(right)
        if op == "|":
            return int(left) | int(right)
        if op == "^":
            return int(left) ^ int(right)
        raise RuntimeSmallCError(f"unknown binary operator {op}")

    def call_user_function(self, name, args):
        func = self.functions[name]
        if len(args) != len(func.params):
            raise RuntimeSmallCError(f"{name}() expects {len(func.params)} args, got {len(args)}")

        old = self.env
        call_env = Environment(self.globals, name=f"call:{name}")
        self.env = call_env
        try:
            for param, value in zip(func.params, args):
                call_env.define(param.name, value)

            try:
                self.execute(func.body)
            except ReturnSignal as r:
                return r.value

            # void-like fallthrough
            return 0
        finally:
            self.env = old

    def truthy(self, value):
        return value != 0 and value is not None

    def vars_snapshot(self):
        return self.globals.snapshot()

    def funcs_snapshot(self):
        return sorted(self.functions.keys())
