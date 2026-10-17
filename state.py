import json
from datetime import date, timedelta
from pathlib import Path

import config

PATH = Path(__file__).parent / "sent.json"


def load():
    if not PATH.exists():
        return {}
    return json.loads(PATH.read_text(encoding="utf-8"))


def save(sent, new_urls, today):
    for u in new_urls:
        sent[u] = today.isoformat()
    limit = (today - timedelta(days=config.STATE_KEEP_DAYS)).isoformat()
    kept = {u: d for u, d in sent.items() if d >= limit}
    PATH.write_text(json.dumps(kept, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
