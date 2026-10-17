import os

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# 記事ごとにLLMへ渡す本文の最大文字数
BODY_CHARS = 3000

# RSSで取得するブログ。ARTICLES_PER_SOURCE件ずつ新しい順に見る
ARTICLES_PER_SOURCE = 3
FEEDS = [
    {"group": "国内ブログ", "source": "メルカリ", "url": "https://engineering.mercari.com/blog/feed.xml"},
    {"group": "国内ブログ", "source": "LINEヤフー", "url": "https://techblog.lycorp.co.jp/ja/feed/index.xml"},
    {"group": "国内ブログ", "source": "サイバーエージェント", "url": "https://developers.cyberagent.co.jp/blog/feed/"},
    {"group": "海外企業", "source": "Google Developers", "url": "https://developers.googleblog.com/rss/"},
    {"group": "海外企業", "source": "Netflix", "url": "https://netflixtechblog.com/feed"},
    {"group": "海外企業", "source": "Amazon Science", "url": "https://www.amazon.science/index.rss"},
    {"group": "海外企業", "source": "OpenAI", "url": "https://openai.com/news/rss.xml"},
]

# Hugging Face Papers: 前日分のうちupvote上位
PAPERS_TOP_N = 5

# 講演: 検索キーワードで候補を集め、開催が近い順にEVENTS_PER_SITE件ずつ
EVENT_KEYWORDS = ["AI", "LLM", "AIエージェント", "生成AI", "機械学習", "Platform Engineering", "アーキテクチャ", "開発"]
EVENTS_PER_SITE = 10
EVENT_CANDIDATES_PER_SITE = 40
# テーマの手がかりにならない集まりを除く(タイトルに含まれていたら除外)
EVENT_EXCLUDE_TITLE = ["もくもく", "朝活", "ゲームジャム", "CoderDojo", "雑談", "交流会", "オフ会"]
REQUEST_INTERVAL_SEC = 1.0

# 送信済みURLを覚えておく日数
STATE_KEEP_DAYS = 90

CATEGORIES = [
    "AI/エージェント関連",
    "AI/フィジカルAI関連",
    "AI/その他深層学習関連",
    "AI/応用領域",
    "AI/ビジネス利用",
    "ソフトウェア開発",
    "その他",
]
