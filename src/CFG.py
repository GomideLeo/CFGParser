import string


class ContextFreeGrammar:
    separator_symbol = '\\'

    def __init__(self, V=set(), Sigma=set(), P=[], s: str = None):
        self.V = V
        self.Sigma = Sigma
        self.P = P
        self.s = s

    @classmethod
    def from_file(cls, in_file):
        cfg = ContextFreeGrammar(V=set(), Sigma=set(), P=[], s=None)

        with open(in_file) as g:
            while l := g.readline():
                v, w = l.split(':')
                w = w.strip()

                if cfg.s is None:
                    cfg.s = v

                cfg.addProduction(v, w, True)

        return cfg

    def __str__(self):
        sorted_V = sorted(self.V, key=lambda v: v if v != self.s else '')
        productions = '\n\t'.join(
            [
                f'{v} -> {" | ".join(map(lambda w: "".join(w), p))}'
                for v, p in filter(
                    lambda p: len(p[1]) > 0,
                    map(
                        lambda v: (
                            v,
                            list(
                                map(
                                    lambda p: p[1] if p[1] != [] else 'λ',
                                    filter(lambda p: p[0] == v, self.P),
                                )
                            ),
                        ),
                        sorted_V,
                    ),
                )
            ]
        )

        return f"""    V: {sorted_V}
    Σ: {sorted(self.Sigma)}
    s: {self.s}
    P:  {productions}"""

    def copy(self, copy_productions=True):
        return ContextFreeGrammar(
            set(self.V),
            set(self.Sigma),
            [(p[0], [*p[1]]) for p in self.P] if copy_productions else [],
            self.s,
        )

    def addProduction(self, v, w, remove_from_Sigma=False):
        if v in self.Sigma:
            if remove_from_Sigma:
                self.Sigma.remove(v)
            else:
                raise Exception(f"'{v}' is already part of the alphabet")

        if v not in self.V:
            self.V.add(v)

        split_w = ContextFreeGrammar._split_sentence(w)
        for s in split_w:
            if s not in self.V:
                self.Sigma.add(s)

        self.P.append((v, split_w))

    def _split_sentence(w):
        symbols = []
        sentence = w

        while (splitStart := sentence.find(ContextFreeGrammar.separator_symbol)) != -1:
            symbols = [*symbols, *[s for s in sentence[:splitStart]]]
            if (
                splitEnd := sentence.find(
                    ContextFreeGrammar.separator_symbol, splitStart + 1
                )
            ) == -1:
                raise Exception(
                    f'Invalid sentence {sentence} - separator does not end.'
                )

            if splitStart + 1 == splitEnd:
                symbols.append(ContextFreeGrammar.separator_symbol)
            else:
                symbols.append(sentence[splitStart + 1 : splitEnd])
            sentence = sentence[splitEnd + 1 :]

        symbols = [*symbols, *[s for s in sentence]]
        return symbols

    def _is_duplicate(production, Ps):
        for p in Ps:
            if (
                p[0] == production[0]
                and len(p[1]) == len(production[1])
                and all(map(lambda ss: ss[0] == ss[1], zip(p[1], production[1])))
            ):
                return True
        return False

    def remove_duplicate_productins(self):
        cfg = self.copy()

        cfg.P = list(
            map(
                lambda p: p[1],
                filter(
                    lambda p: not ContextFreeGrammar._is_duplicate(p[1], cfg.P[: p[0]]),
                    enumerate(cfg.P),
                ),
            )
        )

        return cfg

    # https://www.javatpoint.com/automata-simplification-of-cfg
    def remove_useless_productions(self):
        # Removal of Useless Symbols
        # if a symbol is not reached or it doesn't produce a sentence, remove it and its productions
        simplified_cfg = self.copy()

        final_symbols = set(simplified_cfg.Sigma)
        n_finals = 0
        while len(final_symbols) > n_finals:
            n_finals = len(final_symbols)
            # iterate through the productions while final_symbols doesnt change
            for p in simplified_cfg.P:
                if p[0] in final_symbols:
                    continue

                # if it generates all final symbols, it must be final
                if all(map(lambda s: s in final_symbols, p[1])):
                    final_symbols.add(p[0])

        # filter only useful productions
        simplified_cfg.P = list(
            filter(
                lambda p: all(map(lambda s: s in final_symbols, p[1])), simplified_cfg.P
            )
        )

        used_symbols = set([simplified_cfg.s])
        explore_queue = [simplified_cfg.s]
        while len(explore_queue) > 0:
            v = explore_queue.pop(0)
            P = filter(lambda p: p[0] == v, simplified_cfg.P)

            for p in P:
                for s in p[1]:
                    if s in simplified_cfg.V and s not in used_symbols:
                        used_symbols.add(s)
                        explore_queue.append(s)

            # all symbols found
            if len(used_symbols) == len(simplified_cfg.V):
                break

        simplified_cfg.P = list(
            filter(lambda p: p[0] in used_symbols, simplified_cfg.P)
        )
        simplified_cfg.V = used_symbols

        used_alphabet = set()
        for p in simplified_cfg.P:
            for s in filter(
                lambda s: s not in used_alphabet and s in simplified_cfg.Sigma, p[1]
            ):
                used_alphabet.add(s)
        simplified_cfg.Sigma = used_alphabet

        return simplified_cfg

    def remove_lambda_productions(self):
        cfg = self.copy()

        while (
            len(
                lambda_vars := set(
                    map(
                        lambda p: p[0],
                        filter(lambda p: len(p[1]) == 0 and p[0] != cfg.s, cfg.P),
                    )
                )
            )
            > 0
        ):
            non_lambda = list(filter(lambda p: len(p[1]) > 0, cfg.P))

            for p in non_lambda:
                for i, s in enumerate(p[1]):
                    if s in lambda_vars:
                        new_p = (p[0], [*p[1][:i], *p[1][i + 1 :]])
                        if not ContextFreeGrammar._is_duplicate(new_p, non_lambda):
                            non_lambda.append(new_p)

            cfg.P = non_lambda

        return cfg

    def remove_unit_productions(self):
        cfg = self.copy()

        while unit_p := next(
            (p for p in cfg.P if len(p[1]) == 1 and p[1][0] in cfg.V), False
        ):
            unit_v = unit_p[0]
            generated_v = unit_p[1][0]

            cfg.P = list(
                filter(
                    lambda p: not (
                        p[0] == unit_v and len(p[1]) == 1 and p[1][0] == generated_v
                    ),
                    cfg.P,
                )
            )
            for p in cfg.P:
                if p[0] == generated_v:
                    new_p = (unit_v, p[1])
                    if not ContextFreeGrammar._is_duplicate(new_p, cfg.P):
                        cfg.P.append(new_p)

        return cfg

    def add_new_start(self, start_v='S'):
        def suffix_generator():
            yield ''
            yield "'"

            n = 1
            while True:
                yield str(n)
                n += 1

        cfg = self.copy()
        generator = suffix_generator()

        for suffix in generator:
            new_s = start_v + suffix
            if new_s not in cfg.V and new_s not in cfg.Sigma:
                cfg.P.append((new_s, [cfg.s]))
                cfg.V.add(new_s)
                cfg.s = new_s
                return cfg

    # remove productions with more than one terminal variables or mixed terminals and non-terminals
    def add_terminal_productions(self, possible_Vs: list = None):
        def suffix_generator():
            yield ''
            yield "'"

            n = 1
            while True:
                yield str(n)
                n += 1

        def V_generator(possible_Vs):
            if possible_Vs is not None:
                Vs = possible_Vs
            else:
                Vs = list(string.ascii_uppercase)
                Vs.reverse()

            for suffix in suffix_generator():
                for v in Vs:
                    yield v + suffix

        generator = V_generator(possible_Vs)
        cfg = self.copy()
        terminal_productions = list(
            filter(
                lambda p: len(p[1]) == 1
                and p[1][0] in cfg.Sigma
                and len(list(filter(lambda q: q[0] == p[0], cfg.P))) == 1,
                cfg.P,
            )
        )

        for p in cfg.P:
            if len(p[1]) > 1:
                for i, s in enumerate(p[1]):
                    if s in self.Sigma:
                        if not (
                            terminal_p := next(
                                (p for p in terminal_productions if p[1][0] == s), False
                            )
                        ):
                            for new_v in generator:
                                if new_v not in cfg.V and new_v not in cfg.Sigma:
                                    terminal_p = (new_v, [s])
                                    cfg.P.append(terminal_p)
                                    terminal_productions.append(terminal_p)
                                    cfg.V.add(new_v)
                                    break
                        p[1][i] = terminal_p[0]

        return cfg

    def remove_long_productions(self, possible_Vs: list = None):
        def suffix_generator():
            yield ''
            yield "'"

            n = 1
            while True:
                yield str(n)
                n += 1

        def V_generator(possible_Vs):
            if possible_Vs is not None:
                Vs = possible_Vs
            else:
                Vs = list(string.ascii_uppercase)
                Vs.reverse()

            for suffix in suffix_generator():
                for v in Vs:
                    yield v + suffix

        generator = V_generator(possible_Vs)
        cfg = self.copy()
        short_productions = []

        while long_p := next((p for p in enumerate(cfg.P) if len(p[1][1]) > 2), False):
            i, p = long_p
            while len(p[1]) > 2:
                substitute_vars = p[1][-2:]
                if not (
                    short_p := next(
                        (
                            sp
                            for sp in short_productions
                            if sp[1][0] == substitute_vars[0]
                            and sp[1][1] == substitute_vars[1]
                        ),
                        False,
                    )
                ):
                    for new_v in generator:
                        if new_v not in cfg.V and new_v not in cfg.Sigma:
                            short_p = (new_v, substitute_vars)
                            cfg.P.append(short_p)
                            short_productions.append(short_p)
                            cfg.V.add(new_v)
                            break
                p = (p[0], [*p[1][:-2], short_p[0]])
            cfg.P[i] = p

        return cfg
