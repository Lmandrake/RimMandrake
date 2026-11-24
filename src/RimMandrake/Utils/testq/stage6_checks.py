#!/usr/bin/env python3
"""testq/stage6_checks.py - the program route of each Stage 6 check to a Steve game, and the runner of those routes.
Page: design/specs/2026-11-24-stage-six-checks-to-steve/boundary.md. Tests: selftest_stage6_checks.py.

A check with a modcheck chain goes by its chain (testq_blocks.py). Every other check that a tier list can prove goes by
its own script: ROUTES names the scripts a program can run and read, one verdict per check.

  stage6_checks.py place MOD                 each stage-6 check: takeable | not the lane's | could not look, and its cause
  stage6_checks.py run --mod M --tier T --checks a,b --out DIR [--timeout S]
                                             (the worker, on SteveDesktop, the tier loaded) runs each route once and
                                             writes DIR/checks.json {identity, rows: {check: {verdict, detail, site, ...}}}

`place` and `route` read files only. Verdicts: PASS and FAIL are the script's own; everything else is UNMEASURED with
its cause (a crash, a timeout, no output, INVALID, ERROR, an unverified site, a missing row).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
RIMFLOW = os.path.join(REPO, "src", "RimMandrake", "rimflow")
TAKEABLE, NOT_LANE, NO_LOOK = "takeable", "not the lane's", "could not look"
EK = "src/RimMandrake/ExplosiveKnockback/"
GSS = "src/RimMandrake/GimmeSomeSlack/"
PYRE = "src/RimMandrake/Pyrelands/"
EK_BIOME = "AridShrubland"
SITE = "src/RimMandrake/Utils/testq/stage6_site.py"
LIVE_SITE = "python.exe src/RimMandrake/Utils/live_site.py"
# budget: danger=live_site refuses an old test game as a colony; ends no work: a tick count that the site check is given
FRESH = 100000000       # live_site refuses an old game as "a colony"; on SteveDesktop every game is a test game


def _rimflow(name):
    if RIMFLOW not in sys.path:
        sys.path.append(RIMFLOW)
    return __import__(name)


def _cmd(spec):
    return str(spec.get("command") or "").replace("\\", "/")


# ---- routes: (check id, entry) -> {"key", "steps", "read", "tier", "build", "site"} or why not -------------------------
# key: checks of one key share one run. steps: shell lines in the repo root; {out} is the run's result file (Linux path),
# {wout} the same as Windows spells it, {stamp} a stamp. read: the reader's name. site: what is made before the steps.

# a scene whose site save was built on another tier (it does not load verified on `flowworks`: Steve1, 2026-11-24)
CONCEPT_TIERS = {"scene_source_pays": "fw_gss_sitting"}


def _concept(tid, spec):
    entry = str(spec.get("entry") or "")
    if not entry.startswith("scene_"):
        return None
    return {"key": "concept:" + entry, "read": "concept", "build": "release",
            "tier": spec.get("tier") or CONCEPT_TIERS.get(entry, "flowworks"),
            "steps": ["python.exe -u src/RimMandrake/FlowWorks/northstar/concept_scenes.py --scene %s --out {wout}" % entry]}


def _gss_scene(tid, spec):
    m = re.search(r"validation\.py --scene (\w+)", _cmd(spec))
    if not m:
        return None
    return {"key": "gss_scene:" + m.group(1), "read": "status", "tier": spec.get("tier") or "gimmesomeslack",
            "build": "release", "site": "game",
            "steps": ["python.exe -u %svalidation.py --scene %s --out {wout}" % (GSS, m.group(1))]}


_GSS_SCENES = {}


# proof rows that need FlowWorks loaded (proof_all says so itself on the plain tier: Steve2, 2026-11-24)
GSS_FLOWWORKS_ROWS = ("P_SC_shock_reach_deck_cord_per_value", "P_SC_under_liquid_pit")


def _gss_other_rows(tid, rx):
    """-> the rows matching RX that scene TID's verdict reads; [] none, or the scenes could not be read here."""
    if not _GSS_SCENES:
        _GSS_SCENES["V"] = None
        try:
            import importlib.util
            d = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack")
            if d not in sys.path:
                sys.path.append(d)
            sp = importlib.util.spec_from_file_location("gss_validation", os.path.join(d, "validation.py"))
            m = importlib.util.module_from_spec(sp)
            sp.loader.exec_module(m)
            _GSS_SCENES["V"] = m
        except Exception:       # noqa: BLE001 - a host without its imports (SteveDesktop): the committed blocks decide
            pass
    try:
        return [r for r in _GSS_SCENES["V"].scene_rows_for(tid) if re.match(rx, r)]
    except Exception:       # noqa: BLE001
        return []


