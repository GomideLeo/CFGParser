class ContextFreeGrammar():
    separator_symbol = "\\"

    def __init__(self, V=set(), Sigma=set(),  P=[], s:str=None):
        self.V = V
        self.Sigma = Sigma
        self.P = P
        self.s = s

    @classmethod
    def from_file(cls, in_file):
        cfg = cls(V=set(), Sigma=set(),  P=[], s=None)

        with open(in_file) as g:
            while l:=g.readline():
                v, w = l.split(':')
                w = w.strip()

                if cfg.s is None:
                    cfg.s = v
                
                cfg.addProduction(v, w, True)
        
        return cfg


    def __str__(self):
        sorted_V = sorted(self.V, key=lambda v: v if v != self.s else "")
        productions = '\n\t'.join([f'{v} -> {" | ".join(map(lambda w: "".join(w), p))}' for v, p in filter(lambda p: len(p[1]) > 0, map(lambda v: (v, list(map(lambda p: p[1] if p[1] != [] else 'λ', filter(lambda p: p[0] == v, self.P)))), sorted_V))])
        return f"""    V: {sorted_V}
    Σ: {sorted(self.Sigma)}
    s: {self.s}
    P:  {productions}"""

    def copy(self, copy_productions=True):
        return ContextFreeGrammar(self.V, self.Sigma, self.P if copy_productions else set(), self.s)

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
        simplified_cfg.P = list(filter(lambda p: all(map(lambda s: s in final_symbols, p[1])), simplified_cfg.P))

        used_symbols = set(simplified_cfg.s)
        explore_queue = [simplified_cfg.s]
        while len(explore_queue) > 0:
            v = explore_queue.pop(0)
            P = filter(lambda p: p[0] == v, simplified_cfg.P)

            for p in P:
                for s in p[1]:
                    if s in simplified_cfg.V and s not in used_symbols:
                        used_symbols.add(s)

            # all symbols found
            if len(used_symbols) == len(simplified_cfg.V):
                break
        
        simplified_cfg.P = list(filter(lambda p: p[0] in used_symbols, simplified_cfg.P))
        simplified_cfg.V = used_symbols

        used_alphabet = set()
        for p in simplified_cfg.P:
            for s in filter(lambda s: s not in used_alphabet and s in simplified_cfg.Sigma, p[1]):
                used_alphabet.add(s)
        simplified_cfg.Sigma = used_alphabet

        return simplified_cfg


    def chomskyfy(self):
        # https://www.javatpoint.com/automata-chomskys-normal-form
        chomsky_cfg = self.remove_useless_productions()

        return chomsky_cfg






