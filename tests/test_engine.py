import pytest

from versifier import compose, fault_plea, prose_memo, REGISTERS, FORMS
from versifier.engine import number_words, line_syllables
from versifier.cli import Session


def test_forty_registers():
    assert len(REGISTERS) == 40


def test_deterministic():
    a = compose("a girl", "JOC", "sonnet", seed=7)
    b = compose("a girl", "JOC", "sonnet", seed=7)
    assert a.lines == b.lines


@pytest.mark.parametrize("form,n", [("sonnet", 14), ("quatrain", 4), ("couplets", 8),
                                    ("baciate", 6), ("limerick", 5), ("terzina", 9)])
def test_line_counts(form, n):
    assert len(compose("the sea", "EP", form, seed=1).lines) == n


def test_rhyme_scheme_ends_share_family():
    p = compose("night", "EP", "quatrain", seed=3, knob=0)
    last = [ln.rstrip(",.").split()[-1] for ln in p.lines]
    assert len(last) == 4 and last[0] != last[1]


def test_knob_zero_has_no_license_bends():
    for s in range(30):
        p = compose("machine", "JOC", "sonnet", knob=0, seed=s)
        assert not any("bent to" in n for n in p.notes)


def test_knob_ten_eventually_bends():
    assert any("bent to" in n for s in range(40)
               for n in compose("machine", "JOC", "sonnet", knob=10, seed=s).notes)


def test_porn_withdrawn():
    p = compose("x", "PORN", seed=1)
    assert any("withdrawn" in n for n in p.notes)


def test_bad_inputs():
    with pytest.raises(ValueError):
        compose("x", "NOPE")
    with pytest.raises(ValueError):
        compose("x", "JOC", "haiku")


def test_number_words_matches_original_gag():
    assert number_words(8617) == "eightthousandsixhundredandseventeen"
    assert fault_plea(serial=8617, seed=0).count("Eightthousand") <= 1


def test_fault_mentions_serial():
    assert "8617" in fault_plea(serial=8617)


def test_memo():
    assert "MEMORANDUM No. 0005" in prose_memo("pay clerks", 5)


def test_era_swap():
    p = compose("love", "AMO", "couplets", era="baroque", seed=2)
    assert " your " not in p.text().lower()


def test_syllables():
    assert line_syllables("the sea") == 2


def test_session_flow():
    s = Session(seed=1)
    assert s.handle("a girl") is None
    assert s.handle("JOC") is None
    assert s.handle("sonnet") is None
    out = s.handle("")
    assert "JOC / sonnet" in out and s.stage == 0


def test_session_errors_and_knob():
    s = Session()
    s.handle("x")
    assert "ERROR" in s.handle("ZZZ")
    assert "set to 7" in s.handle("/knob 7")
    assert s.knob == 7
