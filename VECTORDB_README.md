# Vector Database Integration

This module provides ChromaDB integration for storing and querying text embeddings, enabling semantic search capabilities for the audiobook generator.

## Installation

```bash
pip install chromadb>=1.3.0
```

## Quick Start

### 1. Save Embeddings to Vector Database

After generating embeddings (see `EMBEDDINGS_README.md`), save them to ChromaDB:

```bash
python vectordb_save.py "outputs/embeddings/your_file_embeddings.csv"
```

This creates a persistent vector database in `./vectordb/` directory with default collection name `audiobook_embeddings`.

### 2. Query with Semantic Search

Search for similar text segments:

```bash
python vectordb_save.py "outputs/embeddings/your_file_embeddings.csv" --query "audiobook generation" --top-k 5
```

## RAG Q&A (Answer Questions with LLM)

Use `rag_query.py` to retrieve top-k chunks from the vector DB and ask an LLM (Gemini or OpenAI) to answer grounded in those chunks.

### Prerequisites

Set at least one LLM API key:

```powershell
# Gemini (preferred)
$env:GOOGLE_API_KEY = "<YOUR_GEMINI_API_KEY>"

# Or OpenAI
$env:OPENAI_API_KEY = "<YOUR_OPENAI_API_KEY>"
```

### Run a Query

```powershell
# Auto-select provider (Gemini -> OpenAI) and show sources
python rag_query.py --query "What is the objective of the audiobook generator?" --top-k 5 --show-sources

# Force Gemini
python rag_query.py --query "Summarize the milestones" --provider gemini --top-k 3

# Force OpenAI
python rag_query.py --query "List the workflow steps" --provider openai --top-k 5
```

The tool will:
- Retrieve the top-k most similar text chunks from `audiobook_embeddings`
- Build a grounded prompt with those chunks
- Ask the selected LLM to produce a concise answer

If no API key is available, it will return a preview of the retrieved context as a fallback.

## Usage

### Basic Save

```bash
# Save embeddings to default collection
python vectordb_save.py "path/to/embeddings.csv"

# Save to custom collection
python vectordb_save.py "path/to/embeddings.csv" --collection "my_collection"

# Custom database directory
python vectordb_save.py "path/to/embeddings.csv" --db-dir "./my_vectordb"
```

### Semantic Search

```bash
# Find top 5 similar texts
python vectordb_save.py "path/to/embeddings.csv" --query "your search query" --top-k 5

# Search in specific collection
python vectordb_save.py "path/to/embeddings.csv" --query "text" --collection "my_collection"
```

### Batch Processing

```bash
# Adjust batch size for large datasets
python vectordb_save.py "path/to/embeddings.csv" --batch-size 500
```

## Python API

```python
from vectordb_save import (
    load_embeddings_from_csv,
    create_vectordb,
    save_to_vectordb,
    query_vectordb,
    list_collections,
    get_collection_stats
)

# Load and save embeddings
csv_path = "outputs/embeddings/my_embeddings.csv"
texts, embeddings, metadata = load_embeddings_from_csv(csv_path)

# Create or get collection
collection = create_vectordb("my_collection", "./vectordb")

# Save to database
db_path = save_to_vectordb(csv_path, "my_collection", "./vectordb")

# Query similar texts
results = query_vectordb(
    collection_name="my_collection",
    query_text="audiobook generation",
    persist_directory="./vectordb",
    n_results=5
)

for i, (text, distance, metadata) in enumerate(results, 1):
    print(f"{i}. (distance: {distance:.4f})")
    print(f"   {text[:100]}...")
    print()

# List all collections
collections = list_collections("./vectordb")
print(f"Collections: {collections}")

# Get collection statistics
stats = get_collection_stats("my_collection", "./vectordb")
print(f"Documents: {stats['count']}")
print(f"Metadata: {stats['metadata']}")
```

## Understanding Distance Scores

- **Distance**: Lower is better (0 = perfect match)
- **< 0.5**: Very similar texts
- **0.5 - 1.0**: Moderately similar
- **> 1.0**: Less similar

ChromaDB uses cosine distance by default.

## CLI Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `csv_path` | Path to embeddings CSV file | Required |
| `--collection` | Name of vector database collection | `audiobook_embeddings` |
| `--db-dir` | Directory for persistent storage | `./vectordb` |
| `--batch-size` | Documents per batch | `100` |
| `--query` | Text query for semantic search | None |
| `--top-k` | Number of results to return | `5` |

## Database Structure

```
vectordb/
├── chroma.sqlite3           # SQLite database
└── [collection_id]/         # Collection data
    ├── data_level0.bin
    ├── header.bin
    ├── length.bin
    └── link_lists.bin
```

## Features

