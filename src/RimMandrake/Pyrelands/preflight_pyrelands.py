#!/usr/bin/env python3
"""preflight_pyrelands.py -- refuse a dirty Pyrelands north-star site (trial plan §3.8, §3.2, §3.3).

Three gates (plan §3.8, GPT #1). Each EVALUATES EVERY ROW and reports all failures together
(GPT #20); a run proceeds only when every required row is PASS. "Could not ask" is UNMEASURED
and refuses too -- it is never PASS and never "absent".

  Gate A, session   after the cold load, before the quicktest.   rows 3.8.1-3.8.7, 3.8.12,
                    3.2.1-3.2.5, 3.3, 3.8.dialogs, 3.8.snapshot
  Gate B, site      after every fixture reload.                   rows 3.8.8-3.8.11, 3.8.dialogs
  Gate C, post      inside the outermost finally.                 rows C.*

Each row is {id, name, status, ok, observed, expected, required}; the whole set is written
to the run's evidence JSON. Exit status is non-zero and every failing row id is printed.

Live use (bridge holder only; WSL cannot reach the bridge -- run under Windows python.exe
from the repo root, repo-relative paths):
  python.exe src/RimMandrake/Pyrelands/preflight_pyrelands.py --gate A --evidence <out.json>
  python.exe src/RimMandrake/Pyrelands/preflight_pyrelands.py --gate B --tile <id> --evidence ...
  python.exe src/RimMandrake/Pyrelands/preflight_pyrelands.py --gate C --snapshot <dir> --evidence ...

Bridge result shapes are read from each tool's own ResultDescription (JawaBench source) and
are UNPROVEN live until the first run; a missing key reads UNMEASURED by construction.
Item: PYRELANDS_GREEN_MINIMAL_1 (parent PYRELANDS_NORTHSTAR_TRIAL_1). Dev tooling, never
deployed (*.py is excluded by deploy_custom_mods / biomes_compose).
"""
import argparse
import glob
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)

PASS, FAIL, UNMEASURED = "PASS", "FAIL", "UNMEASURED"

# ------------------------------------------------------------------ the per-biome spec (plan §6.9)
# Immutable manifests (plan §1.3 / §2.3a). selftest_pyrelands_site.py asserts these equal
# validation.py's own manifests, so the suite and the pre-flight can never drift apart.
TIER = "pyrelands"
SEAT = "FOUNDRY"
BIOME = "RM_Pyrelands"
SETTINGS = "RimMandrake.Pyrelands.RM_PyrelandsSettings"
BIOME_KEY = "Pyrelands"                    # RM_BiomesSettings.enabled key
PLANTS = ("RM_FE_Plant_EmberGrass", "RM_FE_Plant_Quickgrass", "RM_FE_Plant_ScorchFruit")
ANIMALS = ("RM_FireHawk", "RM_FurnaceBeast",
           "RSW_Anooba", "RSW_Iriaz", "RSW_Nuna", "RSW_Orray", "RSW_Zeer", "RSW_Dalgo", "RSW_Gizka",
           "RM_Emberscythe", "RM_Sytheclaw", "RM_Barbslinger", "RM_FireWasp", "RM_Flamefang",
           "RM_Ashwallow")
WEATHERS = ("RM_FE_Weather_AshFall", "RM_FE_Weather_Cinderfall", "RM_FE_BlackRain")
GROUND = ("RM_FE_Ground_Sand", "RM_FE_Ground_Gravel", "RM_FE_Ground_Soil", "RM_FE_Ground_SoilRich")
ASH = ("RM_FE_Ash_Trace", "RM_FE_Ash_Light", "RM_FE_Ash_Heavy", "RM_FE_Ash_Deep")
DLCS = ("ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
        "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey")

# Shipped defaults, read off RM_PyrelandsSettings (RM_PyrelandsMod.cs) and
# PyrelandsTuning.WorldHerdDefaultCount = 2. Plan §3.3: all features ON, crossBiome* false,
# ashfallRateMultiplier 1, scorchFruitMapCap 40.
DEFAULTS = {
    "pyrelandsEnabled": True, "fulguriteEnabled": True, "fulguriteChance": 0.35,
    "ashDustingEnabled": True, "ashDustingChance": 0.02,
    "scorchFruitEnabled": True, "scorchFruitChance": 0.05, "scorchFruitMapCap": 40,
    "ashfallAccumulationEnabled": True, "ashfallRateMultiplier": 1.0,
    "biomeGenerationEnabled": True, "wildPlantAllowlistEnabled": True,
    "plantGrowthStagesEnabled": True, "scorchedRuinsEnabled": True,
    "burnLineEnabled": True, "fireHawkSpreadEnabled": True, "furnaceThermalEnabled": True,
    "fireClockEnabled": True, "furnaceWorldMigrationEnabled": True, "furnaceHerdCount": 2,
    "burrowOnFireEnabled": True,
    "crossBiomeEnabled": False, "crossBiomeEverywhere": False, "crossBiomeBiomeList": "",
    "crossBiomeCoverage": 1.0,
}

