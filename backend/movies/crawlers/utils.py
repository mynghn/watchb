import requests
from bs4 import BeautifulSoup


class ISO_3166_1:
    url = "https://ko.wikipedia.org/wiki/ISO_3166-1"

    _book: dict
    name_key: str
    numeric_key: str
    alpha2_key: str
    alpha3_key: str

    @classmethod
    def _setup(cls):
        response = requests.get(cls.url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.table.findChildren("tr")
        keys = [header.text.rstrip() for header in rows.pop(0).findChildren("th")]
        (
            cls.name_key,
            cls.numeric_key,
            cls.alpha_2_key,
            cls.alpha_3_key,
        ) = keys

        cls._book = {}
        for row in rows:
            country = {}
            for idx, cell in enumerate(row.findChildren("td")):
                country[keys[idx]] = cell.text.strip().upper()
            for v in country.values():
                cls._book[v] = country

    @classmethod
    def get_country(cls, key: str) -> dict[str, str]:
        if not getattr(cls, "_book", False):
            cls._setup()

        return cls._book.get(key.upper(), {})
