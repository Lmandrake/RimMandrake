#!/usr/bin/env python3
"""lint_xmlonly_defs.py - offline def lint for mods that ship XML and no logic (no kernel to fuzz): AssailantSalvage, HostileFlora,
MandrakePatches, Pyrinth, StrandedQuest, Traces. No game, no build.

    python3 src/RimMandrake/Utils/lint_xmlonly_defs.py <Mod> [--mod-dir <dir>] [--src-dir <dir>] [--quiet]

COMMON checks (every mod; each prints a count so a lint that looked at nothing reads UNMEASURED, never clean):
  xo-parse       every Defs/ and Patches/ file parses, and its root is <Defs> / <Patch>
  xo-unique      no two defs of one type share a defName inside the mod; none collides with a same-type def of ANOTHER mod under src/ (a
                 silent last-loaded-wins overwrite)
  xo-parent      a ParentName resolves to a Name= under src/ ; one that does not but sits within two edits of a known Name is a typo
  xo-refs        an element whose whole text is an own-prefix name (RM_/RUT_/RSW_) names a def that exists under src/ (Defs or added by a patch)
  xo-tex         a texPath under this mod's own Textures folder resolves to a file (base, _north/_south/_east/_west, _a.. variants)
  xo-about       packageId is mandrake.<tier>.<folder lowercase> for the mod's tier; a name, a 1.6 supportedVersions and described
                 dependencies; every dependency/loadAfter packageId is a mod under src/ or a known external one
  xo-patch       every PatchOperation: a Class, and its shape (PatchOperationFindMod has mods; Conditional has xpath; Add/Replace/Insert have
                 xpath and value). MayRequire on a top-level <Operation> is INERT in the 1.6 engine (it can reset ModsConfig when the target mod
                 is absent): flagged
PER-MOD contracts follow in MOD_CHECKS.
"""
import glob
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(REPO, "src")
TIERS = {"RimMandrake": "rm", "RimStarWars": "rsw", "RimUtinni": "rut"}
OWN = re.compile(r"^(RM|RUT|RSW)_[A-Za-z0-9_]+$")
EXTERNAL_PKGS_PREFIX = ("ludeon.", "brrainz.", "oskarpotocki.", "vanillaexpanded.", "rimworld.", "mlie.", "unlimitedhugs.", "taranchuk.", "krkr.", "det.", "owlchemist.")
REF_SKIP_TAGS = {"defName", "label", "labelShort", "description", "texPath", "iconPath", "name", "author", "packageId", "displayName", "url",
                 "steamWorkshopUrl", "reportString", "jobString", "labelNoun", "text", "rulePack", "tradeTags", "tags", "buildingTags", "replaceTags", "line",
                 "settingsKey", "storeAs", "inSignal", "outSignal"}


def read(p):
    return open(p, encoding="utf-8-sig").read()


def lev_le2(a, b):
    """True when the edit distance is exactly 1 (a one-character typo; two edits false-positives vanilla names like BaseWeaponTurret vs RNBaseWeaponTurret)."""
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1] == 1


class Ctx:
    def __init__(self, mod, mod_dir, src_dir):
        self.mod, self.mod_dir, self.src_dir = mod, mod_dir, src_dir
        self.errs, self.warns, self.n = [], [], {}
        self.tier = next((t for t in TIERS if os.path.isdir(os.path.join(src_dir, t, mod))), "RimMandrake")

    def E(self, chk, msg):
        self.errs.append(f"ERROR {chk}: {msg}")

    def W(self, chk, msg):
        self.warns.append(f"WARN  {chk}: {msg}")

    def count(self, k, v=1):
        self.n[k] = self.n.get(k, 0) + v


