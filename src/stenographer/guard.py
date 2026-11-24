"""The diff guard: checks a fair copy against the raw transcript, word by word.

The stenographer may change punctuation, case, paragraphing and dialogue layout freely
(those vanish under normalisation), and may drop pure hesitations ("eh", "mmm") and
immediate stutter repeats ("el el perro"). Every other change to the words is a violation:
it is listed for the author, and if violations exceed the budget the copy is rejected.
Prompts alone do not stop an LLM drifting from the author's voice; this check does.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .textnorm import Op, align, normalize_words

# Only non-lexical hesitations. Words like "este", "pues", "bueno", "o sea", "ah" are left out
# on purpose: in literary prose and dialogue they can be the author's words.
DEFAULT_FILLERS = frozenset({"eh", "ehm", "em", "emm", "mm", "mmm", "hm", "hmm", "mhm", "ehh"})


@dataclass
class Change:
    kind: str  # "filler" | "repeat" (allowed) | "accent" | "sub" | "del" | "ins" (violations)
    raw: str
    clean: str
    context: str

    @property
    def allowed(self) -> bool:
        return self.kind in ("filler", "repeat")


@dataclass
class GuardResult:
    raw_words: int
    changes: list[Change] = field(default_factory=list)
    max_rate: float = 0.0

    @property
    def violations(self) -> list[Change]:
        return [c for c in self.changes if not c.allowed]

    @property
    def rate(self) -> float:
        return len(self.violations) / self.raw_words if self.raw_words else 0.0

    @property
    def passed(self) -> bool:
        return self.rate <= self.max_rate


def _strip_accents(word: str) -> str:
    import unicodedata

    return "".join(c for c in unicodedata.normalize("NFD", word)
                   if unicodedata.category(c) != "Mn")


def _context(words: list[str], pos: int, width: int = 5) -> str:
    left = " ".join(words[max(0, pos - width):pos])
    right = " ".join(words[pos:pos + width])
    return f"…{left} ⟨{right}…"


def check(raw: str, clean: str, max_rate: float = 0.0,
          fillers: frozenset[str] = DEFAULT_FILLERS) -> GuardResult:
    raw_w, clean_w = normalize_words(raw), normalize_words(clean)
    result = GuardResult(raw_words=len(raw_w), max_rate=max_rate)
    for op in align(raw_w, clean_w):
        if op.kind == "equal":
            continue
        result.changes.append(_classify(op, raw_w, fillers))
    return result


def _classify(op: Op, raw_w: list[str], fillers: frozenset[str]) -> Change:
    raw_word = " ".join(op.ref)
    clean_word = " ".join(op.hyp)
    ctx = _context(raw_w, op.ref_pos)
    if op.kind == "del":
        word, pos = op.ref[0], op.ref_pos
        if word in fillers:
            return Change("filler", raw_word, "", ctx)
        neighbours = raw_w[pos - 1:pos] + raw_w[pos + 1:pos + 2]
        if word in neighbours:
            return Change("repeat", raw_word, "", ctx)
        return Change("del", raw_word, "", ctx)
    if op.kind == "sub" and _strip_accents(op.ref[0]) == _strip_accents(op.hyp[0]):
        return Change("accent", raw_word, clean_word, ctx)
    return Change(op.kind, raw_word, clean_word, ctx)


def format_report(result: GuardResult) -> str:
    verdict = "PASS" if result.passed else "REJECT"
    allowed = len(result.changes) - len(result.violations)
    lines = [
        f"{verdict}: {len(result.violations)} word changes / {result.raw_words} raw words "
        f"= {result.rate:.2%} (budget {result.max_rate:.2%}); {allowed} allowed removals",
    ]
    labels = {"sub": "changed", "del": "dropped", "ins": "added", "accent": "accent",
              "filler": "filler", "repeat": "repeat"}
    for c in result.changes:
        mark = " " if c.allowed else "!"
        edit = f"{c.raw or '∅'} → {c.clean or '∅'}"
        lines.append(f" {mark} {labels[c.kind]:8s} {edit:30s} {c.context}")
    return "\n".join(lines)
