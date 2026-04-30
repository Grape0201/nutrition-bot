import io
from datetime import datetime
from PIL import Image, ExifTags
from .config import JST


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
