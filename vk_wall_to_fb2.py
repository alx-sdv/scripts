# getting vk access token
# https://oauth.vk.com/authorize?client_id= <put your app id here> &display=page&redirect_uri=https://oauth.vk.com/blank.html&response_type=token&v=5.69
# about fb2
# http://www.fictionbook.org/index.php/%D0%9E%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B5_%D1%84%D0%BE%D1%80%D0%BC%D0%B0%D1%82%D0%B0_FB2_%D0%BE%D1%82_Sclex
# http://www.fictionbook.org/index.php/XML_%D1%81%D1%85%D0%B5%D0%BC%D0%B0_FictionBook2.2
# TODO: parse token via regular authorization

import requests
from binascii import b2a_base64
from datetime import date
from xml.sax.saxutils import escape
from time import sleep

params = dict(  # put the wall name here:
              domain='perazhki',  # perazhki perawki
              count=100,
              offset=0,
                # put your access token here:
              access_token='',
              v='5.69'
)

poems = []
images = []
wall_url = 'https://api.vk.com/method/wall.get'

try:
    r = requests.get(wall_url, params=params)
    while r.json()['response']['items']:
        for item in r.json()['response']['items']:
            # TODO: parse date and an author
            if not item.get('is_pinned'):
                if not (item.get('attachments') and item.get('attachments')[0].get('photo')):
                    poems.append(escape(item['text'].replace('\r', '')))  # TODO: should not depends on platform
                else:
                    # TODO: parse all attached images
                    image = requests.get(item.get('attachments')[0].get('photo').get('photo_604'))
                    images.append(b2a_base64(image.content).decode('utf-8'))
                    poems.append('<image l:href="#image_{}.jpg"/>'.format(len(images)))

        print('Got {} items. Getting +{} more...'.format(len(poems), params['count']))
        params['offset'] += params['count']
        sleep(1)  # to avoid "Too many requests per second" error
        r = requests.get(wall_url, params=params)
    print('{} items retrieved. Writing a file...'.format(len(poems)))
except:
    print('Something is wrong. Response text: \n{}'.format(r.text))
    quit()


# TODO: use xml builder or any template engine instead of horrible flat text
result_file_name = '{}-{}.fb2'.format(date.today(), params['domain'])
with open(result_file_name, 'w', encoding='utf8') as result_file:
    result_file.write('<?xml version="1.0" encoding="UTF-8"?><FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" xmlns:l="http://www.w3.org/1999/xlink">')
    result_file.write('<description><title-info><book-title>Стишки Пирожки ({} {})</book-title></title-info><document-info><src-url>vk.com/{}</src-url></document-info></description>'.format(params['domain'], date.today(), params['domain']))
    result_file.write('<body><section id="n1"><title><p>Стишки-пирожки</p></title><empty-line/>')
    for item in poems[::-1]:
        result_file.write('<poem><stanza><v>')
        result_file.write('</v><v>'.join([i for i in item.split('\n') if '©' not in i]))
        result_file.write('</v></stanza></poem><empty-line/>')
    result_file.write('</section></body>')
    for i, image in enumerate(images):
        result_file.write('<binary id="image_{}.jpg" content-type="image/jpeg">{}</binary>'.format(i+1, image))
    result_file.write('</FictionBook>')

print('Done. Check the file {}'.format(result_file_name))
