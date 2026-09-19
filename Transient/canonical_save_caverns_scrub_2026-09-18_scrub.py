"""CANONICAL_SAVE_CAVERNS_SCRUB_1 -- remove every BMT_CaveSpiderHead reference from a .rws.

Raw line-based edit: bytes in, bytes out, CRLF and every untouched byte preserved.
Usage: python3 scrub.py <in.rws> <out.rws>
"""
import re
import sys

NEEDLE = b"BMT_CaveSpiderHead"
src, dst = sys.argv[1], sys.argv[2]
raw = open(src, "rb").read()
EOL = b"\r\n" if b"\r\n" in raw[:4096] else b"\n"
lines = raw.split(EOL)
assert EOL.join(lines) == raw
n_before = sum(1 for l in lines if NEEDLE in l)
assert n_before == 89, n_before
assert raw.count(NEEDLE) == 89

kill = set()          # 0-based line indices to delete
counts = {}

def strip(l):
    return l.strip(b"\t ")

def li_block(i_open):
    """Return range of the <li> block whose opening tag is at i_open (matching depth by indentation)."""
    indent = lines[i_open][: len(lines[i_open]) - len(lines[i_open].lstrip(b"\t"))]
    assert strip(lines[i_open]).startswith(b"<li")
    close = indent + b"</li>"
    for j in range(i_open + 1, len(lines)):
        if lines[j] == close:
            return range(i_open, j + 1)
    raise AssertionError("no close for line %d" % (i_open + 1))

# A: weapon things
a = 0
for i, l in enumerate(lines):
    if strip(l) == b"<def>" + NEEDLE + b"</def>":
        assert strip(lines[i - 1]) == b"<li>"
        assert strip(lines[i + 1]).startswith(b"<id>" + NEEDLE)
        blk = li_block(i - 1)
        kill.update(blk); a += 1
counts["A weapon blocks"] = a
assert a == 5

# B, D: single-line def refs
for tag, key, want in ((b"source", "B hediff source", 10), (b"ownerDef", "D battlelog ownerDef", 19), (b"peq", "E tale peq", 13)):
    c = 0
    for i, l in enumerate(lines):
        if strip(l) == b"<" + tag + b">" + NEEDLE + b"</" + tag + b">":
            kill.add(i); c += 1
    counts[key] = c
    assert c == want, (key, c)

# C: rememberedWeapons entry
c = 0
for i, l in enumerate(lines):
    if strip(l) == b"<thing>" + NEEDLE + b"</thing>":
        assert strip(lines[i - 1]) == b"<li>" and strip(lines[i + 1]) == b"</li>"
        kill.update((i - 1, i, i + 1)); c += 1
counts["C rememberedWeapons"] = c
assert c == 1

# E: tale defData defName + defType
c = 0
for i, l in enumerate(lines):
    if strip(l) == b"<defName>" + NEEDLE + b"</defName>":
        assert strip(lines[i - 1]) == b"<defData>"
        assert strip(lines[i + 1]) == b"<defType>Verse.ThingDef</defType>"
        assert strip(lines[i + 2]) == b"</defData>"
        kill.update((i, i + 1)); c += 1
counts["E tale defData"] = c
assert c == 13

# F + G: bare <li>NEEDLE</li> -- two of them; classify by nearest enclosing container
c_f = c_g = 0
for i, l in enumerate(lines):
    if strip(l) == b"<li>" + NEEDLE + b"</li>":
        # walk back to the opening container tag at lower indent
        indent = len(l) - len(l.lstrip(b"\t"))
        for j in range(i - 1, 0, -1):
            lj = lines[j]
            ij = len(lj) - len(lj.lstrip(b"\t"))
            if ij < indent and strip(lj).startswith(b"<") and not strip(lj).startswith(b"</"):
                container = strip(lj); break
        if container == b"<allowedDefs>":
            kill.add(i); c_f += 1
        elif container == b"<keys>":
            # G: key index -> matching values block
            # find <keys> start line j, count <li> between
            keys_open = j
            idx = sum(1 for k in range(keys_open + 1, i) if strip(lines[k]).startswith(b"<li"))
            # find </keys> then <values>
            k = i
            while strip(lines[k]) != b"</keys>": k += 1
            assert strip(lines[k + 1]) == b"<values>"
            vals_open = k + 1
            # walk values <li> blocks
            n = 0; p = vals_open + 1
            while True:
                assert strip(lines[p]).startswith(b"<li"), lines[p]
                blk = li_block(p)
                if n == idx:
                    assert strip(lines[blk[-2]]) == b"<thingDef>" + NEEDLE + b"</thingDef>", lines[blk[-2]]
                    kill.update(blk); kill.add(i); c_g += 1
                    break
                n += 1; p = blk[-1] + 1
        else:
            raise AssertionError(container)
counts["F packUpFilter allowedDefs"] = c_f
counts["G VTE priceHistory key+value"] = c_g
assert c_f == 1 and c_g == 1

removed = [lines[i] for i in sorted(kill)]
needle_removed = sum(1 for l in removed if NEEDLE in l)
assert needle_removed == 89, needle_removed
bytes_removed = sum(len(l) + len(EOL) for l in removed)
out_lines = [l for i, l in enumerate(lines) if i not in kill]
out = EOL.join(out_lines)
assert len(out) == len(raw) - bytes_removed
assert out.count(NEEDLE) == 0
open(dst, "wb").write(out)
print("EOL", EOL, "lines_removed", len(removed), "needle_lines_removed", needle_removed, "bytes_removed", bytes_removed)
for k, v in counts.items():
    print(" ", k, v)
print("in", len(raw), "out", len(out))
