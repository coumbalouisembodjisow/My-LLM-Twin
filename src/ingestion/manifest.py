import hashlib
import json
from pathlib import Path


def calculate_file_hash(file_path):
    """Calcule le SHA-256 d'un fichier PDF."""
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(block)

    return sha256.hexdigest()


def load_manifest(manifest_path):
    """Charge le manifest ou crée une structure vide."""
    manifest_path = Path(manifest_path)

    if not manifest_path.exists():
        return {"version": 1, "documents": {}}

    with open(manifest_path, "r", encoding="utf-8") as file:
        manifest = json.load(file)

    if "documents" not in manifest:
        raise ValueError("Format du manifest invalide.")

    return manifest


def save_manifest(manifest, manifest_path):
    """Sauvegarde le manifest de manière sécurisée."""
    manifest_path = Path(manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = manifest_path.with_suffix(".json.tmp")

    with open(temporary_path, "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=4, ensure_ascii=False)

    temporary_path.replace(manifest_path)