import urllib3
from bs4 import BeautifulSoup
import requests
import os
import csv
import unicodedata
import pandas as pd

def get_links(tag, suffix):
    url = 'https://medium.com/tag/' + tag
    urls = [url + '/' + s for s in suffix]
    links = []
    for url in urls:
        data = requests.get(url)
        soup = BeautifulSoup(data.content, 'html.parser')
        articles = soup.findAll('div', {"class": "postArticle-readMore"})
        for i in articles:
            links.append(i.a.get('href'))
    return links

def get_article(links):
    articles = []
    for link in links:
        try:
            article = {}
            data = requests.get(link)
            
            soup = BeautifulSoup(data.content, 'html.parser')
            author=[]
            title = soup.findAll('title')[0]
            title = title.get_text()
            article['title'] = unicodedata.normalize('NFKD', title)
            #print(article['title'])

            author = soup.findAll('meta', {"name": "author"})[0]
            author = author.get('content')
            article['author'] = unicodedata.normalize('NFKD', author)
            paras = soup.findAll('p')
            text = ''
            nxt_line = '\n'
            for para in paras:
                text += unicodedata.normalize('NFKD',para.get_text()) + nxt_line
            article['text'] = text
            
            articles.append(article)
            
        except KeyboardInterrupt:
            print('Exiting')
            os._exit(status = 0)
        except:
            continue
        
    
    return articles

def save_articles(articles, csv_file,  is_write = True):
    csv_columns = ['title','author','text']
    print(csv_file)
    if is_write:
        with open(csv_file, 'w',encoding="UTF-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, delimiter='|')
            writer.writeheader()
            for data in articles:
                writer.writerow(data)
            csvfile.close()
    else:
        with open(csv_file, 'a+',encoding="UTF-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns,  delimiter='|')
            for data in articles:
                writer.writerow(data)
            csvfile.close()



    
if __name__ == '__main__':
    is_write = True
    tags = input('Write tags in space separated format.\n')
    tags = tags.split(' ')
    file_name = input('Write destination file name.\n')
    if len(file_name.split('.')) == 1:
        file_name += '.csv'
    suffixes = ['', 'latest', 'archive/2000',
            'archive/2010', 'archive/2011', 'archive/2012', 'archive/2013', 'archive/2014', 'archive/2015', 'archive/2016', 'archive/2017', 'archive/2018']
    for tag in tags:
        links = get_links(tag, suffixes)
        articles = get_article(links)
        save_articles(articles, file_name, is_write)
        is_write = False
    # To remove duplicates
    articles = pd.read_csv(file_name, file_name, delimiter=None)
    articles = articles.drop_duplicates()
    articles.to_csv(file_name, sep='|', index=False)
    
