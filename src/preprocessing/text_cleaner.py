
import re
from langchain_core.documents import Document

def clean_text(docs):
    cleaned_docs = []

    for i in range(len(docs)):
        text=docs[i].page_content
        # Remove leading and trailing whitespace
        text = text.strip()

        # Replace multiple spaces and tabs with a single space
        text = re.sub(r"[ \t]+", " ", text)

        # Reduce excessive consecutive line breaks
        text = re.sub(r"\n{3,}", "\n\n", text)
        new_doc=Document(page_content=text,metadata=docs[i].metadata)
        cleaned_docs.append(new_doc)

    return cleaned_docs
