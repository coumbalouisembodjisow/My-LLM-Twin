import pymupdf
from langchain_community.document_loaders import PyMuPDFLoader
import pprint

def pdf_extractor_from_scratch(file):
    try:
        doc=pymupdf.open(file)
        result={}
        for page_index in range(len(doc)): 
            page=doc[page_index] # get the page
            result[page_index]=page.get_text()
            
        return result
    except pymupdf.FileNotFoundError:
        print("Fichier introuvable")
        return None

def pdf_extractor(file_path):
    loader=PyMuPDFLoader(file_path,mode="single")
    docs=loader.load()
    print(len(docs))
    pprint.pp(docs[0].metadata)
    for i in range(len(docs)):
        print(docs[i].page_content)
    return docs

