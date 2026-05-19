"""
AI 語音輸入工具
按住熱鍵（預設 F4）錄音，放開後自動辨識並貼到游標位置。
"""

import sys
import threading
import time
import tkinter as tk

import keyboard
import pyperclip
import pyautogui
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

from config import config
from recorder import AudioRecorder
from transcriber import Transcriber
from polisher import TextPolisher
from overlay import RecordingOverlay


class VoiceInputApp:
    STATUS_IDLE = "idle"
    STATUS_RECORDING = "recording"
    STATUS_PROCESSING = "processing"

    _STATUS_COLOR = {
        STATUS_IDLE:       (80, 180, 80),    # 綠色：待機
        STATUS_RECORDING:  (220, 60, 60),    # 紅色：錄音中
        STATUS_PROCESSING: (60, 130, 220),   # 藍色：處理中
    }

    def __init__(self):
        self.recorder  = AudioRecorder(sample_rate=config.sample_rate)
        self.transcriber = Transcriber()
        self.polisher  = TextPolisher() if config.polish_enabled else None

        self._status      = self.STATUS_IDLE
        self._status_lock = threading.Lock()
        self._icon: Icon | None = None

        # tkinter 主迴圈（用於 overlay）
        self._tk_root: tk.Tk | None = None
        self._overlay: RecordingOverlay | None = None

    # ── 狀態管理 ────────────────────────────────────────────────

    @property
    def status(self) -> str:
        with self._status_lock:
            return self._status

    @status.setter
    def status(self, value: str):
        with self._status_lock:
            self._status = value
        self._refresh_icon(value)
        self._update_overlay(value)
        print(f"[狀態] {value}")

    def _update_overlay(self, value: str):
        if self._overlay is None:
            return
        if value == self.STATUS_RECORDING:
            self._overlay.show("recording")
        elif value == self.STATUS_PROCESSING:
            self._overlay.show("processing")
        elif value == self.STATUS_IDLE:
            self._overlay.hide()

    # ── 錄音流程 ────────────────────────────────────────────────

    def on_hotkey_press(self):
        if self.status != self.STATUS_IDLE:
            return
        self.status = self.STATUS_RECORDING
        self.recorder.start()

    def on_hotkey_release(self):
        if self.status != self.STATUS_RECORDING:
            return
        audio = self.recorder.stop()
        self.status = self.STATUS_PROCESSING

        if audio is None:
            print("[提示] 錄音太短，已忽略")
            self.status = self.STATUS_IDLE
            return

        threading.Thread(target=self._process, args=(audio,), daemon=True).start()

    def _process(self, audio):
        try:
            print("[Whisper] 辨識中...")
            text = self.transcriber.transcribe(audio)

            if not text:
                print("[提示] 未辨識到文字")
                return

            print(f"[辨識結果] {text}")

            if self.polisher:
                # 切換 overlay 為「潤飾中」
                if self._overlay:
                    self._overlay.show("polishing")
                print("[Gemini] 潤飾中...")
                text = self.polisher.polish(text)
                print(f"[潤飾結果] {text}")

            self._paste(text)

        except Exception as e:
            print(f"[錯誤] {e}")
        finally:
            self.status = self.STATUS_IDLE

    def _paste(self, text: str):
        pyperclip.copy(text)
        time.sleep(0.05)
        pyautogui.hotkey("ctrl", "v")

    # ── 系統匣 UI ───────────────────────────────────────────────

    def _make_icon_image(self, status: str) -> Image.Image:
        img  = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        color = self._STATUS_COLOR.get(status, (128, 128, 128))
        draw.ellipse([8, 8, 56, 56], fill=color)
        draw.rectangle([26, 18, 38, 38], fill=(255, 255, 255))
        draw.arc([22, 32, 42, 48], start=0, end=180, fill=(255, 255, 255), width=3)
        draw.line([32, 48, 32, 54], fill=(255, 255, 255), width=3)
        return img

    def _refresh_icon(self, status: str):
        if self._icon is not None:
            self._icon.icon = self._make_icon_image(status)

    def _toggle_polish(self, icon, item):
        if not config.gemini_api_key:
            print("[提示] 未設定 GEMINI_API_KEY，無法啟用潤飾")
            return
        config.use_polish = not config.use_polish
        self.polisher = TextPolisher() if config.polish_enabled else None
        state = "開啟" if config.polish_enabled else "關閉"
        print(f"[設定] AI 潤飾已{state}")

    def _build_menu(self) -> Menu:
        hotkey_label = f"熱鍵：{config.hotkey.upper()}（按住錄音）"
        return Menu(
            MenuItem(hotkey_label, None, enabled=False),
            MenuItem(
                "AI 潤飾",
                self._toggle_polish,
                checked=lambda item: config.polish_enabled,
            ),
            Menu.SEPARATOR,
            MenuItem("退出", self._quit),
        )

    def _quit(self, icon=None, item=None):
        print("[退出] 關閉中...")
        keyboard.unhook_all()
        if self._icon:
            self._icon.stop()
        if self._overlay:
            self._overlay.destroy()
        if self._tk_root:
            self._tk_root.after(0, self._tk_root.quit)

    # ── 啟動 ────────────────────────────────────────────────────

    def run(self):
        keyboard.on_press_key(config.hotkey, lambda _: self.on_hotkey_press())
        keyboard.on_release_key(config.hotkey, lambda _: self.on_hotkey_release())

        polish_status = "開啟" if config.polish_enabled else "關閉（未設定 API 金鑰）"
        print(f"[啟動] AI 語音輸入工具")
        print(f"  熱鍵：{config.hotkey.upper()}")
        print(f"  Whisper 模型：{config.whisper_model}")
        print(f"  AI 潤飾：{polish_status}")
        print("按住熱鍵開始錄音，放開後自動辨識並貼上。")

        # 初始化 tkinter（overlay 用）
        self._tk_root = tk.Tk()
        self._tk_root.withdraw()   # 隱藏主視窗
        self._overlay = RecordingOverlay(self._tk_root)

        # 系統匣圖示在背景執行緒跑
        self._icon = Icon(
            name="VoiceInput",
            icon=self._make_icon_image(self.STATUS_IDLE),
            title="AI 語音輸入",
            menu=self._build_menu(),
        )
        self._icon.run_detached()

        # tkinter mainloop 作為主執行緒事件迴圈
        try:
            self._tk_root.mainloop()
        except KeyboardInterrupt:
            self._quit()


if __name__ == "__main__":
    app = VoiceInputApp()
    app.run()
