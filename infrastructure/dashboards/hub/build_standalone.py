#!/usr/bin/env python3
"""build_standalone.py — turn the hub shell into ONE self-contained .html file
that opens correctly straight off the disk, with no web server and no Artifact.

    python3 infrastructure/dashboards/hub/build_standalone.py

Why this exists: index.html reads each tab's data with fetch("data/*.json").
Browsers refuse a fetch() from a file:// page (opaque origin), so the shell is
only correct when something is SERVING it. This script inlines those five JSON
files into the page as a literal object and rewrites grab() to read from it, so
the same shell works with no origin at all.

The two heavyweight tabs (health, maturity) stay as sibling files rather than
being inlined -- each is a standalone page of its own and together they are
~470 KB. The output is written NEXT TO them so the <iframe src="tabs/...">
relative paths still resolve, and a full-path link is added above each iframe
for the case where the browser declines to load a file:// iframe.

Run regen_hub.py first if the data should be fresh; this script only packages
whatever is on disk right now.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HUB = Path(__file__).resolve().parent
SHELL = HUB / "index.html"
OUT = HUB / "utinni_control_room_standalone.html"

# published path -> source file, matching regen_hub.py's publish set
DATA = {
    "data/art.json": HUB.parent.parent / "artpipe" / "art_status.json",
    "data/artsheets.json": HUB / "data" / "artsheets.json",
    "data/health.json": HUB / "data" / "health.json",
    "data/maturity.json": HUB / "data" / "maturity.json",
    "data/worldmap.json": HUB / "data" / "worldmap.json",
}

TABS = {
    "tabs/health.html": HUB / "tabs" / "health.html",
    "tabs/maturity.html": HUB / "tabs" / "maturity.html",
}

OLD_GRAB = 'async function grab(f){const r=await fetch(f);if(!r.ok)throw new Error(f+" → HTTP "+r.status);return r.json()}'
NEW_GRAB = (
    "async function grab(f){"
    "if(!(f in __INLINE__))throw new Error(f+\" not inlined\");"
    "return __INLINE__[f]}"
)


def win_path(p: Path) -> str:
    """Native Windows path for a /mnt/<drive>/... WSL path."""
    parts = p.as_posix()
    if parts.startswith("/mnt/") and len(parts) > 6 and parts[6] == "/":
        return parts[5].upper() + ":" + parts[6:].replace("/", "\\")
    return str(p)


def main() -> int:
    if not SHELL.is_file():
        print(f"FAIL  missing shell: {SHELL}", file=sys.stderr)
        return 1

    html = SHELL.read_text(encoding="utf-8")

    inline: dict[str, object] = {}
    missing: list[str] = []
    for pub, src in DATA.items():
        if src.is_file():
            try:
                inline[pub] = json.loads(src.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                missing.append(f"{pub} (unparseable: {e})")
        else:
            missing.append(f"{pub} (no such file: {src})")

    if OLD_GRAB not in html:
        print("FAIL  grab() in index.html no longer matches this script's "
              "expected text -- the shell changed; update build_standalone.py.",
              file=sys.stderr)
        return 1
    html = html.replace(OLD_GRAB, NEW_GRAB, 1)

    # </ inside a <script> literal would close the block early
    blob = json.dumps(inline, separators=(",", ":")).replace("</", "<\\/")
    html = html.replace(
        "<script>\nconst $=s=>document.querySelector(s);",
        "<script>\nconst __INLINE__=" + blob + ";\n"
        "const $=s=>document.querySelector(s);",
        1,
    )
    if "__INLINE__=" not in html:
        print("FAIL  could not find the script opening to inject data into.",
              file=sys.stderr)
        return 1

    # A file:// iframe may silently refuse to load; always offer the real path.
    for pub, src in TABS.items():
        needle = f'<iframe src="{pub}"'
        if needle in html:
            note = (f'<p class="note">if the panel below is blank, open it '
                    f'directly: <code>{win_path(src)}</code></p>\n  ')
            html = html.replace(needle, note + needle, 1)

    html = html.replace(
        "<title>Utinni Control Room</title>",
        "<title>Utinni Control Room (local)</title>",
        1,
    )

    OUT.write_text(html, encoding="utf-8")

    size = OUT.stat().st_size
    print(f"OK    {win_path(OUT)}  ({size:,} bytes)")
    print(f"      inlined {len(inline)} data file(s)")
    for pub in inline:
        gen = inline[pub].get("generatedAt") if isinstance(inline[pub], dict) else None
        print(f"        {pub:24} generatedAt={gen}")
    if missing:
        print(f"WARN  {len(missing)} data file(s) NOT inlined -- their tabs will "
              f"read UNMEASURED:")
        for m in missing:
            print(f"        {m}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