# (repo DLL, deployed DLL relative to the Mods folder, owning packageId)
DLLS = (
    ("src/RimMandrake/Pyrelands/Assemblies/FireEcologyHook.dll",
     "RimMandrake.Biomes/Biomes/Pyrelands/Assemblies/FireEcologyHook.dll", "mandrake.rm.biomes"),
    ("src/RimMandrake/BiomesShell/Assemblies/RimMandrake.Biomes.dll",
     "RimMandrake.Biomes/Assemblies/RimMandrake.Biomes.dll", "mandrake.rm.biomes"),
    ("src/RimUtinni/PyrelandsMechanics/Assemblies/RimMandrake.Utinni.PyrelandsMechanics.dll",
     "PyrelandsMechanics/Assemblies/RimMandrake.Utinni.PyrelandsMechanics.dll",
     "mandrake.rut.pyrelandsmechanics"),
    ("src/RimUtinni/UtinniPatches/Assemblies/RimMandrake.Utinni.UtinniPatches.dll",
     "UtinniPatches/Assemblies/RimMandrake.Utinni.UtinniPatches.dll", "mandrake.rut.patches"),
)
DEPLOYED_DIRS = ("RimMandrake.Biomes", "UtinniPatches", "PyrelandsMechanics")
DEPLOY_PLANS = (["--compose", "biomes"], ["--mod", "UtinniPatches", "--mod", "PyrelandsMechanics"])

# Log (plan §3.8 item 7): these refuse; the documented ScorchableGround config errors are allowed.
LOG_FATAL = ("CommonalityOfAnimal",)
LOG_ALLOWED = "burnedDef is flammable"
# 6 terrains (RM_FE_Ash_Trace, RM_FE_Ash_Light, RM_FE_Ground_Sand/Gravel/Soil/SoilRich) carry a flammable burnedDef on
# purpose -- the ash ladder (Defs/TerrainDefs/AshLadder.xml header) -- and vanilla logs each once per pass, twice
# per load: 6 x 2 = 12 lines (MEASURED live 2026-10-01). The earlier "4" counted two of them.
LOG_ALLOWED_MAX = 12
BENIGN_WINDOWS = ("EditWindow_Log", "LudeonTK.EditWindow_Log")
IGNORED_WINDOWS = ("Verse.ImmediateWindow", "LudeonTK.Dialog_DevPalette")   # the dev overlay: cannot be closed, blocks nothing        # auto-closed; anything else refuses (plan §3.8)
QUIET_STORYTELLER = "Tutor"                 # UNMEASURED that it fires nothing; gate B also
                                            # requires the incident queue to be empty.
LAT_MAX = 25.0                              # plan §3.5
TEMP_TOL = 3.0                              # plan §3.4 step 7
TEMP_CELLS = 20                             # plan §3.4 step 11 (GPT #5)
MAP_SIZE = 250
LOADAVG_MAX = 10.0


def def_specs():
    """'DefType/defName' pairs for plan §3.2 item 4 (get_defs takes ONE ';'-joined STRING)."""
    return ([("BiomeDef", BIOME)] + [("PawnKindDef", a) for a in ANIMALS]
            + [("ThingDef", p) for p in PLANTS] + [("WeatherDef", w) for w in WEATHERS]
            + [("TerrainDef", t) for t in GROUND + ASH])


# ------------------------------------------------------------------ rows

class Row(object):
    def __init__(self, rid, name, status, observed=None, expected=None, required=True):
        self.id, self.name, self.status = rid, name, status
        self.observed, self.expected, self.required = observed, expected, required

    @property
    def ok(self):
        return self.status == PASS

    def as_dict(self):
        return {"id": self.id, "name": self.name, "status": self.status, "ok": self.ok,
                "observed": self.observed, "expected": self.expected, "required": self.required}

    def __repr__(self):
        return "<%s %s %s>" % (self.id, self.status, self.name)


class Unmeasured(Exception):
    pass


def _call(s, tool, **p):
    """One bridge read. Absent tool, transport error or success:false -> Unmeasured."""
    tools = getattr(s, "tools", None)
    if tools is not None and tool not in tools:
        raise Unmeasured("tool %s not on this bridge (stale companion deploy?)" % tool)
    try:
        r = s.call(tool, **p)
    except Exception as ex:
        raise Unmeasured("%s raised %s: %s" % (tool, type(ex).__name__, ex))
    if not isinstance(r, dict) or r.get("success") is False:
        raise Unmeasured("%s failed: %s" % (tool, str(r)[:200]))
    return r


def _row(rid, name, fn, required=True):
    """Run one check body; it returns (status, observed, expected). Never raises."""
    try:
        st, obs, exp = fn()
    except Unmeasured as ex:
        st, obs, exp = UNMEASURED, str(ex), None
    except Exception as ex:                       # a bug in a check is not a PASS
        st, obs, exp = UNMEASURED, "check raised %s: %s" % (type(ex).__name__, ex), None
    return Row(rid, name, st, obs, exp, required)


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _norm_val(v):
    """Settings values come back as strings; compare by meaning, not spelling."""
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return round(float(v), 6)
    s = "" if v is None else str(v).strip()
    if s.lower() in ("true", "false"):
        return s.lower() == "true"
    try:
        return round(float(s), 6)
    except ValueError:
        return s


# ------------------------------------------------------------------ environment (injectable)

