import asyncio
import json
from datetime import datetime
from nutrition_bot.services import send_to_gas
from nutrition_bot.config import JST

async def main():
    print("🚀 GASへの書き込みテストを開始します...")
    
    # テストデータの作成
    test_data = {
        "meals": [
            {
                "eaten_at": datetime.now(JST).isoformat(),
                "menu": "テスト用ステーキ（自動テスト）",
                "calories": 500,
                "protein": 40.5,
                "fat": 35.2,
                "carb": 5.0,
                "source_url": "https://example.com/steak"
            },
            {
                "eaten_at": datetime.now(JST).isoformat(),
                "menu": "テスト用サラダ（自動テスト）",
                "calories": 100,
                "protein": 2.0,
                "fat": 0.5,
                "carb": 15.0,
                "source_url": None
            }
        ]
    }
    
    print(f"送信データ:\n{json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    # 実行
    success = await send_to_gas(test_data)
    
    if success:
        print("\n✅ 成功！スプレッドシートを確認してください。")
    else:
        print("\n❌ 失敗。ログや設定（GAS_WEBHOOK_URLなど）を確認してください。")

if __name__ == "__main__":
    asyncio.run(main())
