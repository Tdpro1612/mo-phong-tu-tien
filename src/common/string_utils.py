import re
import unicodedata


def clean_column_name(text):
    """Chuẩn hóa tên cột từ Tiếng Việt về snake_case."""
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r"\(.*?\)", "", text)
    text = unicodedata.normalize("NFD", text)
    text = re.sub(r"[\u0300-\u036f]", "", text)
    text = text.replace("đ", "d")
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^\w]", "", text)
    return text.strip("_")


def remove_accents_and_spaces(text):
    """Chuẩn hóa tên file thành tên bảng."""
    if not text:
        return ""
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = re.sub(r"[\u0300-\u036f]", "", text)
    text = text.replace("đ", "d")
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^\w]", "", text)
    return text
