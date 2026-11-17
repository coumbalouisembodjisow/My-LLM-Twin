from langchain_chroma import Chroma

def retriever(vector_store,query):
    return vector_store.similarity_search_with_score(query=query,k=3)