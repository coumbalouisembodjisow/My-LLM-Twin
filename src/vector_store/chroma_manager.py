from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import hashlib
def initialize_vector_store():
    model_name= "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": False}
    hf = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
    )
    vector_store = Chroma(
    collection_name="all_courses",
    embedding_function=hf,
    persist_directory="./vector_store/chroma_db"
    )
    return vector_store


def generate_chunk_id(chunk):
    to_hash=chunk.page_content + " " + chunk.metadata["source"]
    return hashlib.sha256(to_hash.encode("utf-8")).hexdigest()
    
    
    

def add_documents_to_store(vector_store,chunks):
    ids=[generate_chunk_id(chunk) for chunk in chunks]
    existing_ids=set(vector_store.get()["ids"])
    ids_to_add=[]
    chunks_to_add=[]
    for chunk, chunk_id in zip(chunks, ids):
        if chunk_id not in existing_ids:
            ids_to_add.append(chunk_id)
            chunks_to_add.append(chunk)
            
    if chunks_to_add:
        vector_store.add_documents(documents=chunks_to_add,ids=ids_to_add)
        print(f"{len(chunks_to_add)} nouveaux chunks ajoutés.")
    else:
        print("Aucun nouveau chunk à ajouter.")
        
    return vector_store
    
    