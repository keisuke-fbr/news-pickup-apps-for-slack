"""使い方:
  python main.py [--profile tech|updates]  取得 → 要約 → Slack送信
  python main.py --dry-run                 Slackへ送らず内容を表示(GEMINI_API_KEYは必要)
  python main.py --fetch-only              取得結果だけ表示(APIキー不要)
"""
import sys
from datetime import datetime

import config
import slack
import sources
import state
import summarize


def collect(label, fn, *args):
    try:
        items = fn(*args)
        print(f"{label}: {len(items)}件")
        return items
    except Exception as e:
        print(f"{label}: 取得失敗 {e}")
        return []


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    fetch_only = "--fetch-only" in sys.argv
    dry = "--dry-run" in sys.argv
    today = datetime.now(sources.JST).date()
    sent = state.load()

    if config.MODE == "digest":
        articles = []
        for feed in config.FEEDS:
            articles += collect(feed["source"], sources.fetch_feed, feed, sent)
        articles += collect("Hugging Face Papers", sources.fetch_papers, sent, today)
        events = (collect("connpass", sources.fetch_connpass, sent, today) +
                  collect("TechPlay", sources.fetch_techplay, sent, today))

        for i, it in enumerate(articles):
            it.id = f"a{i}"
        for i, it in enumerate(events):
            it.id = f"e{i}"

        if fetch_only:
            for it in articles + events:
                print(f"- [{it.group}/{it.source}] {it.title} {it.meta}\n  {it.url}\n  {it.body[:100]!r}")
            return
        if not articles and not events:
            print("新着がないため送信しません")
            return

        items = articles + events
        sums = summarize.summarize_articles(items)
        themes = summarize.synthesize(items, sums)
        blocks = slack.build_blocks(f"{today:%Y/%m/%d}", items, themes, len(articles), len(events))
        fallback = f"技術ニュースダイジェスト {today:%Y/%m/%d}"
        new_urls = [it.url for it in items]

    elif config.MODE == "updates":
        articles = []
        for feed in config.FEEDS:
            articles += collect(feed["source"], sources.fetch_feed, feed, sent)

        for i, it in enumerate(articles):
            it.id = f"a{i}"

        if fetch_only:
            for it in articles:
                print(f"- [{it.source}] {it.title}\n  {it.url}\n  {it.body[:100]!r}")
            return
        if not articles:
            print("新着がないため送信しません")
            return

        sums = summarize.summarize_updates(articles)
        if not sums:
            print("製品アップデートに該当する記事がないため送信しません")
            return
        blocks = slack.build_update_blocks(f"{today:%Y/%m/%d}", articles, sums)
        fallback = f"製品アップデート {today:%Y/%m/%d}"
        new_urls = [it.url for it in articles]

    else:
        raise ValueError(f"未知のMODE: {config.MODE}")

    if dry:
        import json
        print(json.dumps(blocks, ensure_ascii=False, indent=1))
        return
    slack.post(blocks, fallback)
    state.save(sent, new_urls, today)
    print("送信しました")


if __name__ == "__main__":
    main()