def _gss_proof(tid, spec):
    if "proof_all.py --live" not in _cmd(spec) and not (
            _cmd(spec) == GSS + "validation.py" and str(spec.get("entry") or "").startswith("scene_")):
        return None
    tier = spec.get("tier") or ("gimmesomeslack_flowworks" if tid in GSS_FLOWWORKS_ROWS else "gimmesomeslack")
    if not tier.startswith("gimmesomeslack"):
        return "its tier %s is a list without the mod: it reads a save that an earlier run on the mod's tier made" % tier
    rows = _gss_other_rows(tid, r"GS\d") if tid.startswith("sc_") else []
    if rows:
        return "its verdict joins the proof's rows with another script's (%s): no one run decides it" % ", ".join(rows)
    rows = _gss_other_rows(tid, r"O\d") if tid.startswith("sc_") else []
    if rows:
        return "its verdict reads offline gate rows (%s), and the gate's C# selftest takes over 15 min on SteveDesktop" % (
            ", ".join(rows))
    return {"key": "gss_proof:" + tier, "read": "gss_proof", "tier": tier, "build": "release",
            "steps": ["python.exe -u %snorthstar/proof_all.py --live --no-shots --skip-offline --out {wout}" % GSS,
                      "python3 %svalidation.py --scenes-from {out} > {out}.scenes 2>&1" % GSS]}


def _gss_gravship(tid, spec):
    e = str(spec.get("entry") or "")
    m = re.search(r"gravship_(on|off)_", e)
    mode = "off_autolink" if e.startswith("GS3_") else m.group(1) if m else None     # gravship_scene.ROW_IDS
    if not mode:
        return None
    return {"key": "gss_gravship:" + mode, "read": "rowfile", "tier": spec.get("tier") or "gimmesomeslack",
            "build": "release", "site": "game",
            "steps": ["python.exe -u %snorthstar/gravship_scene.py %s --out {wout}" % (GSS, mode)]}


def _ek_scenes(tid, spec):
    m = re.search(r"knockback_runner\.py (--scenes [\w,]+(?: --ticks \d+)?(?: --real-seconds [\d.]+)?)", _cmd(spec))
    if not m:
        return None
    return {"key": "ek:" + m.group(1), "read": "ek_scenes", "tier": "explosiveknockback_visit", "build": "proof",
            "site": "biome:" + EK_BIOME, "sweep": True,
            "steps": ["python.exe -u %sknockback_runner.py %s" % (EK, m.group(1))]}


def _ek_walk(tid, spec):
    m = re.search(r"validation\.py --live (walk_storeroom_raid --storeroom \S+ --cover \S+ --gas \S+)", _cmd(spec))
    if not m or "stage_walk_colony.py" not in _cmd(spec):
        return None
    pairs = re.search(r"--frame-pairs \d+", _cmd(spec))
    return {"key": "ek_walk", "read": "ek_walk", "tier": "explosiveknockback_visit", "build": "proof",
            "site": "biome:" + EK_BIOME, "first": True, "save": "EK_WALK_SMALL_COLONY_{stamp}",
            "steps": ["python.exe -u %sproof/stage_walk_colony.py --save EK_WALK_SMALL_COLONY_{stamp}" % EK,
                      "python.exe -u %svalidation.py --live %s --save EK_WALK_SMALL_COLONY_{stamp} %s --out {wout}" % (
                          EK, m.group(1), pairs.group(0) if pairs else "")]}


