import anthropic

from config import config

_SYSTEM_PROMPT = """你是一個語音辨識後處理助手。
使用者提供的是語音轉錄的原始文字，可能含有口語詞、斷句錯誤或錯別字。
請直接輸出修正後的文字，不加任何說明或前綴。
修正原則：修正錯別字、加上適當標點、讓語句通順，但保持原意與語氣。"""


class TextPolisher:
    def __init__(self):
        self._client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    def polish(self, text: str) -> str:
        message = self._client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": text}],
        )
        return message.content[0].text.strip()
