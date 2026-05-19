"""
螢幕底部中央的浮動狀態提示視窗。
所有公開方法均可從任意執行緒安全呼叫（內部透過 root.after 排程到 tkinter 主執行緒）。
"""

import tkinter as tk


class RecordingOverlay:
    _STATES: dict[str, tuple[str, str]] = {
        "recording":  ("🎙  錄音中",  "#ff5555"),
        "processing": ("⏳  辨識中",  "#5599ff"),
        "polishing":  ("✨  潤飾中",  "#55cc88"),
    }

    def __init__(self, root: tk.Tk):
        self._root = root
        self._win: tk.Toplevel | None = None
        self._label: tk.Label | None = None
        self._after_id: str | None = None
        self._dot = 0

    # ── 公開 API（執行緒安全）──────────────────────────────

    def show(self, state: str):
        self._root.after(0, self._do_show, state)

    def hide(self):
        self._root.after(0, self._do_hide)

    def destroy(self):
        self._root.after(0, self._do_destroy)

    # ── 內部（僅在 tkinter 主執行緒執行）──────────────────

    def _ensure_window(self):
        if self._win is not None:
            return
        self._win = tk.Toplevel(self._root)
        self._win.overrideredirect(True)        # 無標題列/邊框
        self._win.attributes("-topmost", True)  # 永遠最前
        self._win.attributes("-alpha", 0.90)
        self._win.configure(bg="#1e1e1e")

        self._label = tk.Label(
            self._win,
            text="",
            fg="white",
            bg="#1e1e1e",
            font=("Microsoft JhengHei UI", 13, "bold"),
            padx=22,
            pady=11,
        )
        self._label.pack()
        self._win.withdraw()

    def _reposition(self):
        self._win.update_idletasks()
        w = self._win.winfo_reqwidth()
        h = self._win.winfo_reqheight()
        sw = self._win.winfo_screenwidth()
        sh = self._win.winfo_screenheight()
        x = (sw - w) // 2
        y = sh - h - 64     # 工具列上方留空
        self._win.geometry(f"{w}x{h}+{x}+{y}")

    def _do_show(self, state: str):
        self._cancel_anim()
        self._ensure_window()
        text, color = self._STATES.get(state, ("…", "white"))
        self._label.config(text=text, fg=color)
        self._reposition()
        self._win.deiconify()
        self._win.lift()
        if state == "recording":
            self._tick_anim()

    def _do_hide(self):
        self._cancel_anim()
        if self._win:
            self._win.withdraw()

    def _do_destroy(self):
        self._cancel_anim()
        if self._win:
            self._win.destroy()
            self._win = None

    # ── 動態點點動畫（錄音中）─────────────────────────────

    def _tick_anim(self):
        if self._win and self._win.winfo_viewable():
            dots = "." * (self._dot % 4)
            self._label.config(text=f"🎙  錄音中{dots}")
            self._dot += 1
            self._after_id = self._root.after(350, self._tick_anim)

    def _cancel_anim(self):
        if self._after_id:
            self._root.after_cancel(self._after_id)
            self._after_id = None
        self._dot = 0
