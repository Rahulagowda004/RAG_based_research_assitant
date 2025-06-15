from scrapper import scrape_url
from retriever import retriever
from pathlib import Path

class Pipeline:
    def __init__(self):
        
        self.url = input("Enter the URL to scrape: ")
        self.output_dir, self.page_identifier = scrape_url(self.url)

        base_vector_db = Path(r"R:/TAZMIC/artifacts/Vector_databases")
        self.vector_db_path = base_vector_db / self.page_identifier

        self.retriever = retriever(
            markdown_path=Path(self.output_dir) / "content.md",  
            collection_name=self.page_identifier,
            directory=self.vector_db_path
        )
        
        