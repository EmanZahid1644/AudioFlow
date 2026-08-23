from pymongo import MongoClient
from dotenv import load_dotenv
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# =========================
# Load Environment Variables
# =========================

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

# =========================
# MongoDB Connection
# =========================

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise RuntimeError(
        "MONGODB_URI is not set. Check backend/.env and ensure it is loaded."
    )

# Shared client instance (lazy)
_mongo_client = None

def get_mongo_client():
    global _mongo_client
    if _mongo_client is None:
        # Timeout increased to 10000ms (10s) to allow SRV DNS resolution and TLS handshake on slower networks
        _mongo_client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
        )
    return _mongo_client

# In-memory store fallback for offline / DB failure mode
_in_memory_db = {
    "users": [],
    "audios": [],
    "samples": []
}

class InMemoryCollection:
    def __init__(self, name):
        self.name = name

    def insert_one(self, doc):
        stored_doc = dict(doc)
        _in_memory_db.setdefault(self.name, []).append(stored_doc)
        class InsertResult:
            inserted_id = stored_doc.get("_id", str(len(_in_memory_db[self.name])))
        return InsertResult()

    def find_one(self, query):
        docs = _in_memory_db.get(self.name, [])
        for doc in docs:
            match = True
            for k, v in query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                return doc
        return None

    def find(self, query=None):
        docs = _in_memory_db.get(self.name, [])
        if not query:
            return list(docs)
        results = []
        for doc in docs:
            match = True
            for k, v in query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                results.append(doc)
        return results

    def delete_many(self, query):
        docs = _in_memory_db.get(self.name, [])
        new_docs = []
        deleted_count = 0
        for doc in docs:
            match = True
            for k, v in query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                deleted_count += 1
            else:
                new_docs.append(doc)
        _in_memory_db[self.name] = new_docs
        class DeleteResult:
            pass
        res = DeleteResult()
        res.deleted_count = deleted_count
        return res

class SafeCollection:
    def __init__(self, name):
        self.name = name
        self.in_memory_fallback = InMemoryCollection(name)

    def _get_coll(self):
        try:
            client = get_mongo_client()
            return client["audioflow"][self.name]
        except Exception as e:
            logger.warning(f"MongoDB client initialization error: {e}")
            return None

    def insert_one(self, doc):
        coll = self._get_coll()
        if coll is not None:
            try:
                return coll.insert_one(doc)
            except Exception as e:
                print(f"Warning: MongoDB connection/operation failed ({e}). Using in-memory fallback.")
        return self.in_memory_fallback.insert_one(doc)

    def find_one(self, query):
        coll = self._get_coll()
        if coll is not None:
            try:
                return coll.find_one(query)
            except Exception as e:
                print(f"Warning: MongoDB connection/operation failed ({e}). Using in-memory fallback.")
        return self.in_memory_fallback.find_one(query)

    def find(self, query=None):
        coll = self._get_coll()
        if coll is not None:
            try:
                return coll.find(query or {})
            except Exception as e:
                print(f"Warning: MongoDB connection/operation failed ({e}). Using in-memory fallback.")
        return self.in_memory_fallback.find(query)

    def delete_many(self, query):
        coll = self._get_coll()
        if coll is not None:
            try:
                return coll.delete_many(query)
            except Exception as e:
                print(f"Warning: MongoDB connection/operation failed ({e}). Using in-memory fallback.")
        return self.in_memory_fallback.delete_many(query)


users_collection = SafeCollection("users")
audios_collection = SafeCollection("audios")
samples_collection = SafeCollection("samples")
print("MongoDB database initialized (lazy-loaded with resilience).")