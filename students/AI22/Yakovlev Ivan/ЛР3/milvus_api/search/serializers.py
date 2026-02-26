from rest_framework import serializers

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    collection_name = serializers.CharField(max_length=255)

class SearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(required=True)
    collection_name = serializers.CharField(required=True)
    top_k = serializers.IntegerField(default=5, min_value=1, max_value=20)

class CollectionCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    dimension = serializers.IntegerField(default=768)
    metric_type = serializers.ChoiceField(choices=["COSINE", "L2", "IP"], default="COSINE")

class SearchResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    distance = serializers.FloatField()
    text = serializers.CharField()
    file_name = serializers.CharField()
    file_path = serializers.CharField()
    chunk_index = serializers.IntegerField()