def index_others(ctx):
    """defName set / Names / (tag, defName) pairs of every other mod under src/, plus text added by patches."""
    names, defs, bymod, patch_text, packages = set(), set(), {}, "", {}
    for p in glob.glob(os.path.join(ctx.src_dir, "*", "*", "Defs", "**", "*.xml"), recursive=True):
        parts = os.path.relpath(p, ctx.src_dir).split(os.sep)
        mod = parts[1]
        if mod == ctx.mod:                  # this mod (the real folder, even when linting a selftest copy of it)
            continue
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for d in root:
            if d.get("Name"):
                names.add(d.get("Name"))
            dn = d.findtext("defName")
            if dn:
                defs.add(dn)
                bymod.setdefault((d.tag.split(".")[-1], dn), mod)
    for p in glob.glob(os.path.join(ctx.src_dir, "*", "*", "Patches", "**", "*.xml"), recursive=True):
        if os.path.relpath(p, ctx.src_dir).split(os.sep)[1] == ctx.mod:
            continue
        patch_text += read(p)
    for p in glob.glob(os.path.join(ctx.src_dir, "*", "*", "About", "About.xml")):
        try:
            pid = ET.parse(p).getroot().findtext("packageId")
        except ET.ParseError:
            continue
        if pid:
            packages[pid.lower()] = p
    return names, defs, bymod, patch_text, packages


