from typing import Any, Type

from django.db.models.query import QuerySet
from rest_framework.mixins import ListModelMixin
from rest_framework.request import Request
from rest_framework.serializers import ModelSerializer


class CollectUserFromRequestMixin:
    def initial(self, request: Request, *args, **kwargs):
        super(CollectUserFromRequestMixin, self).initial(request, *args, **kwargs)
        if "user" not in request.data.keys():
            request.data["user"] = request.user.pk


class SearchAndListModelMixin(ListModelMixin):
    qstring_serializer_class: Type[ModelSerializer]

    def prepare_qstring_data(self) -> dict[str, Any]:
        return self.request.query_params.dict()

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        if self.action == "list":
            qstring_serializer = self.get_serializer(data=self.prepare_qstring_data())
            qstring_serializer.is_valid(raise_exception=True)
            return queryset.filter(**qstring_serializer.validated_data)
        else:
            return queryset

    def get_serializer_class(self) -> Type[ModelSerializer]:
        if self.action == "list":
            return self.qstring_serializer_class
        else:
            return super().get_serializer_class()


class SearchAndIndexModelMixin(SearchAndListModelMixin):
    def prepare_qstring_data(self) -> dict[str, Any]:
        qstring_data = self.request.query_params.dict()
        qstring_data.pop("index_key", None)
        return qstring_data

    def get_serializer(self, *args, **kwargs):
        if self.action == "list" and (args or "instance" in kwargs):
            kwargs.update({"index_key": self.request.query_params.get("index_key")})
        return super().get_serializer(*args, **kwargs)
