from .milvus_client import MilvusClient
from .embedder import Embedder, create_embedding_function

milvus_client = MilvusClient(host="standalone", port=19530)
embedder = Embedder()
embedding_function = embedder.encode  # для DocumentProcessor