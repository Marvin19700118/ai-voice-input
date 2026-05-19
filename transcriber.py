import numpy as np
from faster_whisper import WhisperModel

from config import config


class Transcriber:
    _model: WhisperModel | None = None

    def _get_model(self) -> WhisperModel:
        if self._model is None:
            print(f"[Whisper] 載入模型 {config.whisper_model}（首次需下載，請稍候）...")
            self._model = WhisperModel(
                config.whisper_model,
                device=config.whisper_device,
                compute_type="auto",
            )
            print("[Whisper] 模型載入完成")
        return self._model

    def transcribe(self, audio: np.ndarray) -> str:
        model = self._get_model()
        language = config.whisper_language or None

        segments, _ = model.transcribe(
            audio,
            language=language,
            beam_size=5,
            vad_filter=True,          # 自動過濾靜音
            vad_parameters={"min_silence_duration_ms": 300},
        )

        return "".join(seg.text for seg in segments).strip()