def common(ctx):
    mod = ctx.mod_dir
    names_o, defs_o, bymod_o, patch_text, packages = index_others(ctx)
    own_files = sorted(glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True))
    patch_files = sorted(glob.glob(os.path.join(mod, "Patches", "**", "*.xml"), recursive=True))
    roots = {}
    own_names, own_defs = set(), {}
    for p in own_files + patch_files:
        rel = os.path.relpath(p, mod)
        ctx.count("files")
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError as e:
            ctx.E("xo-parse", f"{rel}: {e}")
            continue
        want = "Patch" if p in patch_files else "Defs"
        if root.tag != want:
            ctx.E("xo-parse", f"{rel}: root is <{root.tag}>, expected <{want}>")
        roots[p] = root
    for p in own_files:
        root = roots.get(p)
        if root is None:
            continue
        for d in root:
            if d.get("Name"):
                own_names.add(d.get("Name"))
            dn = d.findtext("defName")
            if dn:
                k = (d.tag.split(".")[-1], dn)
                ctx.count("defs")
                if k in own_defs:
                    ctx.E("xo-unique", f"{d.tag} {dn} defined in {os.path.relpath(p, mod)} and {own_defs[k]}")
                own_defs[k] = os.path.relpath(p, mod)
                if k in bymod_o:
                    ctx.E("xo-unique", f"{d.tag} {dn} is also defined by mod {bymod_o[k]} (the later-loaded one silently wins)")
    all_names = own_names | names_o
    own_defnames = {dn for (_, dn) in own_defs}
    # parent + refs + textures
    textures = os.path.join(mod, "Textures")
    for p in own_files:
        root = roots.get(p)
        if root is None:
            continue
        rel = os.path.relpath(p, mod)
        for d in root:
            par = d.get("ParentName")
            if par:
                ctx.count("parents")
                if par not in all_names:
                    near = [n for n in all_names if lev_le2(par, n)]
                    if near:
                        ctx.E("xo-parent", f"{rel}: {d.findtext('defName') or d.tag} ParentName {par!r} is not defined but is near {near[:2]} (typo)")
        for el in root.iter():
            if el.tag in ("texPath", "iconPath") and (el.text or "").strip():
                ctx.count("textures")
                tp = el.text.strip()
                folder = os.path.join(textures, os.path.dirname(tp))
                if os.path.isdir(os.path.join(textures, tp)):          # Graphic_Random / Collection: the texPath is a folder of variants
                    if not any(f.lower().endswith((".png", ".jpg")) for f in os.listdir(os.path.join(textures, tp))):
                        ctx.E("xo-tex", f"{rel}: texPath folder {tp} holds no image")
                elif os.path.isdir(folder):
                    base = os.path.basename(tp)
                    hit = any(re.match(re.escape(base) + r"(_(north|south|east|west|[a-z0-9]+))*\.(png|jpg)$", f, flags=re.I) for f in os.listdir(folder))
                    if not hit and OWN.match(base):
                        msg = f"{rel}: texPath {tp} has a folder in this mod's Textures but no file named {base}[_variant].png in it"
                        if tp.endswith("_Top"):        # a door-top overlay: cosmetic, art is owed (listed in the report), not a discarded def
                            ctx.W("xo-tex", msg + " (door-top overlay art owed)")
                        else:
                            ctx.E("xo-tex", msg)
                continue
            txt = (el.text or "").strip()
            if el.tag not in REF_SKIP_TAGS and OWN.match(txt) and not list(el):
                ctx.count("refs")
                if txt not in own_defnames and txt not in defs_o and f"<defName>{txt}</defName>" not in patch_text and txt not in all_names:
                    ctx.E("xo-refs", f"{rel}: <{el.tag}>{txt}</{el.tag}> names a def that exists nowhere under src/")
    # about
    ap = os.path.join(mod, "About", "About.xml")
    try:
        ab = ET.parse(ap).getroot()
        ctx.count("about")
        pid = (ab.findtext("packageId") or "").strip()
        m = re.match(r"mandrake\.(rm|rsw|rut)\.[a-z0-9_.]+$", pid.lower())
        if not m:
            ctx.E("xo-about", f"packageId {pid!r} is not mandrake.<rm|rsw|rut>.<name>")
        elif m.group(1) != TIERS[ctx.tier]:
            ctx.W("xo-about", f"folder is under {ctx.tier} but packageId {pid!r} is tier {m.group(1)} (a misfiled tier directory; deploy maps by folder)")
        if not (ab.findtext("name") or "").strip():
            ctx.E("xo-about", "no <name>")
        if "1.6" not in [li.text for li in ab.findall("supportedVersions/li")]:
            ctx.E("xo-about", "supportedVersions does not list 1.6")
        for li in ab.findall("modDependencies/li"):
            dep = (li.findtext("packageId") or "").strip().lower()
            if not dep:
                ctx.E("xo-about", "a modDependencies entry has no packageId")
            elif dep not in packages and not dep.startswith(EXTERNAL_PKGS_PREFIX) and dep != "mandrake.rm.biomes":
                ctx.W("xo-about", f"dependency {dep!r} is neither a mod under src/ nor a known external prefix")
        for li in ab.findall("loadAfter/li"):
            la = (li.text or "").strip().lower()
            if la and la not in packages and not la.startswith(EXTERNAL_PKGS_PREFIX) and la != "mandrake.rm.biomes":
                ctx.W("xo-about", f"loadAfter {la!r} is neither a mod under src/ nor a known external prefix")
    except (ET.ParseError, OSError) as e:
        ctx.E("xo-about", f"About.xml unreadable: {e}")
    # patches
    for p in patch_files:
        root = roots.get(p)
        if root is None:
            continue
        rel = os.path.relpath(p, mod)
        for op in root.findall("Operation"):
            ctx.count("ops")
            if op.get("MayRequire"):
                ctx.E("xo-patch", f"{rel}: top-level <Operation MayRequire={op.get('MayRequire')!r}> is inert in the 1.6 engine; guard with PatchOperationFindMod/Conditional")
        for op in root.iter():
            cls = op.get("Class")
            if op.tag == "Operation" and not cls:
                ctx.E("xo-patch", f"{rel}: an <Operation> without Class")
                continue
            if not cls or "PatchOperation" not in cls:
                continue
            short = cls.split(".")[-1]
            s = op.findtext("success")
            if s is not None and s.strip() not in ("Always", "Never", "Invert", "Normal"):
                ctx.E("xo-patch", f"{rel}: success {s.strip()!r} is not Always/Never/Invert/Normal")
            if short == "PatchOperationFindMod" and not [li for li in op.findall("mods/li") if (li.text or "").strip()]:
                ctx.E("xo-patch", f"{rel}: PatchOperationFindMod with no <mods>")
            if short == "PatchOperationConditional" and op.find("xpath") is None:
                ctx.E("xo-patch", f"{rel}: PatchOperationConditional with no <xpath>")
            if short in ("PatchOperationAdd", "PatchOperationReplace", "PatchOperationInsert", "PatchOperationAttributeSet", "PatchOperationAddModExtension", "PatchOperationRemove"):
                if op.find("xpath") is None:
                    ctx.E("xo-patch", f"{rel}: {short} with no <xpath>")
                elif short not in ("PatchOperationAttributeSet", "PatchOperationRemove") and op.find("value") is None:
                    ctx.E("xo-patch", f"{rel}: {short} with no <value>")
    return roots


