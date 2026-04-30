import asyncio
import json
import os
from datetime import datetime
from nutrition_bot.services import analyze_with_gemini
from nutrition_bot.config import JST


async def main():
    print("🤖 Geminiによる食事解析テストを開始します...")

    # テスト設定
    image_path = "./scripts/assets/sample_food.png"
    text_input = "今日の朝ごはんです。鮭が美味しそう。"
    eaten_at = datetime.now(JST).isoformat()

    image_data = None
    if os.path.exists(image_path):
        print(f"📸 画像ファイルを読み込んでいます: {image_path}")
        with open(image_path, "rb") as f:
            image_data = f.read()
    else:
        print(
            f"⚠️ 画像ファイルが見つかりません ({image_path})。テキストのみで解析します。"
        )

    print(f"📝 入力テキスト: {text_input}")
    print("⏳ 解析中... (これには数秒〜十数秒かかる場合があります)")

    # 実行
    result = await analyze_with_gemini(image_data, text_input, eaten_at)

    if result:
        print("\n✅ 解析成功！")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("\n❌ 解析失敗。Gemini APIのログを確認してください。")


if __name__ == "__main__":
    asyncio.run(main())
