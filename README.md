# nyhedsoverblik

This is the repository of my app, which you can visit at: https://madslang-nyhedsoverblik-my-app-tutnsz.streamlitapp.com/


It is a news app, that every day at 9AM fetches the headlines from Danish news media: DR, TV2, Jyllandsposten, Berlingske, Politiken, and Ekstra-Bladet. Based on the headlines, I run a clustering analysis and estimate today's topics. 


The app is hosted on Streamlit cloud. Data is fetched using a scheduled Github Action. The clustering analysis is done using DBSCAN on a similarity matrix (Word Mover's Distance) based on Skip-Gram embeddings pre-trained on the CoNLL2017 dataset (thanks [DaNLP](https://github.com/alexandrainst/danlp)!). The description of each topic is made using a [pre-trained summarization model](https://huggingface.co/Danish-summarisation/dansum-mt5-base-v1). 


**TO DO:**
 - Add functionality to go further back in time than just today's headlines
 - Fine-tune clustering model

