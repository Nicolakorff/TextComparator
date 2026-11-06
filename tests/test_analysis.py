import math

from textcomparator import analysis as an


def test_tokenize_removes_stopwords_and_digits():
    assert an.tokenize("El gobierno de 2024 y la gente", "es") == ["gobierno", "gente"]


def test_tokenize_keeps_accents():
    assert "educación" in an.tokenize("La educación pública", "es")


def test_log_likelihood_symmetric_and_signed():
    g = an.log_likelihood(30, 10, 1000, 1000)
    assert g > 0
    assert math.isclose(an.log_likelihood(10, 30, 1000, 1000), -g)


def test_log_likelihood_equal_rates_is_zero():
    assert math.isclose(an.log_likelihood(10, 20, 1000, 2000), 0.0, abs_tol=1e-9)


def test_log_likelihood_known_value():
    # a=100, b=50, n1=n2=10000 -> expected 75 each; G2 = 2*(100 ln(4/3) + 50 ln(2/3))
    expected = 2 * (100 * math.log(100 / 75) + 50 * math.log(50 / 75))
    assert math.isclose(an.log_likelihood(100, 50, 10000, 10000), expected)


def test_keyness_controls_for_text_length():
    t1 = ["casa"] * 20 + ["otro"] * 180        # 10 % casa
    t2 = ["casa"] * 10 + ["otro"] * 90         # 10 % casa, half the length
    df = an.keyness_table(t1, t2, min_total=1)
    row = df[df.word == "casa"].iloc[0]
    assert abs(row.G2) < 1e-6 and row.evidence == ""


def test_keyness_detects_exclusive_word():
    t1 = ["paz"] * 30 + ["pan"] * 70
    t2 = ["pan"] * 100
    df = an.keyness_table(t1, t2, min_total=1)
    row = df[df.word == "paz"].iloc[0]
    assert row.more_in == "Text 1" and row.evidence == "p < 0.0001" and row.log_odds_z > 0


def test_min_total_filters_rare_words():
    df = an.keyness_table(["a1"] * 3 + ["b1"] * 10, ["b1"] * 10, min_total=5)
    assert list(df.word) == ["b1"]


def test_mattr_range_and_repetition():
    assert math.isclose(an.mattr(["x"] * 100, 50), 1 / 50)
    assert math.isclose(an.mattr([str(i) for i in range(100)], 50), 1.0)


def test_text_stats_sentence_length():
    s = an.text_stats("Uno dos tres. Cuatro cinco seis siete.", ["uno"])
    assert s["Words (raw)"] == 7 and s["Avg. sentence length (words)"] == 3.5
