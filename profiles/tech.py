import json
import os

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
BODY_CHARS = 3000
ARTICLES_PER_SOURCE = 3
REQUEST_INTERVAL_SEC = 1.0
STATE_KEEP_DAYS = 90
STATE_FILE = "sent.json"

MODE = "digest"
SLACK_CHANNEL_ENV = "SLACK_USER_ID"

FEEDS = [
    {"group": "国内ブログ", "source": "メルカリ", "url": "https://engineering.mercari.com/blog/feed.xml",
     "alt": "https://engineering.mercari.com/en/blog/feed.xml"},
    {"group": "国内ブログ", "source": "LINEヤフー", "url": "https://techblog.lycorp.co.jp/ja/feed/index.xml"},
    {"group": "国内ブログ", "source": "サイバーエージェント", "url": "https://developers.cyberagent.co.jp/blog/feed/"},
    {"group": "海外企業", "source": "Google Developers", "url": "https://developers.googleblog.com/rss/"},
    {"group": "海外企業", "source": "Netflix", "url": "https://netflixtechblog.com/feed"},
    {"group": "海外企業", "source": "Amazon Science", "url": "https://www.amazon.science/index.rss"},
    {"group": "海外企業", "source": "OpenAI", "url": "https://openai.com/news/rss.xml"},
]

PAPERS_TOP_N = 5

EVENT_KEYWORDS = ["AI", "LLM", "AIエージェント", "生成AI", "機械学習", "Platform Engineering", "アーキテクチャ", "開発"]
EVENTS_PER_SITE = 10
EVENT_CANDIDATES_PER_SITE = 40
EVENT_EXCLUDE_TITLE = ["もくもく", "朝活", "ゲームジャム", "CoderDojo", "雑談", "交流会", "オフ会"]

CATEGORIES = [
    "AI/エージェント関連",
    "AI/フィジカルAI関連",
    "AI/その他深層学習関連",
    "AI/応用領域",
    "AI/ビジネス利用",
    "ソフトウェア開発",
    "その他",
]

ITEM_SPEC = f"""各記事について次のJSONオブジェクトを作る。
{{"id": "入力のid", "category": {json.dumps(CATEGORIES, ensure_ascii=False)} のいずれか1つ,
 "problem": "取り組まれている課題", "benefit": "それによって何がうれしいか",
 "solution": "その解決策", "keywords": ["キーワード", ...]}}
- 日本語で書く。problem/benefit/solutionは各1文以内。keywordsは3〜5個で、英語の技術用語は原語のままにする。
- 講演・イベントは、そのイベントが扱う課題と、紹介される解決策・取り組みとして読み替える。
- 記事に書かれていないことは書かない。本文から読み取れない項目は「記載なし」とする。
- categoryは記事の主題で決める。エージェント関連=自律的にツールを使い作業するLLMエージェント、フィジカルAI=ロボティクスや実世界で動くAI、
  その他深層学習=基盤モデルや学習手法など、応用領域=医療・金融・教育など特定領域へのAI適用、
  ビジネス利用=企業のAI導入事例・業務への組み込み・導入定着・効果測定・組織や人材への影響、ソフトウェア開発=AI以外の開発手法・基盤・組織・運用。"""
