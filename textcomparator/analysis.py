"""Core analysis: tokenization, keyness (log-likelihood and log-odds) and text statistics."""
import math
import re
from collections import Counter

import pandas as pd
from spacy.lang.en import STOP_WORDS as STOP_EN
from spacy.lang.es import STOP_WORDS as STOP_ES

STOPWORDS = {"es": STOP_ES, "en": STOP_EN}
MODELS = {"es": "es_core_news_sm", "en": "en_core_web_sm"}
WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)
SENTENCE_RE = re.compile(r"[.!?…]+[\"')»”]*\s+|\n{2,}")

G2_P01 = 6.63     # chi-square (1 d.f.) critical value, p < 0.01
G2_P0001 = 15.13  # p < 0.0001

_NLP = {}


def _nlp(lang):
    if lang not in _NLP:
        import spacy
        _NLP[lang] = spacy.load(MODELS[lang], disable=["parser", "ner"])
    return _NLP[lang]


def lemmatizer_available(lang):
    try:
        _nlp(lang)
        return True
    except (OSError, ImportError):
        return False


def tokenize(text, lang="es", lemmatize=False, extra_stopwords=()):
    """Lowercased alphabetic tokens without stopwords; optionally lemmatized with spaCy."""
    stop = STOPWORDS[lang] | {w.lower() for w in extra_stopwords}
    if lemmatize:
        nlp = _nlp(lang)
        nlp.max_length = max(nlp.max_length, len(text) + 1000)
        tokens = [t.lemma_.lower() for t in nlp(text) if t.is_alpha]
    else:
        tokens = [w.lower() for w in WORD_RE.findall(text)]
    return [t for t in tokens if t not in stop and len(t) > 1]


def mattr(tokens, window=500):
    """Moving-average type/token ratio: lexical diversity that does not depend on text length."""
    if not tokens:
        return 0.0
    window = min(window, len(tokens))
    counts = Counter(tokens[:window])
    total, n = len(counts) / window, 1
    for i in range(window, len(tokens)):
        counts[tokens[i]] += 1
        out = tokens[i - window]
        counts[out] -= 1
        if counts[out] == 0:
            del counts[out]
        total += len(counts) / window
        n += 1
    return total / n


def text_stats(raw_text, tokens):
    """Basic descriptive numbers for one text."""
    words = WORD_RE.findall(raw_text)
    sentences = [s for s in SENTENCE_RE.split(raw_text) if WORD_RE.search(s)]
    return {
        "Words (raw)": len(words),
        "Content tokens": len(tokens),
        "Distinct content words": len(set(tokens)),
        "Lexical diversity (MATTR-500)": round(mattr(tokens), 3),
        "Avg. sentence length (words)": round(len(words) / len(sentences), 1) if sentences else 0.0,
    }


def log_likelihood(a, b, n1, n2):
    """Dunning's G2 for a word with counts a, b in corpora of size n1, n2 (signed: + means more in text 1)."""
    total = a + b
    e1 = n1 * total / (n1 + n2)
    e2 = n2 * total / (n1 + n2)
    g2 = 2 * ((a * math.log(a / e1) if a else 0.0) + (b * math.log(b / e2) if b else 0.0))
    return g2 if a / n1 >= b / n2 else -g2


def keyness_table(tokens1, tokens2, min_total=5, prior_strength=500):
    """One row per word: counts, per-1000 rates, signed G2 and log-odds z-score.

    z is the log-odds ratio with an informative Dirichlet prior (Monroe, Colaresi & Quinn, 2008),
    which shrinks rare words instead of over-rewarding them.
    """
    c1, c2 = Counter(tokens1), Counter(tokens2)
    n1, n2 = sum(c1.values()), sum(c2.values())
    pooled = c1 + c2
    rows = []
    for word, total in pooled.items():
        if total < min_total:
            continue
        a, b = c1[word], c2[word]
        alpha = prior_strength * total / (n1 + n2)
        alpha0 = prior_strength
        d = (math.log((a + alpha) / (n1 + alpha0 - a - alpha))
             - math.log((b + alpha) / (n2 + alpha0 - b - alpha)))
        z = d / math.sqrt(1 / (a + alpha) + 1 / (b + alpha))
        g2 = log_likelihood(a, b, n1, n2)
        rows.append({
            "word": word, "count_1": a, "count_2": b,
            "per_1000_1": round(1000 * a / n1, 2), "per_1000_2": round(1000 * b / n2, 2),
            "G2": round(g2, 2), "log_odds_z": round(z, 2),
        })
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    strength = df["G2"].abs()
    df["evidence"] = pd.cut(strength, [-1, G2_P01, G2_P0001, float("inf")],
                            labels=["", "p < 0.01", "p < 0.0001"]).astype(str)
    df["more_in"] = df["G2"].apply(lambda g: "Text 1" if g > 0 else "Text 2")
    return df.sort_values("G2", key=abs, ascending=False).reset_index(drop=True)
