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
                self._cons_()
                with self._optional():
                    self._body_()
                    self.ast['body'] = self.last_node
                self._dot_()
            with self._option():
                self._head_()
                self.ast['head'] = self.last_node
                with self._optional():
                    self._cons_()
                    with self._optional():
                        self._body_()
                        self.ast['body'] = self.last_node
                self._dot_()
            with self._option():
                self._wcons_()
                with self._optional():
                    self._body_()
                    self.ast['body'] = self.last_node
                self._dot_()
                self._square_open_()
                self._weight_at_level_()
                self.ast['weight_at_level'] = self.last_node
                self._square_close_()
            with self._option():
                self._optimize_()
                self.ast['optimize'] = self.last_node
                self._dot_()
            self._error('no available options')

        self.ast._define(
            ['body', 'head', 'weight_at_level', 'optimize'],
            []
        )

    @graken()
    def _head_(self):
        with self._choice():
            with self._option():
                with self._group():
                    self._classical_literal_()

                    def block1():
                        self._or_()
                        self._classical_literal_()
                    self._positive_closure(block1)
                self.ast['disjunction'] = self.last_node
            with self._option():
                with self._group():
                    self._classical_literal_()

                    def block3():
                        self._oor_()
                        self._classical_literal_()
                    self._positive_closure(block3)
                self.ast['ordered_disjunction'] = self.last_node
            with self._option():
                self._choice_()
                self.ast['choice'] = self.last_node
            with self._option():
                self._aggregate_()
                self.ast['aggregate'] = self.last_node
            with self._option():
                self._classical_literal_()
                self.ast['atom'] = self.last_node
            self._error('no available options')

        self.ast._define(
            ['disjunction', 'ordered_disjunction', 'choice', 'aggregate', 'atom'],
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
                        self._naf_()
                    self._aggregate_()
                self._error('no available options')

        def block1():
            self._comma_()
            with self._group():
                with self._choice():
                    with self._option():
                        self._naf_literal_()
                    with self._option():
                        with self._optional():
                            self._naf_()
                        self._aggregate_()
                    self._error('no available options')
        self._closure(block1)

    @graken()
    def _choice_(self):
        with self._optional():
            self._term_()
            with self._optional():
                self._binop_()
        self._curly_open_()
        with self._optional():
            self._choice_element_()

            def block0():
                self._semicolon_()
                self._choice_element_()
            self._closure(block0)
        self._curly_close_()
        with self._optional():
            with self._optional():
                self._binop_()
            self._term_()

    @graken()
    def _choice_element_(self):
        self._classical_literal_()
        with self._optional():
            self._colon_()
            with self._optional():
                self._naf_literals_()

    @graken()
    def _aggregate_(self):
        with self._optional():
            self._term_()
            with self._optional():
                self._binop_()
        with self._optional():
            self._aggregate_function_()
        self._curly_open_()
        with self._optional():
            self._aggregate_element_()

            def block0():
                self._semicolon_()
                self._aggregate_element_()
            self._closure(block0)
        self._curly_close_()
        with self._optional():
            with self._optional():
                self._binop_()
            self._term_()

    @graken()
    def _aggregate_element_(self):
        with self._optional():
            self._terms_()
        with self._optional():
            self._colon_()
            with self._optional():
                self._naf_literals_()
                with self._optional():
                    self._colon_()
                    with self._optional():
                        self._naf_literals_()

    @graken()
    def _aggregate_function_(self):
        with self._choice():
            with self._option():
                self._aggregate_count_()
            with self._option():
                self._aggregate_max_()
            with self._option():
                self._aggregate_min_()
            with self._option():
                self._aggregate_sumplus_()
            with self._option():
                self._aggregate_sum_()
            self._error('no available options')

    @graken()
    def _optimize_(self):
        self._optimize_function_()
        self._curly_open_()
        with self._optional():
            self._optimize_element_()

            def block0():
                self._semicolon_()
                self._optimize_element_()
            self._closure(block0)
        self._curly_close_()

    @graken()
    def _optimize_element_(self):
        self._weight_at_level_()
        with self._optional():
            self._colon_()
            with self._optional():
                self._naf_literals_()

    @graken()
    def _optimize_function_(self):
        with self._choice():
            with self._option():
                self._maximize_()
            with self._option():
                self._minimize_()
            self._error('no available options')

    @graken()
    def _weight_at_level_(self):
        self._term_()
        with self._optional():
            self._at_()
            self._term_()
        with self._optional():
            self._comma_()
            self._terms_()

    @graken()
    def _naf_literals_(self):
        self._naf_literal_()

        def block0():
            self._comma_()
            self._naf_literal_()
        self._closure(block0)

    @graken()
    def _naf_literal_(self):
        with self._choice():
            with self._option():
                with self._optional():
                    self._naf_()
                self._classical_literal_()
            with self._option():
                self._builtin_atom_()
            self._error('no available options')

    @graken()
    def _classical_literal_(self):
        with self._optional():
            self._minus_()
        self._id_()
        with self._optional():
            self._paren_open_()
            with self._optional():
                self._terms_()
            self._paren_close_()

    @graken()
    def _builtin_atom_(self):
        self._term_()
        self._binop_()
        self._term_()

    @graken()
    def _binop_(self):
        with self._choice():
            with self._option():
                self._equal_()
            with self._option():
                self._unequal_()
            with self._option():
                self._less_or_eq_()
            with self._option():
                self._greater_or_eq_()
            with self._option():
                self._less_()
            with self._option():
                self._greater_()
            self._error('no available options')

    @graken()
    def _terms_(self):
        self._term_()

        def block0():
            self._comma_()
            self._term_()
        self._closure(block0)

    @graken()
    def _term_(self):
        with self._choice():
            with self._option():
                self._id_()
                with self._optional():
                    self._paren_open_()
                    with self._optional():
                        self._terms_()
                    self._paren_close_()
            with self._option():
                self._number_()
            with self._option():
                self._string_()
            with self._option():
                self._variable_()
            with self._option():
                self._anonymous_variable_()
            with self._option():
                self._paren_open_()
                self._term_()
                self._paren_close_()
            with self._option():
                self._minus_()
                self._term_()
            with self._option():
                self._term_()
                self._arithop_()
                self._term_()
            self._error('no available options')

    @graken()
    def _arithop_(self):
        with self._choice():
            with self._option():
                self._plus_()
            with self._option():
                self._minus_()
            with self._option():
                self._times_()
            with self._option():
                self._div_()
            self._error('no available options')

    @graken()
    def _id_(self):
        self._pattern(r'[a-z_][A-Za-z0-9_]*')

    @graken()
    def _variable_(self):
        self._pattern(r'[A-Z][A-Za-z0-9_]*')

    @graken()
    def _symbolic_constant_(self):
        self._pattern(r'[a-z][A-Za-z0-9_]*')

    @graken()
    def _string_(self):
        self._pattern(r'"(?:\\.|[^|*\\()])+"')

    @graken()
    def _number_(self):
        self._pattern(r'(0|[1-9][0-9]*)')

    @graken()
    def _anonymous_variable_(self):
        self._token('_')

    @graken()
    def _dot_(self):
        self._token('.')

    @graken()
    def _comma_(self):
        self._token(',')

    @graken()
    def _query_mark_(self):
        self._token('?')

    @graken()
    def _colon_(self):
        self._token(':')

    @graken()
    def _semicolon_(self):
        self._token(';')

    @graken()
    def _or_(self):
        with self._choice():
            with self._option():
                self._token('|')
            with self._option():
                self._token(';')
            self._error('expecting one of: ; |')

    @graken()
    def _oor_(self):
        with self._choice():
            with self._option():
                self._token(';;')
            with self._option():
                self._token('||')
            self._error('expecting one of: ;; ||')

    @graken()
    def _naf_(self):
        self._token('not ')

    @graken()
    def _cons_(self):
        self._token(':-')

    @graken()
    def _wcons_(self):
        self._token(':~')

    @graken()
    def _plus_(self):
        self._token('+')

    @graken()
    def _minus_(self):
        self._token('-')

    @graken()
    def _times_(self):
        self._token('*')

    @graken()
    def _div_(self):
        self._token('/')

    @graken()
    def _at_(self):
        self._token('@')

    @graken()
    def _paren_open_(self):
        self._token('(')

    @graken()
    def _paren_close_(self):
        self._token(')')

    @graken()
    def _square_open_(self):
        self._token('[')

    @graken()
    def _square_close_(self):
        self._token(']')

    @graken()
    def _curly_open_(self):
        self._token('{')

    @graken()
    def _curly_close_(self):
        self._token('}')

    @graken()
    def _equal_(self):
        self._token('=')

    @graken()
    def _unequal_(self):
        with self._choice():
            with self._option():
                self._token('<>')
            with self._option():
                self._token('!=')
            self._error('expecting one of: != <>')

    @graken()
    def _less_(self):
        self._token('<')

    @graken()
    def _greater_(self):
        self._token('>')

    @graken()
    def _less_or_eq_(self):
        self._token('<=')

    @graken()
    def _greater_or_eq_(self):
        self._token('>=')

    @graken()
    def _aggregate_count_(self):
        self._token('#count')

    @graken()
    def _aggregate_max_(self):
        self._token('#max')

    @graken()
    def _aggregate_min_(self):
        self._token('#min')

    @graken()
    def _aggregate_sumplus_(self):
        self._token('#sum+')

    @graken()
    def _aggregate_sum_(self):
        self._token('#sum')

    @graken()
    def _minimize_(self):
        with self._choice():
            with self._option():
                self._token('#minimize')
            with self._option():
                self._token('#minimise')
            self._error('expecting one of: #minimise #minimize')

    @graken()
    def _maximize_(self):
        with self._choice():
            with self._option():
                self._token('#maximize')
            with self._option():
                self._token('#maximise')
            self._error('expecting one of: #maximise #maximize')

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
