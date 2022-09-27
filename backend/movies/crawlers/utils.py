import requests
from bs4 import BeautifulSoup


class ISO_3166_1:
    url = "https://ko.wikipedia.org/wiki/ISO_3166-1"

    _book: dict[str, dict[str, dict[str, str]]]
    name_key = "name"
    numeric_key = "numeric"
    alpha_2_key = "alpha_2"
    alpha_3_key = "alpha_3"

    @classmethod
    def _setup(cls):
        response = requests.get(cls.url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.table.findChildren("tr")

        keys = [cls.name_key, cls.numeric_key, cls.alpha_3_key, cls.alpha_2_key]

        cls._book = {k: {} for k in keys}
        for row in rows[1:]:
            country = {}
            for idx, cell in enumerate(row.findChildren("td")):
                country[keys[idx]] = cell.text.strip().upper()
            for k, v in country.items():
                cls._book[k][v] = country

        cls._setup_exceptions()

    @classmethod
    def _setup_exceptions(cls):
        # 유고슬라비아
        yugoslavia = {
            cls.name_key: "유고슬라비아",
            cls.numeric_key: "891",
            cls.alpha_2_key: "YU",
            cls.alpha_3_key: "YUG",
        }
        for k, v in yugoslavia.items():
            cls._book[k][v] = yugoslavia

    @classmethod
    def get_country(cls, **kwargs) -> dict[str, str]:
        if len(kwargs) != 1:
            raise ValueError("Only one search criterion is allowed")

        if not getattr(cls, "_book", False):
            cls._setup()

        criterion, value = list(kwargs.items()).pop()

        return cls._book[criterion].get(value.upper(), {})
