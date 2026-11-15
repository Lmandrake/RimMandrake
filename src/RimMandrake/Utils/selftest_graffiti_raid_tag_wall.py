#!/usr/bin/env python3
# selftest-timeout: 300   (one small net8 build through dotnet.exe, ~10-60 s, plus a 244 MB def dump read)
"""T_RAID_TAG_BUILT_WALL_ONLY (RIMMANDRAKE_KEEP_GRAFFITI_RAID_TAGS_OFF_NATURAL_ROCK): a raider's exit tag lands only on a BUILT wall,
never on natural rock (held walk defect #2: a raider tagged a gold vein). Offline, no game.

What it evaluates, and how:
  1. the chain: RaidExitTaggerMod's TryTagNear reaches GraffitiJobUtility.TryFindWallMarkCellNear, and from there (calls by name across
     src/RimMandrake/Graffiti/Source) the def-level wall predicate RAID_WALL_PREDICATE (today IsBuiltWall, via FacesBuiltWall,
     the raid-only gate; IsPaintableWall, which every colonist placer shares, still takes rock faces). If a fix moves the raid route onto a new `static bool X(ThingDef def)`, point
     RAID_WALL_PREDICATE at it: the chain check then proves the raid route really calls it.
  2. the predicate's body, copied verbatim out of the source, compiled (net8, dotnet.exe) against Verse stubs whose members carry the
     game's own semantics (decompiled Assembly-CSharp: Fillage Full iff fillPercent > 0.99, GraphicData.Linked iff linkType != None,
     IsSmoothed iff building.unsmoothedThing != null), and run on def facts read from the offline def dump (refresh.D_DUMP
     defs/ThingDef.json): MineableGold and Granite must be rejected, and so must every other raw natural rock in the dump
     (building.isNaturalRock, not a smoothed wall); the vanilla Wall must be accepted.
  Smoothed stone walls (natural rock the player smoothed) are listed, not judged: whether they count as built is a design call.

Every run also watches itself: a staged fixed copy of the source in /tmp (IsPaintableWall narrowed to linked, full, not natural rock)
must read GREEN, and two planted mutants (accepts any full edifice; rejects the built wall) must read RED. If the watch fails the
instrument is blind and the verdict is UNMEASURED.

    python3 src/RimMandrake/Utils/selftest_graffiti_raid_tag_wall.py

Exit 0 = today's source keeps raid tags off natural rock; 1 = it does not (expected RED until the mod is fixed); 2 = UNMEASURED.
"""
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import graffiti_src_read as S  # noqa: E402
import winbuild  # noqa: E402

SOURCE = os.path.join(REPO, "src", "RimMandrake", "Graffiti", "Source")
RAID_START = "TryTagNear"                      # RaidExitTagger.cs, the per-raider tag
RAID_FINDER = "TryFindWallMarkCellNear"        # GraffitiJobUtility.cs, the raid's wall-cell search
RAID_WALL_PREDICATE = "IsBuiltWall"            # the def-level wall test the raid route reaches (FacesBuiltWall, raid-only; IsPaintableWall still takes rock for colonists)
MUST_REJECT = ["MineableGold", "Granite"]
MUST_ACCEPT = ["Wall"]
FIXED_BODY = "return def.Fillage == FillCategory.Full && def.building?.isNaturalRock != true && def.graphicData?.Linked == true;"
MUTANTS = [
    ("accepts any full edifice", "return def.Fillage == FillCategory.Full;"),
    ("rejects the built wall too", "return def.Fillage == FillCategory.Full && def.building?.isNaturalRock != true && def.graphicData?.Linked == true && def.fillPercent > 1f;"),
]
LINK_TYPES = ["None", "Basic", "CornerFiller", "CornerOverlay", "Transmitter", "TransmitterOverlay", "Asymmetric"]   # Verse.LinkDrawerType

STUBS = r"""
namespace Verse
{
    public enum FillCategory { None, Partial, Full }
    public enum LinkDrawerType : byte { %s }
    public class BuildingProperties { public bool isNaturalRock, isResourceRock; public ThingDef unsmoothedThing, smoothedThing; }
    public class GraphicData { public LinkDrawerType linkType; public bool Linked => linkType != LinkDrawerType.None; }
    public class DesignationCategoryDef { public string defName; }
    public class ThingDef
    {
        public string defName; public float fillPercent; public bool mineable;
        public BuildingProperties building; public GraphicData graphicData; public DesignationCategoryDef designationCategory;
        public FillCategory Fillage => fillPercent < 0.01f ? FillCategory.None : (fillPercent > 0.99f ? FillCategory.Full : FillCategory.Partial);
        public bool IsSmoothed => building?.unsmoothedThing != null;
        public override string ToString() { return defName; }
    }
}
""" % ", ".join(LINK_TYPES)

