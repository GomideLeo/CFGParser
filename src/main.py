from CFG import ContextFreeGrammar
from CNF import ChomskyNormalForm
from BNF import BinaryNormalForm

import glob
import time
import os

PRINT_ACCEPTED_LANGUAGES = False
GRAMMARS_DIR = './samples/Grammars'
LANGAGES_DIR = './samples/Languages'
OUT_DIR = './test'

print('Testing CNF Parsing')

t0 = time.time()
for g in glob.glob(os.path.join(GRAMMARS_DIR, '*.txt')):
    cfg = ContextFreeGrammar.from_file(g)
    cnf = ChomskyNormalForm.from_CFG(cfg)
    g_name = g.split('\\')[-1].split('.')[0]

    if PRINT_ACCEPTED_LANGUAGES:
        print(f'\nResults for {g_name}:')

    for l in glob.glob(os.path.join(LANGAGES_DIR, '*.txt')):
        l_name = l.split('\\')[-1].split('.')[0]
        accepted = cnf.check_language(
            l, print_out=os.path.join(OUT_DIR, 'CNF', g_name, f'{l_name}.txt')
        )

        if PRINT_ACCEPTED_LANGUAGES:
            print('\t', l_name, ':', 'accepted' if accepted else 'rejected')

t1 = time.time()

total = t1 - t0
print(
    f'Total time to convert grammars and parse sentences: {total:4f}s',
    end='\n\n====================\n',
)

print('Testing BNF Parsing')

t0 = time.time()
for g in glob.glob(os.path.join(GRAMMARS_DIR, '*.txt')):
    cfg = ContextFreeGrammar.from_file(g)
    bnf = BinaryNormalForm.from_CFG(cfg)
    g_name = g.split('\\')[-1].split('.')[0]

    if PRINT_ACCEPTED_LANGUAGES:
        print(f'\nResults for {g_name}:')
    for l in glob.glob(os.path.join(LANGAGES_DIR, '*.txt')):
        l_name = l.split('\\')[-1].split('.')[0]
        accepted = bnf.check_language(
            l, print_out=os.path.join(OUT_DIR, 'BNF', g_name, f'{l_name}.txt')
        )

        if PRINT_ACCEPTED_LANGUAGES:
            print('\t', l_name, ':', 'accepted' if accepted else 'rejected')

t1 = time.time()

total = t1 - t0
print(f'Total time to convert grammars and parse sentences: {total:4f}s')
