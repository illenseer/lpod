from __future__ import (print_function, division, absolute_import,
                        unicode_literals)

from grako.ast import AST
from grako.exceptions import SemanticError
from grako.exceptions import FailedSemantics
from traod.util import flatten


class LogProgSemantics(object):
    """
    Semantics for Logic Programs with Ordered Disjunctions.
    """
    def head(self, ast):
        """
        Flatten lists in head and do not allow normal disjunctions.
        """
        if ast['disjunction']:
            raise SemanticError('Normal disjunctions are not allowed.')
        new_ast = AST()
        for item in ast:
            if ast[item]:
                new_ast[item] = list(flatten(ast[item]))
            else:
                new_ast[item] = None
        return new_ast

    def weight_at_level(self, ast):
        """
        Do not allow Weight Constraints.
        """
        raise SemanticError(
            'Weight constraints or optimize statements are not allowed.'
        )

    def body(self, ast):
        """
        Flatten lists in body.
        """
        new_ast = list(flatten(ast))
        return new_ast

    def _default(self, ast):
        return ast
