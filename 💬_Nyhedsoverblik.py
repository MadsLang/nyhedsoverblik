import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
import numpy as np
import datetime
from src.utils import hide_table_row_index, collapsible_css, collapsible_js, dictSave

today = datetime.datetime.today().strftime("%Y-%m-%d")
DATA_URL = f'data/data{today}.csv'

@st.cache
def load_data():
    df = pd.read_csv(DATA_URL)
    df = df[["title","name","published","link","scrape_time","text"]]
    df = df.sort_values('published', ascending=False)
    return df





big_topics = dictSave.load(f'data/big_topics{today}.json')

# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)
st.markdown(collapsible_css, unsafe_allow_html=True)




# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
df = load_data()
data_load_state.text("")

# js_script = """<script src="scatter.js" charset="utf-8"></script>"""
# st.markdown(js_script, unsafe_allow_html=True)






st.title('Nyhedsoverblik')
st.caption(f"Seneste overskrifter er hentet: {df['scrape_time'].values[0]}")




with st.sidebar:
    st.markdown("""## \U0001F39B    Filtrer nyhederne!""")

    selected_topic = st.selectbox(
        'Dagens emner',
        tuple(['Intet valgt'] + list(big_topics.keys()))
    )
    if selected_topic != 'Intet valgt':
        selected_topic_keywords = big_topics[selected_topic]
        keywords = selected_topic_keywords.split(' ')
        df = df[
            df['title'].apply(
                lambda x: any([k.lower() in x.lower() for k in keywords])
            )
        ]

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
    st.markdown(f"""<div><p> <strong>{df['name'].values[i]}</strong>: <a href={df['link'].values[i]} style=color:#ffffff;text-decoration:none>{df['title'].values[i]} </a> <span style=color:#ff9762;">{df['published'].values[i]}</span> </p></div>""", unsafe_allow_html=True)




