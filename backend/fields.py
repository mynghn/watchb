from typing import Container, Optional, Type

from django.forms.models import model_to_dict
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer


class ModelSerializePrimaryKeyRelatedField(PrimaryKeyRelatedField):
    def __init__(self, **kwargs):
        self.model_serializer_class: Optional[Type[ModelSerializer]] = kwargs.pop(
            "model_serializer_class", None
        )
        if not self.model_serializer_class:
            self.model_serialize_fields: Optional[Container[str]] = kwargs.pop(
                "model_serialize_fields", None
            )
        super().__init__(**kwargs)

    def to_representation(self, value):
        if self.model_serializer_class is not None:
            return self.model_serializer_class(value).to_representation(value)
        else:
            return model_to_dict(value, fields=self.model_serialize_fields)
