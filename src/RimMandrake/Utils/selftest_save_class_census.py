"""selftest_save_class_census.py - a retired donor's Area class in <areaManager><areas> is FATAL and is stripped
byte-exactly (CRLF kept, siblings kept, never in place). Synthetic save; no game, no DLL index (--no-assemblies).
"""
import os
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import save_class_census as C  # noqa: E402

SAVE = ("<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n<savegame><game><maps><li>\r\n"
        "\t<components>\r\n\t\t<li Class=\"AlphaBiomes.MapComponentExtender\" />\r\n"
        "\t\t<li Class=\"RimMandrake.Abyss.RM_MapComponent_Dark\" />\r\n\t</components>\r\n"
        "\t<areaManager>\r\n\t\t<areas>\r\n\t\t\t<li Class=\"Area_Home\">\r\n\t\t\t\t<ID>1</ID>\r\n\t\t\t</li>\r\n"
        "\t\t\t<li Class=\"VFEInsectoids.Area_Hive\">\r\n\t\t\t\t<ID>13</ID>\r\n"
        "\t\t\t\t<innerGrid><li>x</li></innerGrid>\r\n\t\t\t</li>\r\n"
        "\t\t\t<li Class=\"PrisonLabor.Core.LaborArea.Area_Labor\">\r\n\t\t\t\t<ID>14</ID>\r\n\t\t\t</li>\r\n"
        "\t\t</areas>\r\n\t</areaManager>\r\n</li></maps></game></savegame>\r\n")


def case(name, cond, detail=""):
    print("%-4s %s %s" % ("ok" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    d = Path(tempfile.mkdtemp())
    src, dst = d / "s.rws", d / "s_AREAFIX.rws"
    src.write_bytes(SAVE.encode())
    rows = C.census(src, None, set())
    sev = {r["class"]: r["severity"] for r in rows}
    ok = case("area hive is FATAL", sev.get("VFEInsectoids.Area_Hive") == "FATAL", sev)
    ok &= case("alphabiomes component SKIPPED", sev.get("AlphaBiomes.MapComponentExtender") == "SKIPPED")
    ok &= case("own and non-retired classes not flagged", len(rows) == 2)
    gone = C.strip_fatal(src, dst, ["VFEInsectoids.Area_Hive"])
    out = dst.read_bytes()
    areas = ET.parse(dst).getroot().find(".//areas")
    ok &= case("one element removed", len(gone) == 1 and len(areas) == 2)
    ok &= case("neighbours kept", [li.get("Class") for li in areas] == ["Area_Home", "PrisonLabor.Core.LaborArea.Area_Labor"])
    ok &= case("byte-exact", len(out) == len(SAVE.encode()) - len(gone[0].encode()) and b"\r\n" in out and b"Hive" not in out)
    try:
        C.strip_fatal(src, src, ["VFEInsectoids.Area_Hive"])
        ok &= case("refuses in place", False)
    except SystemExit:
        ok &= case("refuses in place", True)
    ok &= case("original untouched", src.read_bytes() == SAVE.encode())
    print("ALL OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