class Env(object):
    """Everything a check reads off the machine. Tests replace any attribute."""

    def __init__(self):
        from game_paths import LOCALLOW, LOCAL_MODS, SAVES
        self.root = ROOT
        self.mods_dir = LOCAL_MODS
        self.config_dir = os.path.join(LOCALLOW, "Config")
        self.player_log = os.path.join(LOCALLOW, "Player.log")
        self.saves_dir = SAVES
        self.python = sys.executable

    def run(self, argv, timeout=600):
        """(returncode, combined output). argv[0] 'py' = this interpreter."""
        argv = [self.python if a == "py" else a for a in argv]
        try:
            p = subprocess.run(argv, cwd=self.root, capture_output=True, text=True,
                               timeout=timeout, encoding="utf-8", errors="replace")
            return p.returncode, (p.stdout or "") + (p.stderr or "")
        except Exception as ex:
            return None, "%s: %s" % (type(ex).__name__, ex)

    def run_wsl(self, argv, timeout=600):
        """Run argv under WSL python3 -- the deploy/rimflow tools are developed and used there (a Windows
        interpreter composes the same files with different line endings and reports drift)."""
        full = ["wsl.exe", "--cd", self.root, "-e"] + argv
        try:
            p = subprocess.run(full, capture_output=True, text=True, timeout=timeout,
                               encoding="utf-8", errors="replace")
            return p.returncode, (p.stdout or "") + (p.stderr or "")
        except Exception as ex:
            return None, "%s: %s" % (type(ex).__name__, ex)

    def manifest(self):
        """The tier's resolved, ordered packageId list -- exactly what --apply writes."""
        import modset_builder as mb
        ordered, missing, banned = mb.resolve_tier(TIER, mb.scan())
        return ordered, missing, banned

    def stamp_status(self, repo_dll):
        """dll_source_stamp recompute at HEAD for one DLL: 'MATCH' or the failure."""
        import dll_source_stamp as ds
        cat = ds.BatchCat(self.root)
        try:
            r = ds.recompute_stamp(cat, "HEAD", repo_dll + ".srchash", self.root)
            return r.status, list(r.detail)
        finally:
            cat.close()

    def loadavg(self):
        try:
            return os.getloadavg()[0]
        except (AttributeError, OSError):
            pass
        rc, out = self.run(["wsl.exe", "-e", "cat", "/proc/loadavg"], timeout=20)
        if rc == 0 and out.split():
            return float(out.split()[0])
        return None

    def log_birth(self):
        """When THIS game process started. Player.log keeps its Windows creation time across relaunches
        (it is truncated in place), so its ctime is the first-ever launch, not this one."""
        try:
            p = subprocess.run(["powershell.exe", "-NoProfile", "-Command",
                                "(Get-Process RimWorldWin64 | Sort-Object StartTime -Descending | "
                                "Select-Object -First 1).StartTime.ToUniversalTime().ToString('o')"],
                               capture_output=True, text=True, timeout=30)
            import datetime
            t = p.stdout.strip()
            if t:
                return datetime.datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp()
        except Exception:
            pass
        st = os.stat(self.player_log)
        # Player.log is recreated at launch; on Windows st_ctime is creation time.
        return getattr(st, "st_birthtime", st.st_ctime)

    def now(self):
        return time.time()


# ------------------------------------------------------------------ gate A (session)

def a1_bridge_lock(env):
    def f():
        rc, out = env.run_wsl(["env", "AGENT_SEAT=" + SEAT, "python3", "src/RimMandrake/rimflow/cli.py", "bridge", "who"], timeout=120)
        if rc is None:
            raise Unmeasured("rimflow bridge who did not run: %s" % out)
        m = re.search(r"bridge held by (\w+)", out)
        held = m.group(1) if m else ("free" if "free" in out.lower() else None)
        if held is None:
            raise Unmeasured("bridge who output not understood: %s" % out.strip()[:160])
        return (PASS if held == SEAT else FAIL), held, SEAT
    return _row("3.8.1", "bridge lock held by this seat", f)


def _newest_deploy_mtime(env):
    newest, path = 0.0, None
    for d in DEPLOYED_DIRS:
        for dp, _dn, fn in os.walk(os.path.join(env.mods_dir, d)):
            for x in fn:
                p = os.path.join(dp, x)
                m = os.path.getmtime(p)
                if m > newest:
                    newest, path = m, p
    return newest, path


def a2_log_after_deploy(env):
    def f():
        if not os.path.isfile(env.player_log):
            raise Unmeasured("no Player.log at %s" % env.player_log)
        newest, path = _newest_deploy_mtime(env)
        if not path:
            raise Unmeasured("no deployed files under %s" % (DEPLOYED_DIRS,))
        born = env.log_birth()
        obs = "Player.log created %s; newest deploy %s (%s)" % (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(born)),
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(newest)), os.path.basename(path))
        return (PASS if born > newest else FAIL), obs, "game launched AFTER the newest deploy"
    return _row("3.8.2", "game started after the newest deploy (plan 3.2.5)", f)


