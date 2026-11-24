"""Shared text normalisation and word alignment, used by both WER and the diff guard.

Normalisation drops what the fair copy is allowed to change freely: case, punctuation
(including ¿ ¡ « » — …), and line/paragraph breaks. It keeps accents and ñ, because
"esta" vs "está" is a different word.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher


def normalize_words(text: str) -> list[str]:
    text = unicodedata.normalize("NFC", text).lower()
    out = []
    for ch in text:
        cat = unicodedata.category(ch)
        # P* = punctuation (incl. rayas, guiones, comillas), S* = symbols.
        out.append(" " if cat[0] in "PS" else ch)
    return "".join(out).split()


@dataclass
class Op:
    kind: str  # "equal" | "sub" | "ins" | "del"
    ref: list[str]  # words on the reference / raw side
    hyp: list[str]  # words on the hypothesis / cleaned side
    ref_pos: int  # index of the first ref word (for context)


def _dp_align(ref: list[str], hyp: list[str], ref_offset: int) -> list[Op]:
    """Minimal word edit distance with backtrace, for small regions."""
    n, m = len(ref), len(hyp)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        d[i][0] = i
    for j in range(m + 1):
        d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if ref[i - 1] == hyp[j - 1] else 1
            d[i][j] = min(d[i - 1][j - 1] + cost, d[i - 1][j] + 1, d[i][j - 1] + 1)
    ops: list[Op] = []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and d[i][j] == d[i - 1][j - 1] + (ref[i - 1] != hyp[j - 1]):
            kind = "equal" if ref[i - 1] == hyp[j - 1] else "sub"
            ops.append(Op(kind, [ref[i - 1]], [hyp[j - 1]], ref_offset + i - 1))
            i, j = i - 1, j - 1
        elif i > 0 and d[i][j] == d[i - 1][j] + 1:
            ops.append(Op("del", [ref[i - 1]], [], ref_offset + i - 1))
            i -= 1
        else:
            ops.append(Op("ins", [], [hyp[j - 1]], ref_offset + i))
            j -= 1
    return ops[::-1]


def align(ref: list[str], hyp: list[str]) -> list[Op]:
    """Word alignment: difflib finds long matching runs cheaply, exact DP resolves the gaps.
    Returns one Op per word (equal/sub/ins/del), in order."""
    ops: list[Op] = []
    matcher = SequenceMatcher(a=ref, b=hyp, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            ops.extend(Op("equal", [ref[i]], [hyp[j1 + k]], i) for k, i in enumerate(range(i1, i2)))
        elif tag == "delete":
            ops.extend(Op("del", [ref[i]], [], i) for i in range(i1, i2))
        elif tag == "insert":
            ops.extend(Op("ins", [], [hyp[j]], i1) for j in range(j1, j2))
        else:
            ops.extend(_dp_align(ref[i1:i2], hyp[j1:j2], i1))
    return ops
