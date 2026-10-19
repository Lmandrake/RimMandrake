"""selftest_save_def_census.py - an unresolved THING def (a def we cut) is counted, split from plain references, and
its plant blocks are removed byte-exactly (CRLF kept, neighbours kept, same-name references kept, never in place)."""
import os
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import save_def_census as D  # noqa: E402

T = lambda d, i: ("\t\t<thing Class=\"Plant\">\r\n\t\t\t<def>%s</def>\r\n\t\t\t<id>%s%d</id>\r\n\t\t\t<pos>(1, 0, 2)</pos>\r\n\t\t</thing>\r\n" % (d, d, i))
SAVE = ("<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n<savegame><things>\r\n" + T("CutTree", 1) + T("Human", 2) + T("CutTree", 3)
        + T("Frame_Human", 4) + "</things><hediffs><li><def>DeadHediff</def></li></hediffs></savegame>\r\n")


def case(name, cond, detail=""):
    print("%-4s %s %s" % ("ok" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    d = Path(tempfile.mkdtemp())
    src, dst = d / "s.rws", d / "s2.rws"
    src.write_bytes(SAVE.encode())
    known = {"Human"}
    r = D.census(src, known)
    ok = case("things counted", r["things_total"] == 4 and r["things"] == [{"def": "CutTree", "kind": "Plant", "count": 2, "src_only": False}], r)
    ok &= case("plain ref split off", [x["def"] for x in r["refs"]] == ["DeadHediff"])
    ok &= case("implied Frame_ resolves via base", not any(x["def"] == "Frame_Human" for x in r["things"]))
    n, skipped = D.strip_things(src, dst, ["CutTree"])
    out = dst.read_bytes()
    ok &= case("two blocks removed", n == 2 and ET.parse(dst).getroot().find("things") is not None and len(ET.parse(dst).getroot().find("things")) == 2)
    ok &= case("byte-exact", len(out) == len(SAVE.encode()) - 2 * len(T("CutTree", 1).encode()) and b"CutTree" not in out and b"\r\n" in out)
    ok &= case("nothing skipped", skipped == [])
    ref = d / "r.rws"
    ref.write_bytes(SAVE.replace("</things>", "<li>CutTree3</li></things>").encode())
    n2, sk2 = D.strip_things(ref, d / "r2.rws", ["CutTree"])
    ok &= case("referenced id kept, listed", n2 == 1 and len(sk2) == 1 and "CutTree3:referenced" in sk2[0], sk2)
    ok &= case("hediff reference kept", b"DeadHediff" in out)
    try:
        D.strip_things(src, src, ["CutTree"])
        ok &= case("refuses in place", False)
    except SystemExit:
        ok &= case("refuses in place", True)
    ok &= case("original untouched", src.read_bytes() == SAVE.encode())
    print("ALL OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
