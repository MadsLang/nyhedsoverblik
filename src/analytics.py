from dataclasses import replace
from math import inf
import pandas as pd
import re
import numpy as np
from danlp.models.embeddings  import load_wv_with_gensim
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sklearn.cluster import DBSCAN
from tqdm import tqdm
import spacy
from thefuzz import fuzz


class TopicModel:
    def __init__(self, df, eps=3, min_samples=2):
        self.df = df
        self.tokenizer_re = r"[åøæÅØÆA-Za-z_]+"
        self.nlp = spacy.load("da_core_news_sm")
        self.pos_tag = ['PROPN', 'ADJ', 'NOUN']
        print('Loading wv...')
        self.model = load_wv_with_gensim('conll17.da.wv')

        print('Loading sum model...')
        self.sum_tokenizer = AutoTokenizer.from_pretrained("Danish-summarisation/dansum-mt5-base-v1")
        self.sum_model = AutoModelForSeq2SeqLM.from_pretrained("Danish-summarisation/dansum-mt5-base-v1") 

        # DBSCAN params (optional)
        self.eps = eps
        self.min_samples = min_samples
        print('Done loading essentials!')

    def tokenizer(self, text, tokenizer_type='basic') -> list:
        if tokenizer_type == 'basic':
            tokens = re.findall(self.tokenizer_re, text)
            return [token.lower() for token in tokens]
        elif tokenizer_type == 'spacy':
            tokens = self.nlp(text.lower())
            return [token.text for token in tokens]
        elif tokenizer_type == 'spacy_no_pos':
            tokens = self.nlp(text.lower())
            return [token.text for token in tokens if(token.pos_ in self.pos_tag)]
        else:
            raise Exception('Tokenizer not recognized! Available options are: basic, spacy, spacy_no_pos')
        
    def tokenize_and_filter_pos(self, titles):
        print('Tokenizing...')
        titles_pos_filtered = []
        for title in tqdm(titles):
            tokenized_title = self.nlp(title.lower())
            title_wo_pos = [token.text for token in tokenized_title if(token.pos_ in self.pos_tag)]
            if len(title_wo_pos) > 0:
                titles_pos_filtered.append(title_wo_pos)
            else:
                titles_pos_filtered.append([token.text for token in tokenized_title])
        return titles_pos_filtered

    def replace_OOV_tokens(self, text):
        subwords = [w for w in list(self.model.vocab.keys()) if w in text]
        ratios = [(w,fuzz.ratio(w,text)) for w in subwords]
        most_sim_in_vocab = max(ratios,key=lambda item:item[1])[0]
        return most_sim_in_vocab

    def compute_distance_matrix(self, texts, model):
        print('Computing distance matrix...')
        dist_matrix = np.zeros((len(texts), len(texts)))
        for i in tqdm(range(len(texts))):
            for j in range(len(texts)):
                if i == j:
                    continue  # self-distance is 0.0
                if i > j:
                    dist_matrix[i, j] = dist_matrix[j, i]  # re-use earlier calc
                
                if model.wmdistance(texts[i], texts[j]) == np.inf: 
                    ijs = []
                    for doc in [texts[i],texts[j]]:
                        ijs.append(
                            [self.replace_OOV_tokens(token) if token not in model.vocab else token for token in doc]
                        )
                    dist_matrix[i, j] = model.wmdistance(ijs[0],ijs[1])
                
                else:
                    dist_matrix[i, j] = model.wmdistance(texts[i], texts[j])

        # this negation simply makes largest dists into smallest (most-negative) sims
        # you could also consider instead a calc that maps all dists to [-1.0, 1.0]
        # sim_matrix = -dist_matrix  
        return dist_matrix

    def get_name_of_cluster(self, values: list, n: int) -> list:
        all_tokens = []
        for title in values:
            tokens = re.findall(self.tokenizer_re, title)
            all_tokens = all_tokens + [token.lower() for token in tokens]

        groupby = {i: all_tokens.count(i) for i in all_tokens}
        agg = pd.DataFrame.from_dict(groupby, orient='index', columns=['count'])
        return ' '.join(agg.sort_values('count', ascending=False).index[0:n].tolist())

    def interpret_topics(self, topic_list: list) -> dict:
   
        topics_with_summary = {}

        for topic in topic_list:
            keywords = topic.split(' ')
            text = '. '.join(
                self.df[
                    self.df['title'].apply(
                        lambda x: any([k.lower() in x.lower() for k in keywords])
                        )
                    ]['title'].values
                )

            inputs = self.sum_tokenizer(text, return_tensors="pt").input_ids
            outputs = self.sum_model.generate(input_ids=inputs)
            summary = self.sum_tokenizer.decode(outputs[0], skip_special_tokens=True)
            topics_with_summary[summary] = topic

        return topics_with_summary

    def get_topics(self):

        titles = self.df['title'].tolist()

        titles_pos_filtered = self.tokenize_and_filter_pos(titles)
        X = self.compute_distance_matrix(titles_pos_filtered, self.model)

        clustering = DBSCAN(
            eps=self.eps, 
            min_samples=self.min_samples,
            metric='precomputed'
        ).fit(X)

        self.df['clustering.labels_'] = clustering.labels_.tolist()
        self.df['titles_pos_filtered'] = [' '.join(t) for t in titles_pos_filtered]

        big_topics = []
        n_biggest_clusters = self.df[self.df['clustering.labels_'] != -1]['clustering.labels_'].value_counts().iloc[:5].index.tolist()
        for c in n_biggest_clusters:
            big_topics.append(
                self.get_name_of_cluster(
                    values=self.df[self.df['clustering.labels_'] == c]['titles_pos_filtered'].values.tolist(), 
                    n=3
                )
            )

        topics_with_summary = self.interpret_topics(big_topics)
            
        for t in topics_with_summary.keys():
            print(t)

        return topics_with_summary




