#!/usr/bin/env python3
"""Proof of STILLSAND_CONTENT_LIVE_PROOF_1: the built Stillsand cast, its four placeholder swaps, the hourbloom wiring
and the zuurrik on blood.

Offline clauses (read the repo at HEAD and its git history; no game):
  O1  The four placeholders are swapped: no PNG in Textures/.../RM_Zuurrik/, .../RM_Vaalok/, RM_DuneCrawler.png or
      RM_GlassPearl.png is a blob that git ever held at a path OUTSIDE that subject (another species' art, or the old
      SWBestiary egg/trophy icon). Byte history, not today's hashes: the Vaalok south was copied from an Aurrok
      south that has since been redrawn, so a compare against today's Aurrok misses it.
  O2  Every texPath/iconPath in Stillsand's Defs and Patches resolves: to a PNG in Stillsand/Textures, or to a texPath
      a vanilla/DLC def uses (the only route to magenta is a path that resolves nowhere).
  O3  The hourbloom is some bloom's bloomPlant (spec 4), and the zuurrik's readable signs are in the source: the wake
      Messages.Message in TryWake and a FleckMaker.ThrowDustPuff on every member in TryBury (spec 2; neither can be
      state-read through the bridge).

Live clauses (validation.py chains site, fauna, flora, zuurrik, log on a Stillsand quicktest map):
  A1  The atlas: fauna.fauna_spawns, flora.flora_spawns and log.log_clean PASS, on a running list that holds neither
      sarg.alphaanimals nor mandrake.rsw.swbestiary (jawa/running_mods).
  A2  The zuurrik: below-threshold dormant, wakes on blood, strips blood, spares the unwounded, toggle off wakes
      nothing, re-buries when quiet: every one PASS.

    python3 src/RimMandrake/Stillsand/prove_stillsand_content.py --clause O1|O2|O3|A1|A2
    python3 src/RimMandrake/Stillsand/prove_stillsand_content.py --offline        # O1-O3 together
    python3 src/RimMandrake/Stillsand/prove_stillsand_content.py --selftest       # offline, against the fake

Exit 0 = the clause holds, 1 = it does not, 2 = UNMEASURED (no game, no git, a tool missing).
A1 and A2 share one run, cached 30 min beside validation.py's hash (agent storage scratch/prove_stillsand_content.json).
"""
import argparse
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
for _p in (UTILS, os.path.join(UTILS, "modcheck")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

TEX = os.path.join(HERE, "Textures")
REL_TEX = os.path.relpath(TEX, ROOT).replace(os.sep, "/")
SUBJECTS = {   # subject -> repo-relative path prefixes that are ITS OWN art
    "RM_Zuurrik": (REL_TEX + "/Things/Pawn/Animal/RM_Zuurrik/",),
    "RM_Vaalok": (REL_TEX + "/Things/Pawn/Animal/RM_Vaalok/",),
    "RM_DuneCrawler": (REL_TEX + "/Things/Item/Resource/RM_DuneCrawler.png",),
    "RM_GlassPearl": (REL_TEX + "/Things/Item/Resource/RM_GlassPearl.png",),
}
DONOR_MODS = ("sarg.alphaanimals", "mandrake.rsw.swbestiary")
VANILLA_DATA = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"
CHAINS = ("site", "fauna", "flora", "zuurrik", "log")
ATLAS = ("fauna.fauna_spawns", "flora.flora_spawns", "log.log_clean")
ZUURRIK = ("zuurrik.zuurrik_below_threshold_dormant", "zuurrik.zuurrik_wakes_on_blood", "zuurrik.zuurrik_strips_blood",
           "zuurrik.zuurrik_spares_unwounded", "zuurrik.zuurrik_toggle_off_no_wake",
           "zuurrik.zuurrik_reburies_when_quiet")
CACHE_S = 30 * 60


# ----------------------------------------------------------------------------- offline

def _git(*args):
    return subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True, text=True, check=True).stdout


def blob_paths(raw):
    """{blob sha: {paths}} over `git log --raw` lines: every path a blob was ever ADDED or MODIFIED at."""
    out = {}
    for line in raw.splitlines():
        if not line.startswith(":"):
            continue
        meta, _, path = line.partition("\t")
        parts = meta.split()
        if len(parts) < 5 or parts[4][:1] not in "AM":
            continue
        out.setdefault(parts[3], set()).add(path)
    return out


def own_files(subject):
    """{repo-relative path: blob sha at HEAD} for the subject's own PNGs."""
    out = {}
    for pre in SUBJECTS[subject]:
        files = _git("ls-files", "-s", "--", pre).splitlines()
        for f in files:
            meta, _, path = f.partition("\t")
            if path.endswith(".png"):
                out[path] = meta.split()[1]
    return out


