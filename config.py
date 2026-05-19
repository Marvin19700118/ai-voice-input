import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    gemini_api_key: str = ""
    whisper_model: str = "base"
    whisper_device: str = "auto"
    whisper_language: str = ""
    hotkey: str = "f4"
    use_polish: bool = True
    sample_rate: int = 16000

    def __post_init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.whisper_model = os.getenv("WHISPER_MODEL", "base")
        self.whisper_device = os.getenv("WHISPER_DEVICE", "auto")
        self.whisper_language = os.getenv("WHISPER_LANGUAGE", "")
        self.hotkey = os.getenv("HOTKEY", "f4")
        self.use_polish = os.getenv("USE_POLISH", "true").lower() == "true"

    @property
    def polish_enabled(self) -> bool:
        return self.use_polish and bool(self.gemini_api_key)


config = Config()
