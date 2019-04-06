# coding=utf-8
'''
    crawling mobile01 forum with keyword "台星", "台灣之星"
    return result of lastest 3 pages with details contains:
    [title, publish_timestamp, page, author, popularity, replys, content]
    content including : [host/not host, name, member_level, personal_score, written_timestamp,
                         discussion by far]
    consist of 3 sub-function:
    crawler, dict2df_sort, data2mysql

    TODO make a header_pool with multi agents,
         using logging

'''
import numpy as np
import pandas as pd
import requests
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
import logging
######################################  headers and pages ################
my_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"}
top3_pages = ['https://www.mobile01.com/topiclist.php?f=18',
              'https://www.mobile01.com/topiclist.php?f=18&p=2',
              'https://www.mobile01.com/topiclist.php?f=18&p=3']
root_path = 'https://www.mobile01.com/'
######################################  keywords #########################
keyword_list = ['台灣之星', '台星']
######################################  MySQL info #######################
connect_info_dict = {'host': '35.234.10.179',
                     'user': 'root',
                     'password': '0000',
                     'db': 'tstar_comments'}
######################################  logger init setting ##############
logger = logging.getLogger(__name__)
logging.basicConfig(filename='crawler.log', level=logging.INFO)


def main():

    logging.basicConfig(filename='test.log', level=logging.INFO)
    logger.info(
        'START Crawling information TIME : {0}'.format(
            datetime.now(
                tz=timezone(
                    timedelta(
                        hours=8)))))

    result_list_form, result_table_form = crawler()

    logging.info(
        'SUCCESSED Crawling TIME : {0}'.format(
            datetime.now(
                tz=timezone(
                    timedelta(
                        hours=8)))))

    logging.info(
        'TRASNFORMAING result to dataframe TIME : {0}'.format(
            datetime.now(
                tz=timezone(
                    timedelta(
                        hours=8)))))

    df_tmp = dict2df_sort(result_table_form)

    logging.info(
        'SAVING dataframe to MySQL 5.7 TIME : {0}'.format(
            datetime.now(
                tz=timezone(
                    timedelta(
                        hours=8)))))

    data2mysql(df_tmp)


def data2mysql(df, if_first=False):
    '''
    初始化MySQL連線，並將dataframe存入MySQL，若需要建立表，則if_first = True，
    df : pandas.DaraFrame
    return : None
    '''
    if if_first:
        db = pymysql.connect(**connect_info_dict)
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS mobile01(
                          created_timestamp DATETIME,
                          crawled  DATETIME,
                          title TEXT,
                          page INT,
                          author TEXT,
                          popularity INT,
                          replys INT,
                          content TEXT)""")
        db.commit()
        db.close()

    engine = create_engine(
        'mysql+pymysql://{0}:{1}@{2}/{3}'.format(
            connect_info_dict['user'],
            connect_info_dict['password'],
            connect_info_dict['host'],
            connect_info_dict['db']))
    df.applymap(str).to_sql(name='mobile01', con=engine,
                            if_exists='append', index=False)

    return None


def dict2df_sort(dict_data):
    '''
    change crawling_result into dataframe
    dict_data : dict
    output : pandas.dataFrame
    '''
    sorted_columns = ['created_timestamp', 'crawled', 'title',
                      'page', 'author', 'popularity', 'replys', 'content']
    dtype_dict = {'created_timestamp': np.datetime64,
                  'crawled': np.datetime64,
                  'page': int,
                  'popularity': int,
                  'replys': int}
    df = pd.DataFrame.from_dict(dict_data)[sorted_columns]
    return df


def crawler():
    '''
    crawling mobile01 forum with keyword "台星", "台灣之星"
    return result of lastest 3 pages with details contains:
    [title, publish_timestamp, page, author, popularity, replys, content]
    content including : [host/not host, name, member_level, personal_score, written_timestamp,
                                             discussion by far]
    return two dict, the first collect by 'topic', the second collect by 'title, page, author,......'
    in my case, first dict to check bugs
    input : None
    return : dict, dict
    generally,

    '''
    result_list_form = []

    for (p, link) in enumerate(top3_pages):
        # get request
        res = requests.get(link,
                           headers=my_headers)
        res.encoding = 'utf-8'

        if res.status_code == 200:
            logging.info(
                'accessed successfully' + '  ' +
                'crawling page {}'.format(
                    p + 1))
        else:
            loging.info('accessed failed at page {}'.format(p + 1))
            loging.info(res.text)
        # complie by bs4
        soup = BeautifulSoup(res.text)
        # get all td tag
        td_set = [ele for ele in soup.find_all('td')]
        # assign now time with 8+
        tzutc_8 = timezone(timedelta(hours=8))
        now_time = datetime.now(tz=tzutc_8)

        for i, tag in enumerate(td_set):
            result_single = {}
            # filter
            # for each keyword
            for keyword in keyword_list:
                # get topic sub-path
                if (tag.attrs['class'] == ['subject']) and (
                        keyword in tag.a.string):
                    # get subject and authur tag
                    result_single['title'] = tag.a.string
                    popularity_raw_data = tag.a.attrs['title']
                    result_single['popularity'] = [
                        int(s) for s in popularity_raw_data.split() if s.isdigit()][0]
                    result_single['replys'] = td_set[i + 1].string
                    gene = td_set[i + 2].strings
                    result_single['created_timestamp'] = str(next(gene))
                    result_single['crawled'] = str(now_time)[:16]
                    result_single['author'] = next(gene)
                    result_single['page'] = p + 1

                    # get contents soup
                    topic_path = tag.a['href']
                    article_res = requests.get(
                        root_path + topic_path, headers=my_headers)
                    article_res.encoding = 'utf-8'
                    if article_res.status_code == 200:
                        logging.info('accessed topic {} successfully'.format(
                            tag.a.string) + '  ' + 'crawling contents.....')
                        article_soup = BeautifulSoup(article_res.text)
                        # 是否為樓主 作者 會員等級 個人積分 發文/回應時間 回應內容
                        content_list = []
                        for tag_author, tag_personal_score, tag_ts, tag_content in zip(
                                article_soup.find_all('div', class_='fn'),
                                article_soup.find_all(
                                    'ul', class_='author-detail'),
                                article_soup.find_all(
                                    'div', class_='date'),
                                article_soup.find_all('div', class_='single-post-content')):
                            content_dict = {}
                            # check the tag_author for detail
                            content_dict['host'] = tag_author.a.nextSibling is not None
                            content_dict['name'] = tag_author.a.string
                            content_dict['member_level'] = tag_author.a['title']
                            # tag_personal_score --> span --> last --> string
                            # --> personal_score
                            content_dict['personal_score'] = tag_personal_score.find_all(
                                'span', class_=None)[-1].string
                            # tag_ts contains "  #1", "  #2" take str type take
                            # :-4
                            content_dict['timestamp'] = str(tag_ts.string)[:-4]
                            # contents
                            content_dict['discussion'] = str(tag_content.div)

                            # append them into list
                            content_list.append(content_dict)
                    else:
                        logging.info(
                            'accessed topic {} failed......'.format(
                                tag.a.string))
                        logging.info(res.text)
                    result_single['content'] = content_list
                    # append into a list
                    result_list_form.append(result_single)

                result_table_form = {
                    k: [d.get(k) for d in result_list_form]
                    for k in set().union(*result_list_form)
                }

    return result_list_form, result_table_form


if __name__ == '__main__':
    main()
