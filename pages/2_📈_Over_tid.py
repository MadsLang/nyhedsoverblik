import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
import numpy as np
import datetime
import glob




@st.cache()
def load_all_data():
    all_files = glob.glob("data/data*.csv")
    dfs = []
    for file_name in all_files:
        df = pd.read_csv(file_name)
        df = df[["title","name","published","link","scrape_time","text"]]
        dfs.append(df)

    df = pd.concat(dfs)
    df = df.sort_values('published', ascending=False)
    return df

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
df = load_all_data()
data_load_state.text("")



with st.sidebar:
    st.markdown("""## \U0001F39B    Filtrer nyhederne!""")

    search_word = st.text_input("Søg i dagens overskrifter \U0001F50E",'')

    options = st.multiselect(
        'Hvilke(t) medie?',
        list(df['name'].unique()),
        None)

if search_word != '':
    df = df[df['title'].apply(lambda x: search_word.lower() in x.lower())]

if options:
    df = df[df['name'].apply(lambda x: x in options)]




g = df['scrape_time'].value_counts().reset_index()
g = g.rename(columns={'index':'Dato','scrape_time':'Antal artikler'})

st.vega_lite_chart(g, {
    "width": 800,"height": 500,
    "mark": {"type": "bar", "color": "#ff9762", "tooltip": True},
    "encoding": {
        "x": {"field": "Dato", "type": "ordinal", "axis": {"labelAngle": 0}},
        "y": {"field": "Antal artikler", "type": "quantitative", "axis": {"tickMinStep": 1}},
        "opacity": {
          "condition": {"test": {"param": "hover", "empty": False}, "value": 0.7},
          "value": 1
        }
    },
    "params": [
    {
        "name": "hover",
        "select": {"type": "point", "on": "mouseover", "clear": "mouseout"}
    }
    ]
}
)




### Zoomable scatter with hover ###

# test = pd.DataFrame(
#     np.random.randn(200, 3),
#     columns=['a', 'b', 'c'])

# st.vega_lite_chart(test, {
#     "width": 800,"height": 500,
#     "params": [{
#         "name": "view",
#         "select": "interval",
#         "bind": "scales"
#     }],
#     'mark': {'type': 'circle', 'tooltip': True},
#     'encoding': {
#         'x': {'field': 'a', 'type': 'quantitative'},
#         'y': {'field': 'b', 'type': 'quantitative'},
#         'size': {'field': 'c', 'type': 'quantitative'},
#         'color': {'field': 'c', 'type': 'quantitative'},
#     },
# })
    
    
    
