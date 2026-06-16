import sys
import os

# Point to your existing rag_system
RAG_PATH = os.path.expanduser("~/rag_system")
sys.path.insert(0, RAG_PATH)

_retriever = None

def _get_retriever():
    """Lazy load the retriever — only initialize when first used."""
    global _retriever
    if _retriever is None:
        try:
            from retriever import RAGRetriever
            _retriever = RAGRetriever(
                docs_folder=os.path.join(RAG_PATH, "documents"),
                store_path=os.path.join(RAG_PATH, "vector_store")
            )
            print("RAG tool connected to rag_system")
        except Exception as e:
            return None, str(e)
    return _retriever, None

def search(query: str, top_k: int = 2) -> str:
    """Search local documents using semantic search."""
    retriever, error = _get_retriever()
    if error:
        return f"RAG system unavailable: {error}"

    try:
        results = retriever.retrieve(query, top_k=top_k)
        if not results:
            return f"No relevant documents found for: {query}"

        output = []
        for r in results:
            output.append(
                f"[Source: {r['source']} | relevance: {r['relevance_score']}]\n{r['text']}"
            )
        return "\n\n".join(output)
    except Exception as e:
        return f"RAG search error: {str(e)}"

def run(action_input: str) -> str:
    """Entry point for agent."""
    return search(action_input.strip())

if __name__ == "__main__":
    print("RAG Tool Tests:")
    print("=" * 40)

    queries = [
        "what is machine learning",
        "who created linux",
        "python libraries"
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        print(search(query))
        print("-" * 30)

