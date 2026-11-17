from pathlib import Path


from src.ingestion.pdf_extractor import pdf_extractor
from src.preprocessing.text_cleaner import clean_text
from src.chunking.text_chunker import text_chunker
from src.embeddings.embedding_model import embedding_model, load_embedding_model
from src.vector_store.chroma_manager import *
from langchain_core.documents import Document
from pathlib import Path

from src.ingestion.manifest import (
    calculate_file_hash,
    load_manifest,
    save_manifest
)

def delete_obsolete_chunks(vector_store, source, keep_ids=None):
    """Supprime les chunks obsolètes d'un PDF dans Chroma."""

    result = vector_store.get(
        where={"source": source},
        include=["metadatas"]
    )

    existing_ids = result["ids"]

    if keep_ids is None:
        ids_to_delete = existing_ids
    else:
        ids_to_delete = [
            chunk_id
            for chunk_id in existing_ids
            if chunk_id not in keep_ids
        ]

    if ids_to_delete:
        vector_store.delete(ids=ids_to_delete)
        print(f"{len(ids_to_delete)} anciens chunks supprimés.")


def multi_pdf_ingestion(courses_dir, collection_name="all_courses", distance_metric="l2"):

    courses_dir = Path(courses_dir).resolve()

    manifest_path = (
        courses_dir.parents[1]
        / "processed"
        / "ingestion_manifest.json"
    )

    manifest = load_manifest(manifest_path)

    vector_store = initialize_vector_store(
        collection_name=collection_name,
        distance_metric=distance_metric
    )

    pdf_files = sorted(courses_dir.rglob("*.pdf"))
    current_files = set()

    # Collection de référence contenant les chunks déjà indexés
    source_store = initialize_vector_store(
        collection_name="all_courses",
        distance_metric="l2"
    )

    for pdf in pdf_files:

        pdf = pdf.resolve()
        relative_path = pdf.relative_to(courses_dir).as_posix()
        source = str(pdf)
        current_files.add(relative_path)

        file_hash = calculate_file_hash(pdf)
        file_stats = pdf.stat()
        previous_data = manifest["documents"].get(relative_path)

        unchanged = (
            previous_data
            and previous_data["sha256"] == file_hash
            and previous_data["source"] == source
        )

        if unchanged:
            print(f"[SKIP] {pdf.name} : aucun retraitement.")
            # Récupération des chunks depuis la collection de référence
            result = source_store.get()
            chunks = [
                Document(page_content=doc, metadata=metadata)
                for doc, metadata in zip(result["documents"], result["metadatas"])
                if metadata.get("source") == source
            ]

        else:
            print(f"[INGESTION] {pdf.name}")

            extracted_docs = pdf_extractor(source)
            cleaned_docs = clean_text(extracted_docs)
            chunks = text_chunker(cleaned_docs)
            print("Extraction :", extracted_docs[0].metadata)
            print("Nettoyage :", cleaned_docs[0].metadata)
            print("Chunking :", chunks[0].metadata)
            # Suppression des anciens chunks dans la collection cible
            delete_obsolete_chunks(vector_store, source)

        if not chunks:
            print(f"[WARNING] Aucun chunk disponible pour {pdf.name}.")
            continue

        # Vérification des IDs déjà présents dans la collection cible
        expected_ids = [generate_chunk_id(chunk) for chunk in chunks]
        existing = vector_store.get(ids=expected_ids)
        existing_ids = set(existing["ids"])

        missing_chunks = [
            chunk for chunk, chunk_id in zip(chunks, expected_ids)
            if chunk_id not in existing_ids
        ]

        if missing_chunks:
            add_documents_to_store(vector_store, missing_chunks)

        # Suppression des anciens chunks obsolètes après indexation
        delete_obsolete_chunks(
            vector_store,
            source,
            keep_ids=set(expected_ids)
        )

        if not unchanged:
            manifest["documents"][relative_path] = {
                "source": source,
                "sha256": file_hash,
                "size": file_stats.st_size,
                "last_modified": file_stats.st_mtime,
                "chunk_count": len(chunks)
            }

            save_manifest(manifest, manifest_path)

        print(f"[SUCCESS] {pdf.name} : {len(chunks)} chunks.")

    # Détection des PDF supprimés
    previous_files = set(manifest["documents"].keys())
    deleted_files = previous_files - current_files

    for relative_path in deleted_files:
        old_source = manifest["documents"][relative_path]["source"]

        print(f"[DELETE] {relative_path}")
        delete_obsolete_chunks(vector_store, old_source)

        del manifest["documents"][relative_path]
        save_manifest(manifest, manifest_path)

    return vector_store
