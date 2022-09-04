from typing import Any, Optional, Type

from django.db.models import Model
from rest_framework.serializers import ValidationError
from rest_framework.settings import api_settings


class GetOrSaveMixin:
    def save(self, **kwargs) -> Model:
        return self.get_instance(**self.validated_data, **kwargs) or super().save(
            **kwargs
        )

    def get_instance(self, **search_kwargs) -> Optional[Model]:
        ModelClass: Type[Model] = self.Meta.model
        if ModelClass._meta.unique_together and set(
            ModelClass._meta.unique_together
        ).issubset(set(search_kwargs.keys())):
            search_kwargs = {
                fname: search_kwargs[fname]
                for fname in ModelClass._meta.unique_together
            }
        for model_field in ModelClass._meta.fields:
            if model_field.unique and model_field.name in search_kwargs.keys():
                search_kwargs = {model_field.name: search_kwargs[model_field.name]}

        try:
            return ModelClass.objects.get(**search_kwargs)
        except ModelClass.DoesNotExist:
            return


class IDsFromAPIValidateMixin:
    api_id_fields: set[str]

    def validate(self, attrs: dict[str, Any]):
        # API id check
        if not self.api_id_fields & set(attrs.keys()):
            raise ValidationError(
                {
                    api_settings.NON_FIELD_ERRORS_KEY: [
                        f"At least one of {self.api_id_fields} should be provided"
                    ]
                },
                code="required",
            )
        return super().validate(attrs)
