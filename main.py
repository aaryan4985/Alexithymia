import os
from langchain_community.document_loaders import PyMuPDFLoader, PyPDFLoader , DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-base-en-v1.5")


def readpdf(dir):
    all_docs = []
    pdf_dir = Path(dir)
    pdf_files = list(pdf_dir.glob("**/*.pdf"))
    print(f"found {len(pdf_files)} files ")
    for pdf_file in pdf_files:
        try:
            loader = PyPDFLoader(str(pdf_file))
            documents = loader.load()
            
            for doc in documents:
                doc.metadata["source_file"] = pdf_file.name
                doc.metadata["file_type"] = 'pdf'
            
            all_docs.extend(documents)
            
        except Exception as e:
            print(e)
    return all_docs

    
pdf_docs = readpdf("./data")

def split_docs(documents, chunk_size = 1000, chunk_overlap=150):
    textSplitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
        length_function = len,
        separators = ["\nChapter ","\nCHAPTER ","\n\n","\n",". ","! ","? "," ",""]
    )
    
    split_docs = textSplitter.split_documents(documents)
    if split_docs:
        print("done splitting")
    return split_docs

chunks = split_docs(pdf_docs)
if chunks:
    embeddings = model.encode([chunk.page_content for chunk in chunks])
    print(f"Successfully generated {len(embeddings)} embeddings!")
else:
    print("No chunks found to encode.")