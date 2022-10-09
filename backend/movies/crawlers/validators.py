import re
from typing import Literal

from django.core.validators import RegexValidator
from rest_framework.serializers import ValidationError

from .utils import ISO_3166_1


class OnlyKoreanValidator(RegexValidator):
    def __init__(self, allowed: str | re.Pattern = []):
        super(OnlyKoreanValidator, self).__init__(regex=r"^[가-힣]*$", code="only-korean")
        self.allowed = allowed

    def __call__(self, value: str):
        self._value = value
        super(OnlyKoreanValidator, self).__call__(self.preprocess(value))

    def preprocess(self, value: str) -> str:
        return re.sub(self.allowed, "", value)

    @property
    def message(self):
        return f"Only Korean and '{self.allowed}' pattern allowed but '{self._value}' encountered."


class CountryCodeValidator:
    def __init__(self, code_type: Literal["alpha_2", "alpha_3", "numeric"]):
        self.code_type = code_type

    def __call__(self, value: str):
        if not ISO_3166_1.get_country(**{self.code_type: value}):
            raise ValidationError(
                f"Valid ISO 3166-1 {self.code_type} code should be provided but '{value}' encountered.",
                code="invalid",
            )


def validate_kmdb_text(text: str) -> str:
    cleansed = re.sub(r"\s?(!HS|!HE)\s?", "", text)  # invalid characters from KMDb
    cleansed = re.sub(r"\s+", " ", cleansed)
    return cleansed.strip()


def get_person_en_name_regex():
    western_alphabets = r"a-zA-Z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u024F\u1E00-\u1EFF"
    name_chunk = rf"[{western_alphabets}0-9]['’]?[{western_alphabets}0-9]*[.,]?"
    last_name_chunk = rf"{name_chunk}[!]?"
    name_chunk = rf"({name_chunk}|'{name_chunk}'|\"{name_chunk}\")"
    last_name_chunk = rf"({last_name_chunk}|'{last_name_chunk}'|\"{last_name_chunk}\")"
    return rf"^({name_chunk}[ ])*{last_name_chunk}$"


PERSON_EN_NAME_REGEX = get_person_en_name_regex()
