from rest_framework.serializers import ListSerializer

from mixins.serializer import SkipChildsMixin


class SkipChildsListSerializer(SkipChildsMixin, ListSerializer):
    pass
