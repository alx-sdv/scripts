from bs4 import BeautifulSoup
from bs4.element import Tag
import requests
import json


# http://marathonbet.ru
# https://www.marathonbet.ru/su/popular/Ice+Hockey/KHL/?menu=52309

result_file = open('mb_output.tsv', 'w', encoding='utf8')
try:
    result_file.write('ID события' +
                      '\t' +
                      'Дата события' +
                      '\t' +
                      'Команда 1' +
                      '\t' +
                      'Команда 2' +
                      '\t' +
                      'ID Выбора' +
                      '\t' +
                      'Тип выбора' +
                      '\t' +
                      'Выбор' +
                      '\t' +
                      'Коэфф' +
                      '\t' +
                      'Прочее'+
                      '\r\n')

    r = requests.get('https://www.marathonbet.ru/su/popular/Ice+Hockey/KHL/?menu=52309')
    html = ''
    for line in r.text.split('\n'):
        html += line.strip()
    document = BeautifulSoup(html, 'html.parser')

    headers = {
                'Host':        'www.marathonbet.ru',
                'User-Agent':  'Mozilla/5.0 Firefox/52.0',
                'Accept':      'application/json, text/javascript, */*; q=0.01',
                'Accept-Language':  'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding':  'gzip, deflate, br',
                'Content-Type':     'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer':          'https://www.marathonbet.ru/su/popular/Ice+Hockey/KHL/?menu=52309',
                'Content-Length':   '51',
                'Cookie':           '',
                'DNT':              '1',
                'Connection':       'keep-alive'
    }

    data = {
                'treeId': '5919455',
                'columnSize': '12',
                'siteStyle': 'MULTIMARKETS'
    }

    bet_table = document.find('table', class_='foot-market')
    for child in bet_table.children:
        if type(child) is Tag:
            if child.get('data-event-treeid'):
                data['treeId'] = child.get('data-event-treeid')
                r = requests.post('https://www.marathonbet.ru/su/markets.htm', headers=headers, data=data)

                s0 = str(r.json())
                s = ''
                for line in s0[37:-17].replace(r'\n', '\n').replace(r"\'", "'").split('\n'):
                    s += line.strip()
                s = s.replace('highlightedclass', 'highlighted class')
                response = BeautifulSoup(s, 'html.parser')
                for item in response.find_all('tr'):
                    if item.has_attr('data-header-highlighted-bounded'):
                        for item2 in item.children:
                            if item2.name == 'td' and item2.has_attr('data-sel'):
                                s2 = json.loads(item2['data-sel'])
                                result_file.write(child.get('data-event-treeid') + #ID события
                                      '\t' +
                                      child.tr.td.table.contents[0].contents[2].string + #Дата события
                                      '\t' +
                                      child.tr.td.table.contents[0].td.div.div.span.string + #Команда 1
                                      '\t' +
                                      child.tr.td.table.contents[1].td.div.div.span.string + #Команда 2
                                      '\t' +
                                      item2.span['data-selection-key'] + #ID Выбора
                                      '\t' +
                                      s2['mn'] + #Тип выбора
                                      '\t' +
                                      s2['sn'] + #Выбор
                                      '\t' +
                                      item2.span.string.replace('.', ',') + #Коэфф
                                      #'\t' +
                                      #item2['data-sel'] + #Прочее
                                      '\r\n'
                                      )
finally:
    result_file.close()
