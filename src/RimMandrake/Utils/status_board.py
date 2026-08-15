#!/usr/bin/env python3
"""Graphical v1 status matrix: rows x (DECIDE, BUILD, CHECK), auto-refreshing."""

import argparse
import json
import os
import time
import tkinter as tk
from tkinter import font as tkfont

DEFAULT_FILE = "/mnt/d/Luke/dev/Rimworld/infrastructure/state/status_matrix.json"
DEFAULT_INTERVAL = 3.0

COLUMNS = ("DECIDE", "BUILD", "CHECK")

STATE_BG = {
    "blocked": "#cc0000",
    "working": "#0b3d16",
    "idle":    "#0b2545",
    "offline": "#000000",
}
UNKNOWN_BG = STATE_BG["offline"]

HEADER_BG = "#1a1a1a"
LABEL_BG = "#141414"
FOOTER_BG = "#0d0d0d"
FG = "#ffffff"
GRID_BG = "#3a3a3a"      # shows through the 1px gaps between cells as gridlines
PAD = 1


def load_rows(path):
    """Return (rows, error_message). Any failure yields ([], message) - never raises."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        rows = data["rows"]
        if not isinstance(rows, list):
            raise TypeError("'rows' is not a list")
        clean = []
        for row in rows:
            name = str(row.get("name", "?"))
            cells = row.get("cells") or {}
            if not isinstance(cells, dict):
                cells = {}
            clean.append((name, cells))
        return clean, None
    except FileNotFoundError:
        return [], "no status file: %s" % path
    except Exception as exc:  # malformed JSON, wrong shape, permissions, encoding
        return [], "unreadable status file (%s): %s" % (type(exc).__name__, exc)


def cell_text_and_bg(cell):
    if not isinstance(cell, dict):
        return "-", UNKNOWN_BG
    try:
        done = int(cell.get("done", 0))
        total = int(cell.get("total", 0))
        text = "%d/%d" % (done, total)
    except (TypeError, ValueError):
        text = "-"
    bg = STATE_BG.get(str(cell.get("state", "")).lower(), UNKNOWN_BG)
    return text, bg


class Board:
    def __init__(self, root, path, interval):
        self.root = root
        self.path = path
        self.interval_ms = max(200, int(interval * 1000))
        self.signature = None  # (row names) - rebuild widgets only when the shape changes
        self.cell_labels = {}
        self.row_labels = []

        root.title("RIMWORLD STATUS")
        root.configure(bg=GRID_BG)

        # Fonts are shared objects so a resize can rescale every widget at once.
        self.cell_font = tkfont.Font(family="TkFixedFont", size=48, weight="bold")
        self.head_font = tkfont.Font(family="TkFixedFont", size=18, weight="bold")
        self.name_font = tkfont.Font(family="TkDefaultFont", size=16, weight="bold")
        self.foot_font = tkfont.Font(family="TkFixedFont", size=10)

        self.grid = tk.Frame(root, bg=GRID_BG)
        self.grid.pack(side="top", fill="both", expand=True)

        self.footer = tk.Label(root, text="", bg=FOOTER_BG, fg="#8a8a8a",
                               font=self.foot_font, anchor="w", padx=6)
        self.footer.pack(side="bottom", fill="x")

        self.message = tk.Label(self.grid, text="", bg="#000000", fg=FG,
                                font=self.name_font, wraplength=900)

        self.grid.bind("<Configure>", self.on_resize)
        self.tick()

    # ---- layout -----------------------------------------------------------

    def build(self, rows):
        for child in self.grid.winfo_children():
            if child is not self.message:
                child.destroy()
        self.cell_labels = {}
        self.row_labels = []
        self.message.place_forget()

        if not rows:
            self.message.place(relx=0.5, rely=0.5, anchor="center")
            return

        tk.Label(self.grid, text="", bg=HEADER_BG).grid(
            row=0, column=0, sticky="nsew", padx=PAD, pady=PAD)
        for c, name in enumerate(COLUMNS, start=1):
            tk.Label(self.grid, text=name, bg=HEADER_BG, fg=FG,
                     font=self.head_font).grid(row=0, column=c, sticky="nsew",
                                               padx=PAD, pady=PAD)

        for r, (name, _cells) in enumerate(rows, start=1):
            lbl = tk.Label(self.grid, text=name, bg=LABEL_BG, fg=FG,
                           font=self.name_font, anchor="w", padx=10, justify="left")
            lbl.grid(row=r, column=0, sticky="nsew", padx=PAD, pady=PAD)
            self.row_labels.append(lbl)
            for c, col in enumerate(COLUMNS, start=1):
                cell = tk.Label(self.grid, text="", fg=FG, font=self.cell_font)
                cell.grid(row=r, column=c, sticky="nsew", padx=PAD, pady=PAD)
                self.cell_labels[(r - 1, col)] = cell

        # Row-label column gets less weight so the numbers own most of the width.
        self.grid.grid_columnconfigure(0, weight=2, uniform="col")
        for c in range(1, len(COLUMNS) + 1):
            self.grid.grid_columnconfigure(c, weight=3, uniform="col")
        self.grid.grid_rowconfigure(0, weight=0, minsize=34)
        for r in range(1, len(rows) + 1):
            self.grid.grid_rowconfigure(r, weight=1, uniform="row")

    def fill(self, rows):
        for i, (_name, cells) in enumerate(rows):
            for col in COLUMNS:
                lbl = self.cell_labels.get((i, col))
                if lbl is None:
                    continue
                text, bg = cell_text_and_bg(cells.get(col))
                lbl.configure(text=text, bg=bg)

    def on_resize(self, event):
        """Scale fonts to cell size so the numbers stay readable across a room."""
        nrows = max(1, len(self.row_labels))
        cell_h = max(20, (event.height - 40) // nrows)
        cell_w = max(20, event.width // (len(COLUMNS) + 2))
        size = max(14, min(cell_h // 2, cell_w // 3))
        if size != self.cell_font.cget("size"):
            self.cell_font.configure(size=size)
            self.head_font.configure(size=max(10, size // 3))
            self.name_font.configure(size=max(9, size // 4))

    # ---- refresh ----------------------------------------------------------

    def tick(self):
        rows, err = load_rows(self.path)
        sig = tuple(name for name, _ in rows) if not err else None
        if sig != self.signature or (err and self.cell_labels):
            self.signature = sig
            self.build(rows)
        if err:
            self.message.configure(text=err)
            self.message.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.fill(rows)

        try:
            age = time.time() - os.path.getmtime(self.path)
            age_txt = "data age %.0fs" % max(0.0, age)
        except OSError:
            age_txt = "data age --"
        self.footer.configure(text="%s   |   %s   |   refresh %.1fs"
                                   % (age_txt, self.path, self.interval_ms / 1000.0))

        self.root.after(self.interval_ms, self.tick)


def main():
    ap = argparse.ArgumentParser(description="RimWorld v1 status matrix board")
    ap.add_argument("--file", default=DEFAULT_FILE, help="status_matrix.json path")
    ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL,
                    help="refresh seconds (default 3)")
    args = ap.parse_args()

    root = tk.Tk()
    root.geometry("1100x620")
    root.minsize(520, 300)
    Board(root, args.file, args.interval)
    root.mainloop()


if __name__ == "__main__":
    main()
