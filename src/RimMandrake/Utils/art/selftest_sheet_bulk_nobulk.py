#!/usr/bin/env python3
"""selftest_sheet_bulk_nobulk.py — the review-sheet template's bulk apply obeys bulk:false and itemOptions.

SHEET_BULK_ENFORCE_NOBULK_FLAG: shift+digit (and the group's "all X" button) called bulkGroup, which
set the option on EVERY shown row of the group, ignoring an option's `bulk:false` and a row's own
`window.itemOptions(it)` list. On an art sheet one keypress set the same letter on many creatures.

This runs the template's own page script (MandrakeWorkflows skills/review-sheets/assets/
sheet_template.html, reached through ~/.claude/skills/review-sheets) in node over a catch-all DOM
stub, then drives the real keydown handler and the real click handler. No browser, no Windows.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

TEMPLATE = Path.home() / ".claude" / "skills" / "review-sheets" / "assets" / "sheet_template.html"

# A DOM that answers everything: any property is another stub, any call returns a stub. Only the
# two JSON islands, the keydown/click listeners and the timers are real.
STUB = r"""
const __listeners = {};
const mk = (name) => {
  const f = function () { return mk(name + '()'); };
  return new Proxy(f, {
    get(t, p) {
      if (p === Symbol.toPrimitive) return () => '';
      if (p === Symbol.iterator) return function* () {};
      if (p === 'then') return undefined;
      if (p === 'length') return 0;
      if (p === 'textContent' || p === 'value' || p === 'innerHTML' || p === 'tagName') return '';
      if (p === 'offsetHeight' || p === 'scrollY' || p === 'innerHeight') return 0;
      if (p === 'addEventListener') return (ev, fn) => { (__listeners[name + ':' + ev] ||= []).push(fn); };
      if (p === 'querySelectorAll') return () => [];
      if (p === 'querySelector') return () => null;
      if (p === 'closest') return () => null;
      if (p in t) return t[p];
      return mk(name + '.' + String(p));
    },
    set(t, p, v) { t[p] = v; return true; },
    apply() { return mk(name + '()'); },
  });
};
const __islands = { CONFIG: JSON.stringify(__CFG), ITEMS: JSON.stringify(__ITEMS) };
globalThis.document = new Proxy({}, { get(t, p) {
  if (p === 'getElementById') return id => (id in __islands) ? { textContent: __islands[id] } : mk('#' + id);
  if (p === 'querySelectorAll') return () => [];
  if (p === 'querySelector') return sel => mk('document.querySelector(' + sel + ')');
  if (p === 'activeElement') return { tagName: 'BODY', classList: { contains: () => false }, blur() {} };
  if (p === 'addEventListener') return (ev, fn) => { (__listeners['document:' + ev] ||= []).push(fn); };
  return mk('document.' + String(p));
} });
globalThis.window = globalThis;
globalThis.addEventListener = (ev, fn) => { (__listeners['window:' + ev] ||= []).push(fn); };
globalThis.localStorage = { getItem: () => null, setItem() {}, removeItem() {} };
globalThis.location = { search: '', hash: '', protocol: 'file:', href: 'file:///x.html', origin: 'null' };
globalThis.history = { replaceState() {} };
globalThis.requestAnimationFrame = fn => 0;
globalThis.matchMedia = () => ({ matches: false, addEventListener() {} });
globalThis.getComputedStyle = () => mk('style');
globalThis.IntersectionObserver = class { observe() {} disconnect() {} };
globalThis.ResizeObserver = class { observe() {} disconnect() {} };
globalThis.CSS = { escape: s => String(s) };
globalThis.fetch = () => new Promise(() => {});
globalThis.alert = () => {};
globalThis.confirm = () => true;
globalThis.navigator = { clipboard: { writeText: () => Promise.resolve() }, userAgent: 'node' };
const __realSetTimeout = setTimeout;
globalThis.setTimeout = () => 0; globalThis.clearTimeout = () => {};
globalThis.setInterval = () => 0; globalThis.clearInterval = () => {};
"""

ITEMS = [
    {"id": "r1", "label": "row one", "group": "G"},
    {"id": "r2", "label": "row two", "group": "G"},
]
OPTS_NOBULK = [
    {"key": "A", "label": "A", "hotkey": "1", "color": "#0a0", "bulk": False},
    {"key": "B", "label": "B", "hotkey": "2", "color": "#a00", "bulk": False},
]
OPTS_BULK = [
    {"key": "A", "label": "A", "hotkey": "1", "color": "#0a0"},
    {"key": "B", "label": "B", "hotkey": "2", "color": "#a00"},
]

DRIVE = r"""
const kd = (__listeners['window:keydown'] || [])[0];
const click = (__listeners['#list:click'] || [])[0];
if (!kd) throw new Error('no keydown listener found');
shown = ITEMS.slice(); focusIdx = 0;
const out = {};
if (__MODE === 'key') {
  kd({ key: '!', shiftKey: true, ctrlKey: false, metaKey: false, altKey: false, target: {}, preventDefault() {} });
} else {
  if (!click) throw new Error('no #list click listener found');
  const tgt = { closest: sel => sel === '[data-bulk]' ? { dataset: { group: 'G', bulk: 'A' } } : null, dataset: {} };
  click({ target: tgt, preventDefault() {} });
}
for (const it of ITEMS) out[it.id] = DEC[it.id] ? DEC[it.id].decision : null;
console.log(JSON.stringify(out));
"""


def page_script() -> str:
    html = TEMPLATE.read_text()
    blocks = re.findall(r"<script>(.*?)</script>", html, re.S)
    if not blocks:
        raise RuntimeError("no bare <script> block in template")
    return max(blocks, key=len)


def run(opts, mode, item_options=None):
    node = shutil.which("node") or str(Path.home() / ".local/bin/node")
    if not Path(node).exists():
        print("UNMEASURED: node not found")
        sys.exit(3)
    cfg = {"sheetId": "selftest_bulk", "title": "t", "options": opts}
    pre = ("const __CFG = %s; const __ITEMS = %s; const __MODE = %s;\n"
           % (json.dumps(cfg), json.dumps(ITEMS), json.dumps(mode))) + STUB
    if item_options is not None:
        pre += ("window.itemOptions = it => { const keys = %s[it.id]; return keys ? __CFG.options.filter(o => keys.includes(o.key)) : null; };\n"
                % json.dumps(item_options))
    prog = pre + page_script() + "\n;(() => {\n" + DRIVE + "\n})();"
    r = subprocess.run([node, "-e", prog], capture_output=True, text=True, timeout=60)
    if r.returncode:
        raise RuntimeError("node failed: " + (r.stderr or r.stdout)[-1200:])
    return json.loads([l for l in r.stdout.splitlines() if l.strip()][-1])


def main() -> int:
    if not TEMPLATE.exists():
        print("UNMEASURED: template not reachable at %s" % TEMPLATE)
        return 3
    fails = []
    checks = [
        ("shift+1 with bulk:false sets nothing", run(OPTS_NOBULK, "key"), {"r1": None, "r2": None}),
        ("all-A button with bulk:false sets nothing", run(OPTS_NOBULK, "click"), {"r1": None, "r2": None}),
        ("control: shift+1 with bulk on sets every row", run(OPTS_BULK, "key"), {"r1": "A", "r2": "A"}),
        ("shift+1 skips a row whose itemOptions lack A",
         run(OPTS_BULK, "key", {"r1": ["B"], "r2": ["A", "B"]}), {"r1": None, "r2": "A"}),
        ("all-A button skips a row whose itemOptions lack A",
         run(OPTS_BULK, "click", {"r1": ["B"], "r2": ["A", "B"]}), {"r1": None, "r2": "A"}),
    ]
    for name, got, want in checks:
        ok = got == want
        print(("PASS" if ok else "FAIL") + ": " + name + ("" if ok else " got=%s want=%s" % (got, want)))
        if not ok:
            fails.append(name)
    print("%d/%d checks pass" % (len(checks) - len(fails), len(checks)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
