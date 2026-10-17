import json
import os
import urllib.request

import config

MAX_BLOCKS = 45
MAX_SOURCES = 4


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(text):
    return {"type": "header", "text": {"type": "plain_text", "text": text[:150]}}


def section(text):
    return {"type": "section", "text": {"type": "mrkdwn", "text": text[:2900]}}


def theme_block(theme, by_id):
    kws = " ".join(f"`{esc(k)}`" for k in theme["keywords"])
    refs = " / ".join(
        f"<{by_id[i].url}|{esc(by_id[i].source)}: {esc(by_id[i].title[:30])}>" for i in theme["source_ids"][:MAX_SOURCES])
    return section(
        f"*◆ {esc(theme['topic'])}*\n"
        f"• 課題: {esc(theme['problem'])}\n• うれしさ: {esc(theme['benefit'])}\n"
        f"• 解決策: {esc(theme['solution'])}\n• キーワード: {kws}"
        + (f"\n_出典: {refs}_" if refs else ""))


def build_blocks(date_str, items, themes_by_cat, n_articles, n_events):
    by_id = {it.id: it for it in items}
    blocks = [header(f"📰 技術トレンド整理 {date_str}"),
              section(f"_記事・論文 {n_articles}件、講演 {n_events}件を読んで整理しました_")]
    for cat in config.CATEGORIES:
        themes = themes_by_cat.get(cat)
        if themes:
            blocks.append({"type": "divider"})
            blocks.append(section(f"*■ {esc(cat)}*"))
            blocks += [theme_block(t, by_id) for t in themes]
    return blocks


def post(blocks, fallback):
    token, user = os.environ["SLACK_BOT_TOKEN"], os.environ["SLACK_USER_ID"]
    for i in range(0, len(blocks), MAX_BLOCKS):
        payload = {"channel": user, "text": fallback, "blocks": blocks[i:i + MAX_BLOCKS],
                   "unfurl_links": False, "unfurl_media": False}
        req = urllib.request.Request(
            "https://slack.com/api/chat.postMessage", data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json; charset=utf-8", "Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.load(r)
        if not resp.get("ok"):
            raise RuntimeError(f"Slack error: {resp.get('error')}")
