#!/usr/bin/env python3
"""Selftest for about_load_order_lint.py: a planted cycle must FAIL, a cycle that only
exists once a composed member folds onto its composite must FAIL, an acyclic tree must
pass, and the real src/ must pass with a non-blind mod count."""
import io
import json
import os
import shutil
import sys
import tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import about_load_order_lint as lint  # noqa: E402


def about(root, rel, pid, after=(), before=()):
    d = os.path.join(root, rel, "About")
    os.makedirs(d, exist_ok=True)
    la = "".join("<li>%s</li>" % x for x in after)
    lb = "".join("<li>%s</li>" % x for x in before)
    with open(os.path.join(d, "About.xml"), "w") as fh:
        fh.write("<ModMetaData><packageId>%s</packageId><loadAfter>%s</loadAfter>"
                 "<loadBefore>%s</loadBefore></ModMetaData>" % (pid, la, lb))


def cycles_of(root):
    buf = io.StringIO()
    with redirect_stdout(buf):
        cycles, warnings, problems, _, _ = lint.run(root, out=print)
    return cycles, warnings


def main():
    fails = []
    tmp = tempfile.mkdtemp(prefix="aboutlo_")
    try:
        # 1. plain three-mod cycle mixing loadAfter and loadBefore: b<a (A after b),
        #    a<c (A before C), c<b (C before B); D hangs off it and is not in it.
        r = os.path.join(tmp, "plain")
        about(r, "RimMandrake/A", "x.a", after=["x.b"], before=["X.C"])  # case-insensitive
        about(r, "RimMandrake/B", "x.b")
        about(r, "RimMandrake/C", "x.c", before=["x.b"])
        about(r, "RimMandrake/D", "x.d", after=["x.a", "brrainz.harmony"])
        c, _ = cycles_of(r)
        if c != [["x.a", "x.b", "x.c"]]:
            fails.append("planted A<->B cycle not reported exactly: %r" % c)

        # 2. acyclic tree passes
        r = os.path.join(tmp, "clean")
        about(r, "RimMandrake/A", "x.a")
        about(r, "RimMandrake/B", "x.b", after=["x.a"])
        about(r, "RimMandrake/C", "x.c", after=["x.b", "x.a"])
        c, _ = cycles_of(r)
        if c:
            fails.append("acyclic tree reported a cycle: %r" % c)

        # 3. the 2026-10-11 shape: a member folded into the composite loadAfter E,
        #    E loadAfter the composite. Only visible after folding.
        r = os.path.join(tmp, "composed")
        os.makedirs(os.path.join(r, "RimMandrake"))
        with open(os.path.join(r, "RimMandrake", "Biomes.compose.json"), "w") as fh:
            json.dump({"target": "T", "compose_wave": 2,
                       "about": {"packageId": "mandrake.rm.biomes"},
                       "entries": [{"key": "Flood", "source": "Flood", "wave": 2},
                                   {"key": "Later", "source": "Later", "wave": 3}]}, fh)
        about(r, "RimMandrake/Flood", "mandrake.rm.flood", after=["mandrake.rm.eg"])
        about(r, "RimMandrake/Later", "mandrake.rm.later")
        about(r, "RimMandrake/EG", "mandrake.rm.eg", after=["mandrake.rm.biomes"])
        about(r, "RimMandrake/Other", "mandrake.rm.other", after=["mandrake.rm.flood"])
        c, w = cycles_of(r)
        if c != [["mandrake.rm.biomes", "mandrake.rm.eg"]]:
            fails.append("folded-member cycle not reported: %r" % c)
        if not any("mandrake.rm.flood" in x and "Other" in x for x in w):
            fails.append("loadAfter naming a folded member id was not warned: %r" % w)
        if any("Flood" in x.split(" names ")[0] for x in w):
            fails.append("a member naming its own composite's members was warned: %r" % w)

        # 4. the real tree
        buf = io.StringIO()
        with redirect_stdout(buf):
            c, _, problems, nmods, _ = lint.run(lint.DEFAULT_SRC, out=print)
        if nmods < 20:
            fails.append("sanity probe: real src scan saw only %d mods" % nmods)
        if c or problems:
            fails.append("real src/ has load-order cycle(s) or unparseable About.xml:\n" + buf.getvalue())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for f in fails:
        print("FAIL " + f)
    print("selftest_about_load_order_lint: %s" % ("OK" if not fails else "%d FAILED" % len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
