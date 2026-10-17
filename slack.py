import json
import os
import urllib.request

import config

MAX_BLOCKS = 45


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(text):
    return {"type": "header", "text": {"type": "plain_text", "text": text[:150]}}


def section(text):
    return {"type": "section", "text": {"type": "mrkdwn", "text": text[:2900]}}


def item_block(item, s):
    kws = " ".join(f"`{esc(k)}`" for k in s["keywords"])
    meta = f"  _{esc(item.source)}{' ・ ' + esc(item.meta) if item.meta else ''}_"
    return section(
        f"*<{item.url}|{esc(item.title)}>*{meta}\n"
        f"• 課題: {esc(s['problem'])}\n• うれしさ: {esc(s['benefit'])}\n"
        f"• 解決策: {esc(s['solution'])}\n• キーワード: {kws}")


def grouped_blocks(items, summaries):
    blocks = []
    for cat in config.CATEGORIES:
        rows = [(it, summaries[it.id]) for it in items if it.id in summaries and summaries[it.id]["category"] == cat]
        if rows:
            blocks.append(section(f"*■ {esc(cat)}*"))
            blocks += [item_block(it, s) for it, s in rows]
    return blocks


def build_blocks(date_str, articles, article_sums, events, event_sums, themes):
    blocks = [header(f"📰 技術ニュースダイジェスト {date_str}")]
    body = grouped_blocks(articles, article_sums)
    if body:
        blocks += [section("*📚 記事・論文*")] + body
    ev_body = grouped_blocks(events, event_sums)
    if themes or ev_body:
        blocks += [{"type": "divider"}, section("*🎤 講演から見る、いま話題のテーマ*")]
        by_id = {e.id: e for e in events}
        for t in themes:
            links = ", ".join(f"<{by_id[i].url}|{esc(by_id[i].title[:40])}>" for i in t.get("event_ids", [])[:3] if i in by_id)
            blocks.append(section(f"*{esc(t.get('theme', ''))}*\n{esc(t.get('summary', ''))}" + (f"\n例: {links}" if links else "")))
        if ev_body:
            blocks += [section("*📅 注目イベント*")] + ev_body
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
