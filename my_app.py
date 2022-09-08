import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
import numpy as np



DATA_URL = 'data/data.csv'

@st.cache
def load_data():
    df = pd.read_csv(DATA_URL)
    df = df[["title","name","published","link","scrape_time"]]
    df = df.sort_values('published', ascending=False)
    return df

# CSS to inject contained in a string
hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """

# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)




# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
df = load_data()
data_load_state.text("")

# js_script = """<script src="scatter.js" charset="utf-8"></script>"""
# st.markdown(js_script, unsafe_allow_html=True)



st.title('Nyhedsoverblik')
st.caption(f"Seneste overskrifter er hentet: {df['scrape_time'].values[0]}")



#st.markdown(f"""<div id='scatter'></div>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""## Filtre""")
    search_word = st.text_input("Søg i dagens overskrifter \U0001F50E",'')

    options = st.multiselect(
        'Hvilke(t) medie?',
        list(df['name'].unique()),
        None)

if search_word != '':
    df = df[df['title'].apply(lambda x: search_word.lower() in x.lower())]

if options:
    df = df[df['name'].apply(lambda x: x in options)]

for i in range(df.shape[0]):
    st.markdown(f"""<div><p> <strong>{df['name'].values[i]}</strong>: {df['title'].values[i]} <span style=color:#ff9762;">{df['published'].values[i]}</span></p></div>""", unsafe_allow_html=True)




#st.table(df)



