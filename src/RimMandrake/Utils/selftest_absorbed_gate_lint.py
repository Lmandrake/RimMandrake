#!/usr/bin/env python3
"""Offline selftest of absorbed_gate_lint.py (LIGHTSABER_ABSORB_COPY_DEPLOYED_BESIDE_DONOR).

    python3 src/RimMandrake/Utils/selftest_absorbed_gate_lint.py

1. Synthetic trees in a temp dir: a donor-keyed FindMod (by display name) and a donor-keyed MayRequire over
   absorbed defNames are RED; the pre-fix RUT_LanternDeepGateKyber.xml shape is RED; a def-keyed
   PatchOperationConditional is GREEN; a FindMod that also lists a non-donor name (our copy's mod) is GREEN;
   a gate over a defName the copy does not own is GREEN; an OWED row is reported not red, and a stale OWED
   row is red; an empty tree is UNMEASURED (exit 2).
2. The repo: exit 0, no hit, and RUT_LanternDeepGateKyber.xml is neither hit nor owed.
"""
import contextlib
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import absorbed_gate_lint as L  # noqa: E402

FAILS = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)


DONOR = "lee.theforce.lightsaber"
DONOR_NAME = "Star Wars : The Force - Lightsaber"
TSV = "packageId\tname\tlifecycle\n%s\t%s\tACTIVE\nsome.other\tOther Mod\tACTIVE\n" % (DONOR, DONOR_NAME)
ABSORBED = """<?xml version="1.0" encoding="utf-8"?>
<!-- Absorbed from lee.theforce.lightsaber (workshop). -->
<Defs>
  <ThingDef><defName>Force_CrystalFormation_Small</defName></ThingDef>
  <ThingDef Name="Force_CrystalBase" Abstract="True"></ThingDef>
</Defs>
"""
REPLACE = """<match Class="PatchOperationReplace">
        <xpath>Defs/ThingDef[defName="%s"]/building/mineableScatterCommonality</xpath>
        <value><mineableScatterCommonality>0</mineableScatterCommonality></value>
      </match>"""
OLD_KYBER_GATE = """<Patch>
  <Operation Class="PatchOperationFindMod">
    <mods><li>%s</li></mods>
    <match Class="PatchOperationSequence"><operations>
      <li Class="PatchOperationReplace">
        <xpath>Defs/ThingDef[defName="Force_CrystalFormation_Small"]/building/mineableScatterCommonality</xpath>
        <value><mineableScatterCommonality>0</mineableScatterCommonality></value>
      </li>
    </operations></match>
  </Operation>
</Patch>
""" % DONOR_NAME
FINDMOD = """<Patch><Operation Class="PatchOperationFindMod"><mods>%s</mods>
      %s
    </Operation></Patch>
"""
MAYREQ = """<Patch><Operation Class="PatchOperationAdd" MayRequire="%s">
  <xpath>Defs/ThingDef[@Name="Force_CrystalBase"]</xpath><value><x/></value></Operation></Patch>
""" % DONOR
CONDITIONAL = """<Patch><Operation Class="PatchOperationConditional">
  <xpath>Defs/ThingDef[defName="Force_CrystalFormation_Small"]/building/mineableScatterCommonality</xpath>
  %s
</Operation></Patch>
""" % (REPLACE % "Force_CrystalFormation_Small")


def tree(tmp, patches, absorbed=True):
    src = os.path.join(tmp, "src")
    os.makedirs(os.path.join(src, "Mod", "Defs"), exist_ok=True)
    os.makedirs(os.path.join(src, "Mod", "Patches"), exist_ok=True)
    if absorbed:
        with open(os.path.join(src, "Mod", "Defs", "Absorbed.xml"), "w", encoding="utf-8") as fh:
            fh.write(ABSORBED)
    for name, body in patches.items():
        with open(os.path.join(src, "Mod", "Patches", name), "w", encoding="utf-8") as fh:
            fh.write(body)
    tsv = os.path.join(tmp, "mods.tsv")
    with open(tsv, "w", encoding="utf-8") as fh:
        fh.write(TSV)
    return src, tsv


