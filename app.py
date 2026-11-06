from pathlib import Path

import altair as alt
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from wordcloud import WordCloud

from textcomparator import analysis as an

st.set_page_config(page_title="Text Comparator", layout="wide")
DATA = Path(__file__).parent / "data"
LANGS = {"Spanish": "es", "English": "en"}
COLORS = {"Text 1": "#2a9d8f", "Text 2": "#e9a03b"}


def load_samples():
    st.session_state["text1"] = (DATA / "sample_A.txt").read_text(encoding="utf-8")
    st.session_state["text2"] = (DATA / "sample_B.txt").read_text(encoding="utf-8")
    st.session_state["lang_name"] = "Spanish"


@st.cache_data(show_spinner="Analysing…")
def analyse(t1, t2, lang, lemmatize, min_total, extra):
    tok1 = an.tokenize(t1, lang, lemmatize, extra)
    tok2 = an.tokenize(t2, lang, lemmatize, extra)
    return {
        "stats": pd.DataFrame({"Text 1": an.text_stats(t1, tok1), "Text 2": an.text_stats(t2, tok2)}),
        "keyness": an.keyness_table(tok1, tok2, min_total),
    }


def cloud(df, text_label, max_words):
    sub = df[df["more_in"] == text_label]
    weights = {w: abs(g) for w, g in zip(sub["word"], sub["G2"]) if abs(g) >= an.G2_P01}
    if not weights:
        return None
    wc = WordCloud(width=700, height=380, background_color="white", max_words=max_words, collocations=False,
                   color_func=lambda *a, **k: COLORS[text_label]).generate_from_frequencies(weights)
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.imshow(wc, interpolation="bilinear"); ax.axis("off")
    return fig


st.title("Text Comparator")
st.caption("Which words characterise each of two texts? Keyness analysis with log-likelihood (G²) and "
           "log-odds ratios, controlling for text length.")

with st.sidebar:
    st.header("Settings")
    st.button("Load sample texts", on_click=load_samples, help="Two Spanish political speeches of different length.")
    lang_name = st.selectbox("Language of both texts", list(LANGS), key="lang_name")
    lang = LANGS[lang_name]
    can_lemma = an.lemmatizer_available(lang)
    lemmatize = st.checkbox("Lemmatize (spaCy)", value=can_lemma, disabled=not can_lemma,
                            help="Groups inflected forms: 'gobiernos' → 'gobierno'.")
    min_total = st.slider("Minimum total occurrences", 1, 20, 5)
    extra = tuple(w.strip() for w in st.text_input("Extra stopwords (comma-separated)").split(",") if w.strip())
    top_n = st.slider("Words shown per text", 5, 30, 15)

c1, c2 = st.columns(2)
text1 = c1.text_area("Text 1", height=180, key="text1")
text2 = c2.text_area("Text 2", height=180, key="text2")

if not (text1.strip() and text2.strip()):
    st.info("Paste two texts, or click **Load sample texts** in the sidebar.")
    st.stop()

res = analyse(text1, text2, lang, lemmatize, min_total, extra)
key = res["keyness"]
if key.empty:
    st.warning("No words reach the minimum number of occurrences. Lower the threshold or use longer texts.")
    st.stop()

tab_dist, tab_stats, tab_cloud, tab_table, tab_method = st.tabs(
    ["Distinctive words", "Text statistics", "Word clouds", "Full table", "Method"])

with tab_dist:
    top = pd.concat([key[key["more_in"] == t].head(top_n) for t in ("Text 1", "Text 2")])
    chart = alt.Chart(top).mark_bar().encode(
        x=alt.X("G2:Q", title="← more in Text 2 · log-likelihood G² · more in Text 1 →"),
        y=alt.Y("word:N", sort=alt.EncodingSortField("G2", order="descending"), title=None,
                axis=alt.Axis(labelOverlap=False, labelLimit=200)),
        color=alt.Color("more_in:N", scale=alt.Scale(domain=list(COLORS), range=list(COLORS.values())), title=None),
        tooltip=["word", "count_1", "count_2", "per_1000_1", "per_1000_2", "G2", "log_odds_z", "evidence"],
    ).properties(height=max(300, 18 * len(top)))
    st.altair_chart(chart, use_container_width=True)
    n_strong = int((key["evidence"] == "p < 0.0001").sum())
    st.caption(f"{len(key)} words analysed; {n_strong} differ at p < 0.0001 (uncorrected for multiple comparisons). "
               "Keyness shows *what differs in vocabulary* — often topic and context — not why.")

with tab_stats:
    st.dataframe(res["stats"], use_container_width=True)
    st.caption("MATTR is a moving-average type/token ratio: unlike the plain ratio, it does not fall just because a text is longer.")

with tab_cloud:
    st.caption("Size = strength of the difference (G²), not raw frequency. Only words significant at p < 0.01 are shown.")
    cc1, cc2 = st.columns(2)
    for col, label in ((cc1, "Text 1"), (cc2, "Text 2")):
        fig = cloud(key, label, 80)
        col.subheader(f"Distinctive of {label}")
        if fig is None:
            col.write("No significant words.")
        else:
            col.pyplot(fig); plt.close(fig)

with tab_table:
    only = st.radio("Show", ["All", "Text 1", "Text 2"], horizontal=True)
    view = key if only == "All" else key[key["more_in"] == only]
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.download_button("Download CSV", view.to_csv(index=False).encode("utf-8"), "keyness.csv", "text/csv")

with tab_method:
    st.markdown("""
**Tokens.** Alphabetic words, lowercased, without stopwords (spaCy lists); optionally lemmatized.

**Rates.** Occurrences per 1,000 content tokens, so texts of different length are comparable.

**Log-likelihood (G²).** Dunning's test of whether a word's rate differs between the texts
(1 degree of freedom: 6.63 ↔ p < 0.01, 15.13 ↔ p < 0.0001). With hundreds of words tested, some false
positives are expected; treat the ranking as exploratory.

**Log-odds z-score.** Log-odds ratio with an informative Dirichlet prior (Monroe, Colaresi & Quinn, 2008),
which shrinks rare words so they do not dominate the ranking.

**Limits.** Both texts must be in the same language. Results depend on stopwords and lemmatization,
and differences usually reflect topic and setting as much as style.
""")
