import re

import pymysql
import requests
from bs4 import BeautifulSoup


def main():
    host = '127.0.0.1'
    user = 'root'
    passwd = '123456'
    db = 'msl_spider'
    dbc = DBController(host, user, passwd, db)
    r = requests.get('https://binbaz.org.sa/')
    soup = BeautifulSoup(r.text, 'lxml')
    #  > li:nth-child(1) > a:nth-child(1)
    lis = soup.select('#categories-tabs > li')
    for li in lis:
        a = li.select("a")[0]
        node_name = a.text.replace('\n', '').replace('  ', '')
        pid = dbc.add(0, 0, node_name, 'binbaz')
        # print(pid)
        div_id = a['aria-controls']
        div_obj = soup.select('#'+div_id)[0]
        o_lis = div_obj.select('div.tree > ul > li')
        for o_li in o_lis:
            # node_name = o_li.select("a")[0].text.replace('\n', '').replace('  ', '')
            # href = o_li.select("a")[0]['href']
            # nid = re.search(r'https://binbaz.org.sa/categories/.*?/(\d+)', href).group(1)
            # print(pid, nid, node_name)
            # o_pid = dbc.add(nid, pid, node_name)
            find_ul(o_li, pid, dbc)


def find_ul(li, pid, dbc):
    node_name = li.select("a")[0].text.replace('\n', '').replace('  ', '')
    href = li.select("a")[0]['href']
    nid = re.search(r'https://binbaz.org.sa/categories/.*?/(\d+)', href).group(1)
    print(pid, nid, node_name)
    pid = dbc.add(nid, pid, node_name, 'binbaz')
    if len(li.select("ul")) > 0:
        lis = li.select("ul > li")
        for li in lis:
            find_ul(li, pid, dbc)
    else:
        return


class DBController(object):
    def __init__(self, host, user, passwd, db):
        self._conn = pymysql.connect(host=host,
                                     user=user,
                                     password=passwd,
                                     db=db,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

    def add(self, nid, pid, node_name, web_site):
        try:
            with self._conn.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO `class_tree` (`nid`, `pid`, `node_name`, `web_site`) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (nid, pid, node_name, web_site))

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            self._conn.commit()
            with self._conn.cursor() as cursor:
                # Read a single record
                sql = "SELECT `id` FROM `class_tree` WHERE `nid`=%s AND  `pid`=%s AND `node_name`=%s AND `web_site`=%s;"
                cursor.execute(sql, (nid, pid, node_name, web_site))
                result = cursor.fetchone()
                return result['id']
        except pymysql.Error as e:
            print(e)


if __name__ == '__main__':
    main()
