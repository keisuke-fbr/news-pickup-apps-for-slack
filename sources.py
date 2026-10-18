import html
import itertools
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import config

JST = timezone(timedelta(hours=9))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"


@dataclass
class Item:
    group: str
    source: str
    title: str
    url: str
    body: str
    meta: str = ""
    id: str = ""


def http_get(url, retries=3):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ja,en;q=0.8"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception as e:
            last = e
            time.sleep(2 * (i + 1))
    raise last


def http_get_text(url):
    return http_get(url).decode("utf-8", errors="replace")


def html_to_text(s):
    s = re.sub(r"(?is)<(script|style|noscript).*?</\1>", "", s)
    s = re.sub(r"(?s)<[^>]+>", "\n", s)
    s = html.unescape(s)
    lines = [ln.strip() for ln in s.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def page_title(page):
    m = re.search(r"(?is)<head.*?<title[^>]*>(.*?)</title>", page)  # body内のSVG <title> を避ける
    title = html.unescape(m.group(1)).strip() if m else ""
    return title.rsplit(" - ", 1)[0] if " - " in title else title


# ---------- RSS ----------

def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _child_text(e, *names):
    for c in e:
        if _local(c.tag) in names and (c.text or "").strip():
            return c.text
    return ""


def _link(e):
    href = ""
    for c in e:
        if _local(c.tag) != "link":
            continue
        if c.get("href"):
            if c.get("rel") in (None, "alternate"):
                return c.get("href")
            href = href or c.get("href")
        elif (c.text or "").strip():
            return c.text.strip()
    return href


def _parse_date(s):
    if not s:
        return None
    try:
        d = parsedate_to_datetime(s)
    except (TypeError, ValueError):
        try:
            d = datetime.fromisoformat(s.strip().replace("Z", "+00:00"))
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def parse_feed(raw):
    root = ET.fromstring(raw)
    entries = []
    for e in root.iter():
        if _local(e.tag) not in ("item", "entry"):
            continue
        entries.append({
            "title": html_to_text(_child_text(e, "title")).replace("\n", " "),
            "url": _link(e),
            "date": _parse_date(_child_text(e, "pubDate", "published", "updated", "date")),
            "body": html_to_text(_child_text(e, "encoded", "content", "description", "summary")),
        })
    floor = datetime.min.replace(tzinfo=timezone.utc)
    entries.sort(key=lambda x: x["date"] or floor, reverse=True)
    return entries


def _article_text(url):
    page = http_get_text(url)
    m = re.search(r"(?is)<article.*?</article>", page)
    return html_to_text(m.group(0) if m else page)


def fetch_feed(feed, sent):
    try:
        raw = http_get(feed["url"])
    except Exception:
        if not feed.get("alt"):
            raise
        print(f"  {feed['source']}: 取得失敗のため予備URLを試します")
        raw = http_get(feed["alt"])
    entries = [e for e in parse_feed(raw) if e["url"] and e["url"] not in sent]
    items = []
    for e in entries[: config.ARTICLES_PER_SOURCE]:
        body = e["body"]
        if len(body) < 500:
            try:
                time.sleep(config.REQUEST_INTERVAL_SEC)
                body = _article_text(e["url"]) or body
            except Exception as ex:
                print(f"  本文取得に失敗 {e['url']}: {ex}")
        items.append(Item(feed["group"], feed["source"], e["title"], e["url"], body[: config.BODY_CHARS]))
    return items


# ---------- Hugging Face Papers ----------

def fetch_papers(sent, today):
    data = []
    for back in range(1, 5):  # 休日で空なら遡る
        d = (today - timedelta(days=back)).strftime("%Y-%m-%d")
        data = json.loads(http_get_text(f"https://huggingface.co/api/daily_papers?date={d}"))
        if data:
            break
    papers = [e["paper"] for e in data]
    papers.sort(key=lambda p: p.get("upvotes") or 0, reverse=True)
    items = []
    for p in papers:
        url = f"https://huggingface.co/papers/{p['id']}"
        if url in sent:
            continue
        items.append(Item("論文", "Hugging Face Papers", p["title"], url,
                          (p.get("summary") or "")[: config.BODY_CHARS], meta=f"👍{p.get('upvotes') or 0}"))
        if len(items) >= config.PAPERS_TOP_N:
            break
    return items


# ---------- イベント ----------

def _event_date(text, marker):
    i = text.find(marker)
    m = re.search(r"(\d{4})/(\d{2})/(\d{2})", text[i:] if i >= 0 else text)
    return date(int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


def _after(text, marker):
    i = text.find(marker)
    return text[i + len(marker):] if i >= 0 else text


def _event_candidates(search_urls, pattern, prefix, sent):
    per_kw = []
    for u in search_urls:
        try:
            found = list(dict.fromkeys(re.findall(pattern, http_get_text(u))))
        except Exception as e:
            print(f"  検索に失敗 {u}: {e}")
            found = []
        per_kw.append([prefix + f for f in found])
        time.sleep(config.REQUEST_INTERVAL_SEC)
    mixed = [u for grp in itertools.zip_longest(*per_kw) for u in grp if u]  # キーワードを均等に混ぜる
    return [u for u in dict.fromkeys(mixed) if u not in sent][: config.EVENT_CANDIDATES_PER_SITE]


def _collect_events(source, urls, parse, today):
    events = []
    for u in urls:
        try:
            page = http_get_text(u)
            title = page_title(page).replace("\n", " ")
            text = html_to_text(page)
            d, body = parse(text)
            if d and d >= today and not any(w in title for w in config.EVENT_EXCLUDE_TITLE):
                events.append((d, Item("講演", source, title, u, body[: config.BODY_CHARS], meta=f"{d:%Y/%m/%d}開催")))
        except Exception as e:
            print(f"  詳細取得に失敗 {u}: {e}")
        time.sleep(config.REQUEST_INTERVAL_SEC)
    events.sort(key=lambda x: x[0])
    return [it for _, it in events[: config.EVENTS_PER_SITE]]


def fetch_connpass(sent, today):
    # start_fromを付けると開催日の近い順に並ぶ(未指定だと関連度順で過去イベントが混ざる)
    searches = ["https://connpass.com/search/?" + urllib.parse.urlencode({"q": kw, "start_from": f"{today:%Y/%m/%d}"})
                for kw in config.EVENT_KEYWORDS]
    urls = _event_candidates(searches, r"https://[a-z0-9\-]+\.connpass\.com/event/\d+/", "", sent)
    return _collect_events("connpass", urls,
                           lambda t: (_event_date(t, "開催日時"), _after(t, "イベントの説明")), today)


def fetch_techplay(sent, today):
    searches = ["https://techplay.jp/event/search?" + urllib.parse.urlencode({"keyword": kw}) for kw in config.EVENT_KEYWORDS]
    urls = _event_candidates(searches, r'href="(/event/\d+)"', "https://techplay.jp", sent)
    return _collect_events("TechPlay", urls,
                           lambda t: (_event_date(t, "基本情報"), _after(_after(t, "イベント内容"), "概要")), today)
