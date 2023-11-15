import string
from CFG import ContextFreeGrammar
import sys


class ChomskyNormalForm(ContextFreeGrammar):
    def __init__(self, V=set(), Sigma=set(), P=[], s: str = None):
        self.V = V
        self.Sigma = Sigma
        self.P = P
        self.s = s

    @classmethod
    def from_CFG(
        cls, cfg: ContextFreeGrammar, remove_useless=True, always_add_start=False
    ):
        # https://www.javatpoint.com/automata-simplification-of-cfg
        chomsky_cfg = cfg.copy()

        if remove_useless:
            chomsky_cfg = chomsky_cfg.remove_duplicate_productins()
            chomsky_cfg = chomsky_cfg.remove_useless_productions()

        # only add new start if it is in the RHS
        if always_add_start:
            chomsky_cfg = chomsky_cfg.add_new_start()
        else:
            for p in chomsky_cfg.P:
                if any(map(lambda s: s == chomsky_cfg.s, p[1])):
                    chomsky_cfg = chomsky_cfg.add_new_start()
                    break

        chomsky_cfg = chomsky_cfg.remove_lambda_productions()
        chomsky_cfg = chomsky_cfg.remove_unit_productions()
        chomsky_cfg = chomsky_cfg.add_terminal_productions()
        chomsky_cfg = chomsky_cfg.remove_long_productions()

        return cls(
            set(chomsky_cfg.V),
            set(chomsky_cfg.Sigma),
            [(p[0], [*p[1]]) for p in chomsky_cfg.P],
            chomsky_cfg.s,
        )

    def is_in_grammar(self, w: list):
        # check if word is in alphabet
        if any(map(lambda s: s not in self.Sigma, w)):
            return False
        
        if len(w) == 0:
            if any(map(lambda p: p[0] == self.s and len(p[1])==0, self.P)):
                return True
            else:
                return False

        T = [[[] for _ in w] for _ in w]
        n = len(w)

        for i, s in enumerate(w):
            for p in filter(lambda p: len(p[1]) == 1 and p[1][0] == s, self.P):
                T[i][i].append(p)

        for j in range(1, n):
            for i in reversed(range(j)):
                for h in range(i, j):
                    for p in filter(lambda p: len(p[1]) == 2, self.P):
                        b = p[1][0]
                        c = p[1][1]
                        if b in set(map(lambda p: p[0], T[i][h])) and c in set(
                            map(lambda p: p[0], T[h + 1][j])
                        ):
                            T[i][j].append(p)

        return self.s in set(map(lambda p: p[0], T[0][n - 1]))

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