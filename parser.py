from typing import List, Optional
from errors import ParseError
from lexer import Token
from ast_nodes import *


class Parser:
    """
    Recursive-descent parser for a practical subset of Small-C.

    Supported:
    - int/char/void variables and functions
    - one-dimensional arrays
    - expression precedence
    - assignment, +=, -=, *=, /=, %= 
    - if/else, while, for, break, continue, return
    - function calls
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.i = 0

    def peek(self, offset=0) -> Token:
        idx = self.i + offset
        if idx >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[idx]

    def at_end(self):
        return self.peek().type == "EOF"

    def check(self, value=None, typ=None):
        tok = self.peek()
        if typ is not None and tok.type != typ:
            return False
        if value is not None and tok.value != value:
            return False
        return True

    def match(self, *values):
        if self.peek().value in values:
            tok = self.peek()
            self.i += 1
            return tok
        return None

    def match_type(self, typ):
        if self.peek().type == typ:
            tok = self.peek()
            self.i += 1
            return tok
        return None

    def consume(self, value=None, typ=None, message="Unexpected token"):
        tok = self.peek()
        if self.check(value, typ):
            self.i += 1
            return tok
        raise ParseError(f"{message}. Got {tok.value!r} at line {tok.line}, col {tok.col}")

    def is_type_keyword(self):
        return self.peek().type == "KEYWORD" and self.peek().value in ("int", "char", "void")

    def parse(self):
        declarations = []
        while not self.at_end():
            if self.is_type_keyword():
                declarations.append(self.parse_global_declaration())
            else:
                tok = self.peek()
                raise ParseError(f"Expected declaration at line {tok.line}, got {tok.value!r}")
        return Program(declarations)

    def parse_type(self):
        tok = self.consume(typ="KEYWORD", message="Expected type")
        if tok.value not in ("int", "char", "void"):
            raise ParseError(f"Expected type at line {tok.line}")
        return tok.value

    def parse_global_declaration(self):
        var_type = self.parse_type()
        name_tok = self.consume(typ="IDENT", message="Expected identifier")

        if self.match("("):
            params = self.parse_params()
            self.consume(")", message="Expected ')' after parameters")
            body = self.parse_block()
            return FunctionDecl(var_type, name_tok.value, params, body, name_tok.line)

        size = None
        if self.match("["):
            size = self.expression()
            self.consume("]", message="Expected ']' after array size")

        init = None
        if self.match("="):
            init = self.expression()

        self.consume(";", message="Expected ';' after variable declaration")
        return VarDecl(var_type, name_tok.value, size, init, name_tok.line)

    def parse_params(self):
        params = []
        if self.check(")"):
            return params
        while True:
            p_type = self.parse_type()
            p_name = self.consume(typ="IDENT", message="Expected parameter name")
            # support int arr[] parameter form as a normal variable name
            if self.match("["):
                if not self.check("]"):
                    self.expression()
                self.consume("]", message="Expected ']' in parameter")
            params.append(VarDecl(p_type, p_name.value, None, None, p_name.line))
            if not self.match(","):
                break
        return params

    def parse_block(self):
        self.consume("{", message="Expected '{'")
        statements = []
        while not self.check("}") and not self.at_end():
            statements.append(self.declaration_or_statement())
        self.consume("}", message="Expected '}'")
        return Block(statements)

    def declaration_or_statement(self):
        if self.is_type_keyword() and self.peek().value != "void":
            return self.parse_local_declaration()
        return self.statement()

    def parse_local_declaration(self):
        var_type = self.parse_type()
        declarations = []

        while True:
            name_tok = self.consume(typ="IDENT", message="Expected variable name")
            size = None
            if self.match("["):
                size = self.expression()
                self.consume("]", message="Expected ']' after array size")

            init = None
            if self.match("="):
                init = self.expression()

            declarations.append(VarDecl(var_type, name_tok.value, size, init, name_tok.line))
            if not self.match(","):
                break

        self.consume(";", message="Expected ';' after variable declaration")

        # One statement node can represent several declarations.
        if len(declarations) == 1:
            return declarations[0]
        return Block(declarations)

    def statement(self):
        if self.check("{"):
            return self.parse_block()
        if self.match("if"):
            self.consume("(", message="Expected '(' after if")
            cond = self.expression()
            self.consume(")", message="Expected ')' after if condition")
            then_branch = self.statement()
            else_branch = None
            if self.match("else"):
                else_branch = self.statement()
            return IfStmt(cond, then_branch, else_branch)

        if self.match("while"):
            self.consume("(", message="Expected '(' after while")
            cond = self.expression()
            self.consume(")", message="Expected ')' after while condition")
            return WhileStmt(cond, self.statement())

        if self.match("for"):
            self.consume("(", message="Expected '(' after for")
            init = None
            if not self.check(";"):
                if self.is_type_keyword() and self.peek().value != "void":
                    init = self.parse_local_declaration()
                else:
                    init = self.expression()
                    self.consume(";", message="Expected ';' after for init")
            else:
                self.consume(";")
            cond = None
            if not self.check(";"):
                cond = self.expression()
            self.consume(";", message="Expected ';' after for condition")
            update = None
            if not self.check(")"):
                update = self.expression()
            self.consume(")", message="Expected ')' after for clauses")
            return ForStmt(init, cond, update, self.statement())

        if self.match("break"):
            self.consume(";", message="Expected ';' after break")
            return BreakStmt()

        if self.match("continue"):
            self.consume(";", message="Expected ';' after continue")
            return ContinueStmt()

        if self.match("return"):
            value = None
            if not self.check(";"):
                value = self.expression()
            self.consume(";", message="Expected ';' after return")
            return ReturnStmt(value)

        if self.match(";"):
            return ExprStmt(None)

        expr = self.expression()
        self.consume(";", message="Expected ';' after expression")
        return ExprStmt(expr)

    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.logical_or()
        if self.peek().value in ("=", "+=", "-=", "*=", "/=", "%="):
            op = self.peek().value
            self.i += 1
            value = self.assignment()
            return Assign(expr, op, value)
        return expr

    def logical_or(self):
        expr = self.logical_and()
        while self.match("||"):
            expr = Binary(expr, "||", self.logical_and())
        return expr

    def logical_and(self):
        expr = self.bitwise_or()
        while self.match("&&"):
            expr = Binary(expr, "&&", self.bitwise_or())
        return expr

    def bitwise_or(self):
        expr = self.bitwise_xor()
        while self.match("|"):
            expr = Binary(expr, "|", self.bitwise_xor())
        return expr

    def bitwise_xor(self):
        expr = self.bitwise_and()
        while self.match("^"):
            expr = Binary(expr, "^", self.bitwise_and())
        return expr

    def bitwise_and(self):
        expr = self.equality()
        while self.match("&"):
            expr = Binary(expr, "&", self.equality())
        return expr

    def equality(self):
        expr = self.comparison()
        while self.peek().value in ("==", "!="):
            op = self.peek().value
            self.i += 1
            expr = Binary(expr, op, self.comparison())
        return expr

    def comparison(self):
        expr = self.term()
        while self.peek().value in ("<", "<=", ">", ">="):
            op = self.peek().value
            self.i += 1
            expr = Binary(expr, op, self.term())
        return expr

    def term(self):
        expr = self.factor()
        while self.peek().value in ("+", "-"):
            op = self.peek().value
            self.i += 1
            expr = Binary(expr, op, self.factor())
        return expr

    def factor(self):
        expr = self.unary()
        while self.peek().value in ("*", "/", "%"):
            op = self.peek().value
            self.i += 1
            expr = Binary(expr, op, self.unary())
        return expr

    def unary(self):
        if self.peek().value in ("!", "-", "+", "~", "++", "--"):
            op = self.peek().value
            self.i += 1
            return Unary(op, self.unary())
        return self.postfix()

    def postfix(self):
        expr = self.primary()
        while True:
            if self.match("["):
                index = self.expression()
                self.consume("]", message="Expected ']'")
                expr = ArrayAccess(expr, index)
            elif self.peek().value in ("++", "--"):
                op = self.peek().value
                self.i += 1
                expr = Postfix(expr, op)
            else:
                break
        return expr

    def primary(self):
        if tok := self.match_type("NUMBER"):
            return Literal(tok.value)
        if tok := self.match_type("STRING"):
            return Literal(tok.value)
        if self.match("("):
            expr = self.expression()
            self.consume(")", message="Expected ')' after expression")
            return expr
        if tok := self.match_type("IDENT"):
            if self.match("("):
                args = []
                if not self.check(")"):
                    while True:
                        args.append(self.expression())
                        if not self.match(","):
                            break
                self.consume(")", message="Expected ')' after call arguments")
                return Call(tok.value, args)
            return Var(tok.value)

        tok = self.peek()
        raise ParseError(f"Expected expression at line {tok.line}, col {tok.col}, got {tok.value!r}")
