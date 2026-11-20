#!/usr/bin/env python3
"""fleet_now.py: FLEET_NOW.html, the browser-tab form of RELENTLESS_NOW.md (the page running_now.py writes each minute).

Wraps that file's body (it is already HTML) in a page with a 60 s self-reload and a visible build time. When the
source is missing or older than 600 s the page says COULD NOT READ, shows no old body, and the run exits 3.
Promises: design/specs/2026-11-19-standing-status-tabs/boundary.md.  Run by rm-fleet-now.timer, every minute.
    python3 src/RimMandrake/Utils/fleet_now.py
"""
import glob
import html
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rmpaths  # noqa: E402

MAX_AGE_S = 600   # ten missed one-minute runs of running_now.py (boundary page, LIMITS)
RELOAD_S = 60     # the source's own cadence
SRC_NAME, OUT_NAME = "RELENTLESS_NOW.md", "FLEET_NOW.html"
# The owner reads RELENTLESS_NOW.md in Typora (profile.data: dark mode, darkTheme blue-topaz-dark.css, measured
# 2026-11-19), so this page carries that theme's CSS. Without it: the panel colours of the page body itself.
FALLBACK_BG, FALLBACK_TEXT, DIM = "#14171c", "#e8eaee", "#98a1af"
THEME_GLOB = "/mnt/c/Users/*/AppData/Roaming/Typora/themes"


def themes_dir():
    d = os.environ.get("TYPORA_THEMES_DIR")
    if d:
        return d
    found = sorted(glob.glob(THEME_GLOB))
    return found[0] if found else None


def theme_css():
    """-> (css, name) of the Typora dark theme with its @import resolved, or (None, why)."""
    d = themes_dir()
    if not d:
        return None, "no Typora themes folder"
    name = "blue-topaz-dark.css"
    try:
        prof = os.path.join(os.path.dirname(d), "profile.data")
        if os.path.isfile(prof):
            cfg = json.loads(bytes.fromhex(open(prof, "rb").read().decode().strip()).decode("utf-8"))
            name = cfg.get("darkTheme") or name
    except (OSError, ValueError):
        pass  # keep the measured default
    try:
        css = open(os.path.join(d, name), encoding="utf-8").read()
        for imp in re.findall(r'@import\s+(?:url\()?["\']?([^"\')]+)["\']?\)?\s*;', css):
            sub = open(os.path.join(d, imp), encoding="utf-8").read()
            css = re.sub(r'@import\s+(?:url\()?["\']?' + re.escape(imp) + r'["\']?\)?\s*;', lambda m: sub, css, count=1)
        return css, name
    except OSError as e:
        return None, "theme not found (%s)" % (e.strerror or e)


def render_md(text):
    try:
        from markdown_it import MarkdownIt
        return MarkdownIt("commonmark", {"html": True}).enable("table").render(text)
    except ImportError:  # no renderer: fences as preformatted text, the rest as written
        parts = re.split(r"^```[^\n]*\n(.*?)^```[ \t]*$", text, flags=re.S | re.M)
        return "".join(p if i % 2 == 0 else "<pre><code>%s</code></pre>" % html.escape(p) for i, p in enumerate(parts))


def page(built, body, problem=None):
    css, why = theme_css()
    if css is None:
        css = ("body{background:%s;color:%s;font-family:Segoe UI,Helvetica,Arial,sans-serif;margin:16px}"
               "pre{background:#0e1014;padding:8px;overflow:auto}" % (FALLBACK_BG, FALLBACK_TEXT))
        look = "Typora theme not found (%s): page colours used." % why
    else:
        look = "Look: Typora theme %s." % why
    head = ('<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="%d">'
            '<title>FLEET_NOW</title><style>%s</style></head><body class="typora-export"><div id="write">'
            % (RELOAD_S, css))
    line = ('<div id="built" style="font-size:12px;color:%s">Built %s by fleet_now.py from RELENTLESS_NOW.md. %s '
            'This tab reloads every minute; a build time older than that means the writer stopped.</div>'
            % (DIM, built, html.escape(look)))
    if problem:
        body = ('<div style="background:#5c1f1a;color:#ffd9d2;padding:12px 16px;border-radius:6px;margin-top:10px;'
                'font-weight:600">COULD NOT READ the fleet page: %s</div>' % html.escape(problem))
    else:
        body = render_md(body)
    return head + line + body + "\n</div></body></html>\n"


def build(src, out, now=None):
    now = time.time() if now is None else now
    built = time.strftime("%I:%M:%S %p %Z", time.localtime(now)).lstrip("0")
    problem, body = None, ""
    try:
        age = now - os.stat(src).st_mtime
        if age > MAX_AGE_S:
            problem = "%s is %d min old (limit %d min)" % (SRC_NAME, age // 60, MAX_AGE_S // 60)
        else:
            with open(src, encoding="utf-8") as f:
                body = f.read()
    except OSError as e:
        problem = "%s: %s" % (SRC_NAME, e.strerror or e)
    text = page(built, body, problem)
    with open(out + ".tmp", "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(out + ".tmp", out)
    return problem


def main():
    src, out = str(rmpaths.rm_path("conductor", SRC_NAME)), str(rmpaths.rm_path("conductor", OUT_NAME))
    problem = build(src, out)
    if problem:
        print("FLEET_NOW.html: COULD NOT READ (%s)" % problem)
        return 3
    print("FLEET_NOW.html written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
