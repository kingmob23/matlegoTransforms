from maltego_trx.entities import Person, Company
from maltego_trx.maltego import UIM_PARTIAL
from maltego_trx.transform import DiscoverableTransform
import requests
import json
from datetime import datetime


class AllOutcomingTxs(DiscoverableTransform):
    """
    Lookup the all outcoming txs from address.
    """

    @classmethod
    def create_entities(cls, request, response):

        def add_txs(txs, color):
            for tx in txs:
                name = cls.get_names(tx)
                if name:
                    response.addEntity(Company, name)
                else:
                    entity = response.addEntity(Person, tx)
                    for i in txs[tx]:
                        date = datetime.fromtimestamp(int(i[0]))
                        entity.addProperty(
                            'time',
                            displayName='time',
                            value=f'{date}'
                        )
                        entity.addProperty(
                            'hash',
                            displayName='hash',
                            value=f'{i[1]}'
                        )
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
        matching_name = ''
        with open("adress_to_names.csv") as f:
            for ln in f.readlines():
                adress, name = ln.split(",", 1)
                if adress.strip().lower() == search_adress.strip().lower():
                    matching_name = name.strip()
        return matching_name


if __name__ == "__main__":
    for i in AllOutcomingTxs.get_address_transactions('0x7e46480d8e28c1d6c55be1b782084dd2c902f99f'):
        name = AllOutcomingTxs.get_names(i)
        if name:
            print(name)
        else:
            print(i)
