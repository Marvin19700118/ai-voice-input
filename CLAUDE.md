# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案簡介

Windows 桌面 AI 語音輸入工具，類似 Typeless。按住熱鍵錄音，放開後用 Whisper 辨識文字，再透過 Claude API 潤飾，最後自動貼到游標位置。

## 環境設定

```bash
# 安裝依賴
pip install -r requirements.txt

# 複製並填寫設定
copy .env.example .env
```

`.env` 必填項目：`ANTHROPIC_API_KEY`（AI 潤飾用，可留空則跳過潤飾）

## 啟動

```bash
python main.py
```

首次執行會自動下載 Whisper 模型（`base` 約 150MB）。

## 使用方式

- 按住 **F4**（可在 `.env` 的 `HOTKEY` 更改）錄音
- 放開後自動辨識並貼到當前游標位置
- 系統匣圖示顏色：綠色=待機、紅色=錄音中、藍色=處理中
- 右鍵系統匣可切換「AI 潤飾」開關

## 架構

```
main.py          # 入口：系統匣 UI、熱鍵事件、串接各模組
config.py        # 從 .env 讀取設定，提供全域 config 物件
recorder.py      # sounddevice 錄音，stop() 回傳 numpy float32 陣列
transcriber.py   # faster-whisper 延遲載入模型，transcribe() 回傳字串
polisher.py      # Claude API (claude-haiku-4-5) 潤飾文字
```

**資料流**：`hotkey press → recorder.start()` → `hotkey release → recorder.stop() → transcriber.transcribe() → polisher.polish() → pyperclip + pyautogui paste`

## 關鍵設定（.env）

| 變數 | 預設 | 說明 |
|------|------|------|
| `WHISPER_MODEL` | `base` | `tiny/base/small/medium/large-v3` |
| `WHISPER_DEVICE` | `auto` | `auto/cpu/cuda` |
| `WHISPER_LANGUAGE` | 空（自動） | `zh/en/ja` 等 |
| `HOTKEY` | `f4` | 任何 keyboard 套件支援的按鍵 |
| `USE_POLISH` | `true` | 設為 `false` 停用 AI 潤飾 |
