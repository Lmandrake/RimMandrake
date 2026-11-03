#!/usr/bin/env python3
"""Selftest for INHABITED_AUGMENTATION_BUILD_1 criteria 1+2 for spec §8.7 (tar refinery) and §8.8 (gas station):
each archetype is built AND wired to a responder, read from the defs as XML elements, never by text grep.

For each of RSW_TarRefinery / RSW_GasStation (StructureInjectionsSW) it requires:
  1. a TileMutatorDef with that defName exists;
  2. its <extraGenSteps> lists the archetype's GenStep, Inhabited_Cast and RM_InhabitedStock, the two
     Inhabited steps guarded by MayRequire="mandrake.rm.inhabited";
  3. that GenStep is a GenStepDef in the mod, of Class ...GenStep_RimplacePlan, whose <planFile> is the
     expected Templates/<name>.txt and exists on disk under the mod;
  4. the plan's header names the template and carries the content sha of design/Jawa/templates/<name>.lua
     as it stands (the same sha rimplace's luaenv writes), so a stale export or a deleted template fails;
  5. Inhabited_Cast and RM_InhabitedStock are GenStepDefs defined somewhere under src/.

Then it runs the same checker on broken copies (the Inhabited <li>s deleted, a planFile pointed at a missing
file, the GenStep dropped from extraGenSteps, a MayRequire removed, a stale template sha) and requires each to
fail, so a green run proves the checker can see each gap.

Usage: selftest_inhabited_augmentation_wiring.py [--root <repo>]   (default: this file's repo)
"""
import hashlib
import os
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MOD = "src/RimStarWars/StructureInjectionsSW"
INHABITED_MOD = "mandrake.rm.inhabited"
INHABITED_STEPS = ("Inhabited_Cast", "RM_InhabitedStock")
# responder TileMutatorDef -> (GenStepDef, template stem)
ARCHETYPES = {
    "RSW_TarRefinery": ("RSW_GenStep_TarRefinery", "tar_refinery"),
    "RSW_GasStation": ("RSW_GenStep_GasStation", "gas_station"),
}


def _defs(root_dir, tag):
    """{defName: element} for every <tag> under root_dir's .xml files, parsed as XML."""
    out = {}
    for dp, _dn, fns in os.walk(root_dir):
        for fn in fns:
            if not fn.endswith(".xml"):
                continue
            try:
                tree = ET.parse(os.path.join(dp, fn))
            except ET.ParseError as e:
                raise SystemExit(f"XML parse error in {os.path.join(dp, fn)}: {e}")
            for el in tree.getroot().iter(tag):
                name = el.findtext("defName")
                if name:
                    out[name.strip()] = el
    return out


def check(repo):
    """Return a list of failure strings (empty = wired)."""
    fails = []
    mod_dir = os.path.join(repo, MOD)
    muts = _defs(os.path.join(mod_dir, "Defs"), "TileMutatorDef")
    gens = _defs(os.path.join(mod_dir, "Defs"), "GenStepDef")
    all_gens = _defs(os.path.join(repo, "src"), "GenStepDef")
    for step in INHABITED_STEPS:
        if step not in all_gens:
            fails.append(f"GenStepDef {step} is not defined under src/")
    for mut, (gen, stem) in ARCHETYPES.items():
        el = muts.get(mut)
        if el is None:
            fails.append(f"TileMutatorDef {mut} not defined in {MOD}/Defs")
            continue
        lis = el.findall("extraGenSteps/li")
        names = [(li.text or "").strip() for li in lis]
        if gen not in names:
            fails.append(f"{mut}: extraGenSteps lacks its GenStep {gen} (has {names})")
        for step in INHABITED_STEPS:
            hits = [li for li in lis if (li.text or "").strip() == step]
            if not hits:
                fails.append(f"{mut}: extraGenSteps lacks {step}")
            elif any(li.get("MayRequire") != INHABITED_MOD for li in hits):
                fails.append(f"{mut}: {step} not guarded by MayRequire=\"{INHABITED_MOD}\"")
        g = gens.get(gen)
        if g is None:
            fails.append(f"GenStepDef {gen} not defined in {MOD}/Defs")
            continue
        gs = g.find("genStep")
        cls = gs.get("Class", "") if gs is not None else ""
        if not cls.endswith("GenStep_RimplacePlan"):
            fails.append(f"{gen}: genStep Class is {cls!r}, not GenStep_RimplacePlan")
        plan_rel = (gs.findtext("planFile") or "").strip() if gs is not None else ""
        want = f"Templates/{stem}.txt"
        if plan_rel != want:
            fails.append(f"{gen}: planFile is {plan_rel!r}, want {want!r}")
        plan = os.path.join(mod_dir, plan_rel) if plan_rel else ""
        if not plan or not os.path.isfile(plan):
            fails.append(f"{gen}: planFile {plan_rel!r} does not exist under {MOD}")
            continue
        with open(plan, encoding="utf-8") as fh:
            head = "".join(fh.readline() for _ in range(3))
        m = re.search(r"^# template\s+(\S+)\s+\(sha ([0-9a-f]{16})\)", head, re.M)
        if not m:
            fails.append(f"{plan_rel}: no '# template <name> (sha ...)' header")
            continue
        if m.group(1) != stem:
            fails.append(f"{plan_rel}: header names template {m.group(1)!r}, want {stem!r}")
        lua = os.path.join(repo, "design/Jawa/templates", f"{stem}.lua")
        if not os.path.isfile(lua):
            fails.append(f"template source {lua} missing")
            continue
        with open(lua, encoding="utf-8") as fh:
            sha = hashlib.sha256(fh.read().encode("utf-8")).hexdigest()[:16]
        if sha != m.group(2):
            fails.append(f"{plan_rel}: header sha {m.group(2)} != {stem}.lua sha {sha} (stale export)")
    return fails


