import streamlit as st
import spacy
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import altair as alt
import subprocess
import importlib.util

if importlib.util.find_spec("en_core_web_sm") is None:
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
if importlib.util.find_spec("es_core_news_sm") is None:
    subprocess.run(["python", "-m", "spacy", "download", "es_core_news_sm"])

try:
    nlp_es = spacy.load("es_core_news_sm")
except OSError:
    spacy.cli.download("es_core_news_sm")
    nlp_es = spacy.load("es_core_news_sm")

try:
    nlp_en = spacy.load("en_core_web_sm")
except OSError:
    spacy.cli.download("en_core_web_sm")
    nlp_en = spacy.load("en_core_web_sm")


def obtener_palabras_filtradas_spacy_multiidioma(texto, idioma='es'):
    if idioma == 'es':
        nlp = nlp_es
    elif idioma == 'en':
        nlp = nlp_en
    else:
        return Counter()

    doc = nlp(texto)
    palabras_filtradas = [
        token.text.lower()
        for token in doc
        if not token.is_stop and not token.is_punct and token.is_alpha
    ]
    return Counter(palabras_filtradas)


def generar_nube_palabras(frecuencia_palabras, nombre, max_words):
    wordcloud = WordCloud(width=800, height=400,
    background_color='black', colormap='YlGnBu_r', max_words=max_words).generate_from_frequencies(frecuencia_palabras)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.set_title(nombre)
    ax.axis('off')
    return fig


st.title("Multi-Language WordCloud Comparator")
st.markdown("This app generates word clouds for two texts in English and Spanish.")
st.markdown("You can compare the most frequent words in each text.")


with st.sidebar:
    st.header("How to use this app")
    st.markdown("1. Insert the texts to compare in the main area.")
    st.markdown("2. Select the language for each text.")
    st.markdown("3. Adjust the maximum number of words for the word clouds.")
    st.markdown("4. Click the button to generate the word clouds and comparison table.")
    st.markdown("5. The app will display the word clouds and a comparison table with the frequencies of each word.")
    st.markdown("6. You can sort columns in ascending or descending order by simply clicking on the column header.")
    st.markdown("7. The app will also show a bar chart comparing the frequencies of the most common words.")
    st.markdown("Made by Nicola Korff")


texto1 = st.text_area("Insert the first text here", height=200)
idioma1 = st.selectbox("Language for Text 1", ["es", "en"], index=0)

texto2 = st.text_area("Insert the second text here", height=200)
idioma2 = st.selectbox("Language for Text 2", ["es", "en"], index=1)

max_palabras_nube = st.slider("Max words in WordCloud", 50, 300, 100)
num_palabras_grafico = st.slider("Number of words to show in the chart", 5, 20, 10)


if "sort_by" not in st.session_state:
    st.session_state["sort_by"] = None


if st.button("Generate WordCloud and Comparison"):
    with st.spinner("Generating Word Clouds..."):
        if texto1 and texto2:
            frecuencia1 = obtener_palabras_filtradas_spacy_multiidioma(texto1, idioma1)
            fig1 = generar_nube_palabras(frecuencia1, f"Text 1 ({idioma1})", max_palabras_nube)

            frecuencia2 = obtener_palabras_filtradas_spacy_multiidioma(texto2, idioma2)
            fig2 = generar_nube_palabras(frecuencia2, f"Text 2 ({idioma2})", max_palabras_nube)


            col1, col2 = st.columns(2)
            with col1:
                st.pyplot(fig1)
            with col2:
                st.pyplot(fig2)


            st.subheader("Comparison of Word Frequencies")
            all_words = set(frecuencia1.keys()) | set(frecuencia2.keys())
            data = {'Word': list(all_words)}
            data[f'Frequency Text 1 ({idioma1})'] = [frecuencia1.get(word, 0) for word in data['Word']]
            data[f'Frequency Text 2 ({idioma2})'] = [frecuencia2.get(word, 0) for word in data['Word']]
            df_comparacion = pd.DataFrame(data)


            def palabras_significativas(row):
                freq1 = row[f'Frequency Text 1 ({idioma1})']
                freq2 = row[f'Frequency Text 2 ({idioma2})']
                if freq1 > 0 and freq2 == 0:
                    return f'Exclusive to Text 1'
                elif freq2 > 0 and freq1 == 0:
                    return f'Exclusive to Text 2'
                elif freq1 > freq2 * 2 and freq1 > 5:
                    return f'Significantly more in Text 1'
                elif freq2 > freq1 * 2 and freq2 > 5:
                    return f'Significantly more in Text 2'
                return ''
        

            df_comparacion['Significance'] = df_comparacion.apply(palabras_significativas, axis=1)

        
            col_orden1, col_orden2 = st.columns(2)

            if st.session_state["sort_by"]:
                df_comparacion = df_comparacion.sort_values(by=st.session_state["sort_by"], ascending=False)
            st.dataframe(df_comparacion, use_container_width=True)  

            st.subheader("Word Frequency Chart (Top by Total Frequency)")
            frecuencia_total = Counter(frecuencia1) + Counter(frecuencia2)
            top_palabras_total = [word for word, freq in frecuencia_total.most_common(num_palabras_grafico)]
            data_grafico = {'Word': top_palabras_total}
            data_grafico[f'Frequency Text 1 ({idioma1})'] = [frecuencia1.get(word, 0) for word in top_palabras_total]
            data_grafico[f'Frequency Text 2 ({idioma2})'] = [frecuencia2.get(word, 0) for word in top_palabras_total]
            df_grafico = pd.DataFrame(data_grafico)

            melted_df_total = pd.melt(df_grafico, id_vars=['Word'], var_name='Text', value_name='Frequency')
            colores_personalizados = {
                f'Frequency Text 1 ({idioma1})': '#6accbc',
                f'Frequency Text 2 ({idioma2})': '#158fad',}

            chart = alt.Chart(melted_df_total).mark_bar().encode(
                x=alt.X('Word:N', sort='-y', title='Word'),
                y=alt.Y('Frequency:Q', title='Frequency'),
                color=alt.Color('Text:N', 
                    scale=alt.Scale(domain=list(colores_personalizados.keys()), 
                                    range=list(colores_personalizados.values())),
                    legend=alt.Legend(title="Text")),
                tooltip=['Word:N', 'Text:N', 'Frequency:Q']
            ).properties(
                width=700,
                height=400,
                title="Word Frequency Comparison"
            ).configure_axis(
                labelFontSize=12,
                titleFontSize=14
            ).configure_title(
                fontSize=18)

            st.altair_chart(chart, use_container_width=True)

        else:
            st.warning("Please insert both texts.")


