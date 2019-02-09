import sys
import os
import datetime
import json
import urllib.error
import urllib.request
from collections import OrderedDict

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup

COUNTS_PER_RANKING = 10

MARKDOWN = """Title: {title}
Date: {date}
Slug: {slug}
Tags: Ranking
Author: Bot

今月もお疲れ様でした。  
<a href="https://evekatsu.github.io/ranking/?date={year}-{month}" target="_blank">{year}年{month}月の日本人PvPランキングの発表です。</a>

注意事項：これは{date_jp}に集計したものです。それ以降に投稿されたキルメールは集計対象外です。


{total_header}

対象：所属するコーポレーション、アライアンスを攻撃したキルメールを除く全て（キル順）

{total_table}

<br />
{solo_header}

対象：キルメールにソロキルのフラグが付いている（ポイント順）

{solo_table}

<br />
{small_gangs_header}

対象：ポイントが1より上の攻撃に参加した人数が100人未満（ポイント順）

{small_gangs_table}

<br />
{brawlers_header}

対象：ポイントが1の攻撃に参加した人数が100人未満（キル順）

{brawlers_table}

<br />
{big_fighters_header}

対象：攻撃に参加した人数が100人以上（ISK順）

{big_fighters_table}

<br />
毎月10日にその前の月のキルメールを集計します。  
来月もよろしくお願いします。
"""

RANKING = OrderedDict([
    (
        'total', {
            'text': 'トータル',
            'query': '',
            'sort': 'Ships',
        }
    ), (
        'solo', {
            'text': 'ソロ',
            'query': '&k=0',
            'sort': 'Points',
        }
    ), (
        'small_gangs', {
            'text': 'スモールギャング',
            'query': '&k=1',
            'sort': 'Points',
        }
    ), (
        'brawlers', {
            'text': 'ブローラー',
            'query': '&k=2',
            'sort': 'Ships',
        }
    ), (
        'big_fighters', {
            'text': 'ビッグファイター',
            'query': '&k=3',
            'sort': 'ISK',
        }
    )
])

def main():
    year = str(int(sys.argv[1]))
    month = str(int(sys.argv[2]))

    try:
        with urllib.request.urlopen('https://evekatsu.github.io/ranking/%s/%s/players_information.json' % (year, month)) as url:
            players_information = json.loads(url.read().decode())
    except urllib.error.HTTPError:
        print('Error: players_information.json')
        return

    filename = 'ranking-%s-%s' % (year, month)
    base_url = 'https://evekatsu.github.io/ranking/?date=%s-%s' % (year, month)
    ranking = OrderedDict()

    driver = webdriver.Chrome()
    for filter_key, filter_values in RANKING.items():
        driver.get(base_url + filter_values['query'])
        WebDriverWait(driver, 60).until(lambda x: x.find_element_by_tag_name('table'))

        driver.find_element_by_class_name('dropdown-toggle').click()
        driver.find_element_by_xpath("//ul[@class='dropdown-menu']/li[3]/a").click()
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        ranking_items = []

        trs = soup.table.tbody.findAll('tr')
        for i in range(COUNTS_PER_RANKING):
            tds = trs[i].findAll('td')

            ranking_item = {}
            for td_index, td_key in ((2, 'id'), (3, 'Ships(+)'), (4, 'Ships(-)'), (5, 'ISK(+)'), (6, 'ISK(-)'), (7, 'Points(+)'), (8, 'Points(-)')):
                value = tds[td_index].span.string.strip()
                if td_index == 5 or td_index == 6:
                    value = int(value.replace(',', '')) / 1000 / 1000 / 1000
                    value = str(round(value, 1)) + 'b'

                ranking_item[td_key] = value
            ranking_items.append(ranking_item)

        ranking[filter_key] = ranking_items
    driver.close()

    format_dict = {}
    format_dict['title'] = '%s年%s月のランキング発表' % (year, month)
    format_dict["slug"] = filename
    format_dict['year'] = year
    format_dict['month'] = month
    format_dict['date'] = datetime.date.today()
    format_dict['date_jp'] = datetime.date.today().strftime('%Y年%m月%d日')

    for filter_key, ranking_items in ranking.items():
        text =  '| <span class="glyphicon glyphicon-sort-by-attributes-alt"></span> '
        text += '| %s | %s | %s ' %(
            '<span class="glyphicon glyphicon-user"></span>',
            '<span class="glyphicon glyphicon-plus"></span>',
            '<span class="glyphicon glyphicon-minus"></span>',
        )
        text += '| <span class="glyphicon glyphicon-tower"></span> '
        text += '| <span class="glyphicon glyphicon-star"></span> '
        text += '|\n| ---- | ---- | ---- | ---- | ---- | ---- |\n'

        for i, ranking_item in enumerate(ranking_items):
            character_information = players_information['character'][ranking_item['id']]
            img_tag = '<img style="margin: 0px; width: 25px; display: inline; vertical-align:middle;" src="https://evekatsu.github.io/data/%s/%s_32%s">'

            text += '| %d | ' % (i + 1)
            text += ' {} {} | '.format(img_tag % ('character', ranking_item['id'], '.jpg'), character_information['name'])
            text += ' %s | ' % (ranking_item[RANKING[filter_key]['sort'] + '(+)'])
            text += ' %s | ' % (ranking_item[RANKING[filter_key]['sort'] + '(-)'])
            text += ' {} | '.format(img_tag % ('corporation', character_information['corporation_id'], '.png'))
            if 'alliance_id' in character_information:
                text += img_tag % ('alliance', character_information['alliance_id'], '.png')
            text += ' |\n'
        format_dict[filter_key + '_table'] = text
        format_dict[filter_key + '_header'] = '<h3><a href="%s" target="_blank">%s</a></h3>' % (
            base_url + RANKING[filter_key]['query'],
            RANKING[filter_key]['text'],
        )

    with open(os.path.join('content', 'ranking', '%s.md' % filename), 'w', encoding='utf-8') as file:
        file.write(MARKDOWN.format(**format_dict))

if __name__ == '__main__':
    main()