### 1. Persistent Storage
- Database survives program restarts
- Stored locally in specified directory
- No external server required

### 2. Batch Processing
- Efficient handling of large datasets
- Configurable batch size
- Progress logging

### 3. Metadata Support
- Source document tracking
- Chunk indexing
- Custom metadata fields

### 4. Collection Management
- Multiple collections in one database
- List all collections
- Get collection statistics

## Use Cases

### Audiobook Chapter Search
```bash
# Generate embeddings for book chapters
python embeddings.py "outputs/text/my_book.txt" --split sentence

# Save to vector database
python vectordb_save.py "outputs/embeddings/my_book_embeddings.csv"

# Find chapters about specific topics
python vectordb_save.py "outputs/embeddings/my_book_embeddings.csv" \
    --query "character development" --top-k 3
```

### Multi-Document Search
```python
# Index multiple documents
for doc_file in document_files:
    # Generate embeddings
    embeddings_csv = generate_embeddings(doc_file)
    
    # Add to shared collection
    save_to_vectordb(embeddings_csv, "all_books", "./vectordb")

# Search across all documents
results = query_vectordb("all_books", "plot twist", n_results=10)
```

### Semantic Content Grouping
```python
# Find related text segments
query_text = "introduction to machine learning"
results = query_vectordb("technical_docs", query_text, n_results=20)

# Group by similarity threshold
similar_texts = [text for text, dist, _ in results if dist < 0.7]
```

## Integration with Embeddings Pipeline

Complete workflow:

```bash
# Step 1: Extract text
python process_file.py "document.pdf"

# Step 2: Generate embeddings
python embeddings.py "outputs/text/document_extracted.txt" --split sentence

# Step 3: Save to vector database
python vectordb_save.py "outputs/embeddings/document_embeddings.csv"

# Step 4: Query
python vectordb_save.py "outputs/embeddings/document_embeddings.csv" \
    --query "key concepts" --top-k 5
```

## Advanced Configuration

### Custom Embedding Model

By default, ChromaDB will handle embeddings internally. If you want to use your own embeddings (as we do):

```python
collection.add(
    ids=["id1", "id2"],
    documents=["text1", "text2"],
    embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]],  # Your embeddings
    metadatas=[{"source": "doc1"}, {"source": "doc2"}]
)
```

### Distance Metrics

ChromaDB supports different distance metrics:
- `l2`: Euclidean distance
- `ip`: Inner product
- `cosine`: Cosine similarity (default)

## Troubleshooting

### Issue: "Collection already exists"
- The collection is reused automatically
- Documents are added to existing collection
- Use different `--collection` name for separate collections

### Issue: "Database locked"
- Close other connections to the database
- Ensure no other processes are accessing `vectordb/`

### Issue: "Dimension mismatch"
- Ensure all embeddings in CSV have same dimension (384 for all-MiniLM-L6-v2)
- Don't mix embeddings from different models

### Issue: "Out of memory"
- Reduce `--batch-size` parameter
- Process documents in smaller chunks

## Performance Tips

1. **Batch Size**: Larger batches = faster insertion (use 500-1000 for large datasets)
2. **Collection Strategy**: Separate collections for different document types
3. **Query Optimization**: Use specific queries for better results
4. **Database Location**: Use SSD for faster I/O

## API Reference

### `load_embeddings_from_csv(csv_path: str)`
Load embeddings from CSV file.

**Returns**: `Tuple[List[str], List[List[float]], List[dict]]`
- texts: List of text segments
- embeddings: List of embedding vectors
- metadata: List of metadata dictionaries

### `create_vectordb(collection_name: str, persist_directory: str)`
Create or retrieve ChromaDB collection.

**Returns**: `chromadb.Collection`

### `save_to_vectordb(csv_path, collection_name, persist_directory, batch_size)`
Save embeddings to vector database in batches.

**Returns**: `str` (database path)

### `query_vectordb(collection_name, query_text, persist_directory, n_results)`
Query vector database for similar texts.

**Returns**: `List[Tuple[str, float, dict]]`
- text: Original text segment
- distance: Similarity score
- metadata: Associated metadata

### `list_collections(persist_directory: str)`
List all collections in database.

**Returns**: `List[str]`

### `get_collection_stats(collection_name: str, persist_directory: str)`
Get collection statistics.

**Returns**: `dict` with keys:
- `count`: Number of documents
- `metadata`: Collection metadata

## Related Documentation

- [Embeddings Generation Guide](EMBEDDINGS_README.md)
- [ChromaDB Official Docs](https://docs.trychroma.com/)
- [Semantic Search Tutorial](https://www.pinecone.io/learn/what-is-semantic-search/)

## Examples

See `vectordb_save.py` for complete implementation examples.
