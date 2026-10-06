from pickle import NONE
import re
import sys
import uuid

import truststore
truststore.inject_into_ssl()

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from fastembed import TextEmbedding
from pickle import NONE
from config import ROOT_DIR,KNOWLEDGE_DIR

QDRANT_URL = "http://localhost:6333"
COLLECTION = "aegis_knowledge"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
VECTOR_SIZE = 384

_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = TextEmbedding(model_name=EMBED_MODEL)
    return _embedder


def chunk_markdown(path):
    txt = path.read_text(encoding="utf-8")
    first_line =txt.strip().splitlines()[0]
    title = first_line.replace("# ", "").strip()

    source  = path.relative_to(ROOT_DIR).as_posix()
    chunks = []
    for section in re.split(r"^## ", txt, flags=re.MULTILINE)[1:]:
        heading, _, body = section.partition("\n")
        chunks.append({
            "source": source,
            "title": title,
            "section": heading.strip(),
            "text": f"{title}\n{heading.strip()}\n{body.strip()}",
        })
    return chunks

def ingest():
    files = sorted(KNOWLEDGE_DIR.rglob("*.md"))
    chunks = [c for f in files for c in chunk_markdown(f)]
    vectors = list(get_embedder().passage_embed([c["text"] for c in chunks]))

    client = QdrantClient(url=QDRANT_URL)
    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)
    client.create_collection(
        COLLECTION,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    points = [
        PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"{c['source']}#{c['section']}")),
            vector=v.tolist(),
            payload=c,
        )
        for c, v in zip(chunks, vectors)
    ]
    client.upsert(COLLECTION, points)
    print(f"Ingested {len(points)} chunks from {len(files)} files into '{COLLECTION}'")

def search(query, limit=3):
    client = QdrantClient(url=QDRANT_URL)
    vector = next(iter(get_embedder().query_embed([query]))).tolist()
    hits = client.query_points(COLLECTION, query=vector, limit=limit).points
    return [
        {
            "score": round(h.score, 3),
            "source": h.payload["source"],
            "section": h.payload["section"],
            "text": h.payload["text"],
        }
        for h in hits
    ]

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "search":
        for r in search(sys.argv[2]):
            print(f"{r['score']}  {r['source']}  ::  {r['section']}")
    else:
        ingest()