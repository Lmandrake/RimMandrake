#!/usr/bin/env python3
"""Offline lint of AcousticScanner (mandrake.rm.acousticscanner): defs/patches vs C# via lint_mod_defs.py (its settings are
instance fields, hence instance_settings), plus the data checks the generic lint cannot see:

  as-banding-floor   RM_AcousticScannerSettings.MinBandSize is >= 7 and the settings slider's lower bound is that floor, so a
                     reading can never be exact (the item's "always banded" criterion)
  as-setting-ranges  every slider's range contains the shipped default and the Reset button writes the declared default
  as-kernel-pure     Kernel/*.cs names no Verse / RimWorld / UnityEngine / HarmonyLib (the offline fuzz compiles it alone)
  as-keyed           every "RM_Acoustic_*" key the C# translates (and RM_Acoustic_Tier + each tier name) exists in Languages/English/Keyed,
                     and its {0}.. placeholders match the argument count at the call
  as-payload         every shipped payload patch (any mod's Patches/ naming RM_AcousticPayloadExtension): FindMod name equals this
                     mod's About name, its BiomeDef xpath names a BiomeDef that exists, every target has a label and a matcher,
                     weight > 0 (a zero/negative weight silences the target: the banding drops it), cellSampleStride >= 1,
                     colour channels within 0..1, and an RM_/RUT_/RSW_ thingDef / pawnRace / terrainDef names a def some mod defines

    python3 src/RimMandrake/Utils/lint_acousticscanner_defs.py [--quiet] [--mod-dir D]
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_mod_defs  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


PREFIX = ("RM_", "RUT_", "RSW_")


def defnames(src_root):
    names = {}
    for p in glob.glob(os.path.join(src_root, "*", "*", "Defs", "**", "*.xml"), recursive=True):
        try:
            txt = re.sub(r"<!--.*?-->", "", open(p, encoding="utf-8-sig", errors="replace").read(), flags=re.S)
        except OSError:
            continue
        for m in re.finditer(r"<(\w[\w.]*)(?:\s[^>]*)?>\s*<defName>([^<]+)</defName>", txt):
            names.setdefault(m.group(2).strip(), set()).add(m.group(1).split(".")[-1])
    return names


def keyed_errors(mod):
    errs = []
    keys = {}
    for kp in glob.glob(os.path.join(mod, "Languages", "*", "Keyed", "*.xml")):
        try:
            for el in ET.parse(kp).getroot():
                keys[el.tag] = el.text or ""
        except ET.ParseError as e:
            errs.append("ERROR as-keyed: %s does not parse: %s" % (os.path.basename(kp), e))
    used = {}
    for cs in glob.glob(os.path.join(mod, "Source", "*.cs")):
        txt = re.sub(r"//[^\n]*", "", open(cs, encoding="utf-8-sig").read())
        for m in re.finditer(r'"(RM_Acoustic_\w+)"\s*\.Translate\(', txt):
            depth, i, args, nonempty = 1, m.end(), 0, False
            while i < len(txt) and depth:
                ch = txt[i]
                depth += ch in "([{"
                depth -= ch in ")]}"
                if depth == 1 and ch == ",":
                    args += 1
                nonempty = nonempty or (depth >= 1 and not ch.isspace() and ch != ")")
                i += 1
            used[m.group(1)] = (args + 1) if nonempty else 0
        for k in re.findall(r'"(RM_Acoustic_\w+)"', txt):
            used.setdefault(k, None)
    for tier in ("Faint", "Moderate", "Strong"):
        used["RM_Acoustic_Tier" + tier] = None
    used.pop("RM_Acoustic_Tier", None)
    if len(keys) < 15:
        errs.append("ERROR as-keyed: only %d keys parsed (sanity probe: the shipped file has 25)" % len(keys))
    for k, argc in sorted(used.items()):
        if k not in keys:
            errs.append("ERROR as-keyed: C# translates %s which Languages/English/Keyed does not define" % k)
        elif argc is not None:
            need = max([int(n) + 1 for n in re.findall(r"\{(\d+)\}", keys[k])] or [0])
            if need != argc:
                errs.append("ERROR as-keyed: %s uses %d placeholder(s) but its call passes %d argument(s)" % (k, need, argc))
    return errs


def payload_files(src_root):
    return [p for p in glob.glob(os.path.join(src_root, "*", "*", "Patches", "**", "*.xml"), recursive=True)
            if "RM_AcousticPayloadExtension" in open(p, encoding="utf-8-sig", errors="replace").read()]


def about_name():
    about = os.path.join(REPO, "src", "RimMandrake", "AcousticScanner", "About", "About.xml")
    try:
        return ET.parse(about).getroot().findtext("name")
    except (OSError, ET.ParseError):
        return None


def check_payloads(files, known, name, stats=None):
    """Errors for the given payload patch files. known = defName -> set of def types; name = this mod's About name."""
    errs = []
    if not files:
        errs.append("ERROR as-payload: no shipped payload patch found (the scanner would hear nothing in every biome)")
    for p in files:
        rel = os.path.basename(os.path.dirname(os.path.dirname(p))) + "/" + os.path.basename(p)
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError as e:
            errs.append("ERROR as-payload: %s does not parse: %s" % (rel, e))
            continue
        for op in root.iter("Operation"):
            if op.get("Class") != "PatchOperationFindMod":
                continue
            mods = [li.text.strip() for li in op.findall("mods/li") if li.text]
            if name and name not in mods:
                errs.append("ERROR as-payload: %s FindMod names %s, not this mod's About name %r (the payload would never apply)" % (rel, mods, name))
        for xp in root.iter("xpath"):
            m = re.search(r'BiomeDef\[defName="([^"]+)"\]', xp.text or "")
            if m and "BiomeDef" not in known.get(m.group(1), set()):
                errs.append("ERROR as-payload: %s patches BiomeDef %s which no mod defines" % (rel, m.group(1)))
        for ext in root.iter("li"):
            if ext.get("Class") != "RimMandrake.AcousticScanner.RM_AcousticPayloadExtension":
                continue
            targets = ext.findall("targets/li")
            if stats is not None:
                stats["payloads"] = stats.get("payloads", 0) + 1
                stats["targets"] = stats.get("targets", 0) + len(targets)
            if not targets:
                errs.append("ERROR as-payload: %s has a payload with no targets" % rel)
            for i, t in enumerate(targets):
                tag = "%s target %d (%s)" % (rel, i, (t.findtext("label") or "?").strip())
                if not (t.findtext("label") or "").strip():
                    errs.append("ERROR as-payload: %s has no label" % tag)
                lists = {k: [li.text.strip() for li in t.findall(k + "/li") if li.text] for k in ("thingDefs", "pawnRaces", "terrainDefs")}
                caves = (t.findtext("hiddenCaves") or "").strip().lower() == "true"
                if not any(lists.values()) and not caves:
                    errs.append("ERROR as-payload: %s matches nothing" % tag)
                w = t.findtext("weight")
                if w is not None and float(w) <= 0:
                    errs.append("ERROR as-payload: %s has weight %s (non-positive weight silences the target)" % (tag, w))
                st = t.findtext("cellSampleStride")
                if st is not None and int(st) < 1:
                    errs.append("ERROR as-payload: %s has cellSampleStride %s (< 1)" % (tag, st))
                col = t.findtext("color")
                if col is not None:
                    vals = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", col)]
                    if len(vals) not in (3, 4) or any(v < 0 or v > 1 for v in vals):
                        errs.append("ERROR as-payload: %s colour %s is not 3-4 channels within 0..1" % (tag, col))
                kind = {"thingDefs": "ThingDef", "pawnRaces": "ThingDef", "terrainDefs": "TerrainDef"}
                for k, names in lists.items():
                    for n in names:
                        if n.startswith(PREFIX) and kind[k] not in known.get(n, set()):
                            errs.append("ERROR as-payload: %s %s names %s which no mod defines as a %s" % (tag, k, n, kind[k]))
    return errs


