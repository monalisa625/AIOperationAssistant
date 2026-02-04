import asyncio
import os
from typing import Any, Dict

import requests


GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"


def _build_github_headers() -> Dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai-ops-assistant",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _search_repositories_sync(query: str, per_page: int = 3) -> Dict[str, Any]:
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": per_page,
    }
    try:
        response = requests.get(
            GITHUB_SEARCH_URL,
            headers=_build_github_headers(),
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        items = []
        for repo in data.get("items", []):
            items.append(
                {
                    "full_name": repo.get("full_name"),
                    "html_url": repo.get("html_url"),
                    "stargazers_count": repo.get("stargazers_count"),
                    "description": repo.get("description"),
                    "language": repo.get("language"),
                }
            )

        return {
            "query": query,
            "total_count": data.get("total_count"),
            "items": items,
        }
    except requests.RequestException as exc:
        return {
            "query": query,
            "error": f"GitHub API request failed: {exc}",
        }


async def search_repositories(query: str, per_page: int = 3) -> Dict[str, Any]:
    """
    Search GitHub repositories using the public search REST API.

    This function is async but uses a threadpool internally because the
    requests library is synchronous.
    """
    return await asyncio.to_thread(_search_repositories_sync, query, per_page)

