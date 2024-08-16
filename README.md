# Browser History Embedding with ChromaDB

This repository contains a utility to embed and search your browser history using ChromaDB and Azure's embedding functionalities. To get started, you need to export your browser history in a .csv file and set up a development environment.

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

   There is no third step.

## Usage

1. **Set Up Environment Variables:**

   Create a `.env` file in the root directory of the repository with the following variables:

   ```env
   AZURE_API_VERSION=<your_azure_api_version>
   AZURE_ENDPOINT=<your_azure_endpoint>
   AZURE_OPENAI_API_KEY=<your_azure_api_key>
   ```

2. **Embed Your Browser History:**

   Run the following command to embed your browser history:

   ```sh
   python main.py --embed path/to/your/history.csv
   ```

3. **Search Your Indexed History:**

   Run the following command to perform a search:

   ```sh
   python main.py "search query"
   ```

   You can optionally filter results by domain:

   ```sh
   python main.py "search query" --domain example.com
   ```
 ## Code

Here's a brief overview of the essential functions in your code:

* **create_chroma_client()**: Initializes a ChromaDB client with a persistent storage path.
* **create_or_get_collection(client)**: Retrieves or creates a ChromaDB collection for storing browser history embeddings.
* **embed_csv(csv_file, collection)**: Reads a CSV file and embeds each row into the specified ChromaDB collection.
* **search(query, collection, n_results=10, domain=None)**: Searches the embeddings in the ChromaDB collection and optionally filters results by domain.
