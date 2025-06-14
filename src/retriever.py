import os
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from model import llm, embedding_model
from langchain_chroma import Chroma
from pathlib import Path
import os

def retriever(markdown_path:Path, directory: Path, collection_name: str) -> object:
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
        
    try:
        vectorstore = Chroma.from_documents(
            documents=pages_split,
            embedding=embedding_model,
            persist_directory=persist_directory,
            collection_name=collection_name
        )
        print(f"Created ChromaDB vector store!")
        
    except Exception as e:
        print(f"Error setting up ChromaDB: {str(e)}")
        raise


    # Now we create our retriever 
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 20}
    )
    
    return retriever