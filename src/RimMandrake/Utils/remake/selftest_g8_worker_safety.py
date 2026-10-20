#!/usr/bin/env python3
"""Selftest for remake/g8_worker_safety.py on a fake capture + fake mod roots."""
import contextlib
import io
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import g8_worker_safety as G  # noqa: E402


def w(p, s, mode="w"):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, mode).write(s)


def biome(name, pkg, wc, gen=True, imp=True):
    return {"defName": name, "packageId": pkg, "fields": {"workerClass": wc, "generatesNaturally": gen, "implemented": imp}}


def build(t, biomes, mods, profile):
    dump = os.path.join(t, "dump")
    w(os.path.join(dump, "manifest.json"), json.dumps({"mods": [{"packageId": p, "rootDir": r} for p, r in mods.items()]}))
    w(os.path.join(dump, "defs", "BiomeDef.json"), json.dumps({"defs": biomes}))
    prof = os.path.join(t, "profile.xml")
    w(prof, "<ModsConfigData><activeMods>%s</activeMods></ModsConfigData>" % "".join("<li>%s</li>" % p for p in profile))
    return dump, prof


def run(dump, prof):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = G.main(["--profile", prof, "--dump", dump])
    return rc, buf.getvalue()


def main():
    fails = []

    def check(c, m):
        if not c:
            fails.append(m)

    t = tempfile.mkdtemp(prefix="g8_selftest_")
    ours, off = os.path.join(t, "ours"), os.path.join(t, "off")
    w(os.path.join(ours, "1.6", "Assemblies", "Ours.dll"), b"\x00My.Ns\x00BiomeWorker_Mine\x00", "wb")
    w(os.path.join(off, "Assemblies", "Off.dll"), b"\x00Off.Ns\x00BiomeWorker_Off\x00", "wb")
    w(os.path.join(off, "Patches", "p.xml"), "<Patch><Operation><xpath>Defs/BiomeDef[defName='Mine']/workerClass</xpath></Operation></Patch>")
    mods = {"ludeon.rimworld": "", "me.ours": ours, "x.off": off}
    base = [biome("Desert", "ludeon.rimworld", "RimWorld.BiomeWorker_Desert")]
    prof = ["ludeon.rimworld", "me.ours"]
    # all safe
    dump, p = build(os.path.join(t, "a"), base + [biome("Mine", "me.ours", "My.Ns.BiomeWorker_Mine"),
                                                  biome("Lantern", "me.ours", None, gen=False),
                                                  biome("Unimpl", "me.ours", None, imp=False)], mods, prof)
    rc, out = run(dump, p)
    check(rc == 0 and "G8 PASS" in out, "safe set not PASS: " + out)
    check("PATCH-EXPOSED" in out, "off-profile patch on Mine not flagged")
    # worker-less natural biome
    dump, p = build(os.path.join(t, "b"), base + [biome("Bad", "me.ours", None)], mods, prof)
    rc, out = run(dump, p)
    check(rc == 1 and "UNSAFE" in out, "worker-less natural biome not FAIL")
    # worker only in an off-profile DLL
    dump, p = build(os.path.join(t, "c"), base + [biome("Dep", "me.ours", "Off.Ns.BiomeWorker_Off")], mods, prof)
    rc, out = run(dump, p)
    check(rc == 1 and "OFF-profile" in out, "off-profile worker not FAIL")
    # worker found nowhere
    dump, p = build(os.path.join(t, "d"), base + [biome("Ghost", "me.ours", "Gh.BiomeWorker_Ghost")], mods, prof)
    check(run(dump, p)[0] == 2, "unknown worker not UNMEASURED")
    # off-profile biome is not judged
    dump, p = build(os.path.join(t, "e"), base + [biome("Theirs", "x.off", None)], mods, prof)
    check(run(dump, p)[0] == 0, "off-profile biome judged")
    # sanity probe: no Desert => UNMEASURED
    dump, p = build(os.path.join(t, "f"), [biome("Mine", "me.ours", "My.Ns.BiomeWorker_Mine")], mods, prof)
    rc, out = run(dump, p)
    check(rc == 2 and "sanity" in out, "missing sanity probe not UNMEASURED")
    if fails:
        print("FAIL selftest_g8_worker_safety:", *fails, sep="\n  ")
        return 1
    print("PASS selftest_g8_worker_safety (7 checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
