
from rest_framework import serializers

class SearchSerializer(serializers.Serializer):
    query = serializers.CharField(allow_blank=False)
    collection_name = serializers.CharField(required=False, default="documents",)
    top_k = serializers.IntegerField(required=False,default=3,)

class CollectionInfoSerializer(serializers.Serializer):
    collection_name = serializers.CharField(required=False, default="documents")

class DocumentChunksSerializer(serializers.Serializer):
    collection_name = serializers.CharField(required=False, default="documents")
    file_path = serializers.CharField(allow_blank=False)
    order_by_index = serializers.BooleanField(required=False, default=True)