def _copy_min(repo, dst):
    # Only the small text trees the checker reads (a few MB), never a whole mod or repo copy.
    for rel in (f"{MOD}/Defs", f"{MOD}/Templates", "src/RimMandrake/Inhabited/Defs", "design/Jawa/templates"):
        shutil.copytree(os.path.join(repo, rel), os.path.join(dst, rel))


def _edit(path, old, new):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    if old not in text:
        raise SystemExit(f"negative control cannot apply: {old!r} not in {path}")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text.replace(old, new))


def negative_controls(repo):
    d = os.path.join(repo, MOD, "Defs")
    tm_tar = "TileMutatorDefs_TarRefinery.xml"
    mutants = {
        "Inhabited <li>s deleted (tar)": [
            (f"{MOD}/Defs/{tm_tar}", '<li MayRequire="mandrake.rm.inhabited">Inhabited_Cast</li>', ""),
            (f"{MOD}/Defs/{tm_tar}", '<li MayRequire="mandrake.rm.inhabited">RM_InhabitedStock</li>', "")],
        "planFile -> missing file (gas)": [
            (f"{MOD}/Defs/GenStepDefs_GasStation.xml", "Templates/gas_station.txt", "Templates/no_such_plan.txt")],
        "GenStep dropped from extraGenSteps (gas)": [
            (f"{MOD}/Defs/TileMutatorDefs_GasStation.xml", "<li>RSW_GenStep_GasStation</li>", "")],
        "MayRequire removed (gas stock)": [
            (f"{MOD}/Defs/TileMutatorDefs_GasStation.xml",
             '<li MayRequire="mandrake.rm.inhabited">RM_InhabitedStock</li>', "<li>RM_InhabitedStock</li>")],
        "template edited after export (tar)": [
            ("design/Jawa/templates/tar_refinery.lua", "\n", "\n-- edited\n")],
    }
    assert os.path.isdir(d)
    bad = []
    for label, edits in mutants.items():
        tmp = tempfile.mkdtemp(prefix="inh_wiring_mut_")
        try:
            _copy_min(repo, tmp)
            for rel, old, new in edits:
                _edit(os.path.join(tmp, rel), old, new)
            fails = check(tmp)
            print(f"  negative control [{label}]: {'RED (good)' if fails else 'GREEN (checker blind!)'}"
                  + (f" - {fails[0]}" if fails else ""))
            if not fails:
                bad.append(label)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return bad


def main():
    args = sys.argv[1:]
    repo = DEFAULT_REPO
    if args[:1] == ["--root"] and len(args) >= 2:
        repo = os.path.abspath(args[1])
    fails = check(repo)
    for f in fails:
        print("FAIL", f)
    if fails:
        print(f"selftest_inhabited_augmentation_wiring: FAIL ({len(fails)} problems) on {repo}")
        return 1
    print(f"wiring OK on {repo}: {', '.join(ARCHETYPES)} -> GenStep + {' + '.join(INHABITED_STEPS)}, plans current")
    bad = negative_controls(repo)
    if bad:
        print(f"selftest_inhabited_augmentation_wiring: FAIL (checker blind to: {bad})")
        return 1
    print("selftest_inhabited_augmentation_wiring: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