def a3_mod_set(s, env):
    """Exact manifest equality, in order (GPT #2) + excluded absent + 5 DLCs."""
    def f():
        manifest, missing, banned = env.manifest()
        if missing or banned:
            return FAIL, "tier unresolvable: missing %s banned %s" % (missing, banned), "a clean tier"
        r = _call(s, "jawa/mod_inventory")
        rows = r.get("mods")
        if not isinstance(rows, list) or not rows:
            raise Unmeasured("mod_inventory returned no mods[]")
        running = [str(m.get("packageId") or "").lower() for m in
                   sorted(rows, key=lambda m: m.get("loadOrder", 0))]
        problems = []
        dupes = sorted({p for p in running if running.count(p) > 1})
        if dupes:
            problems.append("duplicate ids %s" % dupes)
        extra = [p for p in running if p not in manifest]
        lost = [p for p in manifest if p not in running]
        if extra:
            problems.append("extra active %s" % extra)
        if lost:
            problems.append("manifest mods not running %s" % lost)
        if not extra and not lost and running != list(manifest):
            problems.append("order differs from the tier manifest")
        import modset_builder as mb
        excl = [e for e in mb.TIERS[TIER].get("forbid", ()) if e in running]
        if excl:
            problems.append("excluded mods running %s" % excl)
        nodlc = [d for d in DLCS if d not in running]
        if nodlc:
            problems.append("DLC not active %s" % nodlc)
        obs = "%d running; %s" % (len(running), "; ".join(problems) or "equals manifest")
        return (FAIL if problems else PASS), obs, "%d ids in tier order, all 5 DLCs" % len(manifest)
    return _row("3.8.3", "running mod set == tier manifest", f)


def a_deploy_current(env):
    def f():
        out = []
        bad = False
        for args in DEPLOY_PLANS:
            rc, txt = env.run_wsl(["python3", "src/RimMandrake/Utils/deploy_custom_mods.py"] + args)
            if rc is None:
                raise Unmeasured("deploy plan did not run: %s" % txt)
            # `-` lines are files only in the game folder ("kept"); they are not drift, and are the only
            # reason the tool exits 1 when everything else is in sync
            drift = [ln.strip() for ln in txt.splitlines() if re.match(r"\s+[+~]\s", ln)]
            out.append("%s rc=%s drift=%d%s" % (" ".join(args), rc, len(drift),
                                                (" e.g. %s" % drift[:3]) if drift else ""))
            bad = bad or bool(drift) or (rc not in (0, 1))
        return (FAIL if bad else PASS), "; ".join(out), "0 changes (plan only)"
    return _row("3.2.1", "deploy current: compose biomes + UtinniPatches + PyrelandsMechanics", f)


def a4_srchash(env):
    """Repo stamp == deployed stamp, deployed DLL == repo DLL, stamp == recomputed source (3.2.2)."""
    def f():
        problems, seen = [], []
        for repo_dll, dep_rel, _pid in DLLS:
            r_dll = os.path.join(env.root, repo_dll)
            d_dll = os.path.join(env.mods_dir, dep_rel)
            name = os.path.basename(repo_dll)
            for p in (r_dll, r_dll + ".srchash", d_dll, d_dll + ".srchash"):
                if not os.path.isfile(p):
                    problems.append("%s: missing %s" % (name, p))
            if problems and problems[-1].startswith(name):
                continue
            if _sha(r_dll + ".srchash") != _sha(d_dll + ".srchash"):
                problems.append("%s: deployed .srchash != repo .srchash" % name)
            if _sha(r_dll) != _sha(d_dll):
                problems.append("%s: deployed DLL bytes != repo DLL" % name)
            st, detail = env.stamp_status(repo_dll)
            if st != "MATCH":
                problems.append("%s: stamp %s %s" % (name, st, detail[:2]))
            seen.append(name)
        return (FAIL if problems else PASS), "; ".join(problems) or "4 DLLs agree", \
            "source == repo stamp == deployed stamp, DLL bytes equal"
    return _row("3.8.4", ".srchash agrees across source, repo and deployed", f)


def a_loaded_assemblies(s, env):
    """Runtime truth (3.2.3, GPT #3): the running assembly IS the deployed file, once."""
    def f():
        problems, obs = [], []
        for repo_dll, dep_rel, pid in DLLS:
            asm = os.path.basename(repo_dll)[:-4]
            r = _call(s, "jawa/running_mods", assembly=asm, details=False)
            a = r.get("assembly")
            if not isinstance(a, dict) or "matchCount" not in a:
                raise Unmeasured("running_mods gave no assembly block for %s" % asm)
            matches = a.get("matches") or []
            if a.get("matchCount") != 1 or len(matches) != 1:
                problems.append("%s loaded %s times" % (asm, a.get("matchCount")))
                continue
            m = matches[0]
            claimed = [str(c).lower() for c in (m.get("claimedBy") or [])]
            if claimed != [pid]:
                problems.append("%s claimed by %s, want [%s]" % (asm, claimed, pid))
            d_dll = os.path.join(env.mods_dir, dep_rel)
            if not os.path.isfile(d_dll):
                problems.append("%s: deployed file missing" % asm)
            elif str(m.get("sha256") or "").lower() != _sha(d_dll):
                problems.append("%s: running sha256 != deployed file" % asm)
            obs.append("%s mvid=%s" % (asm, m.get("mvid")))
        return (FAIL if problems else PASS), "; ".join(problems + obs), \
            "each assembly loaded once, by its owning mod, from the deployed bytes"
    return _row("3.2.3", "loaded assemblies are the deployed ones", f)


def def_fingerprint(found_rows):
    """sha256 of sorted (defType/defName, owning ModContentPack packageId) -- plan 3.2 item 4."""
    pairs = sorted("%s/%s|%s" % (d.get("defType"), d.get("defName"), d.get("packageId") or d.get("modName"))
                   for d in found_rows)
    return hashlib.sha256("\n".join(pairs).encode()).hexdigest()


