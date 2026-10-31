#!/usr/bin/env python3
"""A review sheet opened without its live writer refuses picks and names the URL that has one.

Owner, 2026-10-31: "You aren't supposed to do this with pages anymore, you're supposed to have the pages auto-write as I
go." The auto-write is the sidecar: serve_gated.py injects `window.__SIDECAR__` and every click POSTs to the decisions file.
A page opened any other way (a copy on D:, a file:// link) used to fall back silently to browser storage, so he worked a
whole sheet and then had to export it by hand. That fallback is now a full-page block with no dismiss button.

The sidecar decides, not the file's location: the check reads what the page was actually served with, so no copy of a sheet
can pass it. A sibling `<sheet>.live.js` written by serve_gated.py carries the current URL; a copy without it still blocks
and says how to get one served.

    inject(html)        put the guard in a page (idempotent), the builders call this
    has_guard(html)     req 16 of scaled_review_gate.py
    write_live(s, url)  serve_gated.py, while the server runs
    clear_live(s)       serve_gated.py, when it stops
"""
from __future__ import annotations

import json
import re
from pathlib import Path

MARK = "sheet-live-guard"
GUARD = """<script id="%s">
(function () {
  if (window.__SIDECAR__) return;
  var stop = function (e) { e.stopImmediatePropagation(); e.preventDefault(); };
  ['keydown', 'keypress', 'keyup', 'click', 'mousedown', 'pointerdown', 'submit', 'change', 'input'].forEach(function (t) {
    window.addEventListener(t, function (e) {
      if (!(e.target && e.target.closest && e.target.closest('#live-guard-box a'))) stop(e);
    }, true);
  });
  document.body.inert = true;
  var box = document.createElement('div');
  box.id = 'live-guard-box';
  box.setAttribute('role', 'alertdialog');
  box.style.cssText = 'position:fixed;inset:0;z-index:2147483647;display:flex;align-items:center;justify-content:center;' +
    'background:rgba(20,20,24,.94);color:#fff;font:18px/1.5 system-ui,sans-serif;text-align:center;padding:40px';
  var say = function (nodes) {
    box.textContent = '';
    var w = document.createElement('div');
    w.style.maxWidth = '720px';
    var h = document.createElement('h1');
    h.textContent = 'This copy cannot save your picks';
    h.style.fontSize = '28px';
    w.appendChild(h);
    nodes.forEach(function (n) { w.appendChild(n); });
    box.appendChild(w);
  };
  var p = function (t) { var e = document.createElement('p'); e.textContent = t; return e; };
  var none = function () {
    say([p('It is not connected to its writer, so nothing you click would reach the decisions file.'),
         p('Open this sheet from RimPulse, or ask the agent to serve it. The served page writes every click as you go.')]);
  };
  document.documentElement.appendChild(box);
  none();
  var stem = decodeURIComponent(location.pathname.split('/').pop() || '').replace(/\\.html?$/i, '');
  if (!stem) return;
  var s = document.createElement('script');
  s.src = encodeURIComponent(stem) + '.live.js';
  s.onload = function () {
    var url = window.__LIVE_SHEET__ && window.__LIVE_SHEET__.url;
    if (!/^http:\\/\\/localhost:\\d+\\//.test(url || '')) return;
    var a = document.createElement('a');
    a.href = url;
    a.textContent = url;
    a.style.cssText = 'color:#8fd3ff;font-size:22px;word-break:break-all';
    say([p('It is not connected to its writer. The live page, which writes every click as you go, is here:'), a]);
  };
  document.documentElement.appendChild(s);
})();
</script>
""" % MARK


OLD_GUARD = re.compile(r'<script id="%s">.*?</script>\n?' % MARK, re.S)


def has_guard(html: str) -> bool:
    """The whole script, not its marker: an empty block with the right id guards nothing."""
    return GUARD in html


def inject(html: str) -> str:
    """Last in the body, so the page's own listeners exist and the sidecar (in <head>) has already run."""
    html = OLD_GUARD.sub("", html)
    at = html.rfind("</body>")
    return html + GUARD if at < 0 else html[:at] + GUARD + html[at:]


def live_path(sheet) -> Path:
    p = Path(sheet)
    return p.with_name(p.stem + ".live.js")


def write_live(sheet, url: str) -> Path:
    out = live_path(sheet)
    out.write_text("window.__LIVE_SHEET__ = " + json.dumps({"url": url}) + ";\n")
    return out


def clear_live(sheet) -> None:
    live_path(sheet).unlink(missing_ok=True)
