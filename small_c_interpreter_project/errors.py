class SmallCError(Exception):
    """Base class for Small-C interpreter errors."""
    pass


class LexError(SmallCError):
    pass


class ParseError(SmallCError):
    pass


class RuntimeSmallCError(SmallCError):
    pass