# ------------------------------------------------------------------ per-mod contracts
def check_traces(ctx, roots):
    v = read(os.path.join(ctx.mod_dir, "validation.py"))
    consts = dict(re.findall(r'^(WALL_SPIKE|FLOOR_SPIKE)\s*=\s*"([^"]+)"', v, flags=re.M))
    defs = {}
    for root in roots.values():
        for d in root.findall("ThingDef"):
            defs[d.findtext("defName")] = d
    for k, dn in consts.items():
        ctx.count("contract")
        if dn not in defs:
            ctx.E("tr-spike", f"validation.py {k} = {dn!r} but the mod defines no such ThingDef")
    for dn, d in defs.items():
        ctx.count("contract")
        f = d.find("filth")
        if d.findtext("thingClass") != "Filth" or d.findtext("category") != "Filth" or f is None:
            ctx.E("tr-filth", f"{dn}: a trace must be thingClass Filth, category Filth, with a <filth> block")
            continue
        for tok in [t.strip() for t in (f.findtext("placementMask") or "").split(",") if t.strip()]:
            if tok not in ("Natural", "Unnatural", "Water"):
                ctx.E("tr-filth", f"{dn}: placementMask token {tok!r} is not a FilthSourceFlags-style mask word")
        if not (f.findtext("placementMask") or "").strip():
            ctx.E("tr-filth", f"{dn}: no placementMask (the filth could never be placed)")
        try:
            if float(f.findtext("cleaningWorkToReduceThickness", "0")) <= 0:
                ctx.E("tr-filth", f"{dn}: cleaningWorkToReduceThickness must be positive")
            if float(f.findtext("disappearsInDays", "0")) < 0:
                ctx.E("tr-filth", f"{dn}: disappearsInDays negative")
        except ValueError:
            ctx.E("tr-filth", f"{dn}: unparsable filth number")
        if f.findtext("rainWashes") not in ("true", "false"):
            ctx.E("tr-filth", f"{dn}: rainWashes missing or not a bool")
        g = d.find("graphicData")
        if g is None or not (g.findtext("texPath") or "").strip() or float(g.findtext("drawSize", "1").split(",")[0].strip("()") or 0) <= 0:
            ctx.E("tr-filth", f"{dn}: graphicData needs a texPath and a positive drawSize")
        if d.findtext("useHitPoints") != "false":
            ctx.E("tr-filth", f"{dn}: a filth must set useHitPoints false")
        m = re.match(r"\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)", g.findtext("color", "") if g is not None else "")
        if m is None or any(int(x) > 255 for x in m.groups()):
            ctx.E("tr-filth", f"{dn}: colour is not a (r,g,b,a) byte quad")


def check_hostileflora(ctx, roots):
    things, kinds = {}, {}
    for root in roots.values():
        for d in root:
            if d.tag == "ThingDef" and d.findtext("race") is not None or (d.tag == "ThingDef" and d.find("race") is not None):
                things[d.findtext("defName")] = d
            if d.tag == "PawnKindDef":
                kinds[d.findtext("defName")] = d
    for dn, d in things.items():
        ctx.count("contract")
        race = d.find("race")
        if race.findtext("manhunterOnDamageChance") not in (None, "0", "0.0"):
            ctx.E("hf-race", f"{dn}: manhunterOnDamageChance is not 0 (the design: a rooted hazard that never turns manhunter)")
        k = kinds.get(dn)
        if k is None:
            ctx.E("hf-race", f"{dn}: no PawnKindDef of the same name (nothing could spawn it)")
            continue
        if k.findtext("race") != dn:
            ctx.E("hf-race", f"{dn}: its PawnKindDef names race {k.findtext('race')!r}")
        ls = k.findall("lifeStages/li")
        ages = race.findall("lifeStageAges/li")
        if ls and ages and len(ls) != len(ages):
            ctx.E("hf-race", f"{dn}: PawnKindDef has {len(ls)} lifeStages for {len(ages)} race lifeStageAges")
        for ex in d.findall("modExtensions/li"):
            c = ex.get("Class", "")
            if c.startswith("RimMandrake.") and ex.get("MayRequire") is None:
                pass


