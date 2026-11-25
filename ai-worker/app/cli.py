"""GitHub Actions에서 쓰는 명령 (D46).

python -m app.cli gittrend --mail-out mail.json   수집·요약·노트·스냅샷·사이트 생성, 메일 내용을 파일로 저장
python -m app.cli site                            노트·스냅샷으로 사이트만 다시 생성
python -m app.cli send-mail mail.json             저장한 메일을 Gmail SMTP로 발송
"""
import argparse
import json
import os
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path

from app.github import get_github_client
from app.gittrend import build_daily
from app.llm import get_llm
from app.site import build_site
from app.timeutil import today_kst
from app.tracing import get_tracer
from app.trending import get_trending_client


def subject(result: dict) -> str:
    if result.get("stale"):
        return f"[Github 트렌딩] {result['date']} · GitHub 목록 갱신 없음"
    return f"[Github 트렌딩] {result['date']} · 신규 {result['new_count']}개"


def cmd_gittrend(args) -> None:
    result = build_daily(get_trending_client(), get_github_client(), get_llm(), get_tracer(), today_kst())
    Path(args.mail_out).write_text(json.dumps({"subject": subject(result), "html": result["email_html"]},
                                              ensure_ascii=False), encoding="utf-8")
    site = build_site()
    print(json.dumps({k: v for k, v in result.items() if k != "email_html"} | {"site": site}, ensure_ascii=False))


def cmd_site(args) -> None:
    print(json.dumps(build_site(), ensure_ascii=False))


def send_mail(mail: dict, user: str, password: str, to: list[str], smtp=smtplib.SMTP_SSL) -> None:
    msg = EmailMessage()
    msg["Subject"], msg["From"], msg["To"] = mail["subject"], user, user
    msg["Bcc"] = ", ".join(to)  # 받는 사람끼리 서로의 주소가 보이지 않게
    msg.set_content("HTML 메일입니다. HTML을 표시할 수 있는 메일 앱에서 열어 주세요.")
    msg.add_alternative(mail["html"], subtype="html")
    with smtp("smtp.gmail.com", 465) as s:
        s.login(user, password)
        s.send_message(msg)


def cmd_send_mail(args) -> None:
    to = [a.strip() for a in os.environ["MAIL_TO"].split(",") if a.strip()]
    if not to:
        sys.exit("MAIL_TO가 비어 있습니다")
    mail = json.loads(Path(args.file).read_text(encoding="utf-8"))
    send_mail(mail, os.environ["GMAIL_USER"], os.environ["GMAIL_APP_PASSWORD"], to)
    print(f"sent to {len(to)} recipient(s)")


def main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="app.cli")
    sub = p.add_subparsers(required=True)
    g = sub.add_parser("gittrend")
    g.add_argument("--mail-out", default="mail.json")
    g.set_defaults(func=cmd_gittrend)
    sub.add_parser("site").set_defaults(func=cmd_site)
    m = sub.add_parser("send-mail")
    m.add_argument("file")
    m.set_defaults(func=cmd_send_mail)
    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
