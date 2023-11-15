from itertools import product
import os

remove_chars = len(os.linesep)


OUT_DIR = 'samples/Languages'


def generateLanguage(rules=lambda _: True, sigma={'a', 'b'}, max_len=8, file_path=None):
    def kleene_star(sigma):
        yield []

        length = 1
        while True:
            for w in product(sigma, repeat=length):
                yield list(w)

            length += 1

    language = []

    for w in kleene_star(sigma):
        if len(w) > max_len:
            break

        if rules(w):
            language.append(w)

    if file_path is not None:
        with open(file_path, 'w') as f:
            for w in language:
                print(
                    ''.join((map(lambda w: w.replace('\\', '\\\\') if len(w) == 1 else f"\\{w}\\", w))),
                    file=f,
                )
            f.truncate(f.tell() - remove_chars)

    return language


def _count(w, s):
    count = 0

    for ss in w:
        if ss == s:
            count += 1

    return count


if __name__ == '__main__':
    generateLanguage(file_path=os.path.join(OUT_DIR, "abstar.txt"))
    generateLanguage(
        rules=lambda w: _count(w, '0') == _count(w, '1')
        and ('0' not in w[w.index('1') :] if '1' in w else True),
        sigma={'0', '1'},
        file_path=os.path.join(OUT_DIR, "0n1n.txt"),
    )
    generateLanguage(
        rules=lambda w: all([s == w[-(i + 1)] for i, s in enumerate(w)]),
        sigma={'0', '1'},
        file_path=os.path.join(OUT_DIR, "01palindrome.txt"),
    )
    generateLanguage(
        rules=lambda w: (
            _count(w, '\\') == 1 and
            (_count(w, 'a') > 0 or (_count(w, 'b') > 0)) and
            ('a' not in w[w.index('\\') :] and 'b' not in w[:w.index('\\')]
            if '\\' in w
            else False)
        ),
        sigma={'b', 'a', '\\'},
        file_path=os.path.join(OUT_DIR, "astarbstarlen1.txt"),
    )