def check_assailant(ctx, roots):
    for root in roots.values():
        for d in root.findall("ThingDef"):
            dn = d.findtext("defName")
            if not dn:
                continue
            ctx.count("contract")
            if not dn.startswith("RUT_"):
                ctx.E("as-def", f"{dn}: an owned RimUtinni prop must carry the RUT_ prefix")
            if d.get("Abstract") == "True":
                continue
            if d.findtext("category") not in ("Building", "Item") and d.get("ParentName") not in ("BuildingBase", "ResourceBase"):
                continue
            for need in ("label", "description"):
                if not (d.findtext(need) or "").strip():
                    ctx.E("as-def", f"{dn}: no <{need}>")
            if d.findtext("category") == "Building" or d.get("ParentName") == "BuildingBase":
                try:
                    if float(d.findtext("statBases/MaxHitPoints", "1")) <= 0:
                        ctx.E("as-def", f"{dn}: MaxHitPoints not positive")
                except ValueError:
                    ctx.E("as-def", f"{dn}: unparsable MaxHitPoints")
            g = d.find("graphicData")
            if g is not None:
                ds = g.findtext("drawSize")
                if ds and any(float(x) <= 0 for x in re.findall(r"[0-9.]+", ds)):
                    ctx.E("as-def", f"{dn}: drawSize {ds} not positive")
            sz = d.findtext("size")
            if sz and any(int(x) <= 0 for x in re.findall(r"\d+", sz)):
                ctx.E("as-def", f"{dn}: size {sz} not positive")
            if d.findtext("selectable") is None and d.findtext("category") == "Building" and d.find("costList") is None and d.find("killedLeavings") is None and d.find("leaveResourcesWhenKilled") is None:
                pass


def check_pyrinth(ctx, roots):
    gen = os.path.join(ctx.mod_dir, "Source", "gen_pyrinth_absorption.py")
    ctx.count("contract")
    if not os.path.exists(gen):
        ctx.E("py-gen", "the generator Source/gen_pyrinth_absorption.py is gone (the absorbed defs have no provenance)")
    shipped = []
    for root in roots.values():
        for d in root:
            dn = d.findtext("defName")
            if dn:
                shipped.append(dn)
    donor_defs = [dn for dn in shipped if dn.startswith("DV_")]
    ctx.count("contract")
    about = read(os.path.join(ctx.mod_dir, "About", "About.xml"))
    if donor_defs and not re.search(r"<incompatibleWith>[^<]*(<li>[^<]*</li>\s*)*<li>det\.epochspyrinth</li>", about, flags=re.I):
        ctx.E("py-ident", f"{len(donor_defs)} defNames are the donor's verbatim (DV_*, e.g. {donor_defs[0]}) but About.xml does not declare incompatibleWith det.epochspyrinth: both active = every def collides")
    # every Absorbed_* patch xpath must target a def this pack or vanilla can supply: at minimum the xpath is well-formed
    for p, root in roots.items():
        for xp in root.iter("xpath"):
            t = (xp.text or "").strip()
            ctx.count("contract")
            if t.count("[") != t.count("]") or t.count("(") != t.count(")") or t.count('"') % 2 or t.count("'") % 2:
                ctx.E("py-xpath", f"{os.path.relpath(p, ctx.mod_dir)}: unbalanced xpath {t!r}")


