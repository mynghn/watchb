from typing import Any, Optional, Type

from django.db.models import Model, UniqueConstraint
from django.db.models.fields.related import RelatedField
from django.forms.models import model_to_dict
from rest_framework.serializers import ValidationError
from rest_framework.settings import api_settings


class GetOrSaveMixin:
    def save(self, **kwargs) -> Model:
        self.instance, extra_kwargs = self.search_instance(**self.validated_data)
        self.instance = super().save(**extra_kwargs | kwargs)
        return self.instance

    def search_instance(
        self, **validated_data
    ) -> tuple[Optional[Model], dict[str, Any]]:
        ModelClass: Type[Model] = self.Meta.model

        search_kwargs = {
            k: v
            for k, v in validated_data.items()
            if v is not None
            and k
            in {
                f.name
                for f in ModelClass._meta.fields
                if not isinstance(f, RelatedField)  # TODO: RelationField Search
            }
        }

        instances = []

        for model_field in ModelClass._meta.fields:
            if (
                model_field.unique
                and model_field.name in search_kwargs.keys()
                and (
                    fetched := ModelClass.objects.filter(
                        **{model_field.name: search_kwargs[model_field.name]}
                    )
                )
            ):
                if (inst := fetched.get()) not in instances:
                    instances.append(inst)

        if constraints := ModelClass._meta.constraints:
            for unique_contraint in [
                c for c in constraints if isinstance(c, UniqueConstraint)
            ]:
                if all(
                    fname in search_kwargs.keys() for fname in unique_contraint.fields
                ) and (
                    fetched := ModelClass.objects.filter(
                        **{
                            fname: search_kwargs[fname]
                            for fname in unique_contraint.fields
                        }
                    )
                ):
                    if (inst := fetched.get()) not in instances:
                        instances.append(inst)

        extra_kwargs = {
            k: v
            for inst in instances
            for k, v in model_to_dict(inst).items()
            if self.validated_data.get(k) not in {None, ""} and v not in {None, ""}
        }

        if len(instances) > 1:
            for idx, inst in enumerate(
                sorted(instances, key=lambda inst: inst.pk, reverse=True)
            ):
                if idx + 1 == len(instances):
                    instance = inst
                else:
                    inst.delete()
        elif len(instances) == 1:
            instance = instances.pop()
        else:
            instance = None

        return instance, extra_kwargs


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
