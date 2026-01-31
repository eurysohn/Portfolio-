import html
import re
import urllib.parse
import urllib.request
from typing import Dict, List


USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"


def _fetch(url: str, timeout: int = 8) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def web_search(query: str, max_results: int = 3) -> List[Dict]:
    try:
        encoded = urllib.parse.quote_plus(query)
        url = f"https://duckduckgo.com/html/?q={encoded}"
        html_text = _fetch(url)
    except Exception:
        return []

    results: List[Dict] = []
    for match in re.finditer(r'class="result__a"\s+href="([^"]+)"[^>]*>(.*?)</a>', html_text):
        link = html.unescape(match.group(1))
        if "uddg=" in link:
            try:
                parsed = urllib.parse.urlparse(link)
                params = urllib.parse.parse_qs(parsed.query)
                if "uddg" in params and params["uddg"]:
                    link = urllib.parse.unquote(params["uddg"][0])
            except Exception:
                pass
        title = re.sub(r"<.*?>", "", match.group(2))
        results.append({"url": link, "title": html.unescape(title), "snippet": ""})
        if len(results) >= max_results:
            break

    snippets = re.findall(r'class="result__snippet".*?>(.*?)</a?>', html_text, flags=re.DOTALL)
    for idx, snippet in enumerate(snippets[: len(results)]):
        clean = re.sub(r"<.*?>", "", snippet)
        results[idx]["snippet"] = html.unescape(clean).strip()

    for r in results:
        r["score"] = 1.0
    return results
