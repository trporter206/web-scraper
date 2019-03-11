from requests import get
from requests.exceptions import RequestException
import requests
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd

url_base = 'http://books.toscrape.com/catalogue/page-1.html'

def simple_get(link):
    try:
        with closing(get(link, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(link,str(e)))
        return None

def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

def log_error(e):
    print(e)

def get_names():
    scraped_data = pd.DataFrame(columns=['Titles', 'UPC','Product Type', 'Price (excl. tax)','Price (incl. tax)', 'Tax', 'Availability', 'Number of reviews'])
    page_count = 1
    titles = []
    for i in range(1,page_count+1):
        link = 'http://books.toscrape.com/catalogue/page-{}.html'.format(i)
        response = simple_get(link)
        if response is not None:
            html = BeautifulSoup(response, 'html.parser')
            list = set(html.find_all('li',class_='col-xs-6 col-sm-4 col-md-3 col-lg-3'))
            for n in list:
                titles.append(n.article.h3.a['title'])
                df = get_data(n.article.h3.a['href'].strip('../../'))
                scraped_data = pd.concat([scraped_data,df.transpose()], ignore_index=True)

    scraped_data['Titles'] = pd.Series(titles)
    return scraped_data

    raise Exception('Error retrieving contents at {}'.format(url_base))

def get_data(info_url):
    link = 'http://books.toscrape.com/catalogue/{}'.format(info_url)
    response = simple_get(link)
    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        table = html.find_all('table')[0]
        df = pd.read_html(str(table))[0]
        df.drop(columns=[0], inplace=True)
        df.rename({0:'UPC',1:'Product Type', 2:'Price (excl. tax)',3:'Price (incl. tax)', 4:'Tax', 5:'Availability', 6:'Number of reviews'}, inplace=True)
        return df

    raise Exception('Error getting contents at {}'.format(link))

table = get_names()
cols = table.columns.tolist()
cols = cols[-1:] + cols[:-1]
table = table[cols]
print table

table.to_csv('export.csv', encoding='utf-8')
