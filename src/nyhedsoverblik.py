import requests
from bs4 import BeautifulSoup
import lxml.html
from lxml import etree
import pandas as pd
import datetime
import numpy as np
import re
from dateutil.parser import parser
from analytics import TopicModel
import json
from utils import dictSave


today = datetime.datetime.today().strftime("%Y-%m-%d")



sites = [
    {
        "name": "DR",
        "url": "https://www.dr.dk/nyheder",
        "link_url": 'https://www.dr.dk',
        "xpaths": {
            "title": "//li[contains(@class,'hydra-latest-news-page__list-item')]//h2|//li[contains(@class,'hydra-latest-news-page__list-item')]//span[@class='dre-teaser-title__text']",
            "text": "//div[@itemprop='articleBody']|//li[contains(@class,'hydra-latest-news-page__list-item')]//span[@class='dre-teaser-title__text']",
            "published": "//span[@class='dre-teaser-meta-label']",
            "link": "//div[@class='dre-share-link-copy-url__copy-link-hidden']|//li[contains(@class,'hydra-latest-news-page__list-item')]//span[@class='dre-teaser-title__text']"
        }
    },
    {
        "name": "TV2",
        "url": f"https://nyheder.tv2.dk/live/{today}-nyhedsoverblik", 
        "link_url": f"https://nyheder.tv2.dk/live/{today}-nyhedsoverblik",
        "xpaths": {
            "title": "//h2[@class='tc_heading tc_post__body__title tc_heading--5']",
            "text": "//div[@class='tc_post__body__post']",
            "published": "//header[@class='tc_post__header']",
            "link": None
        }
    },
    {
        "name": "Jyllandsposten",
        "url": "https://jyllands-posten.dk/seneste/",
        "link_url": "https://jyllands-posten.dk",
        "xpaths": {
            "title": "//a[@class='c-article-teaser-heading__link']",
            "text": None,
            "published": "//div[@class='article-teaser__left-time']",
            "link": "//a[@class='c-article-teaser-heading__link']"
        }
    },
    {
        "name": "Berlingske",
        "url": "https://www.berlingske.dk/nyheder",
        "link_url": "https://www.berlingske.dk",
        "xpaths": {
            "title": "//div[contains(@class,'teaser__content')]",
            "text": None,
            "published": "//div[@class='teaser__date']",
            "link": "//div[contains(@class,'teaser__content')]//a[@class='teaser__title-link']"
        }
    },
    {
        "name": "Politiken",
        "url": "https://politiken.dk/nyheder/",
        "link_url": '',
        "xpaths": {
            "title": "//li[@data-element-type='article']/a",
            "text": None,
            "published": "//li[@data-element-type='article']/ul",
            "link": "//li[@data-element-type='article']/a"

        }
    },
    {
        "name": "Ekstra-Bladet",
        "url": "https://ekstrabladet.dk/nyheder/",
        "link_url": "https://ekstrabladet.dk",
        "xpaths": {
            "title": "//div[@class='card-content']//h2",
            "text": None,
            "published": "//div[@class='card-content']//span[@data-timestamp]",
            "link": "//a[@data-articleid]"
        }
    }
]


def get_html_content(url):
    r = requests.get(url, stream=True)
    r.raw.decode_content = True
    tree = lxml.html.parse(r.raw)
    return tree

def get_meta_tags(tree):
    meta_tag_dict = {}

    try: 
        meta_tag_dict["og:site_name"] = tree.xpath("//meta[@property='og:site_name']")[0].attrib['content']
    except:
        meta_tag_dict["og:site_name"] = np.nan
    
    try:
        meta_tag_dict["og:url"] = tree.xpath("//meta[@property='og:url']")[0].attrib['content']
    except:
         meta_tag_dict["og:url"] = np.nan
    
    try:
        meta_tag_dict["site_description"] = tree.xpath("//meta[@name='description']")[0].attrib['content']
    except:
        meta_tag_dict["site_description"] = np.nan

    return meta_tag_dict


