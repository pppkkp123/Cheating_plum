from typing import Any, Dict, Optional
from errors import RuntimeSmallCError


class Cell:
    """A memory cell with a fake address for pointer simulation."""

    _next_addr = 1000

    @classmethod
    def reset_addresses(cls):
        cls._next_addr = 1000

    def __init__(self, value: Any = 0):
        self.value = value
        self.address = Cell._next_addr
        Cell._next_addr += 4

    def __repr__(self):
        return f"Cell(addr={self.address}, value={self.value!r})"


class PointerValue:
    """Simplified pointer value. It stores a reference to a Cell."""

    def __init__(self, cell: Optional[Cell] = None):
        self.cell = cell

    @property
    def address(self):
        return 0 if self.cell is None else self.cell.address

    def deref_cell(self) -> Cell:
        if self.cell is None:
            raise RuntimeSmallCError("null pointer dereference")
        return self.cell

    def __int__(self):
        return self.address

    def __bool__(self):
        return self.address != 0

    def __repr__(self):
        if self.cell is None:
            return "NULL"
        return f"&{self.cell.address}"


class ArrayValue:
    def __init__(self, size: int, fill=0):
        if size < 0:
            raise RuntimeSmallCError("array size cannot be negative")
        self.items = [Cell(fill) for _ in range(size)]

    def get_cell(self, index: int) -> Cell:
        if index < 0 or index >= len(self.items):
            raise RuntimeSmallCError(f"array index out of bounds (index {index}, size {len(self.items)})")
        return self.items[index]

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return "[" + ", ".join(str(c.value) for c in self.items) + "]"


class Environment:
    def __init__(self, parent: Optional["Environment"] = None, name="scope"):
        self.parent = parent
        self.name = name
        self.values: Dict[str, Cell] = {}

    def define(self, name: str, value=0):
        if name in self.values:
            raise RuntimeSmallCError(f"variable {name!r} already declared in this scope")
        self.values[name] = Cell(value)

    def resolve_cell(self, name: str) -> Cell:
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.resolve_cell(name)
        raise RuntimeSmallCError(f"undefined variable {name!r}")

    def assign(self, name: str, value):
        self.resolve_cell(name).value = value

    def get(self, name: str):
        return self.resolve_cell(name).value

    def snapshot(self):
        data = {}
        cur = self
        depth = 0
        while cur is not None:
            for k, cell in cur.values.items():
                key = k if depth == 0 else f"{k} <outer:{depth}>"
                data[key] = cell.value
            cur = cur.parent
            depth += 1
        return data
