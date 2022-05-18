from maltego_trx.entities import Person, Company
from maltego_trx.maltego import UIM_PARTIAL
from maltego_trx.transform import DiscoverableTransform
import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
import csv


class AllOutcomingTxs(DiscoverableTransform):
    """
    Lookup all outcoming txs from address.
    """

    @classmethod
    def create_entities(cls, request, response):

        def add_time_n_hash(some_entity, properties_list):
            counter = 0
            for i in properties_list:
                date = datetime.fromtimestamp(int(i[0]))
                some_entity.addProperty(
                    'time' + str(counter),
                    displayName='time' + str(counter),
                    value=f'{date}'
                )
                some_entity.addProperty(
                    'hash' + str(counter),
                    displayName='hash' + str(counter),
                    value=f'{i[1]}'
                )
                counter += 1

        def add_txs(txs, color):
            for tx in txs:
                name = cls.get_names(tx.strip().lower())
                if name:
                    entity = response.addEntity(Company, name)
                    entity.addProperty(
                        'address',
                        displayName='address',
                        value=f'{tx}'
                    )
                    add_time_n_hash(entity, txs[tx])

                else:
                    entity = response.addEntity(Person, tx)
                    counter = 0
                    add_time_n_hash(entity, txs[tx])
                    entity.setLinkColor(color)
                    entity.setLinkThickness(3)

        address = request.Value
        link_normal_txs = 'https://api.etherscan.io/api?module=account&action=tokentx&address={address}&page=all&offset=100&startblock=0&endblock=27025780&sort=asc&apikey='
        normal_txs_from_x, normal_txs_to_x = cls.get_address_transactions(address, link_normal_txs)

        if normal_txs_from_x:
            add_txs(normal_txs_from_x, '#318a86')
        if normal_txs_to_x:
            add_txs(normal_txs_to_x, '#ab2424')

    @staticmethod
    def get_address_transactions(raw_address, link):
        api_key = ''
        address = raw_address.lower()

        response_API = requests.get(link + api_key)

        data = response_API.text
        parse_json = json.loads(data)
        result = parse_json['result']

        normal_txs_from_x = {}
        normal_txs_to_x = {}
        for i in result:
            if i['from'] == address:
                if i['to'] in normal_txs_from_x:
                    normal_txs_from_x[i['to']].append([i['timeStamp'], i['hash']])
                else:
                    normal_txs_from_x[i['to']] = [[i['timeStamp'], i['hash']]]

            if i['to'] == address:
                if i['from'] in normal_txs_to_x:
                    normal_txs_to_x[i['from']].append([i['timeStamp'], i['hash']])
                else:
                    normal_txs_to_x[i['from']] = [[i['timeStamp'], i['hash']]]

        return normal_txs_from_x, normal_txs_to_x

    @staticmethod
    def get_names(search_adress):
        with open("adress_to_names.csv") as f:
            for ln in f.readlines():
                if len(ln.split(",")) > 1:
                    adress, nname = ln.split(",")
                    if adress.strip().lower() == search_adress:
                        matching_name = nname.strip()
                        return matching_name

        headers = {
            'Host': 'etherscan.io',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0'
        }

        s = requests.session()
        response = s.get(f'https://etherscan.io/address/{search_adress}', headers=headers)
        data = response.text

        soup = BeautifulSoup(data, 'html.parser')
        info = list(map(str.strip, soup.find('title').string.strip().split('|')))

        if len(info) == 3:
            received_address = info[1].split(' ')[1].lower()
            if search_adress == received_address:
                name = info[0]

                with open('adress_to_names.csv', 'a') as db:
                    writer = csv.writer(db)
                    eman = ' ' + name
                    line = [search_adress, eman]
                    writer.writerow(line)

                return name


if __name__ == "__main__":
    pass