def parse_date(date_string):
    date_string = date_string.lower().strip()

    # replace today
    today_date = datetime.datetime.today()
    for today in ['idag','i dag']:
        date_string = date_string.replace(today, today_date.strftime('%d.%m.%Y'))

    # replace yesterday
    yesterday_date = datetime.datetime.today() + datetime.timedelta(days=1)
    for yesterday in ['igår','i går','i gã¥r']:
        date_string = date_string.replace(yesterday, yesterday_date.strftime('%d.%m.%Y'))

    # replace month to number
    months = {
        '01': [' jan'],
        '02': [' feb'],
        '03': [' mar'],
        '04': [' apr'],
        '05': [' may',' maj'],
        '06': [' jun'],
        '07': [' jul'],
        '08': [' aug'],
        '09': [' sep'],
        '10': [' oct',' okt'],
        '11': [' nov'],
        '12': [' dec']
    }

    for key,values in months.items():
        for value in values:
            date_string = date_string.replace(value,key)

    # if minutes ago
    min_regex = r"\d+(?=\smin)"
    if re.match(min_regex,date_string):
        minutes_ago = int(re.match(min_regex,date_string).group(0))
        timestamp = datetime.datetime.now() - datetime.timedelta(minutes=minutes_ago)

    # if hours ago
    hour_regex = r"\d+(?=\stime)"
    if re.match(hour_regex,date_string):
        hours_ago = int(re.match(hour_regex,date_string).group(0))
        timestamp = datetime.datetime.now() - datetime.timedelta(hours=hours_ago)

    p = parser()
    try:
        timestamp = p.parse(date_string, dayfirst=True, fuzzy=True)
    except:
        return np.NaN


    return timestamp.strftime('%d.%m.%Y %H:%M')

def clean_title(text):

    #string_encode = text.encode("ascii", "ignore")
    #text = string_encode.decode()

    text = ' '.join(text.split())

    encoding_errors = {
        'Ã¥': 'å',
        'Ã©': 'é',
        'Â»': '»',
        'Â«': '«',
        "'": '',
        'Ã¸': 'ø',
        'Ã¦': 'æ',
        'â': '-',
        '»â': '»',
        'jâ': '!',
    }

    for key,value in encoding_errors.items():
        text = text.replace(key,value)

    return text

def get_link(e):
    try:
        link = e.attrib['href']
    except:
        link = ''

    return link

def parse(name, url, link_url, xpath_dict):

    tree = get_html_content(url)


    df = pd.DataFrame(
        {
            "title": [e.text_content() for e in tree.xpath(xpath_dict['title'])],
            "published": [e.text_content() for e in tree.xpath(xpath_dict['published'])],
        }
    )

    df['published'] = df['published'].apply(parse_date)
    df['title'] = df['title'].apply(clean_title)

    if xpath_dict['text'] != None:
        df['text'] = [e.text_content() for e in tree.xpath(xpath_dict['text'])]
    else: 
        df['text'] = ['' for _ in range(df.shape[0])]

    if xpath_dict['link'] != None:
        df['link'] = [get_link(e) for e in tree.xpath(xpath_dict['link'])]

    else:
        df['link'] = ['' for _ in range(df.shape[0])]

    meta_tag_dict = get_meta_tags(tree)
    df['og:site_name'] = [meta_tag_dict['og:site_name'] for _ in range(df.shape[0])]
    df['og:url'] = [meta_tag_dict['og:url'] for _ in range(df.shape[0])]
    df['site_description'] = [meta_tag_dict['site_description'] for _ in range(df.shape[0])]
    
    df['name'] = [name for _ in range(df.shape[0])]
    df['url'] = [url for _ in range(df.shape[0])]
    df['scrape_time'] = [datetime.datetime.now().strftime('%d.%m.%Y %H:%M') for _ in range(df.shape[0])]
    df['link'] = df['link'].apply(lambda x: link_url + x)

    return df


if __name__ == '__main__':
    dfs = []
    for site in sites:
        print('Scraping:',site['name'])
        dfs.append(
            parse(
                name=site['name'],
                url=site['url'],
                link_url=site['link_url'],
                xpath_dict=site['xpaths']
            )
        )

    final_df = pd.concat(dfs)
    final_df.to_csv(f'data/data{today}.csv', encoding='utf-8', index=False)
    print("Finished getting new data!")

    tmodel = TopicModel(df=final_df)
    big_topics = tmodel.get_topics()
    dictSave.save(big_topics, f'big_topics{today}.json')