import json, pathlib
P = pathlib.Path(__file__).parent
d = json.loads((P / "data.json").read_text())
blob = json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/").replace("<!--", "<\\!--")
t = (P / "template.html").read_text()
assert t.count("/*__DATA__*/") == 1
(P / "index.html").write_text(t.replace("/*__DATA__*/", blob))
print("index.html", (P / "index.html").stat().st_size)
