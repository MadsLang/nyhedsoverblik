import streamlit as st
from streamlit.components.v1 import html


st.title('Om denne side')

st.markdown("""
    Dette er en nyhedsapp, som hver dag kl. 09 henter alle overskrifter fra:
     - DR
     - TV2
     - Jyllandsposten
     - Berlingske
     - Politiken
     - Ekstra-Bladet

    Du kan altså se seneste nyt på tværs af danske nyhedsmedier. 
    Idéen er, at du kan få et overblik over dagens emner, og så gå ind på læse artiklerne på mediernes egne sider.
    Du kan filtere eller søge i dagens overskrifter i panelet i venstre side, hvor du også kan se dagens hoved-emner, 
    som jeg har estimeret vha. machine learning. 

    Du kan læse mere om det tekniske og se al kode til siden på min [Github](https://github.com/MadsLang/nyhedsoverblik).

    Har du nogen spørgsmål eller er der tekniske problemer på siden, så [skriv til mig](mailto:madslangs@gmail.com)!
    """)