from stenographer.guard import check

RAW = "eh dijo que no vendría el el lunes porque estaba cansado de esperar"


def test_punctuation_case_and_dialogue_layout_are_free():
    clean = "—Dijo que no vendría el lunes —porque estaba cansado de esperar."
    r = check(RAW, clean)
    assert r.passed
    assert {c.kind for c in r.changes} == {"filler", "repeat"}


def test_changed_word_is_rejected():
    r = check(RAW, "Dijo que no vendría el martes porque estaba cansado de esperar.")
    assert not r.passed
    assert [(c.kind, c.raw, c.clean) for c in r.violations] == [("sub", "lunes", "martes")]


def test_dropped_sentence_is_rejected():
    raw = "Llovía sobre Petersburgo. Nadie lo esperaba en la estación."
    r = check(raw, "Llovía sobre Petersburgo.")
    assert not r.passed
    assert len(r.violations) == 6
    assert all(c.kind == "del" for c in r.violations)


def test_added_words_are_rejected():
    r = check("la ruleta giraba", "La vieja ruleta giraba lentamente.")
    assert [(c.kind, c.clean) for c in r.violations] == [("ins", "vieja"), ("ins", "lentamente")]


def test_accent_change_is_flagged_separately():
    r = check("esta cansado", "Está cansado.")
    assert [c.kind for c in r.violations] == ["accent"]


def test_lexical_fillers_are_not_free():
    # "bueno" can be the author's word, so dropping it is a violation, not a filler.
    r = check("bueno no sé", "No sé.")
    assert [c.raw for c in r.violations] == ["bueno"]


def test_budget():
    raw = " ".join(["palabra"] * 99 + ["fin"])
    clean = " ".join(["palabra"] * 99 + ["final"])
    assert check(raw, clean, max_rate=0.01).passed
    assert not check(raw, clean, max_rate=0.0).passed
