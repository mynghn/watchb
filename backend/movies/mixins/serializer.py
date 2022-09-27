from collections import OrderedDict
from typing import Any, Container, Mapping, Optional, Type

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Model, UniqueConstraint
from django.db.models.fields.related import RelatedField
from django.forms.models import model_to_dict
from drf_writable_nested.mixins import NestedCreateMixin
from rest_framework.fields import SkipField, get_error_detail, set_value
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
    class Meta:
        api_id_fields: set[str]

    def validate(self, attrs: dict[str, Any]):
        # API id check
        if not self.Meta.api_id_fields & set(attrs.keys()):
            raise ValidationError(
                {
                    api_settings.NON_FIELD_ERRORS_KEY: [
                        f"At least one of {self.Meta.api_id_fields} should be provided"
                    ]
                },
                code="required",
            )
        return super().validate(attrs)


class SkipFieldsMixin:
    class Meta:
        can_skip_fields: Container[str]

    def to_internal_value(self, data: Mapping) -> OrderedDict[str, Any]:
        """
        Dict of native values <- Dict of primitive datatypes.
        """
        if not isinstance(data, Mapping):
            message = self.error_messages["invalid"].format(
                datatype=type(data).__name__
            )
            raise ValidationError(
                {api_settings.NON_FIELD_ERRORS_KEY: [message]}, code="invalid"
            )

        ret = OrderedDict()
        errors = OrderedDict()
        skippable_errors = OrderedDict()
        fields = self._writable_fields
        can_skip_fields = getattr(getattr(self, "Meta", None), "can_skip_fields", set())

        for field in fields:
            validate_method = getattr(self, "validate_" + field.field_name, None)
            primitive_value = field.get_value(data)
            try:
                validated_value = field.run_validation(primitive_value)
                if validate_method is not None:
                    validated_value = validate_method(validated_value)
            except ValidationError as exc:
                if field.field_name in can_skip_fields:
                    skippable_errors[field.field_name] = exc.detail
                else:
                    errors[field.field_name] = exc.detail
            except DjangoValidationError as exc:
                err_detail = get_error_detail(exc)
                if field.field_name in can_skip_fields:
                    skippable_errors[field.field_name] = err_detail
                else:
                    errors[field.field_name] = err_detail
            except SkipField:
                pass
            else:
                set_value(ret, field.source_attrs, validated_value)

        if errors:
            raise ValidationError(errors)

        if skippable_errors:
            self.skipped_errors = ValidationError(skippable_errors).detail

        return ret


class NestedCreateMixin(NestedCreateMixin):
    def update_or_create_direct_relations(self, attrs, relations):
        for field_name, (field, field_source) in relations.items():
            obj = None
            data = self.validated_data[field_name]  # use only validated_data
            model_class = field.Meta.model
            pk = self._get_related_pk(data, model_class)
            if pk:
                obj = model_class.objects.filter(
                    pk=pk,
                ).first()
            serializer = self._get_serializer_for_field(
                field,
                instance=obj,
                data=data,
            )

            try:
                serializer.is_valid(raise_exception=True)
                attrs[field_source] = serializer.save(
                    **self._get_save_kwargs(field_name)
                )
            except ValidationError as exc:
                raise ValidationError({field_name: exc.detail})

    def update_or_create_reverse_relations(self, instance, reverse_relations):
        # Update or create reverse relations:
        # many-to-one, many-to-many, reversed one-to-one
        for field_name, (
            related_field,
            field,
            field_source,
        ) in reverse_relations.items():

            # Skip processing for empty data or not-specified field.
            # The field can be defined in validated_data but isn't defined
            # in initial_data (for example, if multipart form data used)
            related_data = self.validated_data.get(field_name, None)
            if related_data is None:
                continue

            if related_field.one_to_one:
                # If an object already exists, fill in the pk so
                # we don't try to duplicate it
                pk_name = field.Meta.model._meta.pk.attname
                if pk_name not in related_data and "pk" in related_data:
                    pk_name = "pk"
                if pk_name not in related_data:
                    related_instance = getattr(instance, field_source, None)
                    if related_instance:
                        related_data[pk_name] = related_instance.pk

                # Expand to array of one item for one-to-one for uniformity
                related_data = [related_data]

            instances = self._prefetch_related_instances(field, related_data)

            save_kwargs = self._get_save_kwargs(field_name)
            if isinstance(related_field, GenericRelation):
                save_kwargs.update(
                    self._get_generic_lookup(instance, related_field),
                )
            elif not related_field.many_to_many:
                save_kwargs[related_field.name] = instance

            new_related_instances = []
            errors = []
            for data in related_data:
                obj = instances.get(self._get_related_pk(data, field.Meta.model))
                serializer = self._get_serializer_for_field(
                    field,
                    instance=obj,
                    data=data,
                )
                try:
                    serializer.is_valid(raise_exception=True)
                    related_instance = serializer.save(**save_kwargs)
                    data["pk"] = related_instance.pk
                    new_related_instances.append(related_instance)
                    errors.append({})
                except ValidationError as exc:
                    errors.append(exc.detail)

            if any(errors):
                if related_field.one_to_one:
                    raise ValidationError({field_name: errors[0]})
                else:
                    raise ValidationError({field_name: errors})

            if related_field.many_to_many:
                # Add m2m instances to through model via add
                m2m_manager = getattr(instance, field_source)
                m2m_manager.add(*new_related_instances)
