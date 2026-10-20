#!/usr/bin/env python3
"""Selftest for remake/g5_reverse_closure.py on a fake capture (retained mod 'me.keep', removed mod 'x.gone')."""
import contextlib
import io
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import g5_reverse_closure as G  # noqa: E402


def w(p, s, mode="w"):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, mode).write(s)


def run(*argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = G.main(list(argv))
    return rc, buf.getvalue()


def setup(t, about_dep=False, unguarded=True, dll=False):
    core, keep, gone = (os.path.join(t, n) for n in ("core", "keep", "gone"))
    w(os.path.join(core, "Defs", "a.xml"), "<Defs><ThingDef><defName>Human</defName></ThingDef>"
      "<StatDef><defName>ArmorRating_Sharp</defName></StatDef></Defs>")
    dep = "<modDependencies><li><packageId>x.gone</packageId></li></modDependencies>" if about_dep else ""
    w(os.path.join(keep, "About", "About.xml"), "<ModMetaData><name>Keep</name><packageId>me.keep</packageId>%s</ModMetaData>" % dep)
    w(os.path.join(gone, "About", "About.xml"), "<ModMetaData><name>Gone Mod</name><packageId>x.gone</packageId></ModMetaData>")
    w(os.path.join(keep, "Defs", "k.xml"), "<Defs><ThingDef><defName>Keeper</defName><costList><li>%s</li></costList>"
      "<x MayRequire=\"x.gone\"><li>GONE_Guarded</li></x><label>GONE_Thing</label></ThingDef></Defs>"
      % ("GONE_Thing" if unguarded else "Keeper"))
    w(os.path.join(keep, "Patches", "p.xml"), "<Patch>"
      "<Operation Class=\"PatchOperationFindMod\"><mods><li>Gone Mod</li></mods><match Class=\"PatchOperationAdd\">"
      "<xpath>Defs/ThingDef[defName=\"GONE_Patched\"]</xpath></match></Operation>"
      "<Operation Class=\"PatchOperationReplace\"><xpath>Defs/StatDef[defName=\"ArmorRating_Sharp\"]/x</xpath></Operation>"
      "</Patch>")
    w(os.path.join(keep, "LoadFolders.xml"), "<loadFolders><v1.6><li>/</li><li IfModActive=\"x.gone\">Mods/Gone</li></v1.6></loadFolders>")
    w(os.path.join(keep, "Mods", "Gone", "Defs", "g.xml"), "<Defs><ThingDef><defName>K2</defName><li>GONE_Thing</li></ThingDef></Defs>")
    if dll:
        w(os.path.join(keep, "1.6", "Assemblies", "K.dll"), b"\x00" + "GONE_Literal".encode("utf-16le") + b"\x00\x00", "wb")
    dump = os.path.join(t, "dump")
    mods = {"ludeon.rimworld": core, "me.keep": keep, "x.gone": gone}
    w(os.path.join(dump, "manifest.json"), json.dumps({"mods": [{"packageId": p, "rootDir": r} for p, r in mods.items()]}))
    defs = [{"defName": "Human", "packageId": "ludeon.rimworld"}, {"defName": "Keeper", "packageId": "me.keep"},
            {"defName": "ArmorRating_Sharp", "packageId": "x.gone"}]  # a Core def a removed mod overrode
    defs += [{"defName": n, "packageId": "x.gone"} for n in ("GONE_Thing", "GONE_Guarded", "GONE_Patched", "GONE_Literal")]
    w(os.path.join(dump, "defs", "ThingDef.json"), json.dumps({"defs": defs}))
    prof = os.path.join(t, "profile.xml")
    w(prof, "<ModsConfigData><activeMods><li>ludeon.rimworld</li><li>me.keep</li></activeMods></ModsConfigData>")
    facts = os.path.join(t, "facts.jsonl")
    w(facts, "")
    return ["--profile", prof, "--dump", dump, "--facts", facts]


def main():
    fails = []

    def check(c, m):
        if not c:
            fails.append(m)

    a = setup(tempfile.mkdtemp(prefix="g5a_"), unguarded=False)
    rc, out = run(*a)
    check(rc == 0 and "G5 PASS" in out, "guarded/clean set not PASS:\n" + out)
    a = setup(tempfile.mkdtemp(prefix="g5b_"))
    rc, out = run(*a)
    check(rc == 1 and "C=1" in out and "GONE_Thing" in out, "unguarded Defs ref not caught (or LoadFolders/label leaked):\n" + out)
    a = setup(tempfile.mkdtemp(prefix="g5c_"), unguarded=False, about_dep=True)
    rc, out = run(*a)
    check(rc == 1 and "HARD 1" in out, "About.xml dep on removed mod not HARD")
    a = setup(tempfile.mkdtemp(prefix="g5d_"), unguarded=False, dll=True)
    rc, out = run(*a)
    check(rc == 1 and "E=1" in out, "UTF-16 DLL literal not caught:\n" + out)
    check("ArmorRating_Sharp" not in out, "overridden Core def counted as removed-only")
    if fails:
        print("FAIL selftest_g5_reverse_closure:", *fails, sep="\n  ")
        return 1
    print("PASS selftest_g5_reverse_closure (5 checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