CSPROJ = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><Nullable>disable</Nullable>
  <ImplicitUsings>disable</ImplicitUsings><AssemblyName>RaidWallProbe</AssemblyName><NoWarn>CS0649;CS0169</NoWarn></PropertyGroup>
</Project>
"""

# ---------------------------------------------------------------- def facts


def dump_facts():
    """{defName: facts} for the named defs and every natural rock in the offline def dump -> (facts, dump path) or (None, why)."""
    import refresh
    path = os.path.join(refresh.D_DUMP, "defs", "ThingDef.json")
    if not os.path.isfile(path):
        return None, "def dump missing: %s (python3 src/RimMandrake/Utils/refresh.py)" % path
    with open(path, "rb") as fh:
        data = fh.read()
    dec = json.JSONDecoder()

    def at(i):
        obj, _ = dec.raw_decode(data[i:i + 4000000].decode("utf-8", "replace"))
        return obj

    def facts(obj):
        f = obj.get("fields") or {}
        b = f.get("building") or None
        g = f.get("graphicData") or None
        return {"defName": obj["defName"], "modName": obj.get("modName"), "fillPercent": f.get("fillPercent") or 0,
                "mineable": bool(f.get("mineable")), "designationCategory": f.get("designationCategory"),
                "building": None if b is None else {k: b.get(k) for k in ("isNaturalRock", "isResourceRock", "unsmoothedThing", "smoothedThing")},
                "linkType": None if g is None else (g.get("linkType") or "None")}

    out = {}
    for name in MUST_REJECT + MUST_ACCEPT:
        i = data.find(b'{"defName":"%s",' % name.encode())
        if i < 0:
            return None, "%s not in the def dump %s" % (name, path)
        out[name] = facts(at(i))
    for m in re.finditer(rb'"isNaturalRock":true', data):
        j = m.start()
        while True:
            j = data.rfind(b'{"defName":"', 0, j)
            if j < 0:
                break
            obj = at(j)
            if obj.get("defType") == "ThingDef" and ((obj.get("fields") or {}).get("building") or {}).get("isNaturalRock") is True:
                out.setdefault(obj["defName"], facts(obj))
                break
    return out, path


def cs_def(d):
    def ref(n):
        return 'new ThingDef { defName = "%s" }' % n if n else "null"
    b = d["building"]
    bs = "null" if b is None else ("new BuildingProperties { isNaturalRock = %s, isResourceRock = %s, unsmoothedThing = %s, smoothedThing = %s }"
                                   % (str(bool(b["isNaturalRock"])).lower(), str(bool(b["isResourceRock"])).lower(), ref(b["unsmoothedThing"]), ref(b["smoothedThing"])))
    gs = "null" if d["linkType"] is None else "new GraphicData { linkType = LinkDrawerType.%s }" % d["linkType"]
    dc = "null" if not d["designationCategory"] else 'new DesignationCategoryDef { defName = "%s" }' % d["designationCategory"]
    return ('new ThingDef { defName = "%s", fillPercent = %sf, mineable = %s, building = %s, graphicData = %s, designationCategory = %s }'
            % (d["defName"], repr(float(d["fillPercent"])), str(d["mineable"]).lower(), bs, gs, dc))

# ---------------------------------------------------------------- source


def predicate_of(root):
    """-> (params, body, chain problem or None) for RAID_WALL_PREDICATE as the raid route reaches it under root."""
    src = S.read_source(root)
    hits = S.find_method(src, RAID_WALL_PREDICATE)
    if len(hits) != 1:
        return None, None, "expected one %s declaration, found %d" % (RAID_WALL_PREDICATE, len(hits))
    _, params, body = hits[0]
    if not re.fullmatch(r"\s*ThingDef\s+def\s*", params):
        return None, None, "%s(%s) is not a `(ThingDef def)` predicate: re-model this test" % (RAID_WALL_PREDICATE, params)
    if RAID_FINDER not in S.reachable(src, RAID_START, depth=2):
        return params, body, "RaidExitTagger's %s no longer calls %s" % (RAID_START, RAID_FINDER)
    if RAID_WALL_PREDICATE not in S.reachable(src, RAID_FINDER):
        return params, body, "the raid finder %s no longer reaches %s" % (RAID_FINDER, RAID_WALL_PREDICATE)
    return params, body, None


def staged_copy(new_body=None, edit=None):
    """A /tmp copy of the Graffiti Source .cs files with the predicate's body replaced; edit = (relative .cs path, old, new) also applied."""
    tmp = tempfile.mkdtemp(prefix="graffiti_raidwall_")
    for d, dirs, files in os.walk(SOURCE):
        dirs[:] = [x for x in dirs if x not in ("SelfTest", "obj", "bin")]
        for f in files:
            if f.endswith(".cs"):
                dst = os.path.join(tmp, os.path.relpath(os.path.join(d, f), SOURCE))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(os.path.join(d, f), dst)
    p = os.path.join(tmp, "GraffitiJobUtility.cs")
    text = open(p, encoding="utf-8-sig").read()
    if new_body is not None:
        m = re.search(r"(static\s+bool\s+%s\s*\(\s*ThingDef\s+def\s*\)\s*\{)(.*?)(\n\s*\})" % RAID_WALL_PREDICATE, text, re.S)
        text = text[:m.start(2)] + "\n            " + new_body + text[m.end(2):]
    open(p, "w", encoding="utf-8").write(text)
    if edit:
        q = os.path.join(tmp, edit[0])
        e = open(q, encoding="utf-8-sig").read()
        if edit[1] not in e:
            shutil.rmtree(tmp, ignore_errors=True)
            print("T_RAID_TAG_BUILT_WALL_ONLY: UNMEASURED - chain mutant anchor %r gone from %s (re-anchor it)" % (edit[1], edit[0]))
            sys.exit(2)
        open(q, "w", encoding="utf-8").write(e.replace(edit[1], edit[2], 1))
    return tmp


