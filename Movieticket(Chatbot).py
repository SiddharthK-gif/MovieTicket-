import re
import urllib.error
import urllib.parse
import urllib.request
from typing import List, Tuple


def fetch_text_from_url(url: str) -> str:
    """Fetch the document from a URL."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; quickstart-research/1.0)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read()
    except urllib.error.URLError as e:
        return f"Fetch failed: {e}"
    except Exception as e:
        return f"Fetch failed: {e}"

    try:
        text = raw.decode("utf-8", errors="replace")
    except Exception:
        text = raw.decode("latin-1", errors="replace")
    return text


def parse_duckduckgo_results(html: str, limit: int = 5) -> List[Tuple[str, str]]:
    """Parse DuckDuckGo HTML search results for titles and URLs."""
    results = []
    for match in re.finditer(
        r'<a[^>]+class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
        html,
        re.IGNORECASE | re.DOTALL,
    ):
        url = urllib.parse.unquote(match.group(1))
        title = re.sub(r"<.*?>", "", match.group(2)).strip()
        if title and url:
            results.append((title, url))
            if len(results) >= limit:
                break
    if not results:
        for match in re.finditer(
            r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            html,
            re.IGNORECASE | re.DOTALL,
        ):
            url = urllib.parse.unquote(match.group(1))
            title = re.sub(r"<.*?>", "", match.group(2)).strip()
            if title and url and len(results) < limit:
                results.append((title, url))
    return results


def search_theaters(date: str, city: str) -> str:
    """Search the internet for theaters with available seats on a specific date."""
    query = f"{city} movie theater availability seats {date}"
    search_url = (
        "https://html.duckduckgo.com/html/?q="
        + urllib.parse.quote_plus(query)
    )
    html = fetch_text_from_url(search_url)
    if html.startswith("Fetch failed:"):
        return html

    results = parse_duckduckgo_results(html, limit=8)
    if not results:
        snippet = html[:800].replace("\n", " ")
        return (
            "No theaters could be extracted from search results. "
            "Here is a search summary:\n" + snippet
        )

    theater_lines = []
    for title, url in results:
        lower_title = title.lower()
        if any(keyword in lower_title for keyword in ["theater", "cinema", "movie", "showtime"]):
            theater_lines.append(f"{title} — {url}")
    if not theater_lines:
        theater_lines = [f"{title} — {url}" for title, url in results]

    header = (
        f"Search results for movie theaters in {city} on {date}:\n"
        "These pages may contain seat availability details."
    )
    return header + "\n\n" + "\n".join(theater_lines)


def main() -> None:
    date = input("Which date do you want to book your movie tickets? ").strip()
    city = input("Which city do you want to book your movie tickets? ").strip()

    if not date or not city:
        print("Please enter both a booking date and a city.")
        return

    print(f"Searching for theaters with available seats in {city} on {date}...\n")
    result = search_theaters(date, city)
    print(result)


if __name__ == "__main__":
    main()