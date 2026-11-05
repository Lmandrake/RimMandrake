#!/usr/bin/env python3
"""selftest_standin_shadowed.py — standin_shadowed.py check (STANDIN_AUDIT_SHADOWED_COPIES_LEFT) must:
  * fail on a Textures/StandIn/<rel>.png whose twin Textures/<rel>.png exists in the same mod while nothing names
    StandIn/<rel> (the 128 retired copies were this shape);
  * not fail on a shadowed stand-in an XML still draws (stem, or a mask `_northm` of a drawn stem): READ, listed;
  * ignore a stand-in with no twin (still the drawn art) and a twin in a DIFFERENT mod;
  * pass the real tree once the shadowed copies are retired.
Runs in a temp tree via ART_SRC_ROOT, then once on the real src/."""
from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def w(p: Path, data: str | bytes):
    p.parent.mkdir(parents=True, exist_ok=True)
    (p.write_bytes if isinstance(data, bytes) else p.write_text)(data)


def run(mod, argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = mod.main(argv)
    return rc, buf.getvalue()


def main() -> int:
    sys.path.insert(0, str(HERE))
    import standin_shadowed as S
    real_rc, real_out = run(S, ["check"])
    check(real_rc == 0, "real tree: no dead shadowed stand-in left (%s)" % real_out.strip().splitlines()[-1])

    with tempfile.TemporaryDirectory(prefix="selftest_standin_shadowed_") as td:
        src = Path(td) / "src"
        a = src / "RimX" / "ModA"
        png = b"\x89PNG\r\n\x1a\n"
        w(a / "Textures" / "StandIn" / "Things" / "Dead.png", png + b"d")
        w(a / "Textures" / "Things" / "Dead.png", png + b"D")
        w(a / "Textures" / "StandIn" / "Things" / "Drawn_south.png", png + b"s")
        w(a / "Textures" / "Things" / "Drawn_south.png", png + b"S")
        w(a / "Textures" / "StandIn" / "Things" / "Drawn_northm.png", png + b"m")
        w(a / "Textures" / "Things" / "Drawn_northm.png", png + b"M")
        w(a / "Textures" / "StandIn" / "Things" / "Lonely.png", png + b"l")
        w(a / "Textures" / "StandIn" / "Things" / "Elsewhere.png", png + b"e")
        w(src / "RimX" / "ModB" / "Textures" / "Things" / "Elsewhere.png", png + b"E")
        w(a / "Defs" / "d.xml", "<Defs><ThingDef><graphicData><texPath>StandIn/Things/Drawn</texPath>"
                                "</graphicData></ThingDef></Defs>")
        old = os.environ.get("ART_SRC_ROOT")
        os.environ["ART_SRC_ROOT"] = str(src)
        try:
            rc, out = run(S, ["check"])
            check(rc == 1 and "StandIn/Things/Dead.png" in out, "unread shadowed stand-in fails check")
            check("Lonely" not in out and "Elsewhere" not in out, "no-twin and other-mod-twin stand-ins ignored")
            rc, out = run(S, ["list"])
            check("READ" in out and "Drawn_south" in out and "Drawn_northm" in out
                  and "dead 1, read 2" in out, "drawn stem and its facing mask are READ, not dead")
            (a / "Textures" / "StandIn" / "Things" / "Dead.png").unlink()
            rc, out = run(S, ["check"])
            check(rc == 0, "check passes once the dead copy is gone")
        finally:
            if old is None:
                os.environ.pop("ART_SRC_ROOT", None)
            else:
                os.environ["ART_SRC_ROOT"] = old
    print("FAILS: %d" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
