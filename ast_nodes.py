from dataclasses import dataclass, field
from typing import List, Optional, Any


@dataclass
class Program:
    declarations: List[Any]


@dataclass
class VarDecl:
    var_type: str
    name: str
    size: Optional[Any] = None
    init: Optional[Any] = None
    line: int = 0


@dataclass
class FunctionDecl:
    return_type: str
    name: str
    params: List[VarDecl]
    body: Any
    line: int = 0


@dataclass
class Block:
    statements: List[Any]


@dataclass
class IfStmt:
    condition: Any
    then_branch: Any
    else_branch: Optional[Any] = None


@dataclass
class WhileStmt:
    condition: Any
    body: Any


@dataclass
class ForStmt:
    init: Optional[Any]
    condition: Optional[Any]
    update: Optional[Any]
    body: Any


@dataclass
class BreakStmt:
    pass


@dataclass
class ContinueStmt:
    pass


@dataclass
class ReturnStmt:
    value: Optional[Any]


@dataclass
class ExprStmt:
    expr: Optional[Any]


@dataclass
class Assign:
    target: Any
    op: str
    value: Any


@dataclass
class Binary:
    left: Any
    op: str
    right: Any


@dataclass
class Unary:
    op: str
    expr: Any


@dataclass
class Postfix:
    expr: Any
    op: str


@dataclass
class Literal:
    value: Any


@dataclass
class Var:
    name: str


@dataclass
class ArrayAccess:
    array: Any
    index: Any


@dataclass
class Call:
    name: str
    args: List[Any]
