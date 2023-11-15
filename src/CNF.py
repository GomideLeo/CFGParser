import string
from CFG import ContextFreeGrammar


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

        return ChomskyNormalForm(
            set(chomsky_cfg.V),
            set(chomsky_cfg.Sigma),
            [(p[0], [*p[1]]) for p in chomsky_cfg.P],
            chomsky_cfg.s,
        )

    def is_in_grammar(self, w: list):
        # check if word is in alphabet
        if any(map(lambda s: s not in self.Sigma, w)):
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
