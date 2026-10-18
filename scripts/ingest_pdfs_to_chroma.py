
import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = PROJECT_ROOT / "data" / "discharge_summaries"
COLLECTION_NAME = "careloop_discharge_summaries"

load_dotenv(PROJECT_ROOT / ".env")

def main():
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is missing. Check your project .env file.")

    pdf_files = sorted(PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDFs found in {PDF_DIR}")

    embeddings = OpenAIEmbeddings(
        model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        add_start_index=True,
    )

    client = chromadb.HttpClient(host="localhost", port=8000)
    vector_store = Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        collection_metadata={"hnsw:space": "cosine"},
    )

    documents = []
    ids = []

    for pdf_path in pdf_files:
        patient_id = pdf_path.stem.removesuffix("_discharge_summary")
        pages = PyPDFLoader(str(pdf_path)).load()
        chunks = splitter.split_documents(pages)

        for chunk_index, chunk in enumerate(chunks):
            chunk.metadata.update(
                {
                    "patient_id": patient_id,
                    "source": pdf_path.name,
                    "chunk_index": chunk_index,
                    "synthetic": True,
                }
            )
            documents.append(chunk)
            ids.append(f"{pdf_path.stem}_chunk_{chunk_index}")

    if not documents:
        raise RuntimeError("No text chunks were extracted from the PDFs.")

    # Deterministic IDs make reruns update existing chunks rather than duplicate them.
    batch_size = 100
    for start in range(0, len(documents), batch_size):
        vector_store.add_documents(
            documents=documents[start : start + batch_size],
            ids=ids[start : start + batch_size],
        )
        print(f"Stored {min(start + batch_size, len(documents))}/{len(documents)} chunks")

    print(f"\nIngestion complete: {len(pdf_files)} PDFs, {len(documents)} chunks.")
    print(f"Chroma collection: {COLLECTION_NAME}")

if __name__ == "__main__":
    main()
