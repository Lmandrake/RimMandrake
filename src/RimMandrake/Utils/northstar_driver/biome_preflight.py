#!/usr/bin/env python3
"""biome_preflight.py -- OFFLINE preflight for a biome north-star round on the `biomes_sprint` tier.

BIOME_SPRINT_PROVE_SCRUB_SETS_PACE, BENCH D0 tooling slice (kickoff packet
design/RimMandrake/biome_sprint_kickoff_2026-10-15.md §1 M1/M2; next_sprint_plan_2026-10-15.md §3 exit criterion).
Each biome has a thin wrapper `src/RimMandrake/<Biome>/preflight_<biome>.py`; this module holds the rows.
Nothing here touches the bridge, the game, ModsConfig.xml or the Saves folder: it READS src/, the deployed
Mods/ folders, the gametex cache and the committed manifests.

Rows (status PASS / FAIL / UNMEASURED; "could not ask" is UNMEASURED, never a pass):
  O-TIER      `biomes_sprint` resolves: nothing missing, no guard refusal, mandrake.rm.biomes in the closure
  O-PLAN      northstar_plan.py imports, USE_SUITE is True, EXPECT_MODS names mandrake.rm.biomes, a preflight exists
  O-DEPLOY    the deployed composite Mods/RimMandrake.Biomes/Biomes/<Biome>/{Defs,Patches,Textures} is byte-equal to
              src/RimMandrake/<Biome>/ (a stale composite makes O-TEX a statement about old files)
  O-ROSTER    the biome's roster (its RM_ BiomeDef(s): inline rows + every patch row, biome_census.read_rosters) is
              non-empty; against the acceptance manifest's roster once one is frozen
  O-TEX       M2: every roster def in the tier resolves to a def in a DEPLOYED tier mod and each of its texPaths to a
              loose PNG in a tier mod's Textures or the base-game bundle index. MISSING / NODEF fail; a vanilla-layout
              path only an unindexed bundle could hold is UNRESOLVED (never claimed missing)
  O-SUITE     required_checks.json is current for the biome's validation.py (script_sha), loads, has > 0 script rows
              and the same count a fresh offline probe declares
  O-MANIFEST  the acceptance manifest (design/RimMandrake/sprint_manifests/<Biome>.json, frozen at S0) exists, has
              requirement ids, and its rows equal the suite's; UNMEASURED until S0 freezes it
  O-SITE      a saved site is declared in modcheck/test_site_saves.SITES and built in its registry; UNMEASURED until a
              live round builds it

    python3 src/RimMandrake/<Biome>/preflight_<biome>.py [--json OUT] [--allow-unmeasured] [--rows O-TEX,O-SUITE]
Exit 0 only when every row run is PASS (--allow-unmeasured relaxes UNMEASURED, never FAIL).
"""
import argparse
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(UTILS, "..", "..", ".."))
for _p in (UTILS, os.path.join(UTILS, "modcheck"), os.path.join(UTILS, "art")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

PASS, FAIL, UNMEASURED = "PASS", "FAIL", "UNMEASURED"
TIER = "biomes_sprint"
COMPOSITE_PID = "mandrake.rm.biomes"
COMPARED = ("Defs", "Patches", "Textures")
MANIFEST_DIR = os.path.join(ROOT, "design", "RimMandrake", "sprint_manifests")
ROWS = ("O-TIER", "O-PLAN", "O-DEPLOY", "O-ROSTER", "O-TEX", "O-SUITE", "O-MANIFEST", "O-SITE")
OURS = re.compile(r"^(RM_|RSW_|RUT_|rut_)")
VANILLA_LAYOUT = ("Things/", "Terrain/", "Mote/")


class Row(object):
    def __init__(self, rid, status, evidence, detail=None):
        self.rid, self.status, self.evidence, self.detail = rid, status, evidence, detail or {}

    def as_dict(self):
        return {"row": self.rid, "status": self.status, "evidence": self.evidence, "detail": self.detail}


class Ctx(object):
    """Every external input a row reads, overridable by the selftest."""

    def __init__(self, biome, **kw):
        self.biome = biome
        self.mod_dir = os.path.join(ROOT, "src", "RimMandrake", biome)
        self.installed = None          # modset_builder.scan(); lazily
        self.tier = None               # ordered packageIds; lazily
        self.gametex = "load"
        self.manifest_path = os.path.join(MANIFEST_DIR, biome + ".json")
        for k, v in kw.items():
            setattr(self, k, v)

    def scan(self):
        if self.installed is None:
            import modset_builder as M
            self.installed = M.scan()
        return self.installed

    def tier_list(self):
        if self.tier is None:
            import modset_builder as M
            ordered, missing, refusals = M.resolve_tier(TIER, self.scan())
            self.tier = (ordered, missing, refusals)
        return self.tier

    def composite_dir(self):
        rec = self.scan().get(COMPOSITE_PID)
        return rec and rec["dir"]


# ---------------------------------------------------------------- helpers

def load_folder_roots(mod_dir):
    """Content roots of an installed mod, as the 1.6 loader sees them: LoadFolders.xml <v1.6> when present, else
    the mod root plus 1.6/ and Common/ when they exist."""
    lf = os.path.join(mod_dir, "LoadFolders.xml")
    roots = []
    if os.path.isfile(lf):
        try:
            v = ET.parse(lf).getroot().find("v1.6")
            if v is not None:
                for li in v.findall("li"):
                    rel = (li.text or "").strip().strip("/")
                    roots.append(os.path.join(mod_dir, rel) if rel else mod_dir)
        except ET.ParseError:
            pass
    if not roots:
        roots = [mod_dir] + [os.path.join(mod_dir, s) for s in ("1.6", "Common")
                             if os.path.isdir(os.path.join(mod_dir, s))]
    return [r for r in roots if os.path.isdir(r)]


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def tree_files(base):
    out = {}
    if not os.path.isdir(base):
        return out
    for dp, _dn, fns in os.walk(base):
        for fn in fns:
            if fn.endswith((".py", ".pyc", ".md")):
                continue
            p = os.path.join(dp, fn)
            out[os.path.relpath(p, base).replace(os.sep, "/").lower()] = p
    return out


def biome_defs(biome):
    """RM_ BiomeDefs declared under src/RimMandrake/<biome>/Defs (biome_census.baroque_biomes, keyed by compose key)."""
    import biome_census as B
    return [b[0] for b in B.baroque_biomes() if b[3] == biome]


def derived_roster(biome):
    """[(biomeDef, field, defName, info)] -- inline + patch rows of the biome's RM_ BiomeDefs, read as XML ELEMENTS."""
    import biome_census as B
    R = B.read_rosters()
    out = []
    for bd in biome_defs(biome):
        for (field, name), info in sorted((R.get(bd) or {}).get("entries", {}).items()):
            out.append((bd, field, name, info))
    return out


def read_manifest(path):
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- def index over the DEPLOYED tier

class DefIndex(object):
    """ThingDef / PawnKindDef elements by defName and by Name, from every deployed tier mod's Defs."""

    def __init__(self):
        self.by_def = {"ThingDef": {}, "PawnKindDef": {}}
        self.by_name = {"ThingDef": {}, "PawnKindDef": {}}
        self.origin = {}
        self.kinds_by_race = {}
        self.files = 0

    def add_tree(self, root_el, pid):
        for d in root_el:
            if not isinstance(d.tag, str) or d.tag not in self.by_def:
                continue
            nm = d.get("Name")
            if nm:
                self.by_name[d.tag][nm] = d
            dn = (d.findtext("defName") or "").strip()
            if dn and d.get("Abstract") != "True":
                self.by_def[d.tag][dn] = d            # later mods win, as the loader's last-definition does
                self.origin[(d.tag, dn)] = pid

    def finish(self):
        for dn, d in self.by_def["PawnKindDef"].items():
            race = self.field(d, "PawnKindDef", "race")
            if race is not None and (race.text or "").strip():
                self.kinds_by_race.setdefault(race.text.strip(), []).append(dn)

    def field(self, d, typ, path, depth=0):
        """The element at `path` on d or its ParentName chain (whole-node inheritance, enough for texPath reads)."""
        el = d.find(path)
        if el is not None or depth > 20:
            return el
        par = d.get("ParentName")
        p = self.by_name[typ].get(par) if par else None
        return self.field(p, typ, path, depth + 1) if p is not None else None


def build_def_index(tier_pids, installed, data_dir=None):
    ix = DefIndex()
    for pid in tier_pids:
        rec = installed.get(pid)
        if not rec:
            continue
        for r in load_folder_roots(rec["dir"]):
            ddir = os.path.join(r, "Defs")
            if not os.path.isdir(ddir):
                continue
            for dp, _dn, fns in os.walk(ddir):
                for fn in sorted(fns):
                    if not fn.lower().endswith(".xml"):
                        continue
                    try:
                        ix.add_tree(ET.parse(os.path.join(dp, fn)).getroot(), pid)
                        ix.files += 1
                    except (ET.ParseError, OSError):
                        continue
    ix.finish()
    return ix


def tex_paths_for(ix, name):
    """(kind, [texPath...]) the game draws for a roster defName, or (None, []) when no deployed def has it."""
    out = []
    d = ix.by_def["ThingDef"].get(name)
    if d is None:
        return None, []
    kind = "race" if ix.field(d, "ThingDef", "race") is not None else "thing"
    if kind == "thing":
        for p in ("graphicData/texPath", "plant/leaflessGraphicPath", "plant/immatureGraphicPath"):
            el = ix.field(d, "ThingDef", p)
            if el is not None and (el.text or "").strip():
                out.append(el.text.strip())
    else:
        for kd in ix.kinds_by_race.get(name, []):
            k = ix.by_def["PawnKindDef"][kd]
            ls = ix.field(k, "PawnKindDef", "lifeStages")
            for li in (ls.findall("li") if ls is not None else []):
                el = li.find("bodyGraphicData/texPath")
                if el is not None and (el.text or "").strip():
                    out.append(el.text.strip())
    for el in d.iter():                       # own extension paths (dew variants, fleck overlays, ...)
        if isinstance(el.tag, str) and el.tag != "texPath" and re.search(r"(texpath|graphicpath)$", el.tag, re.I) \
                and (el.text or "").strip() and "/" in el.text:
            out.append(el.text.strip())
    return kind, list(dict.fromkeys(t.replace("\\", "/") for t in out))


def bundle_has(gix, tp):
    """Base-game bundle index (gametex cache): file, Random-folder dir, or the bare-name rung."""
    key = tp.lower().rstrip("/")
    bf = gix["bundle_files"]
    if key in bf:
        return True
    bdirs = gix.setdefault("_bdirs", {k.rsplit("/", 1)[0] for k in bf if "/" in k})
    if key in bdirs:
        return True
    base = key.split("/")[-1]
    names = gix.setdefault("_bnames", [k for k in bf if k.startswith("name:")])
    return ("name:" + base) in bf or any(re.fullmatch(re.escape("name:" + base) + r"_?[a-z]", k) for k in names)


FACINGS = ("", "_south", "_east", "_north", "_west")


def resolve_loose(tp, roots):
    """A loose PNG for tp under any root: the file, a facing, or a Graphic_Random folder holding a PNG.
    🔴 Never placeholder_lint.resolve here: its mask filter drops every file whose stem ends in `m` + facing, so a
    texPath that itself ends `_m` (RSW_Anooba's `Anooba_m`, a male body) read MISSING (MEASURED 2026-10-16)."""
    for r in roots:
        base = os.path.join(str(r), tp)
        if os.path.isdir(base) and any(f.lower().endswith(".png") for f in os.listdir(base)):
            return base
        for suf in FACINGS:
            if os.path.isfile(base + suf + ".png"):
                return base + suf + ".png"
    return None


def load_gametex():
    import texture_gap_lint as T
    return T.load_index()


# ---------------------------------------------------------------- rows

def o_tier(c):
    ordered, missing, refusals = c.tier_list()
    if missing:
        return Row("O-TIER", FAIL, "tier %s incomplete, not installed: %s" % (TIER, missing))
    if refusals:
        return Row("O-TIER", FAIL, "tier %s refused: %s" % (TIER, refusals))
    if COMPOSITE_PID not in ordered:
        return Row("O-TIER", FAIL, "%s not in the %s closure" % (COMPOSITE_PID, TIER))
    return Row("O-TIER", PASS, "%s resolves to %d mods incl. %s" % (TIER, len(ordered), COMPOSITE_PID),
               {"mods": ordered})


def o_plan(c):
    import importlib.util
    p = os.path.join(c.mod_dir, "northstar_plan.py")
    if not os.path.isfile(p):
        return Row("O-PLAN", FAIL, "no %s" % os.path.relpath(p, ROOT))
    if c.mod_dir not in sys.path:
        sys.path.insert(0, c.mod_dir)
    sys.modules.pop("northstar_site", None)   # each biome has its own northstar_site.py
    spec = importlib.util.spec_from_file_location("ns_plan_%s" % c.biome, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    bad = []
    if getattr(m, "USE_SUITE", None) is not True:
        bad.append("USE_SUITE is not True")
    if COMPOSITE_PID not in tuple(getattr(m, "EXPECT_MODS", ()) or ()):
        bad.append("EXPECT_MODS %r lacks %s" % (getattr(m, "EXPECT_MODS", None), COMPOSITE_PID))
    if not callable(getattr(m, "preflight", None)):
        bad.append("no callable preflight")
    if getattr(m, "MOD", c.biome) != c.biome:
        bad.append("MOD %r != %r" % (m.MOD, c.biome))
    return Row("O-PLAN", FAIL if bad else PASS, "; ".join(bad) or "thin USE_SUITE wrapper, EXPECT_MODS %s"
               % (getattr(m, "EXPECT_MODS", None),))


def o_deploy(c):
    comp = c.composite_dir()
    if not comp:
        return Row("O-DEPLOY", UNMEASURED, "%s not installed (no deployed composite)" % COMPOSITE_PID)
    roots = [os.path.relpath(r, comp).replace(os.sep, "/") for r in load_folder_roots(comp)]
    want_root = None
    for r in roots:
        if r.rstrip("/").split("/")[-1] == c.biome:
            want_root = r
    if want_root is None:
        return Row("O-DEPLOY", FAIL, "LoadFolders.xml of the composite has no root for %s: %s" % (c.biome, roots))
    drift = {"missing": [], "extra": [], "differ": []}
    n = 0
    for sub in COMPARED:
        src = tree_files(os.path.join(c.mod_dir, sub))
        dep = tree_files(os.path.join(comp, want_root, sub))
        n += len(src)
        for k in sorted(set(src) - set(dep)):
            drift["missing"].append("%s/%s" % (sub, k))
        for k in sorted(set(dep) - set(src)):
            drift["extra"].append("%s/%s" % (sub, k))
        for k in sorted(set(src) & set(dep)):
            if os.path.getsize(src[k]) != os.path.getsize(dep[k]) or _sha(src[k]) != _sha(dep[k]):
                drift["differ"].append("%s/%s" % (sub, k))
    tot = sum(len(v) for v in drift.values())
    if tot:
        return Row("O-DEPLOY", FAIL, "composite is stale for %s: %d missing, %d extra, %d differ of %d src files "
                   "(redeploy: deploy_custom_mods.py --compose biomes --apply, by the seat holding the game window)"
                   % (c.biome, len(drift["missing"]), len(drift["extra"]), len(drift["differ"]), n),
                   {k: v[:40] for k, v in drift.items()})
    return Row("O-DEPLOY", PASS, "%d src files byte-equal in the deployed composite (%s)" % (n, want_root))


def roster_for(c):
    """(rows, source) -- the frozen manifest's roster when one exists, else the derived roster."""
    man = read_manifest(c.manifest_path)
    derived = derived_roster(c.biome)
    if man and man.get("roster"):
        return [(r.get("biome"), r.get("field"), r.get("def"), {"may_require": r.get("may_require"),
                 "patch_mod": r.get("patch_mod")}) for r in man["roster"]], "manifest", derived
    return derived, "derived", derived


def o_roster(c):
    rows, source, derived = roster_for(c)
    if not derived:
        return Row("O-ROSTER", FAIL, "no roster rows for %s's BiomeDef(s) %s" % (c.biome, biome_defs(c.biome)))
    by = {}
    for _bd, field, _n, _i in derived:
        by[field] = by.get(field, 0) + 1
    if source == "manifest":
        a = {(r[0], r[1], r[2]) for r in rows}
        b = {(r[0], r[1], r[2]) for r in derived}
        if a != b:
            return Row("O-ROSTER", FAIL, "manifest roster != src roster: %d only in manifest, %d only in src"
                       % (len(a - b), len(b - a)), {"only_manifest": sorted(a - b)[:30], "only_src": sorted(b - a)[:30]})
    return Row("O-ROSTER", PASS, "%d roster rows (%s) from %s" % (len(derived), by, source))


def classify_rows(rows, tier_pids, ix, roots, gix):
    """[(def, class, detail)] for each roster row. Pure over its inputs (the selftest drives it on a fixture).
    Classes: OK, BASEGAME (a ludeon.* def's vanilla-layout path the bundle index lacks: Core's art is not fully
    indexed, and the base game ships its own defs' art), SKIP (row not loaded on the tier), UNRESOLVED, MISSING, NODEF."""
    tier = set(p.lower() for p in tier_pids)
    out = []
    for _bd, field, name, info in rows:
        mr = (info or {}).get("may_require")
        pm = (info or {}).get("patch_mod")
        mrs = [x.strip().lower() for x in (mr or "").split(",") if x.strip()]
        if (mrs and not all(x in tier for x in mrs)) or (pm and pm.lower() not in tier):
            out.append((name, "SKIP", "not loaded on %s (MayRequire %s, patch mod %s)" % (TIER, mr, pm)))
            continue
        kind, tps = tex_paths_for(ix, name)
        if kind is None:
            out.append((name, "NODEF", "%s row names a def no deployed tier mod defines" % field))
            continue
        if not tps:
            out.append((name, "MISSING", "%s def has no texPath (inherited or own)" % kind))
            continue
        worst = "OK"
        notes = []
        for tp in tps:
            if resolve_loose(tp, roots):
                continue
            if gix is not None and bundle_has(gix, tp):
                continue
            if tp.startswith(VANILLA_LAYOUT) and ix.origin.get(("ThingDef", name), "").startswith("ludeon."):
                notes.append("%s (base-game def, base-game art: trusted)" % tp)
                worst = worst if worst in ("MISSING", "UNRESOLVED") else "BASEGAME"
            elif tp.startswith(VANILLA_LAYOUT) and not OURS.match(name) and gix is None:
                notes.append("%s (vanilla layout, no gametex index)" % tp)
                worst = worst if worst == "MISSING" else "UNRESOLVED"
            elif tp.startswith(VANILLA_LAYOUT) and gix is None:
                notes.append("%s (no gametex index to check the base bundle)" % tp)
                worst = worst if worst == "MISSING" else "UNRESOLVED"
            else:
                notes.append(tp)
                worst = "MISSING"
        out.append((name, worst, "; ".join(notes) or "%d texPath(s) resolve" % len(tps)))
    return out


def o_tex(c):
    ordered, missing, refusals = c.tier_list()
    if missing or refusals:
        return Row("O-TEX", UNMEASURED, "tier does not resolve (O-TIER)")
    installed = c.scan()
    rows, source, _d = roster_for(c)
    ix = build_def_index(ordered, installed)
    if ix.files == 0:
        return Row("O-TEX", UNMEASURED, "no deployed Defs read for %s" % TIER)
    roots = []
    from pathlib import Path
    for pid in ordered:
        rec = installed.get(pid)
        for r in (load_folder_roots(rec["dir"]) if rec else []):
            t = os.path.join(r, "Textures")
            if os.path.isdir(t):
                roots.append(Path(t))
    gix = load_gametex() if c.gametex == "load" else c.gametex
    res = classify_rows(rows, ordered, ix, roots, gix)
    # SANITY PROBE: a vanilla race the index must see (the instrument is looking)
    probe_kind, probe_tps = tex_paths_for(ix, "Muffalo")
    if probe_kind != "race" or not probe_tps:
        return Row("O-TEX", UNMEASURED, "sanity probe: Muffalo resolves to %s %s -- the def index is blind"
                   % (probe_kind, probe_tps))
    cnt = {}
    for _n, cl, _dt in res:
        cnt[cl] = cnt.get(cl, 0) + 1
    bad = [(n, cl, dt) for n, cl, dt in res if cl in ("MISSING", "NODEF")]
    unres = [(n, cl, dt) for n, cl, dt in res if cl == "UNRESOLVED"]
    detail = {"counts": cnt, "bad": bad, "unresolved": unres, "source": source, "defFiles": ix.files,
              "textureRoots": len(roots)}
    if bad:
        return Row("O-TEX", FAIL, "%d roster def(s) MISSING/NODEF on the deployed tier: %s"
                   % (len(bad), ", ".join("%s=%s" % (n, cl) for n, cl, _ in bad[:12])), detail)
    if unres:
        return Row("O-TEX", UNMEASURED, "%d roster def(s) UNRESOLVED (base bundle not indexed): %s"
                   % (len(unres), [n for n, _, _ in unres][:12]), detail)
    return Row("O-TEX", PASS, "%s; %s roster" % (cnt, source), detail)


def suite_rows(mod_dir):
    import required_checks as RC
    return ["%s/%s" % (ch, comp) for ch, comp, _t, _s in RC.script_checks(mod_dir)]


def o_suite(c):
    import required_checks as RC
    with open(RC.MANIFEST, encoding="utf-8") as f:
        man = json.load(f)
    m = (man.get("mods") or {}).get(c.biome)
    if not m:
        return Row("O-SUITE", FAIL, "required_checks.json has no %s entry" % c.biome)
    if m.get("load_error"):
        return Row("O-SUITE", FAIL, "validation.py load error: %s" % m["load_error"])
    cur = RC._sha(os.path.join(ROOT, m["script"]))
    committed = [x["id"] for x in m.get("checks", []) if x.get("source") == "script_check"]
    if cur != m.get("script_sha"):
        return Row("O-SUITE", FAIL, "required_checks.json is STALE for %s (script_sha %s, current %s): rerun "
                   "src/RimMandrake/Utils/modcheck/required_checks.py" % (c.biome, m.get("script_sha"), cur))
    probed = suite_rows(c.mod_dir)
    if not committed:
        return Row("O-SUITE", FAIL, "0 script rows (an EMPTY run would pass vacuously)")
    if sorted(probed) != sorted(committed):
        return Row("O-SUITE", FAIL, "probe declares %d rows, manifest %d" % (len(probed), len(committed)),
                   {"only_probe": sorted(set(probed) - set(committed))[:20],
                    "only_committed": sorted(set(committed) - set(probed))[:20]})
    return Row("O-SUITE", PASS, "%d script rows, required_checks current (ns_state %s)" % (len(committed),
               m.get("ns_state")), {"rows": len(committed)})


def o_manifest(c):
    man = read_manifest(c.manifest_path)
    rel = os.path.relpath(c.manifest_path, ROOT)
    if man is None:
        return Row("O-MANIFEST", UNMEASURED, "no acceptance manifest at %s (frozen at S0)" % rel)
    bad = []
    if not man.get("requirement_ids"):
        bad.append("no requirement_ids")
    rows = man.get("rows") or []
    if not rows:
        bad.append("no rows")
    else:
        probed = set(suite_rows(c.mod_dir))
        extra = set(rows) - probed
        if extra:
            bad.append("%d manifest row(s) the suite does not declare: %s" % (len(extra), sorted(extra)[:8]))
    inf = set(man.get("inferred_ok") or ())
    if inf - set(rows):
        bad.append("inferred_ok names rows not in the manifest: %s" % sorted(inf - set(rows))[:8])
    with open(c.manifest_path, "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()[:16]
    return Row("O-MANIFEST", FAIL if bad else PASS, "; ".join(bad) or "%d rows, %d requirement ids, hash %s"
               % (len(rows), len(man["requirement_ids"]), h), {"hash": h})


def o_site(c):
    import test_site_saves as TS
    key = c.biome.lower()
    if key not in TS.SITES:
        return Row("O-SITE", UNMEASURED, "no saved site declared for %s in test_site_saves.SITES" % c.biome)
    reg = TS.read_registry().get(key)
    if not reg:
        return Row("O-SITE", UNMEASURED, "site '%s' declared, not built yet (live round: test_site_saves.py build %s)"
                   % (key, key))
    want = TS.SITES[key].get("biome")
    if want and reg.get("biome") != want:
        return Row("O-SITE", FAIL, "registered site is biome %s, want %s" % (reg.get("biome"), want))
    # the registry is written once before the reload (loadVerified absent) and again after it: only True is built
    if reg.get("loadVerified") is False:
        return Row("O-SITE", FAIL, "site %s saved but its reload read back unclean (loadVerified False)" % reg.get("save"))
    if reg.get("loadVerified") is not True:
        return Row("O-SITE", UNMEASURED, "site %s saved, reload never read back (no loadVerified)" % reg.get("save"))
    return Row("O-SITE", PASS, "site %s built %s at %s" % (reg.get("save"), reg.get("builtUtc"), reg.get("head")))


FUNCS = {"O-TIER": o_tier, "O-PLAN": o_plan, "O-DEPLOY": o_deploy, "O-ROSTER": o_roster, "O-TEX": o_tex,
         "O-SUITE": o_suite, "O-MANIFEST": o_manifest, "O-SITE": o_site}


def run(c, rows=ROWS):
    out = []
    for rid in rows:
        try:
            out.append(FUNCS[rid](c))
        except Exception as ex:   # noqa: BLE001 - a row that raised could not ask
            out.append(Row(rid, UNMEASURED, "%s raised %s: %s" % (rid, type(ex).__name__, str(ex)[:300])))
    return out


def main(biome, argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", help="write the receipt here")
    ap.add_argument("--allow-unmeasured", action="store_true")
    ap.add_argument("--rows", help="comma list of row ids (default all)")
    a = ap.parse_args(argv)
    rows = tuple(a.rows.split(",")) if a.rows else ROWS
    res = run(Ctx(biome), rows)
    for r in res:
        print("%-10s %-10s %s" % (r.rid, r.status, r.evidence))
    ok = all(r.status == PASS or (a.allow_unmeasured and r.status == UNMEASURED) for r in res)
    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump({"biome": biome, "tier": TIER, "ok": ok, "rows": [r.as_dict() for r in res]}, f, indent=1)
    print("%s preflight (offline): %s" % (biome, "READY" if ok else "NOT READY"))
    return 0 if ok else 1
