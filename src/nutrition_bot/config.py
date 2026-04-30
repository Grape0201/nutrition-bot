import os
from datetime import timedelta, timezone
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GAS_WEBHOOK_URL = os.environ["GAS_WEBHOOK_URL"]

# JSTタイムゾーンの設定
JST = timezone(timedelta(hours=9), "Asia/Tokyo")
