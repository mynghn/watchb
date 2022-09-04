from collections import OrderedDict
from typing import Any, Optional, Type

from django.db.models import Field as ModelField
from django.db.models import Model
from drf_writable_nested.mixins import BaseNestedModelSerializer
from rest_framework.serializers import Field as SerializerField
from rest_framework.serializers import ModelSerializer, ValidationError
from rest_framework.settings import api_settings


class GetOrSaveMixin(ModelSerializer):
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


class NestedThroughModelMixin(BaseNestedModelSerializer):
    def update_or_create_through_instance(
        self,
        instance: Model,
        serializer_field_name: str,
        model_field: ModelField,
        serializer_field: SerializerField,
    ):
        """
        Removed last process of update_or_create_reverse_relations(),
        which connects related instance w/ m2m related manger add().
        Instead for through models, try saving with parent model instance as a save kwarg
        """
        related_data = self.get_initial().get(serializer_field_name, None)
        if related_data is None:
            return

        instances = self._prefetch_related_instances(serializer_field, related_data)

        save_kwargs = self._get_save_kwargs(serializer_field_name)

        # Prepare parent model instance
        for f in model_field.remote_field.through._meta.fields:
            if related_model := getattr(f, "related_model", False):
                if isinstance(instance, related_model):
                    parent_instance_kwarg = {f.name: instance}
        assert parent_instance_kwarg

        new_related_instances = []
        errors = []
        for data in related_data:
            obj = instances.get(self._get_related_pk(data, serializer_field.Meta.model))
            serializer = self._get_serializer_for_field(
                serializer_field,
                instance=obj,
                data=data,
            )
            try:
                serializer.is_valid(raise_exception=True)
                through_instance = serializer.save(
                    **save_kwargs, **parent_instance_kwarg
                )
                # data["pk"] = through_instance.pk
                new_related_instances.append(through_instance)
                errors.append({})
            except ValidationError as exc:
                errors.append(exc.detail)

        if any(errors):
            raise ValidationError(
                {serializer_field_name: errors}, code="nested-through"
            )

    def has_through_model(self, model_field: ModelField) -> bool:
        return (
            model_field.many_to_many
            and getattr(model_field.remote_field, "through", False)
            and not model_field.remote_field.through._meta.auto_created
        )

    def update_or_create_reverse_relations(
        self,
        instance: Model,
        reverse_relations: OrderedDict[str, tuple[ModelField, SerializerField, str]],
    ):
        other_reverse_relations = OrderedDict()
        for field_name, (
            related_field,
            serializer_field,
            field_source,
        ) in reverse_relations.items():
            if self.has_through_model(related_field):
                self.update_or_create_through_instance(
                    instance=instance,
                    serializer_field_name=field_name,
                    model_field=related_field,
                    serializer_field=serializer_field,
                )
            else:
                other_reverse_relations[field_name] = (
                    related_field,
                    serializer_field,
                    field_source,
                )
        super().update_or_create_reverse_relations(instance, other_reverse_relations)


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
