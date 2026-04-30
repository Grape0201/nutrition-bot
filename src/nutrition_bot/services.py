import json
import aiohttp
import google.generativeai as genai
from .config import GEMINI_API_KEY, GAS_WEBHOOK_URL
from .models import MealAnalysisResult

# Gemini APIの設定
genai.configure(api_key=GEMINI_API_KEY)


async def send_to_gas(data: dict) -> bool:
    """GASのエンドポイントにデータを送信する"""
    headers = {
        "Content-Type": "application/json",
    }

    url = GAS_WEBHOOK_URL

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status in (200, 201):
                    return True
                else:
                    text = await response.text()
                    print(f"GAS responded with error: {response.status} - {text}")
                    return False
        except Exception as e:
            print(f"Error sending data to GAS: {e}")
            return False


async def analyze_with_gemini(
    image_data: bytes | None, text: str, eaten_at: str
) -> dict | None:
    """Gemini で画像を解析し、栄養素を取得する"""

    prompt = f"""
あなたはプロの栄養士です。提供された食事の画像やテキストから、料理名と正確な栄養素（カロリー、タンパク質、脂質、炭水化物）を推測してください。
場合によっては複数の料理が含まれている可能性があるため、それぞれの料理を個別に抽出してリスト形式で返してください。

以下の手順で推論を行ってください：

1. Vision解析: 画像やテキストから各料理名と推定分量を特定する。
2. Grounding照合: Google検索を使用して、特定された料理の正確な栄養素情報を検索・照合する。
3. 構造化出力: 解析結果をJSON形式で出力してください。

共通の時刻設定:
eaten_at = "{eaten_at}"

ユーザーテキスト入力: {text}
"""

    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            tools=[{"google_search_retrieval": {}}],
        )

        contents: list[str | dict] = [prompt]
        if image_data:
            contents.append(
                {
                    "mime_type": "image/jpeg",
                    "data": image_data,
                }
            )

        response = model.generate_content(
            contents,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=MealAnalysisResult,
            ),
        )

        result_json = json.loads(response.text.strip())
        return result_json

    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None
