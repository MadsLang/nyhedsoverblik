import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
import numpy as np
import datetime




@st.cache()
def load_all_data():
    day = datetime.datetime.today().date()
    dfs = []
    while True:
        try:
            DATA_URL = f'data/data{day.strftime("%Y-%m-%d")}.csv'
            df = pd.read_csv(DATA_URL)
            df = df[["title","name","published","link","scrape_time","text"]]
            df['date_scrape'] = day.strftime("%Y-%m-%d")
            dfs.append(df)
            day = day - datetime.timedelta(days=1) 
        except:
            break

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




g = df['date_scrape'].value_counts().reset_index()
g = g.rename(columns={'index':'Dato','date_scrape':'Antal artikler'})

st.vega_lite_chart(g, {
    "width": 800,"height": 500,
    "mark": {"type": "bar", "color": "#ff9762", "tooltip": True},
    "encoding": {
        "x": {"field": "Dato", "type": "nominal", "axis": {"labelAngle": 0}},
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
    
    
    
