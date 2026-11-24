from stenographer.textnorm import normalize_words
from stenographer.wer import compute_wer


def test_normalisation_keeps_accents_drops_spanish_punctuation():
    assert normalize_words("—¿Está usted seguro? «Sí», dijo… ¡Aleksei!") == [
        "está", "usted", "seguro", "sí", "dijo", "aleksei"]


def test_identical_ignoring_case_and_punctuation():
    assert compute_wer("Hola, mundo.", "hola mundo").wer == 0.0


def test_counts():
    r = compute_wer("el jugador perdió todo en la ruleta",
                    "el jugador perdido todo en ruleta otra vez")
    assert (r.substitutions, r.deletions, r.insertions) == (1, 1, 2)
    assert r.ref_words == 7
    assert abs(r.wer - 4 / 7) < 1e-9


def test_long_text_alignment_is_fast_and_exact():
    # Non-periodic text, like real prose. (On artificially periodic text difflib's anchors can
    # shift by one period and overcount; that does not occur with real dictation.)
    import random

    rng = random.Random(7)
    vocab = [f"palabra{i}" for i in range(3000)]
    ref_words = [rng.choice(vocab) for _ in range(10000)]
    hyp_words = list(ref_words)
    for i in (100, 5000, 9000):
        hyp_words[i] = "distinta"
    r = compute_wer(" ".join(ref_words), " ".join(hyp_words))
    assert (r.substitutions, r.errors) == (3, 3)
