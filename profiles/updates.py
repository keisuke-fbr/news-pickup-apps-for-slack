import os

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
BODY_CHARS = 2000
ARTICLES_PER_SOURCE = 5
REQUEST_INTERVAL_SEC = 1.0
STATE_KEEP_DAYS = 90
STATE_FILE = "sent_updates.json"

MODE = "updates"
SLACK_CHANNEL_ENV = "SLACK_CHANNEL_ID_UPDATES"

# RSSフィードが確認できないサイトは alt に HTMLページを指定してフォールバック
FEEDS = [
    {"group": "製品アップデート", "source": "Anthropic",
     "url": "https://www.anthropic.com/rss.xml",
     "alt": "https://www.anthropic.com/news"},
    {"group": "製品アップデート", "source": "OpenAI",
     "url": "https://openai.com/news/rss.xml"},
    {"group": "製品アップデート", "source": "Google Cloud",
     "url": "https://cloudblog.withgoogle.com/rss/",
     "alt": "https://cloud.google.com/blog/ja"},
    {"group": "製品アップデート", "source": "Databricks",
     "url": "https://www.databricks.com/feed",
     "alt": "https://www.databricks.com/company/newsroom"},
    {"group": "製品アップデート", "source": "AWS",
     "url": "https://aws.amazon.com/about-aws/whats-new/recent/feed/"},
    # RSSがないため、一覧ページのリンクから詳細ページをたどる
    {"group": "製品アップデート", "source": "Hugging Face",
     "url": "https://huggingface.co/changelog",
     "link_pattern": r'href="(/changelog/[^"#?]+)"'},
]

ITEM_SPEC = """各記事について次のJSONオブジェクトを作る。
{"id": "入力のid", "product": "製品名", "update": "アップデート内容(1〜2文)"}
- 製品のアップデート・新機能・新モデルのリリースに関する記事のみ対象とする。
- 採用情報・研究論文・イベント告知・一般的な解説・企業ニュース等は {"id": "...", "skip": true} とする。
- 日本語で書く。updateは1〜2文以内。productは製品の正式名称で書く。
- 記事から製品名が明確でない場合は提供元のサービス名(例: Claude, GPT-4o, Gemini, Databricks Runtime)を使う。"""
