#!/usr/bin/env python3
"""Regression selftest for the 2026-10-20 code-review fixes (offline, tmp dirs only):
ship_remap keeps <things> attributes · founders_drop_retired survives an empty <childhood/> ·
mod_archive.ids_of warns on garbage · world_layers_export.save_mod_ids refuses a save with no modIds ·
g8 DllIndex.owners needs the whole type name · checkpoint G17 fails when make() had a missing source."""
import contextlib, io, os, shutil, sys, tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
U = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, U)
fails = []


def ok(c, m):
    print(("ok   " if c else "FAIL ") + m)
    if not c:
        fails.append(m)


def main():
    t = tempfile.mkdtemp(prefix="rvfix_")
    try:
        import ship_remap
        root = ET.fromstring('<l><things Class="X"><li><defName>A</defName></li></things></l>')
        ship_remap.remap(root, {"terrain": {}, "things": {"A": {"to": None}}, "special_filters_drop": []})
        ok(root.find("things").get("Class") == "X" and len(root.find("things")) == 0, "ship_remap keeps attributes of emptied <things>")

        import founders_drop_retired as F
        r = ET.fromstring("<root><li><childhood/></li></root>")
        try:
            F.process(r, set(), set()); ok(True, "founders: empty <childhood/> no crash")
        except AttributeError:
            ok(False, "founders: empty <childhood/> no crash")

        import mod_archive
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            res = mod_archive.ids_of("<not xml")
        ok(res == [] and "WARN" in err.getvalue(), "mod_archive.ids_of warns on garbage")

        import world_layers_export as W
        p = os.path.join(t, "s.rws"); open(p, "w").write("<savegame><meta></meta></savegame>")
        try:
            W.save_mod_ids(p); ok(False, "save_mod_ids refuses a save without modIds")
        except SystemExit:
            ok(True, "save_mod_ids refuses a save without modIds")

        import g8_worker_safety as G
        d = os.path.join(t, "mod", "Assemblies"); os.makedirs(d)
        open(os.path.join(d, "a.dll"), "wb").write(b"\x00Foo\x00BiomeWorker_X2\x00")
        idx = G.DllIndex({"pkg": os.path.join(t, "mod")})
        ok(idx.owners("Foo.BiomeWorker_X") == set() and idx.owners("Foo.BiomeWorker_X2") == {"pkg"},
           "g8 owners: BiomeWorker_X is not found inside BiomeWorker_X2")

        import checkpoint as C
        ll = os.path.join(t, "LL"); os.makedirs(os.path.join(ll, "Config"))
        open(os.path.join(ll, "Config", "Mod_1_A.xml"), "w").write("a")   # no cherry picker => MISSING
        with contextlib.redirect_stdout(io.StringIO()):
            C.make("C3", os.path.join(t, "out"), "D", ll)
            rc = C.verify(os.path.join(t, "out", "D", "C3"))
        ok(rc == 1, "checkpoint verify FAILs a checkpoint made with a missing source")
    finally:
        shutil.rmtree(t, ignore_errors=True)
    print("%d FAIL" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
