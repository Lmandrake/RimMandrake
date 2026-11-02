"""selftest_save_class_census.py - a retired donor's Area class in <areaManager><areas> is FATAL and is stripped
byte-exactly (CRLF kept, siblings kept, never in place). A dead world-object class is WORLDOBJ, and --strip-dead removes
it (nested and self-closing <li> balanced), dead components and named by-name refs, keeping live siblings; it refuses a
world object whose ID is referenced elsewhere. Synthetic saves; no game, no DLL index (--no-assemblies).
"""
# selftest temp containment (wave 7, DIRTY_CODE_REVIEW_STANDING_LOOP_1): every mkdtemp/mkstemp below,
# and every child process via TMPDIR, lands in one private dir removed at exit — this
# test used to leave its temp dirs behind in the seat TMPDIR on every run.
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_save_class_census_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
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


WORLD = ("<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n<savegame><game><world>\r\n"
         "\t<worldObjects>\r\n\t\t<worldObjects>\r\n"
         "\t\t\t<li Class=\"Settlement\">\r\n\t\t\t\t<ID>1</ID>\r\n\t\t\t</li>\r\n"
         "\t\t\t<li Class=\"AlphaBiomes.WorldObject_Herd\">\r\n\t\t\t\t<ID>107</ID>\r\n"
         "\t\t\t\t<members><innerList><li><lifeStage>1</lifeStage><x Class=\"a\" /></li>"
         "<li Class=\"Verse.Something\" /></innerList></members>\r\n\t\t\t</li>\r\n"
         "\t\t\t<li Class=\"Settlement\">\r\n\t\t\t\t<ID>2</ID>\r\n\t\t\t</li>\r\n"
         "\t\t</worldObjects>\r\n\t</worldObjects>\r\n"
         "\t<components>\r\n\t\t<li Class=\"AlphaBiomes.WorldComp\">\r\n\t\t\t<a>True</a>\r\n\t\t</li>\r\n"
         "\t\t<li Class=\"AlphaBiomes.WorldComp2\" />\r\n"
         "\t\t<li Class=\"RimMandrake.SeaShores.RM_Healer\" />\r\n\t</components>\r\n"
         "\t<filter><allowedDefs>\r\n\t\t<li>Meat_Gone</li>\r\n\t\t<li>Meat_Kept</li>\r\n\t</allowedDefs></filter>\r\n"
         "\t<configs>\r\n\t\t<li>\r\n\t\t\t<animal>Gone</animal>\r\n\t\t</li>\r\n"
         "\t\t<li>\r\n\t\t\t<animal>Kept</animal>\r\n\t\t</li>\r\n\t</configs>\r\n"
         "</world></game></savegame>\r\n")


def world_cases(d):
    src = d / "w.rws"
    src.write_bytes(WORLD.encode())
    rows = C.census(src, None, set())
    sev = {r["class"]: r["severity"] for r in rows}
    ok = case("dead world object is WORLDOBJ", sev.get("AlphaBiomes.WorldObject_Herd") == "WORLDOBJ", sev)
    ok &= case("dead world components SKIPPED", sev.get("AlphaBiomes.WorldComp") == "SKIPPED"
               and sev.get("AlphaBiomes.WorldComp2") == "SKIPPED")
    dst = d / "w_dead.rws"
    res = C.strip_dead(src, dst, rows, ["Meat_Gone", "Gone"])
    root = ET.parse(dst).getroot()
    wos = root.find(".//worldObjects/worldObjects")
    ok &= case("world object gone, settlements kept", [li.findtext("ID") for li in wos] == ["1", "2"], res)
    ok &= case("dead components gone, live kept",
               [li.get("Class") for li in root.find(".//world/components")] == ["RimMandrake.SeaShores.RM_Healer"])
    ok &= case("refs gone, live refs kept",
               [li.text for li in root.find(".//allowedDefs")] == ["Meat_Kept"]
               and [li.findtext("animal") for li in root.find(".//configs")] == ["Kept"], res["refs"])
    out = dst.read_bytes()
    ok &= case("CRLF kept, no blank lines left", b"\r\n" in out and b"\r\n\r\n" not in out and b"\n\t\t\r\n" not in out)
    ok &= case("source untouched", src.read_bytes() == WORLD.encode())
    ref = d / "w_ref.rws"
    ref.write_bytes(WORLD.replace("<ID>2</ID>", "<ID>2</ID><target>WorldObject_107</target>").encode())
    try:
        C.strip_dead(ref, d / "w_ref_dead.rws", C.census(ref, None, set()))
        ok &= case("refuses a referenced world object", False)
    except SystemExit:
        ok &= case("refuses a referenced world object", not (d / "w_ref_dead.rws").exists())
    return ok


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
    ok &= world_cases(d)
    print("ALL OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
