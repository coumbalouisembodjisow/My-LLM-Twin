from src.ingestion.pdf_extractor import pdf_extractor
from src.preprocessing.text_cleaner import clean_text
from src.chunking.text_chunker import text_chunker
from src.embeddings.embedding_model import embedding_model, load_embedding_model
from src.vector_store.chroma_manager import *
if __name__=="__main__":
    file=r"C:\Users\lenovo\My-LLM-Twin\data\raw\courses\Machine_Learning\Regression.pdf"
    extraction=pdf_extractor(file)
    print(extraction)
    cleaned_docs=clean_text(extraction)
    chunks=text_chunker(cleaned_docs)
    print("Recursive chunking===================================================================")
    print(chunks)
    print("Number of chunks==========")
    print(len(chunks))
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i} : {len(chunk.page_content)} caractères")
        
    print("Texte extrait :", len(extraction[0].page_content))
    print("Texte nettoyé :", len(cleaned_docs[0].page_content))
    vector_store=add_documents_to_store(initialize_vector_store(),chunks)
    
    
