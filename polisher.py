from google import genai
from google.genai import types

from config import config

_SYSTEM_PROMPT = """你是一個語音辨識後處理助手。
使用者提供的是語音轉錄的原始文字，可能含有口語詞、斷句錯誤或錯別字。
請直接輸出修正後的文字，不加任何說明或前綴。
修正原則：修正錯別字、加上適當標點、讓語句通順，但保持原意與語氣。"""


class TextPolisher:
    def __init__(self):
        self._client = genai.Client(api_key=config.gemini_api_key)

    def polish(self, text: str) -> str:
        try:
            response = self._client.models.generate_content(
                model="gemini-2.5-flash",
                contents=text,
                config=types.GenerateContentConfig(
                    system_instruction=_SYSTEM_PROMPT,
                ),
            )
            return response.text.strip()
        except Exception as e:
            print(f"[潤飾跳過] {e.__class__.__name__}: {e}")
            return text  # 失敗時回傳原始文字