def judge_o1(history, owned):
    """(code, line). history = blob_paths(); owned = {subject: {path: blob}}. A blob also held outside the
    subject's own prefixes is another thing's art."""
    if not history:
        return 2, "UNMEASURED: git history of src/*.png is empty"
    worn, missing = [], [s for s, f in owned.items() if not f]
    for s, files in sorted(owned.items()):
        for path, blob in sorted(files.items()):
            elsewhere = sorted(p for p in history.get(blob, ()) if not p.startswith(SUBJECTS[s]))
            if elsewhere:
                worn.append("%s is %s's blob %s" % (path.rsplit("/", 1)[-1], elsewhere[0], blob[:8]))
    if missing:
        return 1, "O1 fails: no PNG committed for %s" % missing
    if worn:
        return 1, "O1 fails: %d placeholder(s) still wear other art: %s" % (len(worn), "; ".join(worn))
    return 0, "O1 holds: %d own PNGs across %d subjects, none ever held at another path" % (
        sum(len(f) for f in owned.values()), len(owned))


def clause_o1():
    try:
        hist = blob_paths(_git("log", "--format=", "--raw", "--no-abbrev", "--no-renames", "--", "src/*.png"))
        owned = dict((s, own_files(s)) for s in SUBJECTS)
    except (OSError, subprocess.CalledProcessError) as ex:
        return 2, "UNMEASURED: git unreadable: %s" % ex
    return judge_o1(hist, owned)


PATH_TAGS = re.compile(r"<(texPath|iconPath|\w+TexPath)>\s*([^<]+?)\s*<")


def stillsand_tex_paths():
    out = set()
    for f in glob.glob(os.path.join(HERE, "Defs", "**", "*.xml"), recursive=True) + \
            glob.glob(os.path.join(HERE, "Patches", "**", "*.xml"), recursive=True):
        for m in PATH_TAGS.finditer(open(f, encoding="utf-8").read()):
            out.add((m.group(2), os.path.basename(f)))
    return out


def resolves_own(p):
    base = os.path.join(TEX, p)
    return bool(os.path.isfile(base + ".png") or glob.glob(glob.escape(base) + "_*.png")
                or (os.path.isdir(base) and glob.glob(os.path.join(glob.escape(base), "*.png"))))


def vanilla_tex_paths():
    if not os.path.isdir(VANILLA_DATA):
        return None
    out = set()
    for f in glob.glob(os.path.join(VANILLA_DATA, "*", "Defs", "**", "*.xml"), recursive=True):
        try:
            out.update(m.group(2) for m in PATH_TAGS.finditer(open(f, encoding="utf-8", errors="replace").read()))
        except OSError:
            pass
    return out


def judge_o2(paths, own, vanilla):
    if len(paths) < 40:
        return 2, "UNMEASURED: only %d texPaths parsed from Stillsand (expected 80+): the parser is blind" % len(paths)
    if vanilla is not None and len(vanilla) < 500:
        return 2, "UNMEASURED: only %d vanilla texPaths read from %s" % (len(vanilla), VANILLA_DATA)
    rest = sorted((p, f) for p, f in paths if not own(p))
    if vanilla is None and rest:
        return 2, "UNMEASURED: vanilla Data unreadable and %d paths are not ours: %s" % (len(rest), rest[:4])
    dead = [(p, f) for p, f in rest if p not in vanilla]
    if dead:
        return 1, "O2 fails: %d texPath(s) resolve nowhere (magenta): %s" % (len(dead), dead)
    return 0, "O2 holds: %d texPaths, %d own, %d vanilla (%s)" % (
        len(paths), len(paths) - len(rest), len(rest), ", ".join(p for p, _ in rest))


def clause_o2():
    return judge_o2(stillsand_tex_paths(), resolves_own, vanilla_tex_paths())


def _method(src, name):
    m = re.search(r"\bvoid %s\(\)\s*\{" % name, src)
    if not m:
        return None
    depth, i = 1, m.end()
    while depth and i < len(src):
        depth += {"{": 1, "}": -1}.get(src[i], 0)
        i += 1
    return src[m.end():i]


def judge_o3(bloom_owners, cs):
    bad = []
    if not bloom_owners:
        bad.append("no def or patch names RM_Hourbloom as a <bloomPlant> (spec 4)")
    wake, bury = _method(cs, "TryWake"), _method(cs, "TryBury")
    if wake is None or "Messages.Message(" not in wake:
        bad.append("TryWake sends no Messages.Message (the wake is unsigned)")
    if bury is None or not re.search(r"ThrowDustPuff\(p\.Position[^;]*\);\s*p\.Destroy\(\)", bury):
        bad.append("TryBury does not throw a dust puff at each member as it is removed")
    if bad:
        return 1, "O3 fails: " + "; ".join(bad)
    return 0, "O3 holds: RM_Hourbloom is bloomPlant in %s; wake message and per-member dust puff in source" % (
        ", ".join(sorted(bloom_owners)))


