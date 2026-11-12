"""Embed <out>/page/data.json, items.json and the SheetJS library into template.html -> <out>/page/index.html.

One self-contained file: no network at view time. python3 build_page.py <out>   (gen_matrix.py runs it for you)
"""
import json, pathlib, sys
T = pathlib.Path(__file__).resolve().parent          # template.html, xlsx.full.min.js (SheetJS, Apache-2.0)
P = pathlib.Path(sys.argv[1]).resolve() / "page"     # data.json, items.json in; index.html out
def esc(o): return json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/").replace("<!--", "<\\!--")
t = (T / "template.html").read_text()
x = (T / "xlsx.full.min.js").read_text()
# the library holds "<!--" only inside four regex literals (/<!--(...)-->/); "<\\!--" is the same regex and safe in a script
assert "</script" not in x.lower() and "<script" not in x.lower()
x = x.replace("<!--", "<\\!--")
for k in ("/*__DATA__*/", "/*__XLSX__*/"):
    assert t.count(k) == 1, k
t = t.replace("/*__XLSX__*/", x)
t = t.replace("/*__DATA__*/", esc(json.loads((P / "data.json").read_text())))
items = '<script id="ITEMS" type="application/json">' + esc(json.loads((P / "items.json").read_text())) + "</script>\n"
assert t.count('<script type="application/json" id="data">') == 1
t = t.replace('<script type="application/json" id="data">', items + '<script type="application/json" id="data">')
(P / "index.html").write_text(t)
n = (P / "index.html").stat().st_size
assert n < 16 * 1024 * 1024, n
print("index.html", n)
