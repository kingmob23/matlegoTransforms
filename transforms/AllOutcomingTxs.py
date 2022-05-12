from maltego_trx.entities import Person, Company
from maltego_trx.maltego import UIM_PARTIAL
from maltego_trx.transform import DiscoverableTransform
import requests
import json


class AllOutcomingTxs(DiscoverableTransform):
    """
    Lookup the all outcoming txs from address.
    """

    @classmethod
    def create_entities(cls, request, response):
        address = request.Value

        try:
            txs_from_x = cls.get_address_transactions(address)
            if txs_from_x:
                for tx in txs_from_x:
                    name = cls.get_names(tx)
                    if name:
                        response.addEntity(Company, name)
                    else:
                        response.addEntity(Person, tx)
            else:
                response.addUIMessage('probably bad address')
        except IOError:
            response.addUIMessage("An error occurred reading the CSV file.", messageType=UIM_PARTIAL)

    @staticmethod
    def get_address_transactions(raw_address):
        api_key = ''
        address = raw_address.lower()

        response_API = requests.get(
            f'https://api.etherscan.io/api?module=account&action=tokentx&address={address}&page=all&offset=100&startblock=0&endblock=27025780&sort=asc&apikey={api_key}')

        data = response_API.text
        parse_json = json.loads(data)
        result = parse_json['result']

        txs_from_x = []
        txs_to_x = []
        for i in result:
            if i['from'] == address:
                txs_from_x.append(i['to'])
            if i['to'] == address:
                txs_to_x.append(i['from'])

        return txs_from_x

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
    for i in AllOutcomingTxs.get_address_transactions('0xb3065fE2125C413E973829108F23E872e1DB9A6b'):
        name = AllOutcomingTxs.get_names(i)
        if name:
            print(name)
        else:
            print(i)
