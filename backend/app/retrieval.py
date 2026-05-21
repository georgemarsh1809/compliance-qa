from pathlib import Path
from typing import cast

from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.core.schema import NodeWithScore
from llama_index.embeddings.voyageai import VoyageEmbedding

from app.config import get_settings

DATA_DIR = Path(__file__).parent.parent / "data"
DEFAULT_INDEX_DIR = DATA_DIR / "index"


def load_index(index_dir: Path = DEFAULT_INDEX_DIR) -> VectorStoreIndex:
    settings = get_settings()

    vo = VoyageEmbedding(
        model_name=settings.embedding_model, voyage_api_key=settings.voyage_api_key
    )

    storage_context = StorageContext.from_defaults(persist_dir=index_dir)
    index = load_index_from_storage(storage_context=storage_context, embed_model=vo)

    return index


def retrieve(question: str, top_k: int = 3) -> list[NodeWithScore]:
    index = load_index()

    retriever = index.as_retriever(similarity_top_k=top_k)
    nodes = retriever.retrieve(question)

    return cast(list[NodeWithScore], nodes)


if __name__ == "__main__":
    nodes = retrieve("what is the due diligence defence?", 3)

    for n in nodes:
        print(f"Score: {n.score}")
        print(f"Text: {n.node.text}")
        print(f"Page Label: {n.node.metadata.get('page_label')}")
        print("\n")