def _exit012(tid, spec):
    lines = {PYRE + "gate_live_proof.py": ["A1", "A2"], PYRE + "firefoam_aim_live_proof.py": [""]}.get(
        str(spec.get("file") or "").replace("\\", "/"))
    if not lines:
        return None
    f = spec["file"].replace("\\", "/")
    return {"key": "exit012:" + f, "read": "exit012", "tier": "pyrelands", "build": "release", "site": "game",
            "steps": [("python.exe -u %s %s" % (f, x)).strip() for x in lines]}


ROUTES = (
    (r"FlowWorks/northstar/concept_scenes\.py", _concept),
    (r"GimmeSomeSlack/validation\.py --scene", _gss_scene),
    (r"GimmeSomeSlack/northstar/gravship_scene\.py", _gss_gravship),
    (r"GimmeSomeSlack/(northstar/proof_all|validation)\.py", _gss_proof),
    (r"ExplosiveKnockback/knockback_runner\.py", _ek_scenes),
    (r"ExplosiveKnockback/proof/stage_walk_colony\.py", _ek_walk),
    (r"Pyrelands/(gate_live_proof|firefoam_aim_live_proof)\.py", _exit012),
)


def not_the_lanes(spec, paused=None):
    """-> why a check is not SteveDesktop's at all, or None."""
    BM, RP = _rimflow("build_match"), _rimflow("raid_pause")
    kind = str(spec.get("kind") or "")
    if BM.is_full(spec):
        return "kind %s: his full list, on ArchBig" % kind
    if kind != "live_minimal":
        return "kind %s: SteveDesktop runs the minimal tier" % kind
    if RP.stages(spec) and (RP.paused() if paused is None else paused):
        return RP.WORD
    if re.search(r"\ba game on Archmagi\b", _cmd(spec)):
        return "its command names a game on Archmagi (a frame time of that machine)"
    return None


def route(mod, tid, spec, root=REPO):
    """-> (route dict, None), or (None, why a program cannot run or read this check)."""
    f = str(spec.get("file") or "").replace("\\", "/")
    if spec.get("entry_exists") is False or (spec.get("runs_today") or {}).get("entry_exists") is False:
        return None, "its table says the entry %s does not exist" % spec.get("entry")
    if not f or not os.path.isfile(os.path.join(root, f)):
        return None, "no entry point: its file %s is not on disk" % (f or "(none named)")
    for rx, fn in ROUTES:
        if re.search(rx, _cmd(spec)):
            r = fn(tid, spec)
            if isinstance(r, dict):
                missing = [s for s in re.findall(r"src/\S+\.py", " ".join(r["steps"]))
                           if not os.path.isfile(os.path.join(root, s))]
                if missing:
                    return None, "no entry point: %s is not on disk" % missing[0]
                return r, None
            if r:
                return None, r
    return None, "no program reads a verdict of this check from %s (entry %s)" % (f, spec.get("entry"))


def place(mod, tests, chains_of=None, root=REPO, paused=None):
    """-> {check id: (TAKEABLE | NOT_LANE | NO_LOOK, cause or {"chains"} / {"check"} block)} over the stage-6 entries.
    chains_of: {check: [chains]} a chain route already gives (testq_blocks.derive)."""
    out = {}
    for tid, spec in tests.items():
        if not isinstance(spec, dict) or str(spec.get("stage")) != "6":
            continue
        why = not_the_lanes(spec, paused)
        if why:
            out[tid] = (NOT_LANE, why)
            continue
        ch = (chains_of or {}).get(tid)
        if ch:
            out[tid] = (TAKEABLE, {"chains": list(ch)})
            continue
        r, why = route(mod, tid, spec, root)
        out[tid] = (TAKEABLE, {"check": {"tier": r["tier"], "build": r["build"]}}) if r else (NO_LOOK, why)
    return out


