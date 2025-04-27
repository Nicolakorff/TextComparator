# TextComparator

This Streamlit application allows users to compare the most frequent words in two text inputs, supporting both English and Spanish. It generates interactive word clouds for each text and provides a comparison table of word frequencies, highlighting words that are significantly more frequent or exclusive to one of the texts. Additionally, it displays a bar chart visualizing the top word frequencies across both texts.

**Try it!!** -> [Text Comparator](https://textcomparator-9w7v.onrender.com/)

## Features

- **Multi-Language Support:** Processes text in both English and Spanish.
- **Interactive Word Clouds:** Generates visual representations of the most frequent words in each text.
- **Word Frequency Comparison Table:** Displays the frequency of each word in both texts, with sorting functionality.
- **Significance Highlighting:** Identifies words that are exclusive to one text or significantly more frequent in one over the other.
- **Top Word Frequency Chart:** Shows a bar chart comparing the frequencies of the most common words across both inputs.
- **User-Friendly Interface:** Built with Streamlit for an intuitive and easy-to-use experience.

## How to Use

1.  **Input Texts:** Enter the two texts you want to compare in the provided text areas. (I offer in the datos folder two speeches for the same occasion by two politicians so that you can see the difference in the use of words in each of them and the political intention with the manipulation of language behind them. 
2.  **Select Languages:** Choose the language (English or Spanish) for each text using the dropdown menus.
3.  **Word Cloud Settings:** Adjust the maximum number of words to display in the word clouds using the slider.
4.  **Chart Settings:** Select the number of top words to show in the frequency bar chart.
5.  **Generate Comparison:** Click the "Generate WordCloud and Comparison" button.
6.  **View Results:** The application will display the word clouds side-by-side, a sortable table comparing word frequencies, and a bar chart visualizing the top words.

## Deployment

This application is deployed on Render.

## Technologies Used

* [Streamlit](https://streamlit.io/): For building the interactive web application.
* [NLTK (Natural Language Toolkit)](https://www.nltk.org/): For text processing, including tokenization and stop word removal.
* [Pandas](https://pandas.pydata.org/): For creating and manipulating data tables.
* [Matplotlib](https://matplotlib.org/): Used internally by `WordCloud`.
* [WordCloud](https://amueller.github.io/word_cloud/): For generating word cloud visualizations.
* [Altair](https://altair-viz.github.io/): For creating interactive bar charts.

## Installation (for local development)

1.  **Clone the repository:**
    ```bash
    git clone [URL_DEL_TU_REPOSITORIO]
    cd [NOMBRE_DEL_REPOSITORIO]
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download NLTK data (important for local execution):**
    ```python
    import nltk
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    ```
    You might need to download other resources if you expand the language support.

5.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```

## Contributing

Contributions to this project are welcome. If you have ideas for improving the application or have found a bug, please feel free to open an issue or submit a pull request.

## Author

[Nicola Korff] (https://github.com/Nicolakorff/)

## License

[MIT License]

