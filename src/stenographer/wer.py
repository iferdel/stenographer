"""Word error rate for the engine bake-off.

WER ignores case and punctuation (as published benchmarks do). Punctuation, dialogue rayas
and names still need checking by eye; the error list printed here helps with the names.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .textnorm import Op, align, normalize_words


@dataclass
class WerResult:
    ref_words: int
    substitutions: int
    deletions: int
    insertions: int
    ops: list[Op]

    @property
    def errors(self) -> int:
        return self.substitutions + self.deletions + self.insertions

    @property
    def wer(self) -> float:
        return self.errors / self.ref_words if self.ref_words else 0.0


def compute_wer(reference: str, hypothesis: str) -> WerResult:
    ref, hyp = normalize_words(reference), normalize_words(hypothesis)
    ops = align(ref, hyp)
    counts = Counter(op.kind for op in ops)
    return WerResult(len(ref), counts["sub"], counts["del"], counts["ins"], ops)


def format_report(result: WerResult, top: int = 30) -> str:
    lines = [
        f"WER {result.wer:.2%}  ({result.errors} errors / {result.ref_words} reference words)",
        f"  substitutions {result.substitutions}, deletions {result.deletions}, "
        f"insertions {result.insertions}",
    ]
    confusions = Counter(
        f"{' '.join(op.ref) or '∅'} → {' '.join(op.hyp) or '∅'}"
        for op in result.ops if op.kind != "equal"
    )
    if confusions:
        lines.append(f"Most frequent errors (reference → heard), top {top}:")
        lines += [f"  {n:3d} × {pair}" for pair, n in confusions.most_common(top)]
    return "\n".join(lines)
