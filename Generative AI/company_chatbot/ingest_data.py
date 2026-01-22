import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
import chromadb
from chromadb.config import Settings

# Load environment variables
load_dotenv()

# Constants
DATA_PATH = "data"
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "company_docs"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def load_documents():
    """Load all documents from the data directory"""
    print("Loading documents from data/ folder...")
    
    loader = DirectoryLoader(
        DATA_PATH,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True
    )
    
    documents = loader.load()
    print(f"Loaded {len(documents)} documents")
    return documents


def split_documents(documents):
    """Split documents into smaller chunks for better retrieval"""
    print("Splitting documents into chunks...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")
    return chunks


def create_vector_store(chunks):
    """Create and persist vector store with document embeddings"""
    print("Creating vector store with ChromaDB...")
    
    # Initialize ChromaDB with persistent storage
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    # Delete existing collection if it exists
    try:
        client.delete_collection(COLLECTION_NAME)
    except:
        pass
    
    # Create a new collection (uses ChromaDB's default embedding)
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    
    # Add documents to the collection
    texts = [doc.page_content for doc in chunks]
    metadatas = [doc.metadata for doc in chunks]
    ids = [f"doc_{i}" for i in range(len(chunks))]
    
    # Add in batches to avoid memory issues
    batch_size = 10
    for i in range(0, len(texts), batch_size):
        end = min(i + batch_size, len(texts))
        collection.add(
            documents=texts[i:end],
            metadatas=metadatas[i:end],
            ids=ids[i:end]
        )
        print(f"   Added batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
    
    print(f"Vector store created with {len(chunks)} chunks")
    print(f"Saved to: {CHROMA_PATH}")
    return collection


def main():
    """Main function to orchestrate the ingestion process"""
    print("\n" + "="*60)
    print("COMPANY CHATBOT - DATA INGESTION")
    print("="*60 + "\n")
    
    # Check if data folder exists
    if not os.path.exists(DATA_PATH):
        print(f"Error: {DATA_PATH} folder not found")
        return
    
    try:
        # Step 1: Load documents
        documents = load_documents()
        
        if len(documents) == 0:
            print(f"No documents found in {DATA_PATH} folder")
            return
        
        # Step 2: Split into chunks
        chunks = split_documents(documents)
        
        # Step 3: Create vector store
        create_vector_store(chunks)
        
        print("\n" + "="*60)
        print("DATA INGESTION COMPLETE!")
        print("="*60)
        print("\n💡 You can now run the chatbot:")
        print("   python app.py")
        print()
        
    except Exception as e:
        print(f"\nError during ingestion: {str(e)}")
        raise


if __name__ == "__main__":
    main()
