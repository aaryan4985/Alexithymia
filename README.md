# Alexi Vale - Light Novel RAG System 📚

Alexi Vale is a Retrieval-Augmented Generation (RAG) system built with **LlamaIndex** and **Groq** that acts as a highly analytical, precise, and emotionally restrained literary analyst.

It seamlessly integrates a custom **web scraper** to fetch Light Novel chapters directly from the web, embed them using HuggingFace (`BAAI/bge-large-en-v1.5`), store them in a persistent **ChromaDB** vector database, and answer highly specific queries based *only* on the retrieved context.

## 🌟 Features
- **Integrated Web Scraper**: Built-in Playwright/Cloudscraper fallback system to scrape novel chapters from NovelBin directly into `.jsonl` formats.
- **High-Speed RAG Pipeline**: Powered by LlamaIndex and the blazing fast `llama-3.3-70b-versatile` model via the Groq API.
- **Strict Persona & Hallucination Fallbacks**: Alexi is instructed to be precise. If the vector search does not find the information, he will refuse to answer rather than hallucinate.
- **Intelligent Memory Architecture**: Maintains conversation history via a custom `Memory` class, cleanly separating vector search from LLM context to prevent vector poisoning.

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Alexi.git
   cd Alexi
   ```

2. **Install the dependencies**
   Install the libraries required for the scraper and the RAG engine:
   ```bash
   pip install -r requirement.txt
   cd alexi_rag
   pip install -r requirements.txt
   ```
   *(Note: The scraper may require you to run `playwright install` to download browser binaries).*

3. **Configure Environment Variables**
   Inside the `alexi_rag` folder, copy `.env.example` to `.env` and add your Groq API key:
   ```bash
   cp .env.example .env
   ```
   ```env
   # Inside .env
   GROQ_API_KEY=your_groq_api_key_here
   MODEL_NAME=llama-3.3-70b-versatile
   ```

## 🎮 Usage

Launch the main CLI from the `alexi_rag` directory:

```bash
cd alexi_rag
python main.py
```

Upon launching, the system will ask:
`Do you want to (1) Scrape and ingest a new novel, or (2) Skip to Chat? [1/2]:`

- **Option 1 (Scrape & Ingest)**: Enter a novel name (e.g., `shadow-slave` or `classroom-of-the-elite`). The scraper will download the chapters into `../data`, automatically chunk and embed the text, and store it in ChromaDB.
- **Option 2 (Chat)**: Jump straight into the CLI to chat with Alexi.

### CLI Arguments
You can filter the query engine's vector search using metadata filters:
```bash
python main.py --novel shadow-slave
```

## 📁 Project Structure
```text
Alexi/
├── webscrapper.py           # The novel scraping engine
├── data/                    # Generated .jsonl chapters
├── requirement.txt          # Scraper dependencies
└── alexi_rag/
    ├── main.py              # CLI entry point
    ├── ingest_json.py       # Reads .jsonl and builds ChromaDB vectors
    ├── query_engine.py      # LlamaIndex retrieval & LLM generation
    ├── config.py            # Model & chunking parameters
    ├── memory.py            # Local conversation memory
    ├── prompts.py           # Alexi Vale's system prompt
    ├── requirements.txt     # RAG engine dependencies
    ├── .env.example         # Template for API keys
    └── chroma_db/           # Persistent vector database
```