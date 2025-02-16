from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb

def store_embeddings(file_path: str, document_id: str):
    # Load the document
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # Split the document into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=5000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = splitter.split_documents(documents)

    # Initialize the embedding model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Connect to ChromaDB (Move outside the loop)
    chroma_client = chromadb.HttpClient(host='localhost', port=8000)
    collection = chroma_client.get_or_create_collection('test-collection')

    # Store embeddings
    for idx, chunk in enumerate(chunks):
        chunk_text = chunk.page_content  # Extract text from Document object
        chunk_embedding = model.encode(chunk_text).tolist()

        collection.add(
            ids=[f"{document_id}_{idx}"],  # Unique ID
            documents=[chunk_text],  # Store text
            embeddings=[chunk_embedding]  # Store embedding
        )

def retrieve_context(query: str, top_k: int = 2):
    # Initialize the embedding model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Connect to ChromaDB
    chroma_client = chromadb.HttpClient(host='localhost', port=8000)
    collection = chroma_client.get_collection('test-collection')

    # Encode the query
    query_embedding = model.encode(query).tolist()

    # Retrieve similar documents
    results = collection.query(
        query_embeddings=[query_embedding],  
        n_results=top_k  # Number of results to return
    )

    # Extract relevant context from results
    if "documents" in results and results["documents"]:
        retrieved_contexts = results["documents"][0]  # List of matching texts
    else:
        retrieved_contexts = []

    return retrieved_contexts
