"""GitHub REST API 클라이언트. WF9가 신규 저장소의 README를 받을 때 쓴다."""
import httpx

from app.config import get_settings

API = "https://api.github.com"


class GitHubClient:
    def __init__(self, token: str = "", client: httpx.Client | None = None):
        self._headers = {"Accept": "application/vnd.github.raw", "User-Agent": "git-trend-for-korean",
                         "X-GitHub-Api-Version": "2022-11-28"}
        if token:
            self._headers["Authorization"] = f"Bearer {token}"
        self._client = client or httpx.Client(timeout=30)

    def readme(self, full_name: str) -> str | None:
        r = self._client.get(f"{API}/repos/{full_name}/readme", headers=self._headers)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.text


def get_github_client() -> GitHubClient:
    return GitHubClient(token=get_settings().github_token)
