import os
import tempfile
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from pymilvus import utility

from .services import milvus_client, embedder, embedding_function
from .document_processor import DocumentProcessor
from .serializers import (
    FileUploadSerializer,
    SearchQuerySerializer,
    CollectionCreateSerializer,
    SearchResultSerializer
)


@api_view(['POST'])
def upload_file(request):
    """
    Загрузка файла, чанкирование, генерация эмбеддингов и сохранение в Milvus.
    """
    serializer = FileUploadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    uploaded_file = serializer.validated_data['file']
    collection_name = serializer.validated_data['collection_name']

    # Сохраняем файл во временную директорию
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp:
        for chunk in uploaded_file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    try:
        processor = DocumentProcessor(
            milvus_client=milvus_client,
            chunk_size=256,
            chunk_overlap=64,
            embedding_function=embedding_function
        )
        result = processor.process_file(tmp_path, collection_name)
    except Exception as e:
        result = {'success': False, 'error': str(e)}
    finally:
        os.unlink(tmp_path)  # удаляем временный файл

    if result['success']:
        return Response({
            'message': f"Файл обработан, загружено {result['chunks_count']} чанков",
            'chunks_count': result['chunks_count'],
            'inserted_ids': result.get('inserted_ids', [])
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': result.get('error', 'Неизвестная ошибка')},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def search(request):
    """
    Семантический поиск по коллекции.
    """
    serializer = SearchQuerySerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    q = serializer.validated_data['q']
    collection_name = serializer.validated_data['collection_name']
    top_k = serializer.validated_data['top_k']

    # Генерируем эмбеддинг запроса
    query_vector = embedder.encode_query(q)

    try:
        results = milvus_client.search(
            collection_name=collection_name,
            query_vectors=[query_vector],
            top_k=top_k
        )
        # results[0] – список результатов для одного запроса
        hits = results[0] if results else []
        serializer = SearchResultSerializer(hits, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def collections(request):
    if request.method == 'GET':
        try:
            collections = utility.list_collections()
            return Response({'collections': collections})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    elif request.method == 'POST':
        serializer = CollectionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        name = serializer.validated_data['name']
        dimension = serializer.validated_data['dimension']
        metric_type = serializer.validated_data['metric_type']
        
        try:
            milvus_client.create_collection(
                collection_name=name,
                dimension=dimension,
                metric_type=metric_type,
                description=f"Коллекция {name}"
            )
            return Response({'message': f'Коллекция {name} создана'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET'])
# def list_collections(request):
#     """
#     Список всех коллекций в Milvus.
#     """
#     try:
#         collections = utility.list_collections()
#         return Response({'collections': collections})
#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['POST'])
# def create_collection(request):
#     """
#     Создание новой коллекции.
#     """
#     serializer = CollectionCreateSerializer(data=request.data)
#     if not serializer.is_valid():
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     name = serializer.validated_data['name']
#     dimension = serializer.validated_data['dimension']
#     metric_type = serializer.validated_data['metric_type']

#     try:
#         milvus_client.create_collection(
#             collection_name=name,
#             dimension=dimension,
#             metric_type=metric_type,
#             description=f"Коллекция {name}"
#         )
#         return Response({'message': f'Коллекция {name} создана'}, status=status.HTTP_201_CREATED)
#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_collection(request, name):
    """
    Удаление коллекции.
    """
    try:
        milvus_client.delete_collection(name)
        return Response({'message': f'Коллекция {name} удалена'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)