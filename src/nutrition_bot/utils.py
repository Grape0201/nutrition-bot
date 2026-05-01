import io
import os
import json
import time
import glob
import uuid
from datetime import datetime
from PIL import Image, ExifTags
from .config import JST, DATA_DIR


def get_exif_datetime(image_bytes: bytes) -> datetime | None:
    """画像のEXIFから撮影日時を取得する"""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        exif = image.getexif()
        if not exif:
            return None

        # DateTimeOriginal (タグID 36867) を探す
        for tag_id, value in exif.items():
            tag_name = ExifTags.TAGS.get(tag_id, tag_id)
            if tag_name == "DateTimeOriginal":
                # フォーマット: YYYY:MM:DD HH:MM:SS
                dt = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                # JSTとして扱う
                return dt.replace(tzinfo=JST)
    except Exception as e:
        print(f"Failed to extract EXIF: {e}")
    return None


def save_meal_to_json(result_json: dict):
    """解析結果を個別のJSONファイルとして保存する"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # UUIDを使用してユニークなファイル名を作成
    unique_id = uuid.uuid4().hex
    filename = f"meal_{int(time.time())}_{unique_id}.json"
    filepath = os.path.join(DATA_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result_json, f, ensure_ascii=False, indent=2)


def get_today_meals() -> list:
    """今日の食事データを取得する"""
    today_str = datetime.now(JST).strftime("%Y-%m-%d")
    today_meals = []

    if not os.path.exists(DATA_DIR):
        return []

    # data フォルダ内の全JSONファイルを読み込む
    files = glob.glob(os.path.join(DATA_DIR, "meal_*.json"))
    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "meals" in data:
                    for meal in data["meals"]:
                        # eaten_at の日付が今日かどうか判定
                        if meal.get("eaten_at", "").startswith(today_str):
                            today_meals.append(meal)
        except Exception as e:
            print(f"Failed to read {file}: {e}")

    return today_meals
