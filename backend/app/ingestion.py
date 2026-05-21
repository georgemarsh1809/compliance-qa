from pathlib import Path

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.voyageai import VoyageEmbedding

from app.config import get_settings

DATA_DIR = Path(__file__).parent.parent / "data"
DEFAULT_CORPUS_DIR = DATA_DIR / "corpus"
DEFAULT_INDEX_DIR = DATA_DIR / "index"


def build_index(corpus_dir: Path = DEFAULT_CORPUS_DIR, index_dir: Path = DEFAULT_INDEX_DIR) -> None:
    # Get the settings for the project: pull the embedding model and voyage API key from the .env
    settings = get_settings()

    # 1. Extract the corpus text from the PDF
    reader = SimpleDirectoryReader(input_dir=corpus_dir)
    document = reader.load_data()

    # 2. Instantiate the SentenceSplitter that will chunk the text (with overlap) when the index is built
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)

    # 3. Instantiate the embedding model from Voyage, with the model name and API key
    vo = VoyageEmbedding(
        model_name=settings.embedding_model, voyage_api_key=settings.voyage_api_key
    )

    # 4. Pass the corpus text, the splitter and the embedding model to the VSI to create a Vector Index
    vsi = VectorStoreIndex.from_documents(document, embed_model=vo, transformations=[splitter])

    # 5. Store the index, so it only has to happen once
    vsi.storage_context.persist(persist_dir=index_dir)

    print("embedded")


# "If I'm being run and not just imported"
if __name__ == "__main__":
    build_index()
