from requests import get
from requests.exceptions import RequestException
import requests
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd
from tabulate import tabulate

url_base = 'http://books.toscrape.com/catalogue/category/books_1/index.html'

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
    scraped_data = pd.DataFrame(columns=['UPC','Product Type', 'Price (excl. tax)','Price (incl. tax)', 'Tax', 'Availability', 'Number of reviews'])
    response = simple_get(url_base)
    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        list = set(html.find_all('li',class_='col-xs-6 col-sm-4 col-md-3 col-lg-3'))

        for i,n in enumerate(list):
            df = get_data(n.article.h3.a['href'].strip('../../'),i)
            scraped_data = pd.concat([scraped_data,df.transpose()], ignore_index=True)
        return scraped_data

    raise Exception('Error retrieving contents at {}'.format(url_base))

def get_data(info_url, i):
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
print table

# if __name__ == '__main__':
#     print('Getting list of names...')
#     names = get_names()
#     print('...done.\n')
#
#     results = []
#
#     print('Getting stats for each name...')
#
#     for name in names:
#         try:
#             hits = get_hits_on_name(name)
#             if hits is None:
#                 hits = -1
#             results.append((hits,name))
#         except:
#             results.append((-1,name))
#             log_error('error encountered while processing '
#                         '{}, skipping'.format(name))
#
#     print('...done.\n')
#
#     results.sort()
#     results.reverse()
#
#     if len(results) > 5:
#         top_marks = results[:5]
#     else:
#         top_marks = results
#
#     print('\nthe most popular mathematicians are:\n')
#     for (mark, math) in top_marks:
#         print('{} with {} pageviews'.format(math, mark))
#
#     no_results = len([res for res in results if res[0] == -1])
#     print('\nBut we did not find results for '
#             '{} mathematicians on the list'.format(no_results))