def evaluate(variants, defs):
    """Compile every variant's predicate body against the stubs, run it on every def -> ({variant: {defName: bool}}, problem)."""
    stage = os.path.join(winbuild.BUILD_ROOT, "GraffitiRaidWallProbe_%d" % os.getpid())
    shutil.rmtree(stage, ignore_errors=True)
    os.makedirs(stage)
    try:
        cls = []
        for k, (name, body) in enumerate(variants):
            cls.append("    internal static class V%d { internal static bool P(ThingDef def) {\n%s\n    } }" % (k, body))
        rows = ",\n            ".join(cs_def(d) for d in defs.values())
        main = ("using System;\nusing Verse;\n%s\nnamespace Probe\n{\n%s\n    internal static class Program\n    {\n"
                "        private static int Main()\n        {\n            var defs = new ThingDef[] {\n            %s };\n"
                "            Func<ThingDef, bool>[] v = { %s };\n"
                "            for (int i = 0; i < v.Length; i++) foreach (var d in defs) Console.WriteLine(\"R \" + i + \" \" + d.defName + \" \" + (v[i](d) ? 1 : 0));\n"
                "            return 0;\n        }\n    }\n}\n") % (STUBS, "\n".join(cls), rows, ", ".join("V%d.P" % k for k in range(len(variants))))
        open(os.path.join(stage, "Program.cs"), "w").write(main)
        open(os.path.join(stage, "RaidWallProbe.csproj"), "w").write(CSPROJ)
        b = winbuild.run_interop_captured([winbuild.dotnet_exe(), "build", winbuild.win(os.path.join(stage, "RaidWallProbe.csproj")), "-c", "Release",
                                           "--nologo", "-v", "q"], cwd=stage, capture_output=True, text=True, errors="replace", timeout=400)
        if b.returncode:
            errs = [l.strip() for l in (b.stdout or "").splitlines() if "error" in l][:4]
            return None, "probe build failed (%d): %s (the predicate uses a member the stubs do not model? add it with its game semantics)" % (b.returncode, " | ".join(errs))
        r = winbuild.run_interop_captured([winbuild.dotnet_exe(), winbuild.win(os.path.join(stage, "bin", "Release", "net8.0", "RaidWallProbe.dll"))],
                                          cwd=stage, capture_output=True, text=True, errors="replace", timeout=120)
        out = {name: {} for name, _ in variants}
        for line in (r.stdout or "").splitlines():
            p = line.split()
            if len(p) == 4 and p[0] == "R":
                out[variants[int(p[1])][0]][p[2]] = p[3] == "1"
        if r.returncode or any(len(v) != len(defs) for v in out.values()):
            return None, "probe run rc %d, %s of %d answers" % (r.returncode, [len(v) for v in out.values()], len(defs))
        return out, None
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def judge(answers, defs, chain):
    """-> list of reasons this variant is RED (empty = green)."""
    bad = [chain] if chain else []
    for n in MUST_ACCEPT:
        if not answers[n]:
            bad.append("rejects the built %s" % n)
    raw_rock = [n for n, d in defs.items() if (d["building"] or {}).get("isNaturalRock") and not (d["building"] or {}).get("unsmoothedThing")]
    tagged = [n for n in raw_rock if answers[n]]
    if tagged:
        named = [n for n in MUST_REJECT if n in tagged]
        bad.append("a raid tag can land on natural rock: %s%s" % (", ".join(named) or tagged[0],
                                                                 " and %d more raw rock defs" % (len(tagged) - len(named or tagged[:1])) if len(tagged) > 1 else ""))
    return bad