def deploys(mod, tier, root=REPO):
    """-> the deployable names of OUR mods on TIER besides MOD (the job's --deploy list), or raises."""
    utils = os.path.join(root, "src", "RimMandrake", "Utils")
    for p in (utils, os.path.join(utils, "modcheck")):
        if p not in sys.path:
            sys.path.append(p)
    import modset_builder as MB
    import runner
    have = runner.src_mods_by_id(root)
    td = MB.tier_def(tier)
    if td is None:
        raise ValueError("tier %s is no modset_builder.py tier" % tier)
    folded = runner.composed_into(mod)
    me = have.get(folded[1]) if folded else mod
    want = [p.lower() for p in td["want"]]
    try:
        want = [p.lower() for p in MB.resolve_tier(tier, MB.scan())[0]] or want     # the closure, where this host resolves it
    except Exception:       # noqa: BLE001 - a host without the mods: the tier's own names stand
        pass
    out = []
    for p in want:
        n = have.get(p)
        if n and n != me and n not in out:
            out.append(n)
    return out


# ---- the readers: (text of the steps, exit codes, result file) -> {check: (verdict, detail, site)} ---------------------

def _verdict_of(statuses):
    st = [str(s).upper() for s in statuses]
    return "FAIL" if "FAIL" in st else "PASS" if st and all(s == "PASS" for s in st) else "UNMEASURED"


def _load(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _tail(text, n=400):
    return (text or "").strip()[-n:]


def read_concept(tids, specs, text, rcs, out):
    d = _load(out)
    if not isinstance(d, dict):
        return {t: ("UNMEASURED", "no result file (exit %s): %s" % (rcs[-1], _tail(text)), None) for t in tids}
    site = d.get("site") if isinstance(d.get("site"), dict) else {}
    rows = [r for r in d.get("rows") or [] if isinstance(r, dict)]
    v = _verdict_of(r.get("status") for r in rows)
    if not site.get("verified"):
        v = "UNMEASURED"
    elif v == "PASS" and d.get("status") != "PASS":
        v = "UNMEASURED"            # every row passed and the run still ended on an error: its own, not the mod's
    elif not rows and d.get("status") == "PASS" and all(specs[t].get("entry") == "scene_hole_prison" for t in tids):
        v = "PASS"                  # scene_hole_prison asserts and writes no rows
    bad = "; ".join("%s %s: %s" % (r.get("id"), r.get("status"), str(r.get("detail"))[:160]) for r in rows
                    if r.get("status") != "PASS")
    det = bad or ("%d rows PASS" % len(rows) if rows else "") or str(d.get("error") or "")
    if d.get("error") and v != "PASS":
        det = "%s | %s" % (det, str(d["error"])[:300])
    return {t: (v, det, {"calm_site_verified": True} if site.get("verified") else None) for t in tids}


def read_status(tids, specs, text, rcs, out):
    d = _load(out)
    if not isinstance(d, dict):
        return {t: ("UNMEASURED", "no result file (exit %s): %s" % (rcs[-1], _tail(text)), None) for t in tids}
    rows = [r for r in d.get("rows") or [] if isinstance(r, dict)]
    st = str(d.get("status") or "").upper()
    v = st if st in ("PASS", "FAIL") else "UNMEASURED"
    if v == "FAIL" and rows and _verdict_of(r.get("status") for r in rows) != "FAIL":
        v = "UNMEASURED"            # no row failed: the scene could not ask
    det = "; ".join("%s %s" % (r.get("id"), r.get("status")) for r in rows) or _tail(text)
    return {t: (v, det[:900], {"own_cleared_plot": True, "rows": len(rows)} if rows else None) for t in tids}


def read_gss_proof(tids, specs, text, rcs, out):
    d = _load(out)
    if not isinstance(d, dict) or not isinstance(d.get("rows"), list):
        return {t: ("UNMEASURED", "no proof result (exit %s): %s" % (rcs[0], _tail(text)), None) for t in tids}
    by = {}
    for r in d["rows"]:
        if isinstance(r, dict) and r.get("id"):
            by.setdefault(r["id"], []).append(r)
    for k, v in d.items():          # some rows of a shared session sit in its notes (visit 1, 2026-11-16: S7)
        if k.endswith("_notes") and isinstance(v, list):
            for r in v:
                if isinstance(r, dict) and r.get("id") and r.get("status") and r["id"] not in by:
                    by[r["id"]] = [r]
    pin = [x for k, v in by.items() if k.startswith(("P1_", "P3_")) for x in v]
    sited = len(pin) >= 2 and all(x.get("status") == "PASS" for x in pin) and not d.get("aborted")
    site = {"preflight": {x["id"]: x["status"] for x in pin}} if sited else None
    scenes = {}
    try:
        with open(out + ".scenes", encoding="utf-8", errors="replace") as f:
            for ln in f:
                m = re.match(r"^(sc_\w+)\s+(PASS|FAIL|UNMEASURED)\b\s*(.*)$", ln.strip())
                if m:
                    scenes[m.group(1)] = (m.group(2), m.group(3))
    except OSError:
        pass
    got = {}
    for t in tids:
        if t.startswith("sc_"):
            v, det = scenes.get(t, ("UNMEASURED", "validation.py --scenes-from printed no line for it (exit %s)" % rcs[-1]))
        else:
            rs = by.get(str(specs[t].get("entry") or t[2:])) or by.get(t[2:]) or []
            v, det = (_verdict_of(r.get("status") for r in rs), "; ".join(str(r.get("detail"))[:200] for r in rs)) if rs \
                else ("UNMEASURED", "the proof wrote no row of this name")
        if not sited and v != "UNMEASURED":
            v, det = "UNMEASURED", "the proof's site was not verified (P1/P3 not PASS); it read %s: %s" % (v, det)
        got[t] = (v, det[:900], site)
    return got


def read_ek_scenes(tids, specs, text, rcs, out):
    got = {}
    for t in tids:
        m = re.search(r"--scenes ([\w,]+)", _cmd(specs[t]))
        want = m.group(1).split(",") if m else []
        st = {}
        for ln in (text or "").splitlines():
            x = re.match(r"^(\w+)\s+(PASS|FAIL|INVALID|ERROR)\b\s*(.*)$", ln.strip())
            if x:
                st[x.group(1)] = (x.group(2), x.group(3))
        v = _verdict_of(st.get(w, ("absent",))[0] for w in want)
        if v == "PASS" and rcs[-1] != 0:
            v = "UNMEASURED"
        det = "; ".join("%s %s %s" % (w, *(st.get(w) or ("no line", ""))) for w in want)
        if not st:
            det = "no scene line (exit %s): %s" % (rcs[-1], _tail(text))
        got[t] = (v, det[:900], None)
    return got


def read_ek_walk(tids, specs, text, rcs, out):
    rows = re.findall(r"^([A-Z][A-Z0-9_]+)\s+(PASS|FAIL|UNMEASURED)\b\s*(.*)$", text or "", re.M)
    rows = [r for r in rows if r[0] != "ROW"]
    staged = bool(re.search(r"^STAGED ", text or "", re.M))
    v = _verdict_of(r[1] for r in rows) if staged else "UNMEASURED"
    if v == "PASS" and rcs[-1] != 0:
        v = "UNMEASURED"
    det = "; ".join("%s %s %s" % (a, b, c[:120]) for a, b, c in rows if b != "PASS") or (
        "%d rows PASS" % len(rows) if rows else "no row (exits %s): %s" % (rcs, _tail(text)))
    return {t: (v, det[:900], {"staged": "stage_walk_colony.py read every thing back"} if staged else None) for t in tids}


def read_exit012(tids, specs, text, rcs, out):
    crash = re.search(r"^Traceback \(most recent call last\)", text or "", re.M)
    v = "FAIL" if 1 in rcs and not crash else "PASS" if rcs and all(r == 0 for r in rcs) else "UNMEASURED"
    return {t: (v, "exits %s: %s" % (rcs, _tail(text)), None) for t in tids}


def read_rowfile(tids, specs, text, rcs, out):
    """A result file of rows: the check's verdict is the row of its entry's id. A stop of the game's clock exits 1 as a FAIL
    does (the gravship script), so the exit code decides nothing."""
    d = _load(out)
    rows = [r for r in (d or {}).get("rows") or [] if isinstance(r, dict)] if isinstance(d, dict) else []
    got = {}
    for t in tids:
        hit = [r for r in rows if r.get("id") == specs[t].get("entry")]
        v = _verdict_of(r.get("status") for r in hit) if hit else "UNMEASURED"
        det = "; ".join(json.dumps(r.get("detail"), default=str)[-600:] for r in hit) or "no row of its name (exits %s): %s" % (
            rcs, _tail(text))
        got[t] = (v, det[:900], None)
    return got


READERS = {"rowfile": read_rowfile, "concept": read_concept, "status": read_status, "gss_proof": read_gss_proof, "ek_scenes": read_ek_scenes,
           "ek_walk": read_ek_walk, "exit012": read_exit012}


# ---- the runner (on the game machine) ------------------------------------------------------------------------------

def wpath(path):
    # budget: danger=a hung wslpath holds one game of the lane; its reach leaves no record; no record of its run
    r = subprocess.run(["wslpath", "-w", path], capture_output=True, text=True, timeout=60)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else path


def sh(line, log, timeout):
    """-> (exit code or None on a timeout, stdout then stderr). Two streams into one file glued a stderr line into a row's
    line (Steve2, 2026-11-24), so stderr has its own file. The whole process group dies on a timeout."""
    import signal
    err = log + ".err"
    with open(log, "ab") as f, open(err, "ab") as e:
        f.write(("$ %s\n" % line).encode())
        f.flush()
        at, eat = f.tell(), e.tell()
        p = subprocess.Popen(["bash", "-c", line], cwd=REPO, stdin=subprocess.DEVNULL, stdout=f, stderr=e,
                             start_new_session=True)
        try:
            rc = p.wait(timeout=max(1, timeout))
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL)
            p.wait()
            rc = None
    got = []
    for path, pos in ((log, at), (err, eat)):
        with open(path, "rb") as f:
            f.seek(pos)
            got.append(f.read().decode("utf-8", "replace").replace("\r", ""))
    return rc, got[0] + ("\n--- stderr ---\n" + got[1][-4000:] if got[1].strip() else "")


