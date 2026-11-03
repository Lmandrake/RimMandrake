#!/usr/bin/env python3
"""Static selftest for the five settlement verbs in RimProperty (SETTLEMENT_VERBS_WAVE_1).

Three checks, each proven able to fail by a planted break on a temp copy:
  1. every .cs under RimProperty/Source (SelfTest/ excluded) is in RM_Property.csproj's explicit
     <Compile> list -- the csproj sets EnableDefaultCompileItems=false, and a missing entry builds
     "0 errors" while shipping the verb dead (Pickpocket, d95d7ec55, did exactly that);
  2. RM_SettlementVerbsProof.cs runs all six cases and every option label it clicks is the label its
     provider really builds (a renamed label would make the live proof read "no option");
  3. the committed DLL carries the proof type's name and its .srchash names the proof source.

    python3 src/RimMandrake/Utils/selftest_settlement_verbs_static.py
"""
from __future__ import annotations

import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(os.path.dirname(HERE), "RimProperty")
SRC = os.path.join(MOD, "Source")
DLL = os.path.join(MOD, "Assemblies", "RimMandrakeProperty.dll")

# verb -> (provider source, literal the provider's label is built from, literal the proof clicks)
LABELS = {
    "salvage": ("SalvageClaim/FloatMenuOptionProvider_PaySalvageClaim.cs",
                '"Pay salvage claim fee (" + fee + " silver) on', '"Pay salvage claim fee (" + fee + " silver) on"'),
    "droid": ("SalvageClaim/FloatMenuOptionProvider_PaySalvageClaim.cs",
              '"Pay salvage claim fee (" + fee + " silver) on', '"Pay salvage claim fee (" + fee + " silver) on"'),
    "commerce": ("WalkableCommerce/FloatMenuOptionProvider_BuyMerchandise.cs",
                 '"Buy " + clickedThing.LabelShort + " (" + price + " silver)"',
                 '"Buy " + ware.LabelShort + " (" + price + " silver)"'),
    "pickpocket": ("Pickpocket/FloatMenuOptionProvider_Pickpocket.cs",
                   '"Pickpocket " + stolenItem.LabelShort + " from "', '"Pickpocket " + loot.LabelShort + " from"'),
    "hire": ("HirePlaceless/FloatMenuOptionProvider_HirePlaceless.cs",
             '"Hire " + targetPawn.LabelShort + " (" + fee + " silver)"',
             '"Hire " + drifter.LabelShort + " (" + fee + " silver)"'),
    "bribe": ("Bribe/FloatMenuOptionProvider_Bribe.cs",
              '"Buy " + targetPawn.LabelShort + " a round (" + fee + " silver)"',
              '"Buy " + drinker.LabelShort + " a round (" + fee + " silver)"'),
}
PROOF = "RM_SettlementVerbsProof.cs"


def compile_gaps(src):
    csproj = open(os.path.join(src, "RM_Property.csproj"), encoding="utf-8").read()
    listed = {m.replace("\\", "/") for m in re.findall(r'<Compile Include="([^"]+)"', csproj)}
    gaps = []
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in ("SelfTest", "bin", "obj")]
        for f in files:
            if f.endswith(".cs"):
                rel = os.path.relpath(os.path.join(root, f), src).replace(os.sep, "/")
                if rel not in listed:
                    gaps.append(rel)
    return gaps


def label_faults(src):
    proof = open(os.path.join(src, PROOF), encoding="utf-8").read()
    faults = []
    for verb, (prov, built, clicked) in LABELS.items():
        if 'case "%s":' % verb not in proof:
            faults.append("proof has no case for " + verb)
        if built not in open(os.path.join(src, prov), encoding="utf-8").read():
            faults.append("%s: provider %s no longer builds %s" % (verb, prov, built))
        if clicked not in proof:
            faults.append("%s: proof does not click %s" % (verb, clicked))
    return faults


def dll_faults(dll):
    faults = []
    if b"RM_SettlementVerbsProof" not in open(dll, "rb").read():   # literal existence, not a census
        faults.append("DLL lacks the RM_SettlementVerbsProof type name")
    sh = dll + ".srchash"
    if not os.path.exists(sh) or PROOF not in open(sh, encoding="utf-8").read():
        faults.append(".srchash does not name " + PROOF)
    return faults


def main():
    bad = []
    g, lf, df = compile_gaps(SRC), label_faults(SRC), dll_faults(DLL)
    for name, got in (("compile list", g), ("labels", lf), ("dll", df)):
        print("%-12s %s" % (name, "ok" if not got else "FAIL " + "; ".join(got)))
        bad += got
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "Source")
        shutil.copytree(SRC, src, ignore=shutil.ignore_patterns("bin", "obj", "SelfTest"))
        # planted: drop the Pickpocket provider from the Compile list
        p = os.path.join(src, "RM_Property.csproj")
        s = open(p, encoding="utf-8").read()
        open(p, "w", encoding="utf-8").write(s.replace('<Compile Include="Pickpocket\\FloatMenuOptionProvider_Pickpocket.cs" />', ""))
        if "Pickpocket/FloatMenuOptionProvider_Pickpocket.cs" not in compile_gaps(src):
            bad.append("planted csproj gap not caught")
        # planted: rename the bribe label in the provider
        p = os.path.join(src, LABELS["bribe"][0])
        s = open(p, encoding="utf-8").read()
        open(p, "w", encoding="utf-8").write(s.replace(" a round (", " a drink ("))
        if not any(f.startswith("bribe: provider") for f in label_faults(src)):
            bad.append("planted label rename not caught")
        # planted: a DLL without the proof type
        fake = os.path.join(tmp, "x.dll")
        open(fake, "wb").write(b"MZ nothing here")
        if not dll_faults(fake):
            bad.append("planted bare DLL not caught")
    print("planted breaks %s" % ("caught" if not any(b.startswith("planted") for b in bad) else "MISSED"))
    print("PASS" if not bad else "FAIL")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