def payload_errors(mod):
    src_root = os.path.join(REPO, "src")
    stats = {}
    errs = check_payloads(payload_files(src_root), defnames(src_root), about_name(), stats)
    print("as-payload: %d payloads, %d targets checked" % (stats.get("payloads", 0), stats.get("targets", 0)))
    if stats.get("payloads", 0) < 50:
        errs.append("ERROR as-payload: only %d payloads found; 62 owned BiomeDefs carried one at 27962f76b (sanity probe)" % stats.get("payloads", 0))
    return errs


def main(argv):
    rc = lint_mod_defs.run("AcousticScanner", argv, instance_settings=True)
    if rc == 2:
        return 2
    mod = os.path.join(REPO, "src", "RimMandrake", "AcousticScanner")
    if "--mod-dir" in argv:
        mod = argv[argv.index("--mod-dir") + 1]
    txt = open(os.path.join(mod, "Source", "RM_AcousticScannerMod.cs"), encoding="utf-8-sig").read()
    errs = []
    if "MinBandSize = RM_AcousticKernel.MinBandSize" not in txt:
        errs.append("ERROR as-banding-floor: the settings' MinBandSize is not an alias of the kernel's floor")
    ktxt = open(os.path.join(mod, "Source", "Kernel", "RM_AcousticKernel.cs"), encoding="utf-8-sig").read()
    m = re.search(r"const int MinBandSize = (\d+);", ktxt)
    if not m or int(m.group(1)) < 7:
        errs.append("ERROR as-banding-floor: MinBandSize is %s, must be a literal >= 7" % (m.group(1) if m else "missing"))
    if not re.search(r"list\.Slider\(BandSizeClamped, MinBandSize, MaxBandSize\)", txt):
        errs.append("ERROR as-banding-floor: the band-size slider is not bounded by MinBandSize..MaxBandSize")
    decl = dict(re.findall(r"public (?:bool|float|int) (\w+) = ([^;]+);", txt))
    for fld, lo, hi in re.findall(r"(\w+) = Mathf\.(?:Round|RoundToInt)\(list\.Slider\(\1, (\d+)f?, (\d+)f?\)\)", txt):
        d = float(decl[fld].rstrip("f")) if fld in decl else None
        if d is None or not (float(lo) <= d <= float(hi)):
            errs.append("ERROR as-setting-ranges: %s default %s outside slider %s..%s" % (fld, d, lo, hi))
    reset = txt[txt.index("SettingReset"):]
    for fld, val in decl.items():
        mm = re.search(r"\b%s = ([^;]+);" % fld, reset)
        if mm and mm.group(1).strip() != val.strip():
            errs.append("ERROR as-setting-ranges: Reset writes %s = %s but the declared default is %s" % (fld, mm.group(1), val))
    for kf in glob.glob(os.path.join(mod, "Source", "Kernel", "*.cs")):
        for lineno, line in enumerate(open(kf, encoding="utf-8-sig").read().splitlines(), 1):
            if re.match(r"\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)\b", line):
                errs.append("ERROR as-kernel-pure: %s:%d `%s` (the kernel must stay engine-free)" % (os.path.basename(kf), lineno, line.strip()))
    errs += keyed_errors(mod)
    errs += payload_errors(mod)
    for e in errs:
        print(e)
    return 1 if (errs or rc) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