def a5_defs(s, env, out):
    def f():
        spec = ";".join("%s/%s" % p for p in def_specs())
        r = _call(s, "jawa/get_defs", defs=spec, limit=200)
        if "notFound" not in r or "foundCount" not in r:
            raise Unmeasured("get_defs answered without foundCount/notFound")
        nf = r.get("notFound") or []
        rows = [d for d in (r.get("defs") or []) if d.get("found")]
        want = len(def_specs())
        if not nf and r.get("foundCount") != want:
            raise Unmeasured("foundCount %s != %d asked, notFound empty" % (r.get("foundCount"), want))
        fp = def_fingerprint(rows) if rows else None
        out["def_fingerprint"] = fp
        st = FAIL if nf else (PASS if fp else UNMEASURED)
        return st, "found %s/%d notFound %s fingerprint %s" % (
            r.get("foundCount"), want, nf, (fp or "UNMEASURED")[:16]), "all %d defs found" % want
    return _row("3.8.5", "defs as loaded + def fingerprint", f)


def _settings_xml(env, mod_class):
    hits = glob.glob(os.path.join(env.config_dir, "Mod_*_%s.xml" % mod_class))
    return hits[0] if hits else None


def a6_settings(s, env):
    def f():
        bad = {}
        for field, want in sorted(DEFAULTS.items()):
            r = _call(s, "jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field)
            if "value" not in r:
                raise Unmeasured("mod_settings_field get %s: no value" % field)
            if _norm_val(r["value"]) != _norm_val(want):
                bad[field] = r["value"]
        # RM_BiomesSettings.enabled is a Dictionary -- the bridge tool cannot coerce it, so the
        # per-biome toggle is read from the settings file the game loaded (absent = ON).
        p = _settings_xml(env, "RM_BiomesMod")
        biome = "no settings file (defaults: ON)"
        if p:
            txt = open(p, encoding="utf-8", errors="replace").read()
            m = re.search(r"<key>%s</key>\s*<value>(\w+)</value>" % BIOME_KEY, txt)
            if m and m.group(1).lower() == "false":
                bad["RM_BiomesSettings.enabled[%s]" % BIOME_KEY] = "False"
            biome = "file %s: %s" % (os.path.basename(p), m.group(1) if m else "key absent (ON)")
        obs = ("off-default: %s; " % bad if bad else "all %d at shipped defaults; " % len(DEFAULTS)) + biome
        return (FAIL if bad else PASS), obs, "shipped defaults (plan 3.3)"
    return _row("3.3", "Mod Settings at shipped defaults", f)


def scan_log(text):
    fatal = [ln for ln in text.splitlines() if any(n in ln for n in LOG_FATAL)]
    keys = set(ANIMALS) | set(PLANTS)
    xref = [ln for ln in text.splitlines()
            if "Could not resolve cross-reference" in ln and any(k in ln for k in keys)]
    exc = [ln for ln in text.splitlines() if "Exception" in ln and "RimMandrake.Pyrelands" in ln]
    allowed = sum(1 for ln in text.splitlines() if LOG_ALLOWED in ln)
    return fatal, xref, exc, allowed


def a7_log(env):
    def f():
        if not os.path.isfile(env.player_log):
            raise Unmeasured("no Player.log at %s" % env.player_log)
        with open(env.player_log, "rb") as fh:
            text = fh.read().decode("utf-8", "replace")
        fatal, xref, exc, allowed = scan_log(text)
        bad = fatal + xref + exc
        if allowed > LOG_ALLOWED_MAX:
            bad.append("%d '%s' lines (> %d documented)" % (allowed, LOG_ALLOWED, LOG_ALLOWED_MAX))
        obs = "%d refusing line(s)%s; %d allowed burnedDef lines" % (
            len(bad), (": " + " | ".join(l.strip()[:120] for l in bad[:3])) if bad else "", allowed)
        return (FAIL if bad else PASS), obs, "no CommonalityOfAnimal / roster xref / Pyrelands exception"
    return _row("3.8.7", "log since load is clean", f)


def a12_loadavg(env):
    def f():
        la = env.loadavg()
        if la is None:
            raise Unmeasured("loadavg unreadable (no os.getloadavg, wsl.exe cat /proc/loadavg failed)")
        return (PASS if la < LOADAVG_MAX else FAIL), la, "< %s" % LOADAVG_MAX
    return _row("3.8.12", "loadavg < 10", f)


def dialogs_row(s, rid="3.8.dialogs"):
    """Unexpected dialogs are a REFUSAL, not something to close. Benign ones are closed."""
    def f():
        r = _call(s, "jawa/window_list_close", action="list")
        wins = r.get("windows")
        if not isinstance(wins, list):
            raise Unmeasured("window_list_close list gave no windows[]")
        wins = [w for w in wins if w.get("type") not in IGNORED_WINDOWS]
        benign = [w for w in wins if w.get("type") in BENIGN_WINDOWS]
        other = [w for w in wins if w.get("type") not in BENIGN_WINDOWS]
        for w in benign:
            _call(s, "jawa/window_list_close", action="close", typeName=w.get("type"))
        if other:
            shot = None
            try:
                shot = _call(s, "rimworld/take_screenshot").get("path")
            except Unmeasured:
                pass
            return FAIL, "unexpected: %s screenshot %s" % (
                [(w.get("type"), w.get("optionalTitle")) for w in other], shot), "0 non-benign windows"
        again = [w for w in (_call(s, "jawa/window_list_close", action="list").get("windows") or [])
                 if w.get("type") not in IGNORED_WINDOWS]
        if again:
            return FAIL, "still open after closing benign: %s" % [w.get("type") for w in again], "0"
        return PASS, "closed %d benign, 0 open" % len(benign), "0 open dialogs"
    return _row(rid, "no unexpected dialogs", f)


def snapshot_settings(env, dest):
    """Byte-exact copy of every Config/Mod_*.xml (GPT #4). Returns {name: sha256}."""
    os.makedirs(dest, exist_ok=True)
    out = {}
    for p in sorted(glob.glob(os.path.join(env.config_dir, "Mod_*.xml"))):
        shutil.copy2(p, os.path.join(dest, os.path.basename(p)))
        out[os.path.basename(p)] = _sha(p)
    with open(os.path.join(dest, "snapshot.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    return out


def a_snapshot(env, dest, out):
    def f():
        if not dest:
            raise Unmeasured("no --snapshot dir given; Gate C could not restore byte-exact")
        snap = snapshot_settings(env, dest)
        out["settings_snapshot"] = dest
        return PASS, "%d Mod_*.xml snapshotted to %s" % (len(snap), dest), "snapshot written"
    return _row("3.8.snapshot", "Mod_* settings snapshot", f)


def gate_a(s, env, snapshot_dir=None, out=None):
    out = {} if out is None else out
    try:
        out["storyteller_before"] = _call(s, "jawa/weather_get").get("storyteller")
    except Unmeasured:
        out["storyteller_before"] = None
    return [a1_bridge_lock(env), a2_log_after_deploy(env), a3_mod_set(s, env),
            a_deploy_current(env), a4_srchash(env), a_loaded_assemblies(s, env),
            a5_defs(s, env, out), a6_settings(s, env), a7_log(env), a12_loadavg(env),
            dialogs_row(s), a_snapshot(env, snapshot_dir, out)], out


# ------------------------------------------------------------------ gate B (site)

def sample_cells(size, n, seed_tile, avoid=()):
    """Deterministic per tile; avoids a 3-cell edge band and the given cells."""
    rnd = random.Random("pyrelands-site-%s" % seed_tile)
    sx, sz = size
    cells, avoid = [], set(avoid)
    while len(cells) < n:
        c = (rnd.randrange(3, sx - 3), rnd.randrange(3, sz - 3))
        if c not in avoid and c not in cells:
            cells.append(c)
    return cells


def b8_site(s, tile, expect_temp, out):
    def f():
        mi = _call(s, "jawa/map_info")
        problems = []
        size = (mi.get("sizeX"), mi.get("sizeZ"))
        if size != (MAP_SIZE, MAP_SIZE):
            problems.append("size %sx%s" % size)
        if tile is not None and mi.get("tile") != tile:
            problems.append("map tile %s != site tile %s" % (mi.get("tile"), tile))
        if mi.get("mapBiome") != BIOME:
            problems.append("mapBiome %s" % mi.get("mapBiome"))
        lat = mi.get("latitude")
        if lat is None:
            raise Unmeasured("map_info has no latitude")
        if abs(float(lat)) > LAT_MAX:
            problems.append("|lat| %.1f > %s" % (abs(float(lat)), LAT_MAX))
        mu = _call(s, "jawa/world_mutators_get", tiles=str(mi.get("tile")))
        trows = mu.get("tiles") or []
        if not trows:
            raise Unmeasured("world_mutators_get returned no tile row")
        muts = trows[0].get("mutators")
        if muts is None:
            raise Unmeasured("world_mutators_get row has no mutators[]")
        if muts:
            problems.append("mutators %s" % muts)
        if trows[0].get("landmark"):
            problems.append("landmark %s" % trows[0].get("landmark"))
        # temperature on >= 20 unroofed, non-burning cells (GPT #5)
        fires = _call(s, "jawa/list_things", defName="Fire", rect="0,0,%d,%d" % size, limit=5000)
        if fires.get("isCompleteList") is False:
            raise Unmeasured("fire census truncated")
        burning = {(t.get("x"), t.get("z")) for t in fires.get("things") or []}
        temps, fog, tried = [], 0, 0
        for (x, z) in sample_cells(size, TEMP_CELLS * 3, mi.get("tile"), burning):
            if len(temps) >= TEMP_CELLS:
                break
            tried += 1
            roof = _call(s, "jawa/get_roof_batch", rects="%d,%d,1,1" % (x, z))
            if roof.get("cellsRead") != 1:
                raise Unmeasured("get_roof_batch shape not understood: %s" % str(roof)[:120])
            if any(str(r) not in ("None", "", "null") for r in (roof.get("roofs") or [])):
                continue
            ct = _call(s, "jawa/cell_temperature", cell="%d,%d" % (x, z))
            if not ct.get("ok") or ct.get("temperature") is None:
                raise Unmeasured("cell_temperature not ok at %d,%d" % (x, z))
            temps.append(float(ct["temperature"]))
            ci = _call(s, "rimworld/get_cell_info", x=x, z=z)
            if (ci.get("cell") or ci).get("fogged"):
                fog += 1
        if len(temps) < TEMP_CELLS:
            raise Unmeasured("only %d unroofed cells of %d tried" % (len(temps), tried))
        # The tile write itself: RAW field (never the lazy MinTemperature cache, plan 3.4 step 11).
        raw = _call(s, "jawa/world_tile_get", tiles=str(mi.get("tile")))
        traw = ((raw.get("tiles") or [{}])[0]).get("temperature")
        if traw is None:
            raise Unmeasured("world_tile_get row has no raw temperature")
        if abs(float(traw) - expect_temp) > 0.5:
            problems.append("tile raw temperature %s != written %s" % (traw, expect_temp))
        # Uniformity: every sampled cell agrees with the map's own outdoor reading.
        otemp = mi.get("outdoorTempNow")
        if otemp is None:
            raise Unmeasured("map_info has no outdoorTempNow")
        off = [round(t, 1) for t in temps if abs(t - float(otemp)) > TEMP_TOL]
        if off:
            problems.append("%d/%d cells outside outdoor %.1f+-%s: %s" % (
                len(off), len(temps), float(otemp), TEMP_TOL, off[:5]))
        med = sorted(temps)[len(temps) // 2]
        out["site"] = {"tile": mi.get("tile"), "latitude": lat, "longitude": mi.get("longitude"),
                       "temps": temps, "median": med, "tileRawTemperature": traw,
                       "fogged_sampled": fog, "outdoorTempNow": otemp, "season": mi.get("season"),
                       # CALIBRATING (not gating): the seasonal+daily cycle moves cells around the
                       # tile mean; the owner rules a hard band after the first runs.
                       "calibrating_median_minus_target": round(med - expect_temp, 2)}
        if fog:
            problems.append("%d sampled cells fogged" % fog)
        obs = "tile %s lat %s biome %s raw %s cells %.1f..%.1f (median %.1f)%s" % (
            mi.get("tile"), lat, mi.get("mapBiome"), traw, min(temps), max(temps), med,
            ("; " + "; ".join(problems)) if problems else "")
        return (FAIL if problems else PASS), obs, \
            "%s, %dx%d, no mutators/landmark, |lat|<=%s, raw temp %s, %d cells within %s of outdoor, fog off" % (
                BIOME, MAP_SIZE, MAP_SIZE, LAT_MAX, expect_temp, TEMP_CELLS, TEMP_TOL)
    return _row("3.8.8", "site: biome, mutators, size, temperature, latitude", f)


def b9_weather_paused(s):
    def f():
        w = _call(s, "jawa/weather_get")
        clk = _call(s, "jawa/time_clock")
        problems = []
        cur = w.get("weather")
        if isinstance(cur, dict):          # live shape: {"weather": {"current": "Clear", ...}}
            cur = cur.get("current")
        if cur != "Clear":
            problems.append("weather %s" % cur)
        if clk.get("paused") is None:
            raise Unmeasured("time_clock has no paused field")
        if not clk.get("paused"):
            problems.append("game running")
        return (FAIL if problems else PASS), "; ".join(problems) or "Clear, paused", "Clear, paused"
    return _row("3.8.9", "weather Clear (locked by the site script), game paused", f)


def b10_quiet(s):
    def f():
        w = _call(s, "jawa/weather_get")
        q = _call(s, "jawa/incident_queue_clear")
        problems = []
        if w.get("storyteller") is None:
            raise Unmeasured("weather_get has no storyteller field")
        if QUIET_STORYTELLER not in str(w.get("storyteller")):
            problems.append("storyteller %s" % w.get("storyteller"))
        if q.get("clearedCount") is None:
            raise Unmeasured("incident_queue_clear gave no clearedCount")
        if q["clearedCount"]:
            problems.append("incident queue held %s: %s" % (q["clearedCount"], q.get("cleared")))
        return (FAIL if problems else PASS), "; ".join(problems) or "quiet, queue empty", \
            "storyteller %s, queue empty" % QUIET_STORYTELLER
    return _row("3.8.10", "storyteller quiet, incident queue empty", f)


def b11_colonists(s):
    def f():
        r = _call(s, "jawa/list_pawns", limit=500)
        pawns = r.get("pawns")
        if not isinstance(pawns, list):
            raise Unmeasured("list_pawns gave no pawns[]")
        col = [p for p in pawns if "player" in str(p.get("faction", "")).lower()]
        if any("dead" not in p or "downed" not in p for p in col):
            raise Unmeasured("list_pawns rows lack dead/downed")
        alive = [p for p in col if not p.get("dead")]
        down = [p.get("id") for p in alive if p.get("downed")]
        st = PASS if len(alive) >= 3 and not down else FAIL
        return st, "%d living colonists, downed %s" % (len(alive), down), ">= 3 living, none downed"
    return _row("3.8.11", ">= 3 living colonists, none downed", f)


def gate_b(s, env, tile=None, expect_temp=50.0, out=None):
    out = {} if out is None else out
    return [b8_site(s, tile, expect_temp, out), b9_weather_paused(s), b10_quiet(s),
            b11_colonists(s), dialogs_row(s, "3.8.dialogs-B")], out


# ------------------------------------------------------------------ gate C (post-flight)

def restore_settings(env, src):
    snap = json.load(open(os.path.join(src, "snapshot.json"), encoding="utf-8"))
    for name in snap:
        shutil.copy2(os.path.join(src, name), os.path.join(env.config_dir, name))
    now = {os.path.basename(p): _sha(p) for p in glob.glob(os.path.join(env.config_dir, "Mod_*.xml"))}
    differ = [n for n, h in snap.items() if now.get(n) != h]
    extra = sorted(set(now) - set(snap))
    return differ, extra


def gate_c(s, env, snapshot_dir=None, storyteller_before=None, restore_tier=False, out=None):
    out = {} if out is None else out
    rows = []

    def c_settings_files():
        if not snapshot_dir or not os.path.isfile(os.path.join(snapshot_dir, "snapshot.json")):
            raise Unmeasured("no snapshot to restore from (%s)" % snapshot_dir)
        differ, extra = restore_settings(env, snapshot_dir)
        st = FAIL if differ else PASS
        return st, "differ %s; new since snapshot (left in place) %s" % (differ, extra), "byte-exact"
    rows.append(_row("C.settings_files", "Mod_* settings restored byte-exact", c_settings_files))

    def c_settings_defaults():
        bad = {}
        for field, want in sorted(DEFAULTS.items()):
            v = _call(s, "jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field).get("value")
            if _norm_val(v) != _norm_val(want):
                _call(s, "jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field,
                      value=str(want).lower() if isinstance(want, bool) else str(want))
                v2 = _call(s, "jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field).get("value")
                if _norm_val(v2) != _norm_val(want):
                    bad[field] = v2
        return (FAIL if bad else PASS), bad or "all at defaults", "shipped defaults in memory"
    rows.append(_row("C.settings_defaults", "in-memory settings back at defaults", c_settings_defaults))

    def c_weather():
        r = _call(s, "jawa/weather_set", unlock=True)
        return (PASS if r.get("success") else FAIL), str({k: r.get(k) for k in r if k != "success"})[:160], "unlocked"
    rows.append(_row("C.weather_unlocked", "weather unlocked", c_weather))

    def c_storyteller():
        if not storyteller_before:
            raise Unmeasured("Gate A recorded no storyteller to restore")
        _call(s, "jawa/storyteller_swap", storytellerDef=storyteller_before)
        now = _call(s, "jawa/weather_get").get("storyteller")
        return (PASS if storyteller_before in str(now) else FAIL), now, storyteller_before
    rows.append(_row("C.storyteller_restored", "storyteller restored", c_storyteller))

    def c_bridge():
        env.run(["py", "src/RimMandrake/rimflow/cli.py", "bridge", "release"], timeout=120)
        rc, txt = env.run(["py", "src/RimMandrake/rimflow/cli.py", "bridge", "who"], timeout=120)
        held = re.search(r"bridge held by (\w+)", txt or "")
        return (FAIL if held and held.group(1) == SEAT else PASS), (txt or "").strip()[:160], "not held by %s" % SEAT
    rows.append(_row("C.bridge_released", "bridge released", c_bridge))

    def c_tier():
        if not restore_tier:
            raise Unmeasured("tier not restored: close the game, then re-run gate C with --restore-tier")
        rc, txt = env.run(["py", "src/RimMandrake/Utils/modset_builder.py", "--restore"])
        if rc != 0:
            return FAIL, (txt or "").strip()[-200:], "modset_builder --restore rc 0 (game closed)"
        from northstar_driver.preflight import modlist_fingerprint
        import modset_builder as mb
        a, _ = modlist_fingerprint(mb.CONFIG)
        b, _ = modlist_fingerprint(mb.FULL_BACKUP)
        return (PASS if a == b else FAIL), "ModsConfig %s vs FULL.LATEST %s" % (a[:12], b[:12]), "equal"
    rows.append(_row("C.tier_restored", "full mod list restored (game closed)", c_tier))
    return rows, out


# ------------------------------------------------------------------ verdict / CLI

def verdict(rows):
    bad = [r for r in rows if r.required and r.status != PASS]
    return not bad, bad


def report(rows, gate, out, path=None):
    ok, bad = verdict(rows)
    for r in rows:
        print("%-10s %-20s %s  %s" % (r.status, r.id, r.name, str(r.observed)[:160]))
    doc = {"gate": gate, "ok": ok, "refused_rows": [r.id for r in bad],
           "rows": [r.as_dict() for r in rows], "extra": out, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if path:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=1, sort_keys=True, default=str)
    if ok:
        print("GATE %s: CLEAN (%d rows)" % (gate, len(rows)))
    else:
        print("GATE %s: REFUSED -- %s" % (gate, ", ".join("%s(%s)" % (r.id, r.status) for r in bad)))
    return doc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gate", choices=("A", "B", "C"), required=True)
    ap.add_argument("--tile", type=int, help="gate B: the site tile id")
    ap.add_argument("--temp", type=float, default=50.0, help="gate B: target temperature (plan 3.5)")
    ap.add_argument("--snapshot", help="gate A writes / gate C restores the Mod_* snapshot here")
    ap.add_argument("--storyteller-before", help="gate C: storyteller to restore (gate A evidence)")
    ap.add_argument("--restore-tier", action="store_true", help="gate C: game is CLOSED; restore the full list")
    ap.add_argument("--evidence", help="write the rows JSON here")
    a = ap.parse_args(argv)
    from northstar_driver.session import FastSession
    env = Env()
    s = FastSession(strict=False)
    with s:
        if a.gate == "A":
            rows, out = gate_a(s, env, a.snapshot)
        elif a.gate == "B":
            rows, out = gate_b(s, env, a.tile, a.temp)
        else:
            rows, out = gate_c(s, env, a.snapshot, a.storyteller_before, a.restore_tier)
    doc = report(rows, a.gate, out, a.evidence)
    return 0 if doc["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
