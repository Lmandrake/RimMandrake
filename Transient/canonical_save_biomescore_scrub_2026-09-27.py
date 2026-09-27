"""Scrub biomesteam.biomescore out of CANONICAL_ASHKARR_START_2026-09-12.rws (BMT_FAUNA_ABSORPTION_1).

Binary-mode, line-based surgery on the CRLF save. Never writes in place: reads SRC, writes OUT.
  python3 canonical_save_biomescore_scrub_2026-09-27.py SRC OUT DONOR_NAMES_JSON

DONOR_NAMES_JSON: every defName in biomescore's 1.6 + Common Defs (all confirmed, against the
2026-09-26T20-50-19Z 629-mod dump, to be owned by biomescore alone).
"""
import json, re, sys

SRC, OUT, NAMES = sys.argv[1], sys.argv[2], sys.argv[3]
names = set(json.load(open(NAMES)))
# Donor stuff with a byte-identical RSW_ port already live in SWBestiary: repoint, keep the item.
STUFF_REPOINT = {b"BMT_FragileChitin": b"RSW_FragileChitin", b"BMT_WeakChitin": b"RSW_WeakChitin",
                 b"BiomesCore_CrabShell": b"RSW_BiomesCore_CrabShell"}
PKG = b"biomesteam.biomescore"

data = open(SRC, "rb").read()
lines = data.split(b"\r\n")
ind = lambda l: len(l) - len(l.lstrip(b"\t"))
leaf = re.compile(rb"^\s*<([A-Za-z_]+)>([^<]*)</\1>\s*$")

def parent_li(i):
    d = ind(lines[i])
    for j in range(i - 1, -1, -1):
        s = lines[j].lstrip()
        if ind(lines[j]) == 0:
            continue  # base64 grid payloads and their close tags sit at column 0
        if ind(lines[j]) < d and s.startswith(b"<li") and not s.endswith(b"/>") and b"</li>" not in s:
            return j
        if ind(lines[j]) < d and not s.startswith(b"<li"):
            return None  # parent is not a list entry
    return None

def block_end(j):
    d = ind(lines[j])
    for k in range(j + 1, len(lines)):
        if ind(lines[k]) == d and lines[k].strip() == b"</li>":
            return k
    raise SystemExit("unclosed li at line %d" % j)

delete = set(); log = []; repoint = 0
def kill(a, b, why):
    delete.update(range(a, b + 1)); log.append((why, a, b))

# 1. <meta> parallel lists: resolve index from modIds, apply positionally to all three.
def meta_list(tag):
    s = lines.index(b"\t\t<%s>" % tag); e = lines.index(b"\t\t</%s>" % tag)
    return list(range(s + 1, e))
ids, steam, mnames = meta_list(b"modIds"), meta_list(b"modSteamIds"), meta_list(b"modNames")
assert len(ids) == len(steam) == len(mnames)
k = [i for i, l in enumerate(ids) if lines[l].strip() == b"<li>" + PKG + b"</li>"]
assert len(k) == 1, k
k = k[0]
assert lines[mnames[k]].strip() == b"<li>Biomes! Core</li>", lines[mnames[k]]
for L in (ids[k], steam[k], mnames[k]): kill(L, L, "meta")

dict_kill = {}  # keys-line-index -> set(entry idx)
for i, l in enumerate(lines):
    s = l.strip()
    # 2. MapComponents whose class lives in BiomesCore.dll
    if s.startswith(b'<li Class="BiomesCore.') and s.endswith(b"/>"):
        kill(i, i, "class"); continue
    m = leaf.match(l)
    if not m:
        continue
    tag, val = m.group(1), m.group(2)
    v = val.decode()
    if tag == b"stuff" and val in STUFF_REPOINT:
        lines[i] = l.replace(b">" + val + b"<", b">" + STUFF_REPOINT[val] + b"<"); repoint += 1; continue
    if v not in names and not v.startswith("Thing_BMT_Hermetic"):
        continue
    if tag == b"li":  # flat def list entry, or a dictionary key
        pj = next(j for j in range(i - 1, -1, -1) if 0 < ind(lines[j]) < ind(l))
        par = lines[pj].strip()
        if par == b"<keys>":
            dict_kill.setdefault(pj, set()).add(i)
        else:
            kill(i, i, "flat:" + par.decode())
        continue
    if tag == b"app":  # tale's notable-apparel def: drop the field (reads as none)
        kill(i, i, "tale-app"); continue
    if tag == b"wornApparel":
        continue  # goes with its hediff block
    j = parent_li(i)
    assert j is not None, (i, l)
    kill(j, block_end(j), "block:" + tag.decode() + ":" + v)

# 3. dictionaries: remove key i and value i together, positionally
for kl, keylines in dict_kill.items():
    d = ind(lines[kl])
    ke = next(x for x in range(kl + 1, len(lines)) if ind(lines[x]) == d and lines[x].strip() == b"</keys>")
    keys = [x for x in range(kl + 1, ke) if ind(lines[x]) == d + 1]
    vs = ke + 1
    assert lines[vs].strip() == b"<values>", lines[vs]
    ve = next(x for x in range(vs + 1, len(lines)) if ind(lines[x]) == d and lines[x].strip() == b"</values>")
    starts = [x for x in range(vs + 1, ve) if ind(lines[x]) == d + 1 and lines[x].strip().startswith(b"<li")]
    assert len(starts) == len(keys), (len(starts), len(keys))
    for x in keylines:
        n = keys.index(x)
        kill(x, x, "dict-key")
        a = starts[n]; b = a if lines[a].strip().endswith(b"/>") else block_end(a)
        keyname = leaf.match(lines[x]).group(2)
        assert any(b">" + keyname + b"<" in lines[y] for y in range(a, b + 1)), ("dict misaligned", keyname)
        kill(a, b, "dict-val")

# safety: ids declared inside deleted blocks must not be referenced from surviving lines
dead_ids = set()
for i in delete:
    m = re.match(rb"^\s*<id>([^<]+)</id>", lines[i])
    if m: dead_ids.add(b"Thing_" + m.group(1))
out_lines = [l for i, l in enumerate(lines) if i not in delete]
out = b"\r\n".join(out_lines)
for t in dead_ids:
    assert out.count(b">" + t + b"<") == 0, t
open(OUT, "wb").write(out)
from collections import Counter
print("removed lines", len(delete), "bytes", len(data) - len(out), "repointed stuff", repoint)
print(Counter(w.split(":")[0] for w, _, _ in log))
print("dead thing ids (unreferenced after):", sorted(x.decode() for x in dead_ids))
for w, a, b in log:
    if w.startswith("block"): print(" ", w, "lines", a + 1, "-", b + 1)
