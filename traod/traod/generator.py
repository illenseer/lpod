from __future__ import (print_function, division, absolute_import,
                        unicode_literals)


def generate_prog(ast, backend, generator, strategy):
    """
    Generate logic program from AST corresponding to backend, generator and
    strategy.
    """
    if generator == 'split':
        return generate_split(ast, backend, strategy)
    elif generator == 'cabalar':
        return generate_cabalar(ast, backend, strategy)


def generate_split(ast, backend, strategy):
    """
    Generate program with with split programs via choice rules.
    """
    stmts = []
    od_count = 0
    max_deg_count = 0

    for statement in ast.statements:
        additional_rules = []

        if statement.body:
            body = ''.join(statement.body)
        else:
            body = ''

        if statement.head:
            if statement.head.ordered_disjunction:
                od_count += 1
                deg_count = 0
                ods = ''.join(statement.head.ordered_disjunction).split(';;')
                choice = ''
                sat_choice = ''
                ld_el = ''

                if backend == 'asprin':
                    ar = 'od_body({nr}){body}.'.format(
                        nr=od_count,
                        body=':-' + body if statement.body else ''
                    )
                    additional_rules.append(ar)
                    ar = 'od_atoms({nr},1):-not od_body({nr}).'.format(nr=od_count)
                    additional_rules.append(ar)

                for od in ods:
                    deg_count += 1
                    if deg_count > max_deg_count:
                        max_deg_count = deg_count
                    choice_el = 'od_atoms({r},{d})'.format(
                        r=od_count,
                        d=deg_count
                    )
                    if deg_count != 1:
                        choice += ';'
                        sat_choice += ','
                    choice += choice_el
                    sat_choice += 'not {ch}'.format(ch=choice_el)
                    ar = '{od}:-{ch}{ld}{body}'.format(
                        od=od,
                        ch=choice_el,
                        ld=ld_el,
                        body=',' + body + '.' if statement.body else '.'
                    )
                    additional_rules.append(ar)
                    arc = ':-not {ch},{od}{ld}{body}'.format(
                        ch=choice_el,
                        od=od,
                        ld=ld_el,
                        body=',' + body + '.' if statement.body else '.'
                    )
                    additional_rules.append(arc)
                    ld_el += ',not {}'.format(od)
                head = '{{{choice}}}=1'.format(choice=choice)
                satisfied = 'satisfied({nr},1):-{sc}.'.format(
                    nr=od_count,
                    sc=sat_choice
                )
                additional_rules.append(satisfied)
            elif statement.head.atom:
                head = ''.join(statement.head.atom)
            elif statement.head.choice:
                head = ''.join(statement.head.choice)
        else:
            head=''

        if head or body:
            stmt = '{head}{body}.'.format(
                head=head,
                body=':-' + body if statement.body else ''
            )
            stmts.append(stmt)

        for rule in additional_rules:
            stmts.append(rule)

    generic_satisfied = 'satisfied(R,D):-od_atoms(R,D).'
    stmts.append(generic_satisfied)

    if backend == 'metalpod':
        stmts.append('optimize({}).'.format(strategy))
    elif backend == 'asprin':
        asprin_stmts = generate_asprin_preference_spec(
            strategy,
            od_count,
            max_deg_count
        )
        stmts += asprin_stmts

    return '\n'.join(stmts)


