from rest_framework.views import APIView
from .serializers import SearchSerializer,CollectionInfoSerializer,DocumentChunksSerializer
from rest_framework.response import Response
from rest_framework import status
from .API import search,collection_info, document_chunks

# Create your views here.

class SearchView(APIView):
    def post(self, request):
        serializer = SearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        hits = search(
            query=data["query"],
            top_k=data["top_k"],
            collection_name=data["collection_name"],
        )

        return Response(
            {"results": hits},
            status=status.HTTP_200_OK
        )
    
class CollectionInfoView(APIView):
    def get(self, request):
        serializer = CollectionInfoSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        info = collection_info(collection_name=data["collection_name"])

        return Response(info, status=status.HTTP_200_OK)

class DocumentChunksView(APIView):
    def get(self, request):
        serializer = DocumentChunksSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        chunks = document_chunks(
            collection_name=data["collection_name"],
            file_path=data["file_path"],
            order_by_index=data["order_by_index"],
        )

        return Response({"chunks": chunks}, status=status.HTTP_200_OK)

