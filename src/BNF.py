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
        cls,
        cfg: ContextFreeGrammar,
        remove_useless=True,
        always_add_start=False,
        remove_lambdas=False,
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

        if remove_lambdas:
            chomsky_cfg = chomsky_cfg.remove_lambda_productions()
        # chomsky_cfg = chomsky_cfg.remove_unit_productions()
        # chomsky_cfg = chomsky_cfg.add_terminal_productions()
        chomsky_cfg = chomsky_cfg.remove_long_productions()

        return cls(
            set(chomsky_cfg.V),
            set(chomsky_cfg.Sigma),
            [(p[0], [*p[1]]) for p in chomsky_cfg.P],
            chomsky_cfg.s,
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
