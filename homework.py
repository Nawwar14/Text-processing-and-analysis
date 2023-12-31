# -*- coding: utf-8 -*-
"""

Automatically generated by Colaboratory.

"""

 %%capture
 !pip install scrapy
 !pip install pymorphy2
 !pip install natasha

# Create a scrapy project in local session storage
import scrapy
!scrapy startproject article_crawler

%cd ./article_crawler

# Create a spider file in folder spider for parsing
%%writefile ./article_crawler/spiders/article_spider.py

 import scrapy
 HOST = 'https://habr.com'
 class ArticleSpider(scrapy.Spider):
     name = "article"
     def start_requests(self):
         start_urls = [
             'https://habr.com/search/?q=блокчейн&target_type=posts&order=relevance',
         ]
         for url in start_urls:
             yield scrapy.Request(url=url, callback=self.parse_article_notes)
 
     def parse_article_text(self, response):
       return {'title': response.meta['title'],
               'description' : "".join(response.xpath(".//div[@class='tm-article-body']//text()").extract())}

     def parse_article_notes(self, response):
      articles = response.xpath("//article")
       for article in articles:
         title = "".join(article.xpath(".//h2//span//text()").extract())
         link = article.xpath(".//h2/a/@href").extract_first()
         # description = "".join(article.xpath(".//div[contains(@class, 'article-formatted-body')]//text()").extract())
         yield scrapy.Request(HOST + link, callback=self.parse_article_text, meta={'title': title})

"""check the settings (article_crawler/article_crawler/spiders/)\
```ROBOTSTXT_OBEY = False ```\
must be (it's by default but ... may be it isn't)
"""

!scrapy crawl article -o parsed_articles.json

 picture for tag cloud
 !wget -O circle.jpg 'https://i.ytimg.com/vi/VAtUG5Sj5JM/maxresdefault.jpg'
# russian stop-words 559
 !wget -O  stop_words_ru.txt 'https://raw.githubusercontent.com/stopwords-iso/stopwords-ru/master/stopwords-ru.txt'
 stop_words_ru = []
 with open('stop_words_ru.txt', 'r') as file:
   stop_words_ru = file.read().split()
   stop_words_ru.extend(['b', 'a', 'ffffffffffffffffffffffffffffffffffffffff'])

cd /content/article_crawler

ls

# Text preprocessing
import json
import string
from collections import Counter
from nltk import FreqDist
from natasha import (
    PER,
    NamesExtractor,
    MorphVocab,
    Doc,
    Segmenter,
    NewsEmbedding,
    NewsNERTagger,
    NewsMorphTagger,
    NewsSyntaxParser
)
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
from PIL import Image

  # Read file and create text for analysis
with open('parsed_articles.json', 'r') as json_file:
  articles_dict = json.load(json_file)
  text = ""
  for article in articles_dict:
    text += article['description']

  punctuation = string.punctuation + '\n\xa0«»,\t—…'

  segmenter = Segmenter()
  morph_vocab = MorphVocab()

  emb = NewsEmbedding()
  morph_tagger = NewsMorphTagger(emb)
  syntax_parser = NewsSyntaxParser(emb)
  ner_tagger = NewsNERTagger(emb)
  names_extractor = NamesExtractor(morph_vocab)

  doc = Doc(text)

  doc.segment(segmenter)
  doc.tag_morph(morph_tagger)
  doc.tag_ner(ner_tagger)

  for token in doc.tokens:
    token.lemmatize(morph_vocab)
  # lemmatization
  text = [_.lemma for _ in doc.tokens]
  text = [word for word in text if word not in punctuation]
  text = [word for word in text if word not in stop_words_ru]
  print("Top 10 most frequent words")
  print(Counter(text).most_common(10))

  for span in doc.spans:
    if span.type == PER:
      span.normalize(morph_vocab)
      span.extract_fact(names_extractor)
  names = set([_.normal for _ in doc.spans if _.fact])
  print("Key names")
  print(names)

  mask = np.array(Image.open('circle.jpg'))
  cloud = WordCloud(mask=mask, contour_width=10, contour_color='#2e3043', background_color='#272d3b', colormap='Set3', max_words=80).generate(" ".join(text))
  plt.figure(figsize=(9,5))
  plt.imshow(cloud)
  plt.axis('off')