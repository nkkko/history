# Browser History Embedding with ChromaDB

This repository contains a utility to embed and search your browser history using ChromaDB. It supports both local embeddings and optional Azure embedding functionalities. To get started, you need to export your browser history in a .csv file and set up a development environment.

## Prerequisites

* [Daytona](https://github.com/daytonaio/daytona)

## Exporting Browser History

To export your browser history, use the [Export Chrome History](https://chromewebstore.google.com/detail/export-chrome-history/dihloblpkeiddiaojbagoecedbfpifdj?hl=en) Chrome extension. Ensure you save the history as a `.csv` file.

## Setting Up Development Environment

### Creating a Dev Environment with Daytona

#### Steps to Set Up Daytona Workspace

1. **Install Daytona**:
    ```bash
    (curl -L https://download.daytona.io/daytona/install.sh | sudo bash) && daytona server stop && daytona server -y && daytona
    ```

2. **Create Daytona Workspace:**

   Run the following command in your terminal to create a new Daytona workspace:

   ```sh
   daytona create https://github.com/nkkko/history --code
   ```

## Usage

1. **Set Up Environment Variables (Optional for Azure):**

   If you want to use Azure embeddings, create a `.env` file in the root directory of the repository with the following variables:

   ```env
   AZURE_API_VERSION=<your_azure_api_version>
   AZURE_ENDPOINT=<your_azure_endpoint>
   AZURE_OPENAI_API_KEY=<your_azure_api_key>
   ```

   Note: If you don't set up these variables, the script will use a local embedding model by default.

2. **Embed Your Browser History:**

   Run the following command to embed your browser history:

   ```sh
   python search.py --embed path/to/your/history.csv
   ```

   By default, this uses a local embedding model (all-MiniLM-L6-v2). To use Azure embeddings, add the `--azure` flag:

   ```sh
   python search.py --embed path/to/your/history.csv --azure
   ```

3. **Search Your Indexed History:**

   Run the following command to perform a search:

   ```sh
   python search.py "search query"
   ```

   You can use additional options to filter and sort results:

   - `--domain`: Filter results by domain
   - `--newest`: Sort results by newest date and time
   - `--azure`: Use Azure OpenAI embeddings (optional, uses local model by default)
   - `--visit-count`: Filter by minimum visit count
   - `--typed-count`: Filter by minimum typed count
   - `--transition`: Filter by transition type (link, typed, or reload)

   Example:
   ```sh
   python search.py "search query" --domain example.com --newest --visit-count 5
   ```

## Project Structure

```
history
├── requirements.txt
├── README.md
└── search.py
```

- `requirements.txt`: Contains all the necessary Python packages for the project.
- `README.md`: This file, containing project documentation.
- `search.py`: The main script for embedding and searching browser history.

## Key Functions in search.py

- `create_chroma_client()`: Initializes a ChromaDB client with a persistent storage path.
- `create_or_get_collection(client, embedding_function)`: Retrieves or creates a ChromaDB collection for storing browser history embeddings.
- `embed_csv(csv_file, collection)`: Reads a CSV file and embeds each row into the specified ChromaDB collection.
- `search(query, collection, n_results=10, domain=None, newest=False, visit_count=None, typed_count=None, transition=None)`: Searches the embeddings in the ChromaDB collection with various filtering options.

For more details on usage and implementation, please refer to the `search.py` file.

## Embedding Models

- **Default (Local) Model**: The script uses the `all-MiniLM-L6-v2` model from SentenceTransformers by default. This model is run locally and doesn't require any API keys or internet connection for embeddings.
- **Azure OpenAI (Optional)**: If you prefer to use Azure's embedding service, you can set up the necessary environment variables and use the `--azure` flag when running the script.

Choose the embedding model that best suits your needs and computational resources.