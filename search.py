import chromadb
import csv
import argparse
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import os
from tqdm import tqdm
from datetime import datetime
import warnings
warnings.filterwarnings("ignore", message="`clean_up_tokenization_spaces` was not set")

# Load environment variables
load_dotenv()

# Read the API key from the environment variable
azure_api_version = os.getenv("AZURE_API_VERSION")
azure_endpoint = os.getenv("AZURE_ENDPOINT")
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")

# Default embedding function (all-MiniLM-L6-v2)
default_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

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

def create_or_get_collection(client, embedding_function):
    return client.get_or_create_collection(
        name="browser_history",
        embedding_function=embedding_function
    )

def embed_csv(csv_file, collection):
    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        rows = list(csv_reader)  # Convert to list to get the total length for tqdm
        for row in tqdm(rows, desc="Embedding CSV Rows", unit="row"):
            # Check if the ID already exists
            existing = collection.get(ids=[row['id']])
            if not existing['ids']:
                try:
                    collection.add(
                        documents=[f"{row['title']} - {row['url']}"],
                        ids=[row['id']],
                        metadatas=[{
                            "title": row['title'],
                            "url": row['url'],
                            "date": row['date'],
                            "time": row['time'],
                            "visitCount": int(row['visitCount']),
                            "typedCount": int(row['typedCount']),
                            "transition": row['transition']
                        }]
                    )
                except Exception as e:
                    print(f"Error adding row with ID {row['id']}: {str(e)}")
    print(f"Embedded data from {csv_file}")

def search(query, collection, n_results=10, domain=None, newest=False, visit_count=None, typed_count=None, transition=None):
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
        if (domain is None or domain in metadata['url']) and \
           (visit_count is None or metadata['visitCount'] <= visit_count) and \
           (typed_count is None or metadata['typedCount'] <= typed_count) and \
           (transition is None or metadata['transition'] == transition):
            filtered_results['documents'].append(doc)
            filtered_results['metadatas'].append(metadata)
            filtered_results['distances'].append(distance)

    if newest:
        combined = list(zip(filtered_results['documents'], filtered_results['metadatas'], filtered_results['distances']))
        combined.sort(key=lambda x: datetime.strptime(f"{x[1]['date']} {x[1]['time']}", "%m/%d/%Y %H:%M:%S"), reverse=True)
        filtered_results['documents'], filtered_results['metadatas'], filtered_results['distances'] = zip(*combined) if combined else ([], [], [])

    return filtered_results

def main():
    parser = argparse.ArgumentParser(description="Embed and search browser history using ChromaDB")
    parser.add_argument("--embed", help="CSV file to embed")
    parser.add_argument("--domain", help="Domain to filter URLs", default=None)
    parser.add_argument("--newest", action="store_true", help="Sort results by newest date and time")
    parser.add_argument("--azure", action="store_true", help="Use Azure OpenAI embeddings")
    parser.add_argument("--visit-count", type=int, help="Minimum visit count", default=None)
    parser.add_argument("--typed-count", type=int, help="Minimum typed count", default=None)
    parser.add_argument("--transition", help="Transition type can be link, typed or reload", default=None)
    parser.add_argument("query", nargs="?", help="Search query")
    args = parser.parse_args()

    embedding_function = azure_ef if args.azure else default_ef

    client = create_chroma_client()
    collection = create_or_get_collection(client, embedding_function)

    if args.embed:
        embed_csv(args.embed, collection)
    elif args.query:
        results = search(args.query, collection, domain=args.domain, newest=args.newest,
                         visit_count=args.visit_count, typed_count=args.typed_count, transition=args.transition)
        if results['documents']:
            max_distance = max(results['distances'])
            for i, (doc, metadata, distance) in enumerate(zip(results['documents'], results['metadatas'], results['distances']), 1):
                relevance = 1.0 - (distance / max_distance)  # Normalizing distance, higher means more relevant
                print(f"{i}. {metadata['title']}")
                print(f"   URL: {metadata['url']}")
                print(f"   Date: {metadata['date']} Time: {metadata['time']}")
                print(f"   Visit Count: {metadata['visitCount']}")
                print(f"   Typed Count: {metadata['typedCount']}")
                print(f"   Transition: {metadata['transition']}")
                print(f"   Relevance: {relevance:.2f}")
                print()
        else:
            print("No results found.")
    else:
        print("Please provide either --embed CSV_FILE or a search query.")

if __name__ == "__main__":
    main()