def main(argv):
    defs, path = dump_facts()
    if defs is None:
        print("T_RAID_TAG_BUILT_WALL_ONLY: UNMEASURED - " + path)
        return 2
    rock = [n for n, d in defs.items() if (d["building"] or {}).get("isNaturalRock")]
    smoothed = sorted(n for n in rock if (defs[n]["building"] or {}).get("unsmoothedThing"))
    print("def facts from %s: %d natural rock defs (%d smoothed, not judged), built %s" % (path, len(rock), len(smoothed), MUST_ACCEPT))
    for n in MUST_REJECT + MUST_ACCEPT:
        print("  %s" % json.dumps(defs[n], sort_keys=True))
    p_today, b_today, chain_today = predicate_of(SOURCE)
    if b_today is None:
        print("T_RAID_TAG_BUILT_WALL_ONLY: UNMEASURED - " + chain_today)
        return 2
    fixed = staged_copy(FIXED_BODY)
    unchained = staged_copy(FIXED_BODY, edit=("RaidExitTagger.cs", "GraffitiJobUtility.%s(" % RAID_FINDER, "RaidCellFinder.AnyStandableNear("))
    ungated = staged_copy(FIXED_BODY, edit=("GraffitiJobUtility.cs", " && FacesBuiltWall(c, map);", ";"))
    try:
        _, b_fixed, chain_fixed = predicate_of(fixed)
        _, _, chain_unchained = predicate_of(unchained)
        _, _, chain_ungated = predicate_of(ungated)
    finally:
        for d in (fixed, unchained, ungated):
            shutil.rmtree(d, ignore_errors=True)
    variants = [("today", b_today), ("fixed copy", b_fixed)] + [("mutant: " + n, b) for n, b in MUTANTS]
    ans, why = evaluate(variants, defs)
    if ans is None:
        print("T_RAID_TAG_BUILT_WALL_ONLY: UNMEASURED - " + why)
        return 2
    verdicts = {"today": judge(ans["today"], defs, chain_today), "fixed copy": judge(ans["fixed copy"], defs, chain_fixed),
                "mutant: the raid stops using the walled finder": [chain_unchained] if chain_unchained else [],
                "mutant: the finder drops its built-wall gate": [chain_ungated] if chain_ungated else []}
    for n, _ in MUTANTS:
        verdicts["mutant: " + n] = judge(ans["mutant: " + n], defs, None)
    for k, v in verdicts.items():
        print("  %-52s %s" % (k, "GREEN" if not v else "RED: " + "; ".join(v)))
    blind = []
    if verdicts["fixed copy"]:
        blind.append("the staged fixed copy reads RED")
    blind += ["%s reads GREEN" % k for k in verdicts if k.startswith("mutant") and not verdicts[k]]
    if blind:
        print("T_RAID_TAG_BUILT_WALL_ONLY: UNMEASURED - the watch failed (%s): this instrument is blind" % "; ".join(blind))
        return 2
    if verdicts["today"]:
        print("T_RAID_TAG_BUILT_WALL_ONLY: FAIL - %s (watch: fixed copy green, %d mutants red)" % ("; ".join(verdicts["today"]), len(MUTANTS) + 2))
        return 1
    print("T_RAID_TAG_BUILT_WALL_ONLY: PASS - raid tags reach built walls only (watch: fixed copy green, %d mutants red)" % (len(MUTANTS) + 2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
