#!/usr/bin/env python3
"""Offline: batch.py reads each check's own verdict from a shared runner process. Planted fault: scene b FAILs inside a group of
three checks (b alone red, a and c green); a crash after scene a leaves b UNMEASURED, never PASS; INVALID is UNMEASURED."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import batch
OUT = "a                PASS fine\na                advanced 300/300 ticks in 5 s via x\nb                FAIL it broke\nc                PASS fine ok\nVERDICT FAIL  (3 scenes) -> p\n"
r = batch.scene_rows(OUT); ok = True
def case(name, got, want):
    global ok
    ok &= got == want
    print("  %-34s %s %s" % (name, got, "ok" if got == want else "WRONG want %s" % (want,)))
case("planted fail in b is red", batch.check_verdict(["b"], r, 1, OUT)[0], "FAIL")
case("neighbour a stays green", batch.check_verdict(["a"], r, 1, OUT)[0], "PASS")
case("neighbour c stays green", batch.check_verdict(["c"], r, 1, OUT)[0], "PASS")
case("two-scene check with b is red", batch.check_verdict(["a", "b"], r, 1, OUT)[0], "FAIL")
r2 = batch.scene_rows("a                PASS fine\nTraceback boom\n")
case("crash: a kept green", batch.check_verdict(["a"], r2, 1, "")[0], "PASS")
case("crash: b unmeasured not pass", batch.check_verdict(["b"], r2, 1, "")[0], "UNMEASURED")
case("invalid is unmeasured", batch.check_verdict(["d"], batch.scene_rows("d                INVALID x\n"), 1, "")[0], "UNMEASURED")
case("advanced line is no row", batch.scene_rows("a advanced 3/3 ticks in 1 s"), {})
print("SELFTEST OK" if ok else "SELFTEST BROKEN"); sys.exit(0 if ok else 1)
