# Nutrition Discord Bot

AI（Gemini 1.5 Flash / 2.0 Flash Lite）を活用して、Discordに投稿された食事の画像やテキストから栄養素を自動解析し、Googleスプレッドシートに記録するDiscordボットです。

## 🌟 主な機能

- **食事の自動解析**: 送信された写真や説明テキストから、料理名、カロリー、タンパク質、脂質、炭水化物をAIが推測します。
- **Google 検索連携**: AIが最新の情報を検索して、より正確な栄養素情報を取得します（Google Search Grounding）。
- **自動ロギング**: 解析結果を Google Apps Script (GAS) を通じて Google スプレッドシートに自動保存します。
- **スマートな時刻取得**: 画像のEXIFデータから撮影日時を取得し、記録時刻として優先的に使用します（EXIFがない場合は投稿時刻を使用）。

## 📋 事前準備

このボットを使用するには、以下の設定が必要です。

1.  **Discord Bot Token**: [Discord Developer Portal](https://discord.com/developers/applications) でボットを作成し、トークンを取得してください。
2.  **Gemini API Key**: [Google AI Studio](https://aistudio.google.com/) でAPIキーを取得してください。
3.  **Google Apps Script (GAS)**:
    - スプレッドシートを作成し、それを受け取るためのGASウェブアプリをデプロイしてください。
    - POSTリクエストを受け取り、スプレッドシートにデータを書き込むエンドポイントが必要です。

## 🛠 セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/your-username/nutrition-discord-bot.git
cd nutrition-discord-bot
```

### 2. 環境変数の設定

`.env` ファイルを作成し、以下の情報を入力してください。

```env
DISCORD_BOT_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_gemini_api_key
GAS_WEBHOOK_URL=your_gas_webhook_url
```

### 3. 依存関係のインストール

このプロジェクトは [uv](https://github.com/astral-sh/uv) を使用しています。

```bash
uv sync
```

## 🚀 実行方法

以下のコマンドでボットを起動します。

```bash
uv run nutrition-bot
```

## 📖 使い方

1.  Discordサーバーにボットを招待します（メッセージの読み取り権限が必要です）。
2.  食事の画像、または食事の内容を書いたテキストをメッセージとして送信します。
3.  AIが解析を開始し、完了すると栄養素情報がリプライされます。
4.  同時に、設定した Google スプレッドシートへデータが転送されます。

## 🧪 開発とテスト

### テストの実行

```bash
uv run pytest
```

### GAS連携のテストスクリプト

`scripts/test_gas_integration.py` を使用して、GASエンドポイントが正しく動作するか確認できます。

```bash
uv run python scripts/test_gas_integration.py
```

## 📄 ライセンス

[MIT License](LICENSE)