def run(patches, owed=None, absorbed=True):
    with tempfile.TemporaryDirectory() as tmp:
        src, tsv = tree(tmp, patches, absorbed)
        return L.scan(src=src, tsv=tsv, allow={}, owed=owed or {}, repo=tmp)


def lis(*names):
    return "".join("<li>%s</li>" % n for n in names)


def synthetic():
    r = run({"old.xml": OLD_KYBER_GATE})
    check(len(r["hits"]) == 1 and r["hits"][0]["ownedDefs"] == ["Force_CrystalFormation_Small"],
          "pre-fix kyber gate (FindMod on donor name over owned def) must be one hit: %r" % r["hits"])
    r = run({"pid.xml": FINDMOD % (lis(DONOR), REPLACE % "Force_CrystalFormation_Small")})
    check(len(r["hits"]) == 1, "FindMod naming the donor packageId must hit: %r" % r["hits"])
    r = run({"mr.xml": MAYREQ})
    check(len(r["hits"]) == 1 and r["hits"][0]["ownedDefs"] == ["Force_CrystalBase"],
          "MayRequire=donor over an owned abstract Name must hit: %r" % r["hits"])
    r = run({"cond.xml": CONDITIONAL})
    check(not r["hits"] and r["patchFiles"] == 1, "def-keyed Conditional must be green: %r" % r)
    r = run({"or.xml": FINDMOD % (lis(DONOR_NAME, "Jawa Armoury Rebalance"), REPLACE % "Force_CrystalFormation_Small")})
    check(not r["hits"], "FindMod that also lists a non-donor name keeps the gate alive, must be green: %r" % r["hits"])
    r = run({"other.xml": FINDMOD % (lis(DONOR_NAME), REPLACE % "Force_SomethingNotOurs")})
    check(not r["hits"], "gate over a def the copy does not own must be green: %r" % r["hits"])
    r = run({"old.xml": OLD_KYBER_GATE}, owed={("src/Mod/Patches/old.xml", DONOR): "ITEM_X"})
    check(not r["hits"] and len(r["owed"]) == 1 and not r["staleOwed"], "OWED row must report, not hit: %r" % r)
    r = run({"cond.xml": CONDITIONAL}, owed={("src/Mod/Patches/cond.xml", DONOR): "ITEM_X"})
    check(r["staleOwed"] == ["src/Mod/Patches/cond.xml [%s]" % DONOR], "stale OWED row must be listed: %r" % r)
    r = run({"old.xml": OLD_KYBER_GATE}, absorbed=False)
    check(r["absorbedDonors"] == 0 and not r["hits"], "no absorbed copy -> no donors: %r" % r)


def repo():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = L.main([])
    out = buf.getvalue()
    check(code == 0, "repo lint must exit 0, got %s:\n%s" % (code, out[-2000:]))
    check("HIT " not in out, "repo lint printed a HIT:\n%s" % out[-2000:])
    check("RUT_LanternDeepGateKyber.xml" not in out, "kyber gate still reported:\n%s" % out[-2000:])
    r = L.scan()
    check(r["absorbedDonors"] >= 1 and r["patchFiles"] >= 100, "repo scan looks blind: %r" % {
        k: r[k] for k in ("absorbedDonors", "absorbedNames", "patchFiles", "donorRows")})
    check(any("Absorbed_TheForceLightsaber" in f for f in L.absorbed_copies().get(DONOR, {}).get("files", [])),
          "lint no longer sees the absorbed lightsaber copy")


def unmeasured():
    with tempfile.TemporaryDirectory() as tmp:
        src, tsv = tree(tmp, {}, absorbed=False)
        with contextlib.redirect_stdout(io.StringIO()):
            code = L.main(["--src", src, "--tsv", tsv])
        check(code == 2, "empty tree must be UNMEASURED (exit 2), got %s" % code)


def main():
    synthetic()
    unmeasured()
    repo()
    for f in FAILS:
        print("FAIL", f)
    print("selftest_absorbed_gate_lint: %s (%d failure(s))" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
