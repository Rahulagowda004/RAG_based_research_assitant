from scrapper import scrape_url
from retriever import retriever
from pathlib import Path
from mas import CreateRagAgent

class Pipeline:
    def __init__(self):
        
        print(f"{'*'*25}scrapper initialized{'*'*25}")
        self.url = input("Enter the URL to scrape: ")
        self.output_dir, self.page_identifier = scrape_url(self.url)
        print(f"{'*'*25}scrapper completed{'*'*25}")

        print(f"{'*'*25}retriever initialized{'*'*25}")
        base_vector_db = Path(r"R:/TAZMIC/artifacts/Vector_databases")
        self.vector_db_path = base_vector_db / self.page_identifier
        self.retriever = retriever(
            markdown_path=Path(self.output_dir) / "content.md",  
            collection_name=self.page_identifier,
            directory=self.vector_db_path
        )
        print(f"{'*'*25}retriever completed{'*'*25}")
        
        print(f"{'*'*25}RAG agent initialized{'*'*25}")
        self.rag_agent = CreateRagAgent(
            retriever=self.retriever
        )
        print(f"{'*'*25}RAG agent completed{'*'*25}")
    
    def query(self, question: str) -> str:
        """
        Query the RAG agent with a question
        """
        return self.rag_agent.query_agent(question)
    
    def run_interactive_session(self):
        """
        Start an interactive Q&A session
        """
        self.rag_agent.run_console_agent()
    
    def process_multiple_queries(self, questions: list) -> dict:
        """
        Process multiple questions and return results
        """
        results = {}
        for i, question in enumerate(questions, 1):
            print(f"\nProcessing question {i}/{len(questions)}: {question}")
            results[question] = self.rag_agent.query_agent(question)
        return results

if __name__ == "__main__":
    pipeline = Pipeline()
    
    # Option 1: Single query
    # response = pipeline.query("What is this document about?")
    # print(f"Response: {response}")
    
    # Option 2: Interactive session
    pipeline.run_interactive_session()
    
    # Option 3: Multiple queries
    # questions = [
    #     "What is the main topic?",
    #     "What are the key points?",
    #     "Can you summarize this?"
    # ]
    # results = pipeline.process_multiple_queries(questions)
    # for question, answer in results.items():
    #     print(f"Q: {question}")
    #     print(f"A: {answer}\n")