def make_site(r, log, sh_=sh):
    """Make the route's site -> (site dict or None, why not). A script that loads its own site needs none."""
    want = r.get("site")
    if not want:
        return {}, None
    steps = [LIVE_SITE + " --game --max-ticks %d" % FRESH]
    if want.startswith("biome:"):
        steps.append(LIVE_SITE + " --biome %s --max-ticks %d" % (want[6:], FRESH))
    for s in steps:
        rc, text = sh_(s, log, 900)
        if rc != 0:
            return None, "site not made (exit %s): %s" % (rc, _tail(text, 240))
    rc, text = sh_("python.exe -u %s%s%s" % (SITE, " --sweep" if r.get("sweep") else "",
                                             " --biome " + want[6:] if want.startswith("biome:") else ""), log, 180)
    site = None
    for x in re.finditer(r"SITE_JSON (?=\{)", text or ""):
        try:
            site = json.JSONDecoder().raw_decode(text, x.end())[0]
        except ValueError:
            pass
    if rc != 0 or not site:
        return None, "site not read (exit %s): %s" % (rc, _tail(text, 240))
    return site, None


def run(mod, tier, ids, outdir, timeout=28800, root=REPO, sh_=sh, tests=None, identity=None):  # budget: danger=a hung run holds one game of the lane with no end; longest=2554s of 430 runs with this bound (testq done records, phase_s, 14 days to 2026-11-24)
    """Run each check's route once per key -> {check: row}. The caller has the tier loaded and proven exact."""
    if tests is None:
        with open(os.path.join(root, "design", "concepts", mod, "version", "test_table.json"), encoding="utf-8") as f:
            tests = json.load(f).get("tests") or {}
    os.makedirs(outdir, exist_ok=True)
    end, rows, groups = time.time() + timeout, {}, {}

    def put(t, verdict, detail, site=None, **kw):
        rows[t] = dict({"verdict": verdict, "detail": str(detail)[:1500], "site": site or None}, **kw)
    for t in ids:
        spec = tests.get(t)
        if not isinstance(spec, dict):
            put(t, "UNMEASURED", "no check of this name in the test table at this commit")
            continue
        r, why = route(mod, t, spec, root)
        why = not_the_lanes(spec) or why
        if why or r["tier"] != tier:
            put(t, "UNMEASURED", why or "its tier is %s, the load is %s" % (r["tier"], tier))
            continue
        groups.setdefault(r["key"], (r, []))[1].append(t)
    for n, key in enumerate(sorted(groups, key=lambda k: (not groups[k][0].get("first"), k))):
        r, tids = groups[key]
        base = os.path.join(outdir, "run_%02d" % n)
        out, log = base + ".json", base + ".log"
        stamp = time.strftime("%Y%m%dT%H%M%S")
        fill = {"out": out, "wout": "'%s'" % wpath(out), "stamp": stamp}
        left = end - time.time()
        if left < 60:
            for t in tids:
                put(t, "UNMEASURED", "not reached: the job's time ended before its run")
            continue
        site, why = make_site(r, log, sh_)
        if why:
            for t in tids:
                put(t, "UNMEASURED", why)
            continue
        text, rcs = "", []
        for s in r["steps"]:
            rc, tx = sh_(s.format(**fill), log, end - time.time())
            rcs.append(rc)
            text += tx
            if rc is None or (rc != 0 and r["read"] == "ek_walk" and len(rcs) == 1):
                break
        if None in rcs:
            for t in tids:
                put(t, "UNMEASURED", "timed out: %s" % _tail(text, 240))
            continue
        for t, (v, det, seen) in READERS[r["read"]](tids, {t: tests[t] for t in tids}, text, rcs, out).items():
            held = ["non-colonist pawns swept before the check", "incident queue emptied before the check"] \
                if r.get("sweep") else []
            if r.get("site") and not seen:
                seen = site
            put(t, v, det, seen, held=held, command="; ".join(s.format(**dict(fill, wout="<out>", out="<out>"))
                                                               for s in r["steps"]), log=os.path.basename(log))
    return rows


