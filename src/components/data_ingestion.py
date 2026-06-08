import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

class DataIngestion:
    def __init__(self, pdf_path="data/college_pdf.pdf", persist_dir="./student_db"):
        self.pdf_path = pdf_path
        self.persist_dir = persist_dir
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    def ingest(self):
        """Loads PDF, splits it into chunks, and persists to Chroma DB if not already present."""
        if not os.path.exists(self.pdf_path):
            print(f"⚠️ Warning: Reference source file '{self.pdf_path}' was not found.")
            return None

        # Check if DB directory exists and is populated
        if os.path.exists(self.persist_dir) and len(os.listdir(self.persist_dir)) > 0:
            print("✅ Vector Store directory already exists. Loading existing instance.")
            return Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings,
                collection_name="college_documents"
            )

        print("🚀 Starting Data Ingestion from PDF...")
        loader = PyPDFLoader(self.pdf_path)
        documents = loader.load()
        print(f"✅ Pages Loaded: {len(documents)}")

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(documents)
        print(f"✅ Chunks Created: {len(chunks)}")

        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_dir,
            collection_name="college_documents"
        )
        print("✅ Vector Store Created and Persisted successfully.")
        return vector_store

    def get_retriever(self):
        """Returns the retriever instance from the persistent vector store."""
        vector_store = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embeddings,
            collection_name="college_documents"
        )
        return vector_store.as_retriever(search_kwargs={"k": 3})
