from functools import lru_cache
from pathlib import Path
from typing import cast

from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.core.schema import NodeWithScore
from llama_index.embeddings.voyageai import VoyageEmbedding

from app.config import get_settings

DATA_DIR = Path(__file__).parent.parent / "data"
DEFAULT_INDEX_DIR = DATA_DIR / "index"


@lru_cache
def load_index(index_dir: Path = DEFAULT_INDEX_DIR) -> VectorStoreIndex:
    # 1. Get settings (inside the function so config isn't build on import - cached settings are reused)
    settings = get_settings()

    # 2. Instantiate the embedding model from Voyage, with the model name and API key
    vo = VoyageEmbedding(
        model_name=settings.embedding_model, voyage_api_key=settings.voyage_api_key
    )

    # 3. Extract the index from storage
    storage_context = StorageContext.from_defaults(persist_dir=index_dir)

    # 4. Load the index
    index = load_index_from_storage(storage_context=storage_context, embed_model=vo)

    return index


def retrieve(question: str, top_k: int = 3) -> list[NodeWithScore]:
    # 1. Load the index
    index = load_index()

    # 2. Instantiate the retriever with the index, defining the amount of similar nodes needed (top_k: 3 is a default)
    retriever = index.as_retriever(similarity_top_k=top_k)

    # 3. Retrieve the nodes (chunks of text) with the highest similarity to the meaning of the question
    nodes = retriever.retrieve(question)

    return cast(list[NodeWithScore], nodes)


if __name__ == "__main__":
    nodes = retrieve("what is the due diligence defence?", 3)

    for n in nodes:
        print(f"Score: {n.score}")
        print(f"Text: {n.node.text}")
        print(f"Page Label: {n.node.metadata.get('page_label')}")
        print("\n")
