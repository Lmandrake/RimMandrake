"""Selftest: biome_world_switch_check.py (BIOME_WORLD_SWITCH_WAVE_1) sees donors and passes the canonical save.

Offline, read-only. Checks:
  - short_hash reproduces ShortHashGiver on names whose hash is known (the dump's own values);
  - the canonical start save (canon.yml planet.start_savegame) reads PASS (exit 0) exactly when every painted
    def is declared by a src BiomeDef, and FAIL (exit 1) naming each dead RM_/RUT_ name when one is not
    (state-independent: green before and after the repaint of RM_Wasteland / RM_NightsideIce);
  - the pre-switch draft save, judged as if canonical, reads FAIL (exit 1): the instrument sees donors.
"""
import contextlib
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biome_world_switch_check as C  # noqa: E402

fails = []


def ok(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


def run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = C.main(argv)
    return code, buf.getvalue()


fwd, rev = C.worldmap.load_hash_table("BiomeDef")
for name in ("ExtremeDesert", "Desert", "AridShrubland", "RM_Stillsand"):
    if name in rev:
        ok(C.short_hash(name) == rev[name], "short_hash(%s) == dump %s" % (name, rev[name]))
ok(sum(1 for h, n in fwd.items() if C.short_hash(n) == h) >= 0.9 * len(fwd), "formula agrees with >=90% of the dump")

src = C.src_biome_defs()
groups = {}
for n in C.candidate_names(src):
    if n not in rev:
        groups.setdefault(C.short_hash(n), set()).add(n)
names, _, _ = C.decode(C.canonical_save(), fwd, {h: next(iter(ns)) for h, ns in groups.items() if len(ns) == 1},
                       {h for h in groups if h in fwd})
dead = sorted({n for n in names if C.OWNED.match(n) and n not in src})
code, out = run([])
last = out.strip().splitlines()[-1] if out.strip() else ""
if dead:
    ok(code == 1 and all(n in out for n in dead), "canonical save FAILs on dead names %s (exit %s): %s" % (dead, code, last))
else:
    ok(code == 0, "canonical save PASS (exit %s): %s" % (code, last))
code, out = run(["--save", C.PROBE_SAVE, "--probe", ""])
ok(code == 1, "pre-switch draft save FAILs (exit %s)" % code)

print("ALL PASS" if not fails else "%d FAIL" % len(fails))
sys.exit(1 if fails else 0)
