from collections import OrderedDict, defaultdict
from itertools import chain
from typing import Any, Container, Iterable, Mapping, Optional, Type

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Manager, Model, UniqueConstraint
from django.db.models.fields.related import RelatedField
from django.forms.models import model_to_dict
from drf_writable_nested.mixins import NestedCreateMixin
from rest_framework.fields import SkipField, get_error_detail, set_value
from rest_framework.serializers import (
    LIST_SERIALIZER_KWARGS,
    BaseSerializer,
    ListSerializer,
    Serializer,
    ValidationError,
)
from rest_framework.settings import api_settings
from rest_framework.utils.html import is_html_input, parse_html_list
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

from decorators import lazy_load_property


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


class RequiredTogetherMixin:
    class Meta:
        required_together_fields: Iterable[str]

    def validate(self, attrs: dict[str, Any]):
        # API id check
        if all(attrs.get(f) in (None, "") for f in self.Meta.required_together_fields):
            raise ValidationError(
                {
                    api_settings.NON_FIELD_ERRORS_KEY: [
                        f"At least one of {self.Meta.required_together_fields} needed"
                    ]
                },
                code="required",
            )
        return super().validate(attrs)


class CollectSkippedErrorsMixin:
    skipped_field_errors: OrderedDict
    skipped_child_errors: list

    def merge_serializer_errors(self, *serializer_errors):
        return {
            fname: self.merge_serializer_errors(
                *map(lambda err: err.get(fname, {}), serializer_errors)
            )
            if any(
                (ferr := err.get(fname, [])) and isinstance(ferr, dict)
                for err in serializer_errors
            )
            else list(
                chain.from_iterable(
                    map(lambda err: err.get(fname, []), serializer_errors)
                )
            )
            for fname in chain(*serializer_errors)
        }

    @lazy_load_property
    def skipped_errors(self) -> dict | list[dict]:
        if isinstance(self, SkipChildsMixin):
            return getattr(self, "skipped_child_errors", [])
        else:
            skipped_field_errors = getattr(self, "skipped_field_errors", {})
            nested_errors = {
                fname: nested_errors
                for fname, field in self.fields.items()
                if isinstance(field, BaseSerializer)
                and (nested_errors := getattr(field, "skipped_errors", False))
            }
            intersections = {}
            for fname in skipped_field_errors.keys():
                if fname in nested_errors.keys():
                    skipped_field_err = skipped_field_errors[fname]
                    nested_err = nested_errors[fname]
                    assert type(skipped_field_err) == type(nested_err)
                    if isinstance(nested_err, dict):
                        merged = self.merge_serializer_errors(
                            skipped_field_err, nested_err
                        )
                    elif (
                        isinstance(nested_err, list)
                        and (len(skipped_field_err) == len(nested_err))
                        and all(isinstance(err, dict) for err in nested_err)
                    ):
                        merged = [
                            self.merge_serializer_errors(*errors)
                            for errors in zip(skipped_field_err, nested_err)
                        ]
                    else:
                        raise TypeError(
                            f"Undefined serializer error type encountered: {type(nested_err)}"
                        )
                    intersections[fname] = merged
            return skipped_field_errors | nested_errors | intersections

    @skipped_errors.deleter
    def skipped_errors(self):
        del self._skipped_errors
        if hasattr(self, "skipped_field_errors"):
            del self.skipped_field_errors
        if hasattr(self, "skipped_child_errors"):
            del self.skipped_child_errors
        if isinstance(self, Serializer):
            for f in self.fields.values():
                if isinstance(f, BaseSerializer) and getattr(
                    f, "skipped_errors", False
                ):
                    del f.skipped_errors


class SkipFieldsMixin(CollectSkippedErrorsMixin):
    skipped_field_errors: OrderedDict

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
            self.skipped_field_errors = skippable_errors

        return ret


