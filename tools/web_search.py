import urllib.request
import urllib.parse
import json
import re

def search(query: str, max_results: int = 3) -> str:
    """
    Search the web using DuckDuckGo instant answer API.
    No API key needed — completely free.
    """
    # Clean query
    query = query.strip()
    encoded_query = urllib.parse.quote(query)

    # DuckDuckGo instant answer API
    url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "AutoAgent/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

        results = []

        # Abstract (main answer)
        if data.get("Abstract"):
            results.append(f"Summary: {data['Abstract']}")
            if data.get("AbstractURL"):
                results.append(f"Source: {data['AbstractURL']}")

        # Instant answer
        if data.get("Answer"):
            results.append(f"Answer: {data['Answer']}")

        # Related topics
        topics = data.get("RelatedTopics", [])[:max_results]
        for topic in topics:
            if isinstance(topic, dict) and topic.get("Text"):
                results.append(f"- {topic['Text'][:200]}")

        if results:
            return "\n".join(results)
        else:
            return f"No direct results found for '{query}'. Try a more specific query."

    except urllib.error.URLError as e:
        return f"Network error: {str(e)}"
    except Exception as e:
        return f"Search error: {str(e)}"

def run(action_input: str) -> str:
    """Entry point for agent — search the web."""
    return search(action_input.strip())

if __name__ == "__main__":
    queries = [
        "Python programming language",
        "what is machine learning",
        "Linux kernel creator",
    ]

    print("Web Search Tool Tests:")
    print("=" * 40)
    for query in queries:
        print(f"\nQuery: {query}")
        print(search(query))
        print("-" * 30)