def generate_cabalar(ast, backend, strategy):
    """
    Generate program with with Cabalar translation for ordered disjunctions.
    """
    stmts = []
    od_count = 0
    max_deg_count = 0

    for statement in ast.statements:
        additional_rules = []

        if statement.body:
            body = ''.join(statement.body)
        else:
            body = ''

        if statement.head:
            if statement.head.ordered_disjunction:
                od_count += 1
                deg_count = 0
                ods = ''.join(statement.head.ordered_disjunction).split(';;')
                head = ''
                ld_el = ''

                ar = 'od_body({nr}){body}.'.format(
                    nr=od_count,
                    body=':-' + body if statement.body else ''
                )
                additional_rules.append(ar)
                ar = 'satisfied({nr},1):-not od_body({nr}).'.format(nr=od_count)
                additional_rules.append(ar)

                for od in ods:
                    deg_count += 1
                    if deg_count > max_deg_count:
                        max_deg_count = deg_count
                    od_atom = 'satisfied({r},{d})'.format(
                        r=od_count,
                        d=deg_count
                    )
                    ar = '{od}:-not not {od}{ld}{body}'.format(
                        od=od,
                        ld=ld_el,
                        body=',' + body + '.' if statement.body else '.'
                    )
                    additional_rules.append(ar)
                    ar = '{od_atom}:-not not {od}{ld}{body}'.format(
                        od_atom=od_atom,
                        od=od,
                        ld=ld_el,
                        body=',' + body + '.' if statement.body else '.'
                    )
                    additional_rules.append(ar)
                    ld_el += ',not {}'.format(od)
                if not body:
                    ld_el = ld_el[1:]
                ar = ':-{body}{ld}.'.format(body=body,ld=ld_el)
                additional_rules.append(ar)
                body = ''
            elif statement.head.atom:
                head = ''.join(statement.head.atom)
            elif statement.head.choice:
                head = ''.join(statement.head.choice)
        else:
            head=''

        if head or body:
            stmt = '{head}{body}.'.format(
                head=head,
                body=':-' + body if statement.body else ''
            )
            stmts.append(stmt)

        for rule in additional_rules:
            stmts.append(rule)

    if backend == 'metalpod':
        stmts.append('optimize({}).'.format(strategy))
    elif backend == 'asprin':
        asprin_stmts = generate_asprin_preference_spec(
            strategy,
            od_count,
            max_deg_count
        )
        stmts += asprin_stmts


    return '\n'.join(stmts)


def generate_asprin_preference_spec(strategy, od_count, deg_count):
    """
    Generate preference rules for asprin.
    """
    stmts = []

    stmts.append('rule(1..{}).'.format(od_count))
    stmts.append('deg(1..{}).'.format(deg_count))

    pareto_per_rule_tmpl = (
        '#preference(od{nr},less(weight))'
        '{{D,{nr}::satisfied({nr},D):deg(D)}}.'
    )
    pareto_combine_tmpl = (
        '#preference(all,pareto){{{rules}}}.\n'
        '#optimize(all).'
    )
    incl_per_deg_tmpl = (
        '#preference(od{nr},superset)'
        '{{satisfied(R,{nr}):rule(R)}}.'
    )
    incl_card_combine_tmpl = (
        '#preference(all,lexico){{{rules}}}.\n'
        '#optimize(all).'
    )
    card_per_deg_tmpl = (
        '#preference(od{nr},more(cardinality))'
        '{{satisfied(R,{nr}):rule(R)}}.'
    )

    if strategy == 'pareto':
        combine_names = ''
        for od in range(1, od_count + 1):
            stmts.append(pareto_per_rule_tmpl.format(nr=od))
            if od > 1:
                combine_names += ';'
            combine_names += 'name(od{nr})'.format(nr=od)
        stmts.append(pareto_combine_tmpl.format(rules=combine_names))

    elif strategy == 'incl':
        combine_names = ''
        for deg in range(1, deg_count + 1):
            inv_deg = deg_count - deg + 1
            stmts.append(incl_per_deg_tmpl.format(nr=deg))
            if deg > 1:
                combine_names += ';'
            combine_names += '{inv}::name(od{nr})'.format(inv=inv_deg, nr=deg)
        stmts.append(incl_card_combine_tmpl.format(rules=combine_names))

    elif strategy == 'card':
        combine_names = ''
        for deg in range(1, deg_count + 1):
            inv_deg = deg_count - deg + 1
            stmts.append(card_per_deg_tmpl.format(nr=deg))
            if deg > 1:
                combine_names += ';'
            combine_names += '{inv}::name(od{nr})'.format(inv=inv_deg, nr=deg)
        stmts.append(incl_card_combine_tmpl.format(rules=combine_names))

    return stmts