def clause_o3():
    owners = set()
    for f in glob.glob(os.path.join(HERE, "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        if any((e.text or "").strip() == "RM_Hourbloom" for e in root.iter("bloomPlant")):
            owners.add(os.path.basename(f))
    try:
        cs = open(os.path.join(HERE, "Source", "RM_MapComponent_Zuurrik.cs"), encoding="utf-8").read()
    except OSError as ex:
        return 2, "UNMEASURED: %s" % ex
    return judge_o3(owners, cs)


# ----------------------------------------------------------------------------- live

def _load_validation():
    import importlib.util
    spec = importlib.util.spec_from_file_location("stillsand_validation", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    return v


def run_chains(V, session, anchor):
    """{component key: [verdict, detail]} for CHAINS, plus "running_mods": [packageIds] or None."""
    from suite import TestContext
    V._STATE.clear()
    out = {}
    try:
        r = session.call("jawa/running_mods", details=False) or {}
        out["running_mods"] = [str(p).lower() for p in (r.get("packageIds") or [])] or None
    except Exception:
        out["running_mods"] = None
    for name, fn in V.suite.chains:
        if name not in CHAINS:
            continue
        t = TestContext(session, anchor=anchor)
        try:
            fn(t)
        except Exception as ex:
            out[name + ".<CRASH>"] = ["CRASH", "%s: %s" % (type(ex).__name__, ex)]
            continue
        for c in t.components:
            out["%s.%s" % (name, c.name)] = [c.verdict, c.detail]
    return out


def judge_live(res, clause):
    crash = dict((k, v[1]) for k, v in res.items() if k.endswith(".<CRASH>"))
    if crash:
        return 2, "UNMEASURED: a chain crashed: %s" % crash
    keys = ATLAS if clause == "A1" else ZUURRIK
    miss = [k for k in keys if k not in res]
    if miss:
        return 2, "UNMEASURED: components missing from the run: %s" % miss
    if clause == "A1":
        mods = res.get("running_mods")
        if not mods:
            return 2, "UNMEASURED: jawa/running_mods unreadable"
        donors = [d for d in DONOR_MODS if d in mods]
        if donors:
            return 2, "UNMEASURED: the running list holds %s: the free-mod load is not what ran" % donors
    verdicts = dict((k, res[k][0]) for k in keys)
    red = dict((k, res[k]) for k in keys if res[k][0] == "FAIL")
    if red:
        return 1, "%s fails: %s" % (clause, red)
    if any(v != "PASS" for v in verdicts.values()):
        return 2, "UNMEASURED: %s" % dict((k, res[k]) for k in keys if res[k][0] != "PASS")
    return 0, "%s holds: %s all PASS" % (clause, ", ".join(k.split(".")[1] for k in keys))


def _cache_path():
    import rmpaths
    return str(rmpaths.rm_path("scratch", "prove_stillsand_content.json"))


def _vhash():
    h = hashlib.sha256()
    for f in ("validation.py", "prove_stillsand_content.py"):
        with open(os.path.join(HERE, f), "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()[:16]


def live_result():
    path = _cache_path()
    try:
        with open(path, encoding="utf-8") as fh:
            c = json.load(fh)
        if c.get("vhash") == _vhash() and time.time() - c.get("at", 0) < CACHE_S:
            print("[prove] reusing the run of %s (%s)" % (time.ctime(c["at"]), path), file=sys.stderr)
            return c["res"]
    except (OSError, ValueError):
        pass
    V = _load_validation()
    import runner
    from rimdrive import Session
    runner.ensure_playing_map()
    with Session(lock=None, focus=False) as s:
        res = run_chains(V, s, runner._default_anchor(s))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"vhash": _vhash(), "at": time.time(), "res": res}, fh, indent=1, default=str)
    return res


# ----------------------------------------------------------------------------- selftest

def selftest():
    import selftest_stillsand as S
    bad = []

    class Fake(S.Fake):
        mods = ["ludeon.rimworld", "mandrake.rm.stillsand"]

        def t_running_mods(self, **k):
            return {"success": True, "packageIds": list(self.mods)}

    def run(broken=(), mods=None):
        S.V._STATE.clear()
        g = Fake(broken)
        if mods is not None:
            g.mods = mods
        return run_chains(S.V, g, (125, 125))

    cases = [((), None, 0, 0), (("oorrik_nre",), None, 1, 0), (("set_plants_drops",), None, 1, 0),
             (("log_error",), None, 1, 0), (("no_wake",), None, 0, 1), (("bites_unwounded",), None, 0, 1),
             (("no_bury",), None, 0, 1), (("zuurrik_ignores_toggle",), None, 0, 1),
             ((), ["ludeon.rimworld", "sarg.alphaanimals"], 2, 0), ((), [], 2, 0)]
    for broken, mods, w1, w2 in cases:
        res = run(broken, mods)
        got = (judge_live(res, "A1")[0], judge_live(res, "A2")[0])
        if got != (w1, w2):
            bad.append("%s mods=%s: want A1=%d A2=%d, got %s" % (broken or "healthy", mods, w1, w2, got))
    if judge_live({}, "A2")[0] != 2 or judge_live({"zuurrik.<CRASH>": ["CRASH", "x"]}, "A1")[0] != 2:
        bad.append("judge_live: a missing or crashed run did not read 2")
    # O1: a blob also held at another species' path is worn art; own-only history holds
    z = REL_TEX + "/Things/Pawn/Animal/RM_Zuurrik/RM_Zuurrik_south.png"
    a = REL_TEX + "/Things/Pawn/Animal/RM_Aurrok/RM_Aurrok_south.png"
    hist = blob_paths(":000000 100644 %s %s A\t%s\n:100644 100644 %s %s M\t%s\n" % ("0" * 40, "b" * 40, a, "0" * 40,
                                                                                  "b" * 40, z))
    if judge_o1(hist, {"RM_Zuurrik": {z: "b" * 40}})[0] != 1:
        bad.append("judge_o1: a blob also held at RM_Aurrok did not read 1")
    if judge_o1(blob_paths(":000000 100644 %s %s A\t%s\n" % ("0" * 40, "c" * 40, z)),
                {"RM_Zuurrik": {z: "c" * 40}})[0] != 0:
        bad.append("judge_o1: an own-only blob did not read 0")
    if judge_o1(hist, {"RM_Zuurrik": {}})[0] != 1 or judge_o1({}, {"RM_Zuurrik": {z: "b"}})[0] != 2:
        bad.append("judge_o1: missing art / empty history misread")
    # O2: a path that resolves nowhere is magenta; vanilla-only resolves; a blind parse is unmeasured
    paths = set(("Things/P%d" % i, "f.xml") for i in range(50))
    own = (lambda p: p != "Things/P0" and p != "Things/P1")
    van = set(["Things/P0"] + ["v%d" % i for i in range(600)])
    if judge_o2(paths, own, van)[0] != 1 or judge_o2(paths, own, van | {"Things/P1"})[0] != 0:
        bad.append("judge_o2: dead or vanilla path misread")
    if judge_o2(set(list(paths)[:5]), own, van)[0] != 2:
        bad.append("judge_o2: a blind parse did not read 2")
    # O3 against the real source, and a sign-stripped copy
    cs = open(os.path.join(HERE, "Source", "RM_MapComponent_Zuurrik.cs"), encoding="utf-8").read()
    if judge_o3({"x.xml"}, cs)[0] != 0:
        bad.append("judge_o3: the real source did not hold: %s" % judge_o3({"x.xml"}, cs)[1])
    if judge_o3({"x.xml"}, cs.replace("Messages.Message(", "Log.Message("))[0] != 1 or \
            judge_o3({"x.xml"}, cs.replace("FleckMaker.ThrowDustPuff", "// puff"))[0] != 1 or \
            judge_o3(set(), cs)[0] != 1:
        bad.append("judge_o3: a stripped sign or unwired hourbloom did not read 1")
    for b in bad:
        print("  BAD:", b)
    print("prove_stillsand_content selftest: %d live cases + judge probes, %s" % (len(cases), "FAIL" if bad else "ok"))
    return 1 if bad else 0


OFFLINE = {"O1": clause_o1, "O2": clause_o2, "O3": clause_o3}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--clause", choices=("O1", "O2", "O3", "A1", "A2"))
    g.add_argument("--offline", action="store_true")
    g.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        err, sys.stderr = sys.stderr, open(os.devnull, "w")
        try:
            return selftest()
        finally:
            sys.stderr = err
    if a.offline or a.clause in OFFLINE:
        worst = 0
        for c in (sorted(OFFLINE) if a.offline else [a.clause]):
            code, line = OFFLINE[c]()
            print(line)
            worst = max(worst, code)
        return worst
    try:
        res = live_result()
    except Exception as ex:
        print("UNMEASURED: %s: %s" % (type(ex).__name__, ex))
        return 2
    code, line = judge_live(res, a.clause)
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
