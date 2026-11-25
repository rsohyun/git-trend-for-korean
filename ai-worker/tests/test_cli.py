import json

from app import cli
from tests.test_gittrend import DAY1, DAY2, fakes  # noqa: F401,F811  가짜 GitHub 트렌딩·README 응답 재사용


class FakeSMTP:
    sent = []

    def __init__(self, host, port):
        assert (host, port) == ("smtp.gmail.com", 465)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def login(self, user, password):
        self.user = user

    def send_message(self, msg):
        FakeSMTP.sent.append(msg)


def test_send_mail_uses_bcc_and_html():
    cli.send_mail({"subject": "제목", "html": "<p>본문</p>"}, "me@gmail.com", "pw", ["a@x.com", "b@x.com"],
                  smtp=FakeSMTP)
    msg = FakeSMTP.sent[-1]
    assert msg["To"] == "me@gmail.com" and msg["Bcc"] == "a@x.com, b@x.com" and msg["Subject"] == "제목"
    assert "<p>본문</p>" in msg.get_body(("html",)).get_content()


def _run_cli(monkeypatch, tmp_path, day):
    from app.github import get_github_client
    from app.main import app
    from app.trending import get_trending_client

    monkeypatch.setattr(cli, "get_trending_client", app.dependency_overrides[get_trending_client])
    monkeypatch.setattr(cli, "get_github_client", app.dependency_overrides[get_github_client])
    monkeypatch.setattr(cli, "today_kst", lambda: day)
    monkeypatch.setenv("SITE_DIR", str(tmp_path / "site"))
    from app.config import get_settings

    get_settings.cache_clear()
    mail_out = tmp_path / "mail.json"
    cli.main(["gittrend", "--mail-out", str(mail_out)])
    return json.loads(mail_out.read_text(encoding="utf-8"))


def test_gittrend_command_writes_mail_and_site(fakes, fake_llm, monkeypatch, tmp_path):  # noqa: F811
    mail = _run_cli(monkeypatch, tmp_path, DAY1)
    assert mail["subject"] == "[Github 트렌딩] 2026-11-05 · 신규 0개" and "acme/rea" in mail["html"]
    assert "acme/weekonly" in (tmp_path / "site/index.html").read_text(encoding="utf-8")


def test_mail_subject_counts_new_in_week_and_today(fakes, fake_llm, monkeypatch, tmp_path):  # noqa: F811
    _run_cli(monkeypatch, tmp_path, DAY1)
    fakes["lists"]["weekly"].append(("acme/both", 10, 10))
    fakes["lists"]["daily"].append(("acme/both", 5, 10))
    fakes["lists"]["monthly"].append(("acme/monthonly", 99, 10))
    mail = _run_cli(monkeypatch, tmp_path, DAY2)
    assert mail["subject"] == "[Github 트렌딩] 2026-11-06 · 신규 1개"


def test_subject_says_list_not_updated_when_stale():
    assert cli.subject({"date": "2026-11-25", "new_count": 0, "stale": True}) == \
        "[Github 트렌딩] 2026-11-25 · GitHub 목록 갱신 없음"
    assert cli.subject({"date": "2026-11-25", "new_count": 3}) == "[Github 트렌딩] 2026-11-25 · 신규 3개"
