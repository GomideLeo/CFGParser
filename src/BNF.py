import sys
from CFG import ContextFreeGrammar


class BinaryNormalForm(ContextFreeGrammar):
    def __init__(self, V=set(), Sigma=set(), P=[], s: str = None):
        self.V = V
        self.Sigma = Sigma
        self.P = P
        self.s = s

    @classmethod
    def from_CFG(
        cls,
        cfg: ContextFreeGrammar,
        remove_useless=True,
        always_add_start=False,
        remove_lambdas=False,
    ):
        # https://www.javatpoint.com/automata-simplification-of-cfg
        binary_cfg = cfg.copy()

        if remove_useless:
            binary_cfg = binary_cfg.remove_duplicate_productins()
            binary_cfg = binary_cfg.remove_useless_productions()

        if always_add_start:
            binary_cfg = binary_cfg.add_new_start()

        if remove_lambdas:
            binary_cfg = binary_cfg.remove_lambda_productions()

        binary_cfg = binary_cfg.remove_long_productions()

        return cls(
            set(binary_cfg.V),
            set(binary_cfg.Sigma),
            [(p[0], [*p[1]]) for p in binary_cfg.P],
            binary_cfg.s,
        )

    def find_nullable(self):
        nullable = set()
        todo = set()
        occurs = {v: set() for v in self.V}

        for p in filter(lambda p: len(p[1]) == 1 and p[1][0] in self.V, self.P):
            occurs[p[1][0]].add((p[0]))

        for p in filter(
            lambda p: len(p[1]) == 2 and p[1][0] in self.V and p[1][1] in self.V, self.P
        ):
            occurs[p[1][0]].add((p[0], p[1][1]))
            occurs[p[1][1]].add((p[0], p[1][0]))

        for p in filter(lambda p: len(p[1]) == 0, self.P):
            nullable.add(p[0])
            todo.add(p[0])

        while len(todo) > 0:
            B = todo.pop()
            for o in filter(
                lambda o: len(o) == 1 or len(o) == 2 and o[1] in nullable, occurs[B]
            ):
                if o[0] not in nullable:
                    nullable.add(o[0])
                    todo.add(o[0])

        return nullable

    def find_unit_relation(self):
        nullable = self.find_nullable()
        unit_relation = {v: set() for v in self.V}

        for p in self.P:
            if len(p[1]) == 1:
                unit_relation[p[0]].add(p[1][0])
            elif len(p[1]) == 2:
                if p[1][0] in nullable:
                    unit_relation[p[0]].add(p[1][1])
                if p[1][1] in nullable:
                    unit_relation[p[0]].add(p[1][0])

        return unit_relation

    def find_inverse_unit_relation(self):
        unit_relation = self.find_unit_relation()
        inverse_unit_relation = {v: set() for v in [*self.V, *self.Sigma]}

        for y in unit_relation:
            for A in unit_relation[y]:
                inverse_unit_relation[A].add(y)

        return inverse_unit_relation

    def is_in_language(self, w: list):
        # check if word is in alphabet
        if any(map(lambda s: s not in self.Sigma, w)):
            return False

        # Check if lambda is in language
        if len(w) == 0:
            if any(map(lambda p: p[0] == self.s and len(p[1]) == 0, self.P)):
                return True
            else:
                return False

        Ug = self.find_inverse_unit_relation()

        T = [[None for _ in w] for _ in w]
        Tprime = [[None for _ in w] for _ in w]
        n = len(w)

        for i, s in enumerate(w):
            T[i][i] = set(Ug[s])

        for j in range(1, n):
            for i in reversed(range(j)):
                Tprime[i][j] = set()
                for h in range(i, j):
                    for p in filter(lambda p: len(p[1]) == 2, self.P):
                        A = p[0]
                        y = p[1][0]
                        z = p[1][1]
                        if (y in T[i][h] or y in set(*[Ug[s] for s in T[i][h]])) and (
                            z in T[h + 1][j] or z in set(*[Ug[s] for s in T[h + 1][j]])
                        ):
                            Tprime[i][j].add(A)
                T[i][j] = set()
                for t in Tprime[i][j]:
                    for s in Ug[t]:
                        T[i][j].add(s)

        return self.s in T[0][n - 1]

    def check_language(self, in_language_path, print_out=True):
        language_in_grammar = True
        print_values = True

        out_f = sys.stdout
        if type(print_out) == str:
            out_f = open(print_out, 'w')
        elif not print_out:
            print_values = False

        with open(in_language_path, 'r') as in_file:
            while w := in_file.readline():
                w = w.strip()

                split_w = ContextFreeGrammar._split_sentence(w)
                w_in_self = self.is_in_grammar(split_w)
                language_in_grammar = language_in_grammar and w_in_self

                if not language_in_grammar and not print_values:
                    return language_in_grammar
                else:
                    print(f'{w if len(w) > 0 else "λ"}:{w_in_self}', file=out_f)

        if type(print_out) == str:
            out_f.close()

        return language_in_grammar
