from maltego_trx.entities import Company
from maltego_trx.maltego import UIM_PARTIAL
from maltego_trx.transform import DiscoverableTransform


class NameFromAdressCSV(DiscoverableTransform):
    """
    Lookup the project name associated with blockchain adress number.
    """

    @classmethod
    def create_entities(cls, request, response):
        adress = request.Value

        try:
            names = cls.get_names(adress)
            if names:
                for name in names:
                    response.addEntity(Company, name)
            else:
                response.addUIMessage("The adress number given did not match any numbers in the CSV file")
        except IOError:
            response.addUIMessage("An error occurred reading the CSV file.", messageType=UIM_PARTIAL)

    @staticmethod
    def get_names(search_adress):
        matching_names = []
        with open("adress_to_names.csv") as f:
            for ln in f.readlines():
                adress, name = ln.split(",", 1)
                if adress.strip().lower() == search_adress.strip():
                    matching_names.append(name.strip())
        return matching_names


if __name__ == "__main__":
    print(NameFromAdressCSV.get_names('0xd90e2f925da726b50c4ed8d0fb90ad053324f31b'))
