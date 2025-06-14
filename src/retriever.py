import os
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from model import llm, embedding_model
from langchain_chroma import Chroma
from pathlib import Path
import os

def retriever(markdown_path:Path, directory: Path, collection_name: str):
    """Function to retrieve and process documents from a markdown file, split them into chunks, and store them in a vector database."""
    loader = UnstructuredMarkdownLoader(
        "R:/TAZMIC/artifacts/research_papers/biology/content.md",
        mode="single",
        strategy="fast",
    )

    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    pages_split = text_splitter.split_documents(docs) 

    persist_directory = r"R:/TAZMIC/artifacts/Vector_databases/biology"
    collection_name = "biology"

    if not os.path.exists(persist_directory):
        os.makedirs(persist_directory)