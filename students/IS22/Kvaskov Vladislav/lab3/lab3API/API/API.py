from mil.milvus_client import MilvusClient
from mil.embedder import Embedder

connect_milvus = MilvusClient(host="standalone", port=19530)

embedder = Embedder(model_name="intfloat/multilingual-e5-base",batch_size=32)

def search(query: str, top_k: int, collection_name: str ):
    query_embedding = embedder.encode_query(query)

    responce = connect_milvus.search(
        collection_name=collection_name,
        query_vectors=[query_embedding],
        top_k=top_k,
    )

    return responce[0] if responce else []

def collection_info(collection_name: str) -> dict:

    return connect_milvus.get_collection_info(collection_name)

def document_chunks(collection_name: str, file_path: str, order_by_index: bool = True) -> list[dict]:
   
    return connect_milvus.get_document_chunks(
        collection_name=collection_name,
        file_path=file_path,
        order_by_index=order_by_index
    )
    

