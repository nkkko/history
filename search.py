import chromadb
import csv
import argparse
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import os
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Read the API key from the environment variable
azure_api_version = os.getenv("AZURE_API_VERSION")
azure_endpoint = os.getenv("AZURE_ENDPOINT")
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")

# Azure embedding function
azure_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=azure_api_key,
    api_base=azure_endpoint,
    api_type="azure",
    api_version=azure_api_version,
    model_name="text-embedding-3-small"  # Use the deployment name instead of model name
)

def create_chroma_client():
    return chromadb.PersistentClient(path="./chroma_db")

def create_or_get_collection(client):
    return client.get_or_create_collection(
        name="browser_history",
        embedding_function=azure_ef
    )

def embed_csv(csv_file, collection):
    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        rows = list(csv_reader)  # Convert to list to get the total length for tqdm
        for row in tqdm(rows, desc="Embedding CSV Rows", unit="row"):
            collection.add(
                documents=[f"{row['title']} - {row['url']}"],
                ids=[row['id']],
                metadatas=[{"title": row['title'], "url": row['url']}]
            )
    print(f"Embedded data from {csv_file}")

def search(query, collection, n_results=10, domain=None):
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    filtered_results = {
        'documents': [],
        'metadatas': [],
        'distances': []
    }

    for i, (doc, metadata, distance) in enumerate(zip(results['documents'][0], results['metadatas'][0], results['distances'][0])):
        if domain is None or domain in metadata['url']:
            filtered_results['documents'].append(doc)
            filtered_results['metadatas'].append(metadata)
            filtered_results['distances'].append(distance)

    return filtered_results

def main():
    parser = argparse.ArgumentParser(description="Embed and search browser history using ChromaDB")
    parser.add_argument("--embed", help="CSV file to embed")
    parser.add_argument("--domain", help="Domain to filter URLs", default=None)
    parser.add_argument("query", nargs="?", help="Search query")
    args = parser.parse_args()

    client = create_chroma_client()
    collection = create_or_get_collection(client)

    if args.embed:
        embed_csv(args.embed, collection)
    elif args.query:
        results = search(args.query, collection, domain=args.domain)
        for i, (doc, metadata, distance) in enumerate(zip(results['documents'], results['metadatas'], results['distances']), 1):
            print(f"{i}. {metadata['title']}")
            print(f"   URL: {metadata['url']}")
            print(f"   Relevance: {1 - distance:.2f}")
            print()
    else:
        print("Please provide either --embed CSV_FILE or a search query.")

if __name__ == "__main__":
    main()