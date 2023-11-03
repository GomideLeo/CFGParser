class ContextFreeGrammar():
    separator_symbol = "\\"

    def __init__(self, V=set(), Sigma=set(),  P=[], S:str=None):
        self.V = V
        self.Sigma = Sigma
        self.P = P
        self.S = S

    @classmethod
    def from_file(cls, in_file):
        cfg = cls()

        with open(in_file) as g:
            while l:=g.readline():
                v, w = l.split(':')
                w = w.strip()

                if cfg.S is None:
                    cfg.S = v
                
                cfg.addProduction(v, w, True)
        
        return cfg


    def __str__(self):
        productions = '\n\t'.join([f'{v} -> {" | ".join(map(lambda w: "".join(w), p))}' for v, p in filter(lambda p: len(p[1]) > 0, map(lambda v: (v, list(map(lambda p: p[1] if p[1] != [] else 'λ', filter(lambda p: p[0] == v, self.P)))), self.V))])
        return f"""    V: {self.V}
    Σ: {self.Sigma}
    S: {self.S}
    P:  {productions}"""

    def copy(self, copy_productions=True):
        return ContextFreeGrammar(self.V, self.Sigma, self.P if copy_productions else [], self.S)

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
            if (splitEnd := sentence.find(ContextFreeGrammar.separator_symbol, splitStart+1)) == -1:
                raise Exception(f'Invalid sentence {sentence} - separator does not end.')
            
            if (splitStart+1 == splitEnd):
                symbols.append(ContextFreeGrammar.separator_symbol)
            else:
                symbols.append(sentence[splitStart+1:splitEnd])
            sentence = sentence[splitEnd+1:]

        symbols = [*symbols, *[s for s in sentence]]
        return symbols

    def chomskyfy(self):
        chomsky_cfg = self.copy(False)
        return chomsky_cfg






