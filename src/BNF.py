import string
from CFG import ContextFreeGrammar


class BinaryNormalForm(ContextFreeGrammar):
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
        # chomsky_cfg = chomsky_cfg.remove_unit_productions()
        # chomsky_cfg = chomsky_cfg.add_terminal_productions()
        chomsky_cfg = chomsky_cfg.remove_long_productions()

        return BinaryNormalForm(
            set(chomsky_cfg.V),
            set(chomsky_cfg.Sigma),
            [(p[0], [*p[1]]) for p in chomsky_cfg.P],
            chomsky_cfg.s,
        )
