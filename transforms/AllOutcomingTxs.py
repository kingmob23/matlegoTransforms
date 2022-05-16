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
    Lookup the all outcoming txs from address.
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
        txs_from_x, txs_to_x = cls.get_address_transactions(address)
        if txs_from_x:
            add_txs(txs_from_x, '#318a86')
        if txs_to_x:
            add_txs(txs_to_x, '#ab2424')

    @staticmethod
    def get_address_transactions(raw_address):
        api_key = ''
        address = raw_address.lower()

        response_API = requests.get(
            f'https://api.etherscan.io/api?module=account&action=tokentx&address={address}&page=all&offset=100&startblock=0&endblock=27025780&sort=asc&apikey={api_key}')

        data = response_API.text
        parse_json = json.loads(data)
        result = parse_json['result']

        txs_from_x = {}
        txs_to_x = {}
        for i in result:
            if i['from'] == address:
                if i['to'] in txs_from_x:
                    txs_from_x[i['to']].append([i['timeStamp'], i['hash']])
                else:
                    txs_from_x[i['to']] = [[i['timeStamp'], i['hash']]]

            if i['to'] == address:
                if i['from'] in txs_to_x:
                    txs_to_x[i['from']].append([i['timeStamp'], i['hash']])
                else:
                    txs_to_x[i['from']] = [[i['timeStamp'], i['hash']]]

        return txs_from_x, txs_to_x

    @staticmethod
    def get_names(search_adress):
        # matching_name = ''
        # with open("adress_to_names.csv") as f:
        #     for ln in f.readlines():
        #         adress, name = ln.split(",", 1)
        #         if adress.strip().lower() == search_adress:
        #             matching_name = name.strip()
        #             return matching_name

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
    for i in AllOutcomingTxs.get_address_transactions('0x7e46480d8e28c1d6c55be1b782084dd2c902f99f'):
        for tx in i:
            name = AllOutcomingTxs.get_names(tx.lower())
            if name:
                print(name)
            else:
                print(tx)
