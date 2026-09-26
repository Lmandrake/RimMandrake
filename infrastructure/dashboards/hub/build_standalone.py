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
~700 KB. Their <iframe src="tabs/..."> paths are PUBLISHED paths, not disk
paths: `tabs/maturity.html` has no file behind it at all, it is published from
Transient/project_maturity_dashboard.html. So this script resolves every tab
through publish_ready.json (regen_hub.py's own output, the single source of
truth for that mapping) and copies each one into tabs/ so the relative path
resolves off the disk too. A full-path link is added above each iframe for the
case where the browser declines to load a file:// iframe at all.

Run regen_hub.py first -- this script packages whatever is on disk right now,
and it needs that script's publish_ready.json to exist.
"""
from __future__ import annotations

import json
import shutil
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

READY = HUB / "data" / "publish_ready.json"

# Published paths the shell embeds in an <iframe>. Their real sources are
# resolved from publish_ready.json, never assumed to live under tabs/.
TAB_PATHS = ("tabs/health.html", "tabs/maturity.html")


def resolve_tabs() -> tuple[dict[str, Path], list[str]]:
    """published path -> the file on disk it is published FROM."""
    if not READY.is_file():
        return {}, [f"{READY} missing -- run regen_hub.py first"]
    try:
        entries = json.loads(READY.read_text(encoding="utf-8")).get("files", [])
    except json.JSONDecodeError as e:
        return {}, [f"{READY} unparseable: {e}"]

    by_published = {e.get("published"): e.get("source") for e in entries}
    found: dict[str, Path] = {}
    problems: list[str] = []
    for pub in TAB_PATHS:
        src = by_published.get(pub)
        if not src:
            problems.append(f"{pub} not in publish_ready.json")
            continue
        p = Path(src)
        if not p.is_file():
            problems.append(f"{pub} -> {p} (no such file)")
            continue
        found[pub] = p
    return found, problems

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

    # The iframe srcs are PUBLISHED paths; put a real file behind each one so
    # the same relative path resolves from the disk. A file:// iframe may still
    # refuse to load, so always print the openable path above it too.
    tabs, tab_problems = resolve_tabs()
    missing.extend(tab_problems)
    for pub, src in tabs.items():
        dest = HUB / pub
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.resolve() != dest.resolve():
            shutil.copyfile(src, dest)
        needle = f'<iframe src="{pub}"'
        if needle in html:
            note = (f'<p class="note">if the panel below is blank, open it '
                    f'directly: <code>{win_path(dest)}</code></p>\n  ')
            html = html.replace(needle, note + needle, 1)
        else:
            missing.append(f"{pub} has no <iframe> in the shell any more")

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
    print(f"      staged {len(tabs)} embedded tab(s)")
    for pub, src in tabs.items():
        print(f"        {pub:24} <- {win_path(src)}")
    if missing:
        print(f"WARN  {len(missing)} item(s) NOT packaged -- those tabs will be "
              f"blank or read UNMEASURED:")
        for m in missing:
            print(f"        {m}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