def check_stranded(ctx, roots):
    v = os.path.join(REPO, "skills", "rimworld-quests", "scripts", "validate_quest.py")
    qdir = os.path.join(ctx.mod_dir, "Defs", "QuestScriptDefs")
    ctx.count("contract")
    if not os.path.exists(v):
        print("LINT UNMEASURED: the quest validator is missing")
        ctx.n["__unmeasured"] = 1
        return
    r = subprocess.run([sys.executable, v, "--dir", qdir, "--quiet"], capture_output=True, text=True)
    out = r.stdout + r.stderr
    if "QuestScriptDef(s) checked" not in out:
        print("LINT UNMEASURED: the quest validator printed no summary: " + out.strip()[:120])
        ctx.n["__unmeasured"] = 1
        return
    for l in out.splitlines():
        if l.startswith("ERROR") or " ERROR" in l[:12]:
            ctx.E("sq-quest", l.strip()[:200])
    # the quest reads history events by defName: each must exist in this mod
    events = {d.findtext("defName") for root in roots.values() for d in root.findall("HistoryEventDef")}
    qtext = read(os.path.join(qdir, "Quest_Stranded.xml"))
    for ev in set(re.findall(r"<(?:goodwillChangeReason|historyDef|historyEvent|goodwillReason)>\s*(RM_\w+)\s*<", qtext)):
        ctx.count("contract")
        if ev not in events:
            ctx.E("sq-quest", f"the quest names history event {ev} which this mod does not define")
    for dn in events:
        ctx.count("contract")
        if dn and dn not in qtext:
            ctx.W("sq-quest", f"history event {dn} is defined but the quest never names it")


def check_mandrakepatches(ctx, roots):
    mod = ctx.mod_dir
    spec = os.path.join(mod, "validation.py")
    ctx.count("contract")
    if not os.path.exists(spec):
        ctx.E("mp-patches", "validation.py (the unguarded-op static check) is missing")
    for p, root in roots.items():
        if os.sep + "Patches" + os.sep not in p:
            continue
        rel = os.path.relpath(p, mod)
        for op in root.findall("Operation"):
            ctx.count("contract")
            cls = (op.get("Class") or "").split(".")[-1]
            if cls not in ("PatchOperationFindMod", "PatchOperationConditional", "PatchOperationSequence"):
                ctx.E("mp-patches", f"{rel}: top-level {cls or '(no class)'} is unguarded: a fix for another mod must be wrapped in FindMod / Conditional so it cannot fail when the target is absent")
    # scripts under Source/ must have the textures they claim to write
    for py in glob.glob(os.path.join(mod, "Source", "*", "*.py")):
        ctx.count("contract")
        try:
            compile(read(py), py, "exec")
        except SyntaxError as e:
            ctx.E("mp-patches", f"{os.path.relpath(py, mod)}: {e}")


MOD_CHECKS = {"Traces": check_traces, "HostileFlora": check_hostileflora, "AssailantSalvage": check_assailant, "Pyrinth": check_pyrinth,
              "StrandedQuest": check_stranded, "MandrakePatches": check_mandrakepatches}
MINIMUMS = {"files": 1, "defs": 0, "about": 1, "contract": 1}


def main(argv):
    if "--mod-dir" in argv and (not argv or argv[0].startswith("-")):
        mod = os.path.basename(os.path.normpath(argv[argv.index("--mod-dir") + 1]))      # selftest copies are named after the mod
    elif not argv or argv[0].startswith("-"):
        print(__doc__)
        return 2
    else:
        mod = argv[0]
    src_dir = argv[argv.index("--src-dir") + 1] if "--src-dir" in argv else SRC
    quiet = "--quiet" in argv
    mod_dir = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else None
    ctx = Ctx(mod, None, src_dir)
    mod_dir = mod_dir or os.path.join(src_dir, ctx.tier, mod)
    ctx.mod_dir = mod_dir
    if not os.path.isdir(mod_dir):
        print(f"LINT UNMEASURED: {mod_dir} is not a directory")
        return 2
    roots = common(ctx)
    fn = MOD_CHECKS.get(mod)
    if fn:
        fn(ctx, roots)
    if ctx.n.get("__unmeasured"):
        return 2
    for k, mn in MINIMUMS.items():
        if ctx.n.get(k, 0) < mn and not ctx.errs:
            print(f"LINT UNMEASURED: xo check {k} saw {ctx.n.get(k, 0)} (< {mn}); a blind lint is not a pass")
            return 2
    if not quiet:
        for l in ctx.warns:
            print(l)
    for l in ctx.errs:
        print(l)
    print(f"{mod.lower()} xml-only lint: " + ", ".join(f"{v} {k}" for k, v in sorted(ctx.n.items())) + f", {len(ctx.errs)} ERROR, {len(ctx.warns)} WARN")
    return 1 if ctx.errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
