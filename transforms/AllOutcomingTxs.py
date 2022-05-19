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

        def add_properties(some_entity, properties_list):
            counter = 0
            for i in properties_list:
                some_entity.addProperty(
                    'type' + str(counter),
                    displayName='type ' + str(counter),
                    value=f'{i[0]}'
                )

                some_entity.addProperty(
                    'direction' + str(counter),
                    displayName='direction ' + str(counter),
                    value=f'{i[1]}'
                )
                
                date = datetime.fromtimestamp(int(i[2]))
                some_entity.addProperty(
                    'time' + str(counter),
                    displayName='time ' + str(counter),
                    value=f'{date}'
                )

                some_entity.addProperty(
                    'hash' + str(counter),
                    displayName='hash ' + str(counter),
                    value=f'{i[3]}'
                )
                counter += 1

        def add_txs(txs, color, style):
            for tx in txs:
                name = cls.get_names(tx.strip().lower())
                if name:
                    entity = response.addEntity(Company, name)
                    entity.addProperty(
                        'address',
                        displayName='address',
                        value=f'{tx}'
                    )
                    add_properties(entity, txs[tx])

                else:
                    entity = response.addEntity(Person, tx)
                    add_properties(entity, txs[tx])
                    entity.setLinkColor(color)
                    entity.setLinkThickness(3)
                    entity.setLinkStyle(style)

        address = request.Value

        link_normal_txs = f'https://api.etherscan.io/api?module=account&action=tokentx&address={address}' \
                          f'&page=all&offset=100&startblock=0&endblock=27025780&sort=asc&apikey='
        normal_txs = cls.get_address_transactions(address, link_normal_txs, 'normal')

        # link_internal_txs = f'https://api.etherscan.io/api?module=account&action=txlistinternal&address={address}' \
        #                     f'&endblock=2702578&page=all&offset=10&sort=asc&apikey='
        # internal_txs_of_x = cls.get_address_transactions(address, link_internal_txs)

        link_ERC20 = f'https://api.etherscan.io/api?module=account&action=tokentx&address={address}' \
                     f'&page=all&offset=100&startblock=0&endblock=27025780&sort=asc&apikey='
        normal_n_ERC20_txs = cls.get_address_transactions(address, link_ERC20, 'ERC20', normal_txs)

        if normal_n_ERC20_txs:
            add_txs(normal_n_ERC20_txs, '#040404', 0)

    @staticmethod
    def get_address_transactions(raw_address, link, txs_type, result_dict=None):
        api_key = '9CA95D75FTTENE2CDY24J6WXXC1IZT8W4N'
        address = raw_address.lower()

        response_API = requests.get(link + api_key)

        data = response_API.text
        parse_json = json.loads(data)
        result = parse_json['result']

        message = parse_json['message']
        if message != "No transactions found":

            if result_dict:
                normal_txs = result_dict
            else:
                normal_txs = {}

            for i in result:
                if i['from'] == address:
                    if i['to'] in normal_txs:
                        normal_txs[i['to']].append([txs_type, 'received', i['timeStamp'], i['hash']])
                    else:
                        normal_txs[i['to']] = [[txs_type, 'received', i['timeStamp'], i['hash']]]

                elif i['to'] == address:
                    if i['from'] in normal_txs:
                        normal_txs[i['from']].append([txs_type, 'sent', i['timeStamp'], i['hash']])
                    else:
                        normal_txs[i['from']] = [[txs_type, 'sent', i['timeStamp'], i['hash']]]

            return normal_txs

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
                name = soup.find('span').string
                if name:
                    with open('adress_to_names.csv', 'a') as db:
                        writer = csv.writer(db)
                        eman = ' ' + name
                        line = [search_adress, eman]
                        writer.writerow(line)

                    return name


if __name__ == "__main__":
    # address = '0xb3065fE2125C413E973829108F23E872e1DB9A6b'
    # api_key = '9CA95D75FTTENE2CDY24J6WXXC1IZT8W4N'
    #
    # link_normal_txs = f'https://api.etherscan.io/api?module=account&action=tokentx&address={address}' \
    #                   f'&page=all&offset=100&startblock=0&endblock=27025780&sort=asc&apikey='
    # normal_txs = \
    #     AllOutcomingTxs.get_address_transactions(address, link_normal_txs + api_key, 'normal')
    #
    # link_ERC20 = f'https://api.etherscan.io/api?module=account&action=tokentx&address={address}' \
    #              f'&page=all&offset=100&startblock=0&endblock=27025780&sort=asc&apikey='
    # all_txs = \
    #     AllOutcomingTxs.get_address_transactions(address, link_ERC20 + api_key, 'ERC20', normal_txs)
    #
    # print(all_txs)
    print(AllOutcomingTxs.get_names('0xd90e2f925DA726b50C4Ed8D0Fb90Ad053324F31b'.strip().lower()))
