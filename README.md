# news_app

技術ブログ・論文・勉強会の情報を集め、Geminiで要約して毎朝7:00(JST)にSlackのDMへ送る。

## セットアップ
1. **Slack App**: https://api.slack.com/apps で作成 → OAuth & Permissions で Bot Token Scope に `chat:write` を追加 → ワークスペースへインストールして `xoxb-...` を取得。App Home の「Messages Tab」を有効にする。自分のメンバーID(プロフィール → ︙ → メンバーIDをコピー)も控える。
2. **Gemini**: https://aistudio.google.com/apikey でAPIキーを取得。
3. **GitHub**: このフォルダをリポジトリにpushし、Settings → Secrets and variables → Actions に登録する。
   - `SLACK_BOT_TOKEN` / `SLACK_USER_ID` / `GEMINI_API_KEY`
4. Actions タブの `daily-news` から `Run workflow` で手動実行して確認する。

## ローカル実行
```
python main.py --fetch-only                 # 取得のみ(キー不要)
GEMINI_API_KEY=... python main.py --dry-run # 要約してSlack用JSONを表示
```

## 調整
`config.py` で取得元、件数、イベントの検索キーワード、除外語、カテゴリを変えられる。
送信済みURLは `sent.json` に記録され、次回以降は重複して送らない。
