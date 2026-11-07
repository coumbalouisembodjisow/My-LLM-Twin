import pymupdf

def pdf_extractor(file):
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


if __name__=="__main__":
    file=r"C:\Users\lenovo\My-LLM-Twin\data\raw\courses\Machine_Learning\Regress.pdf"
    extraction=pdf_extractor(file)
    print(extraction)
