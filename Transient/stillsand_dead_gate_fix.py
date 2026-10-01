#!/usr/bin/env python3
"""Repoint COMPOSED dead gates (rows in Transient/stillsand_dead_gate_sweep_results.txt) to mandrake.rm.biomes."""
import re, pathlib, collections
ROOT = pathlib.Path(__file__).resolve().parent.parent
SHIP = "mandrake.rm.biomes"
sec = False
rows = collections.defaultdict(set)
for ln in (ROOT / "Transient/stillsand_dead_gate_sweep_results.txt").read_text().splitlines():
    if ln.startswith("## "):
        sec = ln.startswith("## COMPOSED")
        continue
    m = re.match(r"  (\S+):(\d+) \[(\w+)\] (\S+)$", ln)
    if sec and m:
        rows[m.group(1)].add((int(m.group(2)), m.group(3), m.group(4)))
for f, items in rows.items():
    p = ROOT / f
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    lines = raw.decode("utf-8").split("\n")
    for ln, kind, pid in items:
        i = ln - 1
        if kind in ("loadAfter", "dependency"):
            # About blocks are reported at block start line: replace within the block
            end = i
            while end < len(lines) and not re.search(r"</(loadAfter|modDependencies)>", lines[end]):
                end += 1
            rng = range(i, end + 1)
        else:
            rng = [i]
        for j in rng:
            lines[j] = re.sub(r"(?<![\w.])" + re.escape(pid) + r"(?![\w.])", SHIP, lines[j])
    text = "\n".join(lines)
    # collapse duplicate comma lists in MayRequire
    def dedupe(m):
        seen = []
        for x in m.group(2).split(","):
            if x.strip() not in [s.strip() for s in seen]:
                seen.append(x)
        return m.group(1) + ",".join(seen) + '"'
    text = re.sub(r'(MayRequire(?:ByAnyOf)?=")([^"]*)"', dedupe, text)
    # drop duplicate <li>SHIP</li> within one list
    def dedupe_li(m):
        blk = m.group(0)
        first = True
        out = []
        for l in blk.split("\n"):
            if f"<li>{SHIP}</li>" in l:
                if not first:
                    continue
                first = False
            out.append(l)
        return "\n".join(out)
    text = re.sub(r"<loadAfter>.*?</loadAfter>", dedupe_li, text, flags=re.S)
    p.write_bytes(text.encode("utf-8"))
    print("fixed", f, len(items))
