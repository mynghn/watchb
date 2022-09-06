import re
from typing import Literal

from django.core.validators import RegexValidator
from pycountry import countries
from rest_framework.serializers import ValidationError


class OnlyKoreanValidator(RegexValidator):
    def __init__(self, allowed: str | re.Pattern = []):
        super(OnlyKoreanValidator, self).__init__(regex=r"^[가-힣]*$", code="only-korean")
        self.allowed = allowed

    def __call__(self, value: str):
        super(OnlyKoreanValidator, self).__call__(self.preprocess(value))

    def preprocess(self, value: str) -> str:
        return re.sub(self.allowed, "", value)

    @property
    def message(self):
        return f"Only Korean and '{self.allowed}' pattern allowed"


class CountryCodeValidator:
    def __init__(self, code_type: Literal["alpha_2", "alpha_3", "numeric"]):
        self.code_type = code_type

    def __call__(self, value: str):
        if not countries.get(**{self.code_type: value}):
            raise ValidationError(
                f"ISO 3166-1 {self.code_type} code should be provided.",
                code="ISO-3166-1",
            )


def validate_kmdb_text(text: str) -> str:
    cleansed = re.sub(r"\s(!HS|!HE)\s", "", text)  # invalid characters from KMDb
    cleansed = re.sub(r"\s+", " ", cleansed)
    return cleansed
