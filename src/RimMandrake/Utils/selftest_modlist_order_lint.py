#!/usr/bin/env python3
"""Selftest for modlist_order_lint.py (MODLIST_ORDER_FIX_LOADAFTER_WAS_A_SUGGESTION).

1. a planted list breaking a loadAfter, a loadBefore and a modDependencies edge FAILS, naming each;
2. --fix re-sorts it stably (unconstrained mods keep their order) and it then passes;
3. a cycle refuses --fix and leaves the file untouched;
4. the committed ModsConfig.FULL.LATEST.xml passes against the real src/ About.xml files, with a
   non-blind count, and mandrake.rut.patches sits after mandrake.rsw.swbestiary (the instance)."""
import io
import os
import shutil
import sys
import tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modlist_order_lint as lint  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FULL = os.path.join(ROOT, "infrastructure", "state", "modlists", "ModsConfig.FULL.LATEST.xml")


def about(src, rel, pid, after=(), before=(), deps=()):
    d = os.path.join(src, rel, "About")
    os.makedirs(d, exist_ok=True)
    li = lambda xs: "".join("<li>%s</li>" % x for x in xs)  # noqa: E731
    dp = "".join("<li><packageId>%s</packageId></li>" % x for x in deps)
    with open(os.path.join(d, "About.xml"), "w") as fh:
        fh.write("<ModMetaData><packageId>%s</packageId><modDependencies>%s</modDependencies>"
                 "<loadAfter>%s</loadAfter><loadBefore>%s</loadBefore></ModMetaData>"
                 % (pid, dp, li(after), li(before)))


def modsconfig(path, ids):
    with open(path, "w") as fh:
        fh.write("<?xml version='1.0' encoding='utf-8'?>\n<ModsConfigData><version>1.6</version><activeMods>%s"
                 "</activeMods><knownExpansions><li>ludeon.rimworld.odyssey</li></knownExpansions></ModsConfigData>"
                 % "".join("<li>%s</li>" % i for i in ids))


def run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = lint.main(argv)
    return rc, buf.getvalue()


def main():
    fails = []
    tmp = tempfile.mkdtemp(prefix="modlistorder_")
    try:
        src = os.path.join(tmp, "src")
        # Y loadAfter Z (the UtinniPatches/SWBestiary shape), X loadBefore W, V depends on U.
        about(src, "RimUtinni/Y", "mandrake.rut.y", after=["mandrake.rsw.z"])
        about(src, "RimStarWars/Z", "mandrake.rsw.z")
        about(src, "RimMandrake/X", "mandrake.rm.x", before=["other.w"])
        about(src, "RimMandrake/V", "mandrake.rm.v", deps=["other.u"])
        cfg = os.path.join(tmp, "ModsConfig.xml")
        start = ["ludeon.rimworld", "other.w", "mandrake.rut.y", "other.a", "mandrake.rsw.z",
                 "mandrake.rm.v", "other.b", "other.u", "mandrake.rm.x", "other.c"]
        modsconfig(cfg, start)
        rc, out = run([cfg, "--src", src])
        if rc != 1 or out.count("BROKEN") != 3:
            fails.append("1. planted list: rc=%s, %d BROKEN (want 1, 3)\n%s" % (rc, out.count("BROKEN"), out))
        for want in ("mandrake.rut.y loads after mandrake.rsw.z", "mandrake.rm.x loads before other.w",
                     "mandrake.rm.v loads after other.u"):
            if want not in out:
                fails.append("1. missing %r" % want)
        rc, out = run([cfg, "--src", src, "--fix"])
        got = lint.read_list(cfg)
        if rc != 0 or "0 broken -> OK" not in out:
            fails.append("2. --fix did not leave it OK: rc=%s\n%s" % (rc, out))
        pos = {p: i for i, p in enumerate(got)}
        for a, b in (("mandrake.rsw.z", "mandrake.rut.y"), ("mandrake.rm.x", "other.w"), ("other.u", "mandrake.rm.v")):
            if pos[a] > pos[b]:
                fails.append("2. after --fix %s still after %s: %s" % (a, b, got))
        free = [p for p in start if p in ("ludeon.rimworld", "other.a", "other.b", "other.c")]
        if [p for p in got if p in free] != free or sorted(got) != sorted(start):
            fails.append("2. --fix was not a stable permutation: %s" % got)
        if "knownExpansions" not in open(cfg).read():
            fails.append("2. --fix dropped the rest of the file")
        # 3. cycle: Z loadAfter Y too.
        about(src, "RimStarWars/Z", "mandrake.rsw.z", after=["mandrake.rut.y"])
        modsconfig(cfg, start)
        before = open(cfg).read()
        rc, out = run([cfg, "--src", src, "--fix"])
        if rc != 1 or "cycle" not in out or open(cfg).read() != before:
            fails.append("3. cycle: rc=%s, file changed=%s\n%s" % (rc, open(cfg).read() != before, out))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # 4. the real list against the real About files.
    rc, out = run([FULL])
    last = out.strip().splitlines()[-1] if out.strip() else ""
    if rc != 0:
        fails.append("4. FULL.LATEST breaks our About edges:\n%s" % out)
    try:
        nours = int(last.split(" listed, ")[1].split(" with")[0])
    except (IndexError, ValueError):
        nours = 0
    if nours < 30:
        fails.append("4. sanity: only %d listed mods matched a repo About.xml (blind?): %s" % (nours, last))
    ids = [p.lower() for p in lint.read_list(FULL)]
    if ids.index("mandrake.rut.patches") < ids.index("mandrake.rsw.swbestiary"):
        fails.append("4. instance: mandrake.rut.patches still loads before mandrake.rsw.swbestiary")
    for f in fails:
        print("FAIL " + f)
    print("selftest_modlist_order_lint: %s (%s)" % ("FAILED" if fails else "OK", last))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
