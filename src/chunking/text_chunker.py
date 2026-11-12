from langchain_text_splitters import RecursiveCharacterTextSplitter

def text_chunker(cleaned_docs):
    text_splitter=RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        is_separator_regex=False
    )
    chunks=text_splitter.split_documents(cleaned_docs)
    return chunks