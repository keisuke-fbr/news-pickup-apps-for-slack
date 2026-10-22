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
        f"<{by_id[i].url}|{esc(by_id[i].source)}>" for i in theme["source_ids"][:MAX_SOURCES])
    return section(
        f"*◆ {esc(theme['topic'])}*\n"
        f"• *課題* {esc(theme['problem'])}\n"
        f"• *うれしさ* {esc(theme['benefit'])}\n"
        f"• *解決策* {esc(theme['solution'])}\n"
        f"• *キーワード* {kws}"
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


def build_update_blocks(date_str, items, sums):
    by_id = {it.id: it for it in items}
    blocks = [
        header(f"📦 製品アップデート {date_str}"),
        section(f"_{len(sums)}件のアップデートを検出しました_"),
    ]
    by_source = {}
    for item_id, s in sums.items():
        by_source.setdefault(by_id[item_id].source, []).append((item_id, s))
    for source, entries in by_source.items():
        blocks.append({"type": "divider"})
        blocks.append(section(f"*■ {esc(source)}*"))
        for item_id, s in entries:
            it = by_id[item_id]
            blocks.append(section(
                f"*◆ {esc(s['product'])}*\n"
                f"{esc(s['update'])}\n"
                f"_<{it.url}|記事を読む>_"
            ))
    return blocks


def post(blocks, fallback):
    token = os.environ["SLACK_BOT_TOKEN"]
    channel = os.environ[config.SLACK_CHANNEL_ENV]
    for i in range(0, len(blocks), MAX_BLOCKS):
        payload = {"channel": channel, "text": fallback, "blocks": blocks[i:i + MAX_BLOCKS],
                   "unfurl_links": False, "unfurl_media": False}
        req = urllib.request.Request(
            "https://slack.com/api/chat.postMessage", data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json; charset=utf-8", "Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.load(r)
        if not resp.get("ok"):
            raise RuntimeError(f"Slack error: {resp.get('error')}")