class SkipChildsMixin(CollectSkippedErrorsMixin):
    skipped_child_errors: list

    def to_internal_value(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        List of dicts of native values <- List of dicts of primitive datatypes.
        """
        if is_html_input(data):
            data = parse_html_list(data, default=[])

        if not isinstance(data, list):
            message = self.error_messages["not_a_list"].format(
                input_type=type(data).__name__
            )
            raise ValidationError(
                {api_settings.NON_FIELD_ERRORS_KEY: [message]}, code="not_a_list"
            )

        if not self.allow_empty and len(data) == 0:
            message = self.error_messages["empty"]
            raise ValidationError(
                {api_settings.NON_FIELD_ERRORS_KEY: [message]}, code="empty"
            )

        if self.max_length is not None and len(data) > self.max_length:
            message = self.error_messages["max_length"].format(
                max_length=self.max_length
            )
            raise ValidationError(
                {api_settings.NON_FIELD_ERRORS_KEY: [message]}, code="max_length"
            )

        if self.min_length is not None and len(data) < self.min_length:
            message = self.error_messages["min_length"].format(
                min_length=self.min_length
            )
            raise ValidationError(
                {api_settings.NON_FIELD_ERRORS_KEY: [message]}, code="min_length"
            )

        ret = []
        errors = []

        for item in data:
            try:
                if getattr(self.child, "skipped_errors", False):
                    import ipdb

                    ipdb.set_trace()
                validated = self.child.run_validation(item)
            except ValidationError as exc:
                err = exc.detail
            else:
                ret.append(validated)
                err = {}
            if getattr(self.child, "skipped_errors", False):
                assert isinstance(self.child, CollectSkippedErrorsMixin)
                err = self.child.merge_serializer_errors(self.child.skipped_errors, err)
                del self.child.skipped_errors
            errors.append(err)

        if any(errors):
            self.skipped_child_errors = errors  # do not raise errors

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


class SkipChildsListSerializer(SkipChildsMixin, ListSerializer):
    pass


class IndexedListSerializer(ListSerializer):
    def __init__(self, *args, **kwargs):
        index_key = kwargs.pop("index_key")
        super().__init__(*args, **kwargs)
        if index_key and index_key not in (
            indexable_fields := self.child.Meta.indexable_fields
            if hasattr(self.child, "Meta")
            and hasattr(self.child.Meta, "indexable_fields")
            else {f.source for f in self.child._readable_fields}
        ):
            raise ValueError(
                f"index_key '{index_key}' not in indexable_fields {indexable_fields}"
            )
        self.index_key = index_key

    def to_representation(self, data):
        """
        List of object instances -> List of dicts of primitive datatypes.
        """
        # Dealing with nested relationships, data can be a Manager,
        # so, first get a queryset from the Manager if needed
        iterable = data.all() if isinstance(data, Manager) else data
        if self.index_key:
            idx_representation = {
                "index_key": self.index_key,
                "results": defaultdict(list),
            }
            for item in iterable:
                if isinstance(item, Model):
                    if hasattr(item, self.index_key):
                        idx_field = getattr(item, self.index_key)
                        if isinstance(idx_field, Model):
                            idx_key = idx_field.pk  # use related model pk as index
                        else:
                            idx_key = idx_field
                    else:
                        raise ValueError(
                            f"Cannot find index key '{self.index_key}' in model '{item.__class__.__name__}' attributes"
                        )
                else:
                    if self.index_key in item.keys():
                        idx_key = item[self.index_key]
                    else:
                        raise ValueError(
                            f"Cannot find index key '{self.index_key}' in mapping {item} keys"
                        )
                idx_representation["results"][idx_key].append(
                    self.child.to_representation(item)
                )
            return idx_representation
        else:
            return [self.child.to_representation(item) for item in iterable]

    @property
    def data(self):
        ret = super(ListSerializer, self).data
        if isinstance(ret, dict):
            return ReturnDict(ret, serializer=self)
        elif isinstance(ret, list):
            return ReturnList(ret, serializer=self)


class UseIndexedListSerializerMixin:
    @classmethod
    def many_init(cls, *args, **kwargs):
        index_key = kwargs.pop("index_key", None)
        allow_empty = kwargs.pop("allow_empty", None)
        max_length = kwargs.pop("max_length", None)
        min_length = kwargs.pop("min_length", None)
        child_serializer = cls(*args, **kwargs)
        list_kwargs = {
            "child": child_serializer,
        }
        list_kwargs["index_key"] = index_key
        if allow_empty is not None:
            list_kwargs["allow_empty"] = allow_empty
        if max_length is not None:
            list_kwargs["max_length"] = max_length
        if min_length is not None:
            list_kwargs["min_length"] = min_length
        list_kwargs.update(
            {
                key: value
                for key, value in kwargs.items()
                if key in LIST_SERIALIZER_KWARGS
            }
        )
        return IndexedListSerializer(*args, **list_kwargs)
