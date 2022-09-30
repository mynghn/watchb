import re
from typing import Optional

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class PasswordValidator(RegexValidator):
    code = "invalid"
    default_message = (
        "Password should contain at least 8 characters and "
        "two character types out of three (english alphabet, number, special character) types"
    )

    def __init__(self, message: Optional[str] = None):
        self.message = message or self.default_message

    def __call__(self, value: Optional[str]):
        if value is not None:
            en = re.compile(r"[a-z]", flags=re.IGNORECASE)
            num = re.compile(r"[0-9]")
            special_char = re.compile(r"[^a-z0-9]", flags=re.IGNORECASE)
            if (
                len(value) >= 8
                and sum(map(lambda p: bool(p.search(value)), [en, num, special_char]))
                >= 2
            ):
                return
        raise ValidationError(self.message, code=self.code)