def read_identity(mod, tier, root=REPO):
    """build_match.identity on this machine, or {"why": [...]}: an identity that could not be read is said, never guessed."""
    try:
        BM = _rimflow("build_match")
        return BM.identity(root, mod, tier=tier)
    except Exception as e:      # noqa: BLE001
        return {"why": ["the identity could not be read (%s: %s)" % (type(e).__name__, e)]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("place")
    p.add_argument("mod")
    r = sp.add_parser("run")
    for k in ("--mod", "--tier", "--checks", "--out"):
        r.add_argument(k, required=True)
    r.add_argument("--timeout", type=int, default=28800)  # budget: danger=a hung run holds one game of the lane with no end; longest=2554s of 430 runs with this bound (testq done records, phase_s, 14 days to 2026-11-24)
    a = ap.parse_args(argv)
    if a.cmd == "place":
        import testq_blocks as B
        got = B.plan(a.mod)["placed"]
        for t, (st, x) in got.items():
            print("  %-34s %-15s %s" % (t, st, x if isinstance(x, str) else json.dumps(x, sort_keys=True)))
        n = {s: sum(1 for v in got.values() if v[0] == s) for s in (TAKEABLE, NOT_LANE, NO_LOOK)}
        print("%s: %d checks: %d takeable, %d not the lane's, %d could not look" % (
            a.mod, len(got), n[TAKEABLE], n[NOT_LANE], n[NO_LOOK]))
        return 0
    ids = [x for x in a.checks.split(",") if x]
    rows = run(a.mod, a.tier, ids, a.out, a.timeout)
    doc = {"mod": a.mod, "tier": a.tier, "identity": read_identity(a.mod, a.tier), "rows": rows}
    tmp = os.path.join(a.out, "checks.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, default=str)
    os.replace(tmp, os.path.join(a.out, "checks.json"))
    for t in ids:
        print("%-34s %-10s %s" % (t, rows[t]["verdict"], rows[t]["detail"].replace("\n", " ")[:160]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
