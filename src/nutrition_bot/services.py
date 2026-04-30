import aiohttp
from google import genai
from google.genai import types
from .config import GEMINI_API_KEY, GAS_WEBHOOK_URL

# Gemini APIの設定
client = genai.Client(api_key=GEMINI_API_KEY)


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
3. 構造化出力: 解析結果を必ず以下の**単一のJSONオブジェクト**形式で出力してください。リスト形式(`[...]`)で囲わず、`{{ "meals": [...] }}` の形式にしてください。他のテキストは一切含めないでください。フィールド名は必ずこの通りにしてください。

JSON Structure:
{{
  "meals": [
    {{
      "eaten_at": "{eaten_at}",
      "menu": "料理名",
      "calories": 整数(kcal),
      "protein": 小数(g),
      "fat": 小数(g),
      "carb": 小数(g),
      "source_url": "参照したURL(あれば)"
    }}
  ]
}}

共通の時刻設定:
eaten_at = "{eaten_at}"

ユーザーテキスト入力: {text}
"""

    try:
        contents: list[str | types.Part] = [prompt]
        if image_data:
            contents.append(
                types.Part.from_bytes(
                    data=image_data,
                    mime_type="image/jpeg",
                )
            )

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=contents,  # type: ignore
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
            ),
        )

        if response.text:
            # テキストからJSON部分を抽出してパース
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            import json

            try:
                return json.loads(text)
            except Exception as json_err:
                print(f"JSON Parsing Error: {json_err}\nRaw text: {text}")
                return None

        return None

    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None
