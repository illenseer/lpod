from __future__ import (print_function, division, absolute_import,
                        unicode_literals)

from grako.parsing import graken, Parser
from grako.util import re, RE_FLAGS


class LogProgParser(Parser):
    def __init__(self, whitespace=None, nameguard=None, **kwargs):
        super(LogProgParser, self).__init__(
            whitespace=whitespace,
            nameguard=nameguard,
            comments_re='%\\*([^*]|\\*[^%])*\\*%',
            eol_comments_re='%([^*\\n][^\\n]*)?\\n',
            ignorecase=None,
            **kwargs
        )

    @graken()
    def _program_(self):

        def block1():
            self._statement_()
        self._positive_closure(block1)

        self.ast['statements'] = self.last_node
        self._check_eof()

        self.ast._define(
            ['statements'],
            []
        )

    @graken()
    def _directive_(self):
        self._token('@@')
        self._cut()
        with self._group():
            with self._choice():
                with self._option():
                    with self._group():
                        with self._choice():
                            with self._option():
                                self._token('comments')
                            with self._option():
                                self._token('eol_comments')
                            with self._option():
                                self._token('whitespace')
                            self._error('expecting one of: comments eol_comments whitespace')
                    self.ast['name'] = self.last_node
                    self._token('::')
                    self._cut()
                    self._regex_()
                    self.ast['value'] = self.last_node
                with self._option():
                    with self._group():
                        with self._choice():
                            with self._option():
                                self._token('nameguard')
                            with self._option():
                                self._token('ignorecase')
                            self._error('expecting one of: ignorecase nameguard')
                    self.ast['name'] = self.last_node
                    self._token('::')
                    self._cut()
                    self._boolean_()
                    self.ast['value'] = self.last_node
                self._error('no available options')

        self.ast._define(
            ['name', 'value'],
            []
        )

    @graken()
    def _statement_(self):
        with self._choice():
            with self._option():
                self._CONS_()
                with self._optional():
                    self._body_()
                    self.ast['body'] = self.last_node
                self._DOT_()
            with self._option():
                self._head_()
                self.ast['head'] = self.last_node
                with self._optional():
                    self._CONS_()
                    with self._optional():
                        self._body_()
                        self.ast['body'] = self.last_node
                self._DOT_()
            with self._option():
                self._WCONS_()
                with self._optional():
                    self._body_()
                    self.ast['body'] = self.last_node
                self._DOT_()
                self._SQUARE_OPEN_()
                self._weight_at_level_()
                self.ast['weight_at_level'] = self.last_node
                self._SQUARE_CLOSE_()
            self._error('no available options')

        self.ast._define(
            ['body', 'head', 'weight_at_level'],
            []
        )

    @graken()
    def _head_(self):
        with self._choice():
            with self._option():
                with self._group():
                    self._classical_literal_()

                    def block1():
                        self._OR_()
                        self._classical_literal_()
                    self._positive_closure(block1)
                self.ast['disjunction'] = self.last_node
            with self._option():
                with self._group():
                    self._classical_literal_()

                    def block3():
                        self._OOR_()
                        self._classical_literal_()
                    self._positive_closure(block3)
                self.ast['ordered_disjunction'] = self.last_node
            with self._option():
                self._choice_()
                self.ast['choice'] = self.last_node
            with self._option():
                self._aggregate_()
                self.ast['choice'] = self.last_node
            with self._option():
                self._classical_literal_()
                self.ast['atom'] = self.last_node
            self._error('no available options')

        self.ast._define(
            ['disjunction', 'ordered_disjunction', 'choice', 'atom'],
            []
        )

    @graken()
    def _body_(self):
        with self._group():
            with self._choice():
                with self._option():
                    self._naf_literal_()
                with self._option():
                    with self._optional():
                        self._NAF_()
                    self._aggregate_()
                self._error('no available options')

        def block1():
            self._COMMA_()
            with self._group():
                with self._choice():
                    with self._option():
                        self._naf_literal_()
                    with self._option():
                        with self._optional():
                            self._NAF_()
                        self._aggregate_()
                    self._error('no available options')
        self._closure(block1)

    @graken()
    def _choice_(self):
        with self._optional():
            self._term_()
            with self._optional():
                self._binop_()
        self._CURLY_OPEN_()
        with self._optional():
            self._choice_elements_()
        self._CURLY_CLOSE_()
        with self._optional():
            with self._optional():
                self._binop_()
            self._term_()

    @graken()
    def _choice_elements_(self):
        with self._optional():
            self._choice_elements_()
            self._SEMICOLON_()
        self._choice_element_()

    @graken()
    def _choice_element_(self):
        self._classical_literal_()
        with self._optional():
            self._COLON_()
            with self._optional():
                self._naf_literals_()

    @graken()
    def _aggregate_(self):
        with self._optional():
            self._term_()
            self._binop_()
        self._aggregate_function_()
        self._CURLY_OPEN_()
        with self._optional():
            self._aggregate_elements_()
        self._CURLY_CLOSE_()
        with self._optional():
            self._binop_()
            self._term_()

    @graken()
    def _aggregate_elements_(self):
        with self._optional():
            self._aggregate_elements_()
            self._SEMICOLON_()
        self._aggregate_element_()

    @graken()
    def _aggregate_element_(self):
        with self._optional():
            self._basic_terms_()
        with self._optional():
            self._COLON_()
            with self._optional():
                self._naf_literals_()
                with self._optional():
                    self._COLON_()
                    with self._optional():
                        self._naf_literals_()

    @graken()
    def _aggregate_function_(self):
        with self._choice():
            with self._option():
                self._AGGREGATE_COUNT_()
            with self._option():
                self._AGGREGATE_MAX_()
            with self._option():
                self._AGGREGATE_MIN_()
            with self._option():
                self._AGGREGATE_SUMPLUS_()
            with self._option():
                self._AGGREGATE_SUM_()
            self._error('no available options')

    @graken()
    def _weight_at_level_(self):
        self._term_()
        with self._optional():
            self._AT_()
            self._term_()
        with self._optional():
            self._COMMA_()
            self._terms_()

    @graken()
    def _naf_literals_(self):
        with self._optional():
            self._naf_literals_()
            self._COMMA_()
        self._naf_literal_()

    @graken()
    def _naf_literal_(self):
        with self._choice():
            with self._option():
                with self._optional():
                    self._NAF_()
                self._classical_literal_()
            with self._option():
                self._builtin_atom_()
            self._error('no available options')

    @graken()
    def _classical_literal_(self):
        with self._optional():
            self._MINUS_()
        self._ID_()
        with self._optional():
            self._PAREN_OPEN_()
            with self._optional():
                self._terms_()
            self._PAREN_CLOSE_()

    @graken()
    def _builtin_atom_(self):
        self._term_()
        self._binop_()
        self._term_()

    @graken()
    def _binop_(self):
        with self._choice():
            with self._option():
                self._EQUAL_()
            with self._option():
                self._UNEQUAL_()
            with self._option():
                self._LESS_OR_EQ_()
            with self._option():
                self._GREATER_OR_EQ_()
            with self._option():
                self._LESS_()
            with self._option():
                self._GREATER_()
            self._error('no available options')

    @graken()
    def _terms_(self):
        with self._optional():
            self._terms_()
            self._COMMA_()
        self._term_()

    @graken()
    def _term_(self):
        with self._choice():
            with self._option():
                self._ID_()
                with self._optional():
                    self._PAREN_OPEN_()
                    with self._optional():
                        self._terms_()
                    self._PAREN_CLOSE_()
            with self._option():
                self._NUMBER_()
            with self._option():
                self._STRING_()
            with self._option():
                self._VARIABLE_()
            with self._option():
                self._ANONYMOUS_VARIABLE_()
            with self._option():
                self._PAREN_OPEN_()
                self._term_()
                self._PAREN_CLOSE_()
            with self._option():
                self._MINUS_()
                self._term_()
            with self._option():
                self._term_()
                self._arithop_()
                self._term_()
            self._error('no available options')

    @graken()
    def _basic_terms_(self):
        with self._optional():
            self._basic_terms_()
            self._COMMA_()
        self._basic_term_()

    @graken()
    def _basic_term_(self):
        with self._choice():
            with self._option():
                self._ground_term_()
            with self._option():
                self._variable_term_()
            self._error('no available options')

    @graken()
    def _ground_term_(self):
        with self._choice():
            with self._option():
                self._SYMBOLIC_CONSTANT_()
            with self._option():
                self._STRING_()
            with self._option():
                with self._optional():
                    self._MINUS_()
                self._NUMBER_()
            self._error('no available options')

    @graken()
    def _variable_term_(self):
        with self._choice():
            with self._option():
                self._VARIABLE_()
            with self._option():
                self._ANONYMOUS_VARIABLE_()
            self._error('no available options')

    @graken()
    def _arithop_(self):
        with self._choice():
            with self._option():
                self._PLUS_()
            with self._option():
                self._MINUS_()
            with self._option():
                self._TIMES_()
            with self._option():
                self._DIV_()
            self._error('no available options')

    @graken()
    def _ID_(self):
        self._pattern(r'[a-z_][A-Za-z0-9_]*')

    @graken()
    def _VARIABLE_(self):
        self._pattern(r'[A-Z][A-Za-z0-9_]*')

    @graken()
    def _SYMBOLIC_CONSTANT_(self):
        self._pattern(r'[a-z][A-Za-z0-9_]*')

    @graken()
    def _STRING_(self):
        self._pattern(r'"(?:\\.|[^|*\\()])+"')

    @graken()
    def _NUMBER_(self):
        self._pattern(r'(0|[1-9][0-9]*)')

    @graken()
    def _ANONYMOUS_VARIABLE_(self):
        self._token('_')

    @graken()
    def _DOT_(self):
        self._token('.')

    @graken()
    def _COMMA_(self):
        self._token(',')

    @graken()
    def _QUERY_MARK_(self):
        self._token('?')

    @graken()
    def _COLON_(self):
        self._token(':')

    @graken()
    def _SEMICOLON_(self):
        self._token(';')

    @graken()
    def _OR_(self):
        with self._choice():
            with self._option():
                self._token('|')
            with self._option():
                self._token(';')
            self._error('expecting one of: ; |')

    @graken()
    def _OOR_(self):
        with self._choice():
            with self._option():
                self._token(';;')
            with self._option():
                self._token('||')
            self._error('expecting one of: ;; ||')

    @graken()
    def _NAF_(self):
        self._token('not ')

    @graken()
    def _CONS_(self):
        self._token(':-')

    @graken()
    def _WCONS_(self):
        self._token(':~')

    @graken()
    def _PLUS_(self):
        self._token('+')

    @graken()
    def _MINUS_(self):
        self._token('-')

    @graken()
    def _TIMES_(self):
        self._token('*')

    @graken()
    def _DIV_(self):
        self._token('/')

    @graken()
    def _AT_(self):
        self._token('@')

    @graken()
    def _PAREN_OPEN_(self):
        self._token('(')

    @graken()
    def _PAREN_CLOSE_(self):
        self._token(')')

    @graken()
    def _SQUARE_OPEN_(self):
        self._token('[')

    @graken()
    def _SQUARE_CLOSE_(self):
        self._token(']')

    @graken()
    def _CURLY_OPEN_(self):
        self._token('{')

    @graken()
    def _CURLY_CLOSE_(self):
        self._token('}')

    @graken()
    def _EQUAL_(self):
        self._token('=')

    @graken()
    def _UNEQUAL_(self):
        with self._choice():
            with self._option():
                self._token('<>')
            with self._option():
                self._token('!=')
            self._error('expecting one of: != <>')

    @graken()
    def _LESS_(self):
        self._token('<')

    @graken()
    def _GREATER_(self):
        self._token('>')

    @graken()
    def _LESS_OR_EQ_(self):
        self._token('<=')

    @graken()
    def _GREATER_OR_EQ_(self):
        self._token('>=')

    @graken()
    def _AGGREGATE_COUNT_(self):
        self._token('#count')

    @graken()
    def _AGGREGATE_MAX_(self):
        self._token('#max')

    @graken()
    def _AGGREGATE_MIN_(self):
        self._token('#min')

    @graken()
    def _AGGREGATE_SUMPLUS_(self):
        self._token('#sum+')

    @graken()
    def _AGGREGATE_SUM_(self):
        self._token('#sum')

    @graken()
    def _regex_(self):
        with self._choice():
            with self._option():
                self._token('?/')
                self._cut()
                self._pattern(r'(.|\n)+?(?=/\?)')
                self.ast['@'] = self.last_node
                self._pattern(r'/\?+')
                self._cut()
            with self._option():
                self._token('/')
                self._cut()
                self._pattern(r'(.|\n)+?(?=/)')
                self.ast['@'] = self.last_node
                self._token('/')
                self._cut()
            self._error('expecting one of: / ?/')

    @graken()
    def _boolean_(self):
        with self._choice():
            with self._option():
                self._token('True')
            with self._option():
                self._token('False')
            self._error('expecting one of: False True')
