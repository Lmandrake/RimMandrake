#!/usr/bin/env python3
"""relentless_live_round.py -- one game-up sitting of the live tier: every built item that has a written proof for a
live criterion it owes gets relentless_live.run(), several per sitting (RA_S09_LIVE_WIRE_ONE_REAL_LEAF).

    python3 src/RimMandrake/rimflow/relentless_live_round.py eligible        # what a round would try, and why not the rest
    python3 src/RimMandrake/rimflow/relentless_live_round.py round [--max 6]
    python3 src/RimMandrake/rimflow/relentless_live_round.py census [--last 300]   # runs.jsonl sorted by cause

The supervisor (relentless.py tick, live_tick) starts `round` detached, at most one at a time, every live.round_every_s.
A round's end wakes the supervisor's game pass (wake_supervisor), so the next proof starts now and not at the next tick.

WHERE A PROOF COMES FROM: a line in infrastructure/state/live_proofs/<ID>.txt, one per criterion:

    live-proof A2: python3 src/RimMandrake/Utils/live_log_check.py --absent RUT_PaleMoss

A proof that needs mods its build did not change (a harness item, a proof over another mod) names them on one line, so
the round runs it on any game holding them and their About.xml dependencies, and UNMEASURED ("not in the running load",
which the game phase restages) on any other (PROOF_TIERS_WIDEN_SMALL_LIST_FIRST_ALWAYS):

    live-mods: Graffiti, SacredGraffiti

An item whose whole job is a deploy commits no mod file, so no commit says what to deploy, and a worker may not --apply
(live.forbid_re). It names the trees it owes the game, which also makes them live-mods:

    live-deploy: Armoury, StarWarsPatches
    live-proof A1: python3 src/RimMandrake/rimflow/relentless_live_round.py deployed --item <ID>

A drifting tree reads UNMEASURED "not deployed", so the game phase stages and its staging worker applies them; `deployed
--lint` is the offline proof (RELENTLESS_DEPLOY_WIRE_NOBODY_MAY_APPLY).

A criterion at level GREEN-FULL is the FINAL verification on the whole full list: it runs only when that tier is up.

Not the item's prose: the Marker's box leaves infrastructure/state/items out (walls.marker.tree_exclude), so a proof kept
there could never be checked blind. The prose keeps the why; the .txt holds only the lines.

Nothing here turns a criterion's English into a proof: a guessed proof would pass criteria nobody proved. A criterion with
no line is counted as `no proof` in `eligible` and waits for one.

A round, in order:
  1. no running game -> one rounds.jsonl row and nothing else (no bridge, no plan);
  1b. the canaries (relentless_canary.py), run here in the service's own process and cached by environment fingerprint:
     interop, the game's identity, our bridge identity, a bridge round trip, the load's identity, a known observation and
     a wrong expectation rejected. Sick -> one rounds.jsonl row "stopped: canary <name>: ..." and no proof spends a slot;
  2. candidates: built/validated, built sha, an owed criterion at a live level with a live-proof line, of any owner and
     any mod (FlowWorks and Gimme Some Slack included: FOUNDRY retired 2026-11-02, owner by card, and its acceptance
     sweeps became this lane);
  3. history (live/runs.jsonl): a criterion already PASS, FAIL or REFUSED on the same built sha is not run again (a FAIL
     stands until a new build; a refusal of a criterion cut on the ledger stands until its prose holds it whole);
     UNMEASURED retries after live.unmeasured_retry_s, and never on the game and build it ran on when the proof ran and
     measured nothing or a final clause found the small tier (due: DUD_HERE, WAITS_TIER), and never on its build at all
     once the row is a `defect` (relentless_live's cap);
  4. each run is relentless_live.run(): flyer and forbidden-proof refusal, files changed since the build, the deploy plan
     (args derived from the item's own mods, one plan per args per round), the game started after the deploy, the bridge
     taken with --idle-ok and released at once after each proof, the verdict a `rimflow verify` on the built sha;
  5. the round stops early when the game went away or the bridge is held by someone else.
"""
import argparse
import calendar
import fcntl
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless_live as L     # noqa: E402

# Bare, or wrapped whole in one pair of Markdown backticks; a bare command keeps its own backticks (echo `date`).
LINE = (r"^\s*(?:[-*]\s+)?(?:`{verb}\s+(?P<cid1>[A-Z]{{1,3}}\d{{1,3}})\s*:\s*(?P<cmd1>[^`\s][^`]*?)`"
        r"|{verb}\s+(?P<cid2>[A-Z]{{1,3}}\d{{1,3}})\s*:\s*(?P<cmd2>\S.*?))\s*$")
PROOF_LINE = re.compile(LINE.format(verb="live-proof"))
# `live-site <CID>: <cmd>`: what makes the map or save the proof reads, run first with the bridge held (relentless_live)
SITE_LINE = re.compile(LINE.format(verb="live-site"))
PROOFS_DIR = "infrastructure/state/live_proofs"
DEFAULTS = {"round_max": 6, "unmeasured_retry_s": 6 * 3600, "round_every_s": 1800}
STOP = ("no running game to test", "bridge not taken")
# a proof that ran on the game and measured nothing (relentless_game.RAN_DUD's words), or a site that would not prepare:
# rerun on the same game and build it can only say the same again
SAME_GAME_DUD = re.compile(r"the proof (exited \d+: it did not measure|timed out)|^site not prepared")
WAITS_TIER, DUD_HERE = "waits for the full-list tier", "measured nothing on this game"    # due()'s, relentless_game reads


def rules(r):
    out = dict(DEFAULTS)
    out.update((r or {}).get("live") or {})
    return out


def proof_lines(prose, pattern=PROOF_LINE):
    """An item's prose -> {criterion id: proof command}. A second line for the same criterion is ignored (first wins).
    pattern=SITE_LINE reads the `live-site` lines the same way."""
    out = {}
    for line in (prose or "").splitlines():
        m = pattern.match(line)
        if m:
            cid, cmd = (m.group("cid1"), m.group("cmd1")) if m.group("cid1") else (m.group("cid2"), m.group("cmd2"))
            out.setdefault(cid, cmd.strip())
    return out


LIVE_MODS = re.compile(r"^\s*(?:[-*]\s+)?`?live-(?:mods|deploy)\s*:\s*(?P<mods>[^`]*)`?\s*$")
LIVE_DEPLOY = re.compile(r"^\s*(?:[-*]\s+)?`?live-deploy\s*:\s*(?P<mods>[^`]*)`?\s*$")


def live_mods(text, pattern=LIVE_MODS):
    """A live_proofs file -> the mod folders its `live-mods:` and `live-deploy:` lines name (every line, in order, no
    repeats): what the running game must load. pattern=LIVE_DEPLOY: only what it must also hold whole."""
    out = []
    for line in (text or "").splitlines():
        m = pattern.match(line)
        if m:
            for x in re.split(r"[\s,]+", m.group("mods")):
                if x and x not in out:
                    out.append(x)
    return out


def is_package(name):
    """A `live-mods:` entry that names a mod by packageId (7f.alienworlds, ferny.worldbuilder), not a repo mod folder:
    packageIds always hold a dot; a mod folder rarely does.
    LIVE_MODS_FIX_WORKSHOP_UNNAMEABLE: TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING's clause needed Alien Worlds and
    Worldbuilder, workshop mods a folder-only line could not name, and read "Type not found: PlanetTypeManager" 20 times.
    A packageId is enabled with its dependency closure across the workshop and the game's Mods folder
    (modset_builder.package_closure) and checked in the running load; it is never deployed (it is no tree of ours).
    The dot rule alone read the composed folder RimMandrake.Biomes as a packageId; a dotted name some mod folder holds
    is a folder (relentless_live.is_package, OPS_CHURN_DIAGNOSE_OLLOPOM_JLHV_AJHK)."""
    return L.is_package(name)


def loadable(dirs, mods, shells):
    """The src/<tier>/<dir> names a commit touched -> the mod folders a load must hold. A repo mod or folded source keeps
    its name; a compose shell (BiomesShell) stands for its composed mod (RimMandrake.Biomes); any other dir (Utils,
    bridgetools, rimflow: tooling, no About.xml) is no mod. OPS_CHURN_DIAGNOSE_PLAYER_YGLE_IHKT: 20 game-phase items
    named Utils, bridgetools or BiomesShell, and modlist_swap --enable refused every batch load one of them rode
    ("no About.xml with a packageId"), so PLAYER_START_SITE_1 was held on its riders' names. Pure."""
    return sorted({shells.get(d, d) for d in dirs if d in mods or d in shells})


def folders(mods):
    """The repo mod folders of a mod list: what a deploy plan may name (a packageId is no tree of ours)."""
    return [m for m in mods if not is_package(m)]


def live_deploy(text):
    """A live_proofs file -> the mod folders whose whole tree the build owes the game folder (`live-deploy:`); a
    packageId there owes no tree (is_package) and is only loaded, as on a `live-mods:` line."""
    return folders(live_mods(text, LIVE_DEPLOY))


TERMINAL = ("PASS", "FAIL", "REFUSED")
# OPS_RELENTLESS_LIVE_MEASURE_RESTORE_LRPU: relentless_live.run's deploy and running-load gates read the item's mods and
# its build, never the clause, so a clause stopped there speaks for every clause of that build on that game (2026-11-05:
# TAOZIN L1-L3 wrote one "no readable packageId" three times in 17 s, a third of live_measured_pct's window never ran)
ITEM_GATED = "a sibling clause stopped at the item's deploy or load gate"


def item_gate(row):
    """True when a runs.jsonl row stopped at an ITEM-level gate (relentless_live.UNDEPLOYED): no proof ran."""
    return bool(row) and row.get("outcome") == "UNMEASURED" and "proof_exit" not in row and (
        row.get("why") or "").startswith(L.UNDEPLOYED)


def history(rows):
    """runs.jsonl rows -> {(item, criterion, sha): the row that decides}: a terminal row (PASS, FAIL, REFUSED) stands for
    its build whatever came after it; otherwise the newest row. A void row (relentless_attrib.resume: those rows were
    read through an instrument since repaired) ends every earlier row of its item on its sha."""
    out = {}
    for row in rows:
        if row.get("void") and row.get("item") and row.get("sha"):
            for k in [k for k in out if k[0] == row["item"] and k[2] and (k[2] == row["sha"] or (
                    len(k[2]) >= 7 and len(row["sha"]) >= 7 and (k[2].startswith(row["sha"]) or row["sha"].startswith(k[2]))))]:
                del out[k]
            continue
        if row.get("item") and row.get("criterion"):
            k = (row["item"], row["criterion"], row.get("sha"))
            last = out.get(k, {})
            if not decides(last) or last.get("cut"):     # a cut refusal yields to a later row
                out[k] = row
    return out


def decides(row):
    """A row that stands for its build whatever comes after: PASS, FAIL, REFUSED, a build the game can never run
    (relentless_live.STALE) and a cause that outlived a reload (row `defect`). Rerunning any of them on the same sha can
    only write the same row again (LIVE_REFUSAL_SILENCE_SAME_TEXT_HELD: 18 stale-build rows reran six-hourly)."""
    return bool(row) and (row.get("outcome") in TERMINAL or bool(row.get("defect"))
                          or (row.get("outcome") == "UNMEASURED" and (row.get("why") or "").startswith(L.STALE)))


def due(last, sha, now, retry_s, game=None, per_game=True):
    """-> None when this criterion may run now, else why not. `last` is its deciding runs.jsonl row on `sha`, or None.
    game: the running game's start (relentless_live.iso); a reload request made on it stands until another game runs.
    per_game: an undeployed build waits for another game (the cron round); a game phase's own round passes False, its
    staging is what deploys it."""
    if not last or last.get("sha") != sha:
        return None
    if last.get("outcome") in TERMINAL:
        return "judged on this build"
    if decides(last):
        return "no game can measure this build"
    if per_game and (last.get("why") or "").startswith(L.UNDEPLOYED) and game and last.get("game") == game:
        return "not deployed on this game"      # only a load (the game phase's staging) deploys and enables it
    if (last.get("why") or "").startswith(L.RELOAD) and game and last.get("game") == game:
        return "reload needed"
    # LIVE_SLOTS_MEASURE_NOT_REFUSE_IN_SLOT: the same game and the same build can only say the same thing again. A final
    # clause read FINAL_WAIT, or a proof that RAN and measured nothing, waits for a new build (a new sha: another `last`)
    # or another game; a game phase's round is no exception (2026-11-03 17:47-18:16Z: GRAFFITI A2/F1/F2 and GENERATOR A2
    # re-ran every 15 min on one game, six UNMEASURED runs that could not differ)
    if game and last.get("outcome") == "UNMEASURED":
        why, on = last.get("why") or "", last.get("game")
        if why.startswith(L.FINAL_WAIT) and (on == game or (not on and last.get("at", "") >= game)):
            return WAITS_TIER       # a row before 2026-11-03 has no game: written after this game started, it is its
        if on == game and SAME_GAME_DUD.search(why):
            return DUD_HERE
    try:
        at = calendar.timegm(time.strptime(last.get("at", ""), "%Y-%m-%dT%H:%M:%SZ"))
    except ValueError:
        return None
    if now - at < retry_s:
        return "unmeasured lately"
    return None


def candidates(items, proofs_of, hist, now, retry_s, game=None):
    """-> (todo [(item id, criterion, proof, built sha)], counts {why skipped: n}). Pure apart from proofs_of.
    proofs_of(item id) -> the text of its live_proofs file, empty when it has none.
    `items` are ledger items in relentless_live.Fx.item's shape (criteria already whole or marked cut)."""
    todo, counts = [], {}

    def skip(why):
        counts[why] = counts.get(why, 0) + 1

    for it in items:
        if it["state"] not in L.TESTABLE or not it.get("built_sha"):
            continue
        crit = {c["id"]: c for c in it.get("criteria") or []}
        owed = [c for c in it.get("outstanding") or [] if c in crit and crit[c]["level"] in L.LIVE_LEVELS]
        if not owed:
            continue
        proofs = proof_lines(proofs_of(it["id"]))
        # a sibling's item-level gate on this build and this game holds every clause, as it would hold the clause itself
        # (due: "not deployed on this game"); a game phase's round (retry 0) has just staged, so it runs again
        gated = bool(retry_s) and game and any(
            k[0] == it["id"] and k[2] == it["built_sha"] and item_gate(v) and v.get("game") == game
            for k, v in hist.items())
        for cid in owed:
            if cid not in proofs:
                skip("no proof")
                continue
            last = hist.get((it["id"], cid, it["built_sha"]))
            if last and last.get("cut") and not crit[cid].get("cut"):
                last = None     # refused while cut on the ledger; its prose now holds it whole: run it
            if gated and not decides(last):
                skip("not deployed on this game")
                continue
            why = due(last, it["built_sha"], now, retry_s, game, per_game=bool(retry_s))   # a game phase restages
            if why:
                skip(why)
                continue
            todo.append((it["id"], cid, proofs[cid], it["built_sha"]))
    return todo, counts


def deploy_args(mods, folded):
    """The item's mod folders -> deploy_custom_mods.py plan arguments covering each. A folder folded into the composed
    biomes mod is planned through --compose biomes, the rest beside it with --with, or alone with --mod."""
    mods = sorted(set(mods))
    targets = {t for t, _k in folded.values()}      # RimMandrake.Biomes itself: the composed mod, planned by --compose
    if any(m in folded or m in targets for m in mods):
        return " ".join(["--compose biomes"] + ["--with %s" % m for m in mods if m not in folded and m not in targets])
    return " ".join("--mod %s" % m for m in mods)


def item_mods(fx, item_id, sha):
    """The build's mod folders: those of the built commit, or, when it touched no shippable mod file, those of every
    commit citing the item (relentless_live.build_shas, PROOF_SHA_FIX_DEPLOYS_NOTHING_TWICE: a proof-only fix landed
    last deployed nothing and checked no running-load gap). Raises ValueError as mods_of does."""
    if item_id is None or not hasattr(fx, "cited"):
        return list(fx.mods_of(sha))
    return sorted({m for s in L.build_shas(fx, sha, item_id) for m in fx.mods_of(s)})


def mod_gap(fx, sha, text, running=True, item=None):
    """What a run of this build would find missing from the game, asked BEFORE a game slot is spent
    (LIVE_MODLIST_ENFORCE_BEFORE_SLOT: 6 of 28 live runs were HORRORS 'UtinniPatches not enabled in ModsConfig',
    GRAFFITI 'not in the running load', DRAWBRIDGE a stale FlowWorks DLL). The build's mods plus its `live-mods:` are
    planned once (deploy_custom_mods.py, read only). -> {"mods", "off": {folder: flag} (NOT DEPLOYED / not enabled in
    ModsConfig), "dll": [stale or missing DLLs in the game folder], "running": why the RUNNING load lacks them or None,
    "error": why the plan could not be read or None}. running=False skips the bridge read (no game, or a staging).
    item: the item built at `sha`, so a proof-only built commit stands for its item's mods (item_mods)."""
    out = {"mods": [], "off": {}, "dll": [], "running": None, "error": None}
    try:
        mods = sorted(set(item_mods(fx, item, sha)) | set(live_mods(text)))
    except ValueError as e:
        out["error"] = str(e)[:200]
        return out
    out["mods"] = mods
    if not mods:
        return out
    _plan_into(fx, mods, out)
    if running and not out["error"]:
        out["running"] = fx.running_load_gap(mods)
    return out


def batch_gap(fx, builds):
    """mod_gap for every build riding one load, for ONE deploy plan over their union: [(sha, proofs text[, item])] -> one gap.
    A staging needs only the union (enable_set, dll_mods); planned per item, 17 riders took 17 sequential plans of
    about 140 s over the Windows mount before the tick's 20-minute kill (TICK_SPEED_FIX_GAME_IDLES_WAITING). A build whose
    mods cannot be read rides without them and says so in `error`; the others still plan."""
    out = {"mods": [], "off": {}, "dll": [], "running": None, "error": None}
    mods = set()
    for b in builds:
        sha, text, item = (tuple(b) + (None,))[:3]
        try:
            mods |= set(item_mods(fx, item, sha)) | set(live_mods(text))
        except ValueError as e:
            out["error"] = str(e)[:200]
    out["mods"] = sorted(mods)
    if mods:
        _plan_into(fx, out["mods"], out)
    return out


def _plan_into(fx, mods, out):
    """The one plan over `mods` into a gap's off, dll and error. Headers and DLLs are all a gap reads, so --gate: 35 s
    where the full plan's byte compare and def guard took 260 s of a supervisor tick. A run still gates on the full plan
    (relentless_live.run), so other drifting files are caught there."""
    mods = folders(mods)        # a packageId is loaded (modlist_enable, running_load_gap), never planned
    if not mods:
        return
    rc, plan = fx.deploy_plan(deploy_args(mods, fx.folded()) + " --gate", L.live_rules({})["gate_plan_max_s"])
    if rc not in (0, 1):
        out["error"] = "the deploy plan failed (exit %s): %s" % (rc, (plan or "")[-200:])
        return
    _covered, drift, off = L.plan_sections(plan)
    out["off"] = off
    out["dll"] = sorted({"%s/%s" % (sec, e) if not e.startswith(sec + "/") else e
                         for sec, flag, e in drift if flag != "H" and e.lower().endswith(".dll")})


class RoundFx(L.Fx):
    """relentless_live.Fx plus what a round needs: every item, one plan per args, the lane and the compose manifest."""

    def __init__(self, *a, **kw):
        L.Fx.__init__(self, *a, **kw)
        self._plans = {}

    def canary(self, root, r, now):
        """The live harness's canaries, cached by environment fingerprint (relentless_canary.gate) -> None or why not."""
        import relentless_canary
        return relentless_canary.gate(relentless_canary.ShellFx(self), root, r, now)

    def items(self):
        import model
        out = []
        for it in model.replay(model.read()).items.values():
            if it.state not in L.TESTABLE:
                continue
            out.append({"id": it.id, "state": it.state, "built_sha": it.built_sha, "title": it.title or "",
                        "criteria": [L.whole_criterion(c, self.prose(it.id)) for c in it.criteria or []],
                        "outstanding": list(it.outstanding or [])})
        return out

    def proofs(self, item_id):
        p = os.path.join(self.books, PROOFS_DIR, item_id + ".txt")
        if not os.path.isfile(p):
            return ""
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()

    def deploy_plan(self, args, timeout):
        if args not in self._plans:
            self._plans[args] = L.Fx.deploy_plan(self, args, timeout)
        return self._plans[args]

    def folded(self):
        sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
        import deploy_custom_mods
        return deploy_custom_mods.folded()

    def has_mod(self, mod):
        """A mod folder the repo ships, by the deploy tool's own discovery (a folded mod counts: `--compose` plans it)."""
        sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
        import deploy_custom_mods
        return mod in deploy_custom_mods.folded() or mod in deploy_custom_mods.mod_dirs()

    def mod_names(self):
        """-> ({repo mod folder or folded source}, {compose shell source: composed target}), read once per RoundFx."""
        if getattr(self, "_mod_names", None) is None:
            sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
            import biomes_compose
            import deploy_custom_mods as D
            m = biomes_compose.load_manifest(D.SRC_ROOT) or {}
            shells = {m["shell"]["source"]: m["target"]} if (m.get("shell") or {}).get("source") else {}
            self._mod_names = (set(D.mod_dirs()) | set(D.folded()), shells)
        return self._mod_names

    def mods_of(self, sha):
        return loadable({m for m, _ in L.game_files(self.touched(sha), self.shippable)}, *self.mod_names())


def read_rows(path):
    rows = []
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    continue
    return rows


def plan(fx, root, r, now, only=None, game=None):
    """-> (todo, counts) for this moment. Read-only. `only`: one item, the supervisor's game phase for it
    (relentless_game.py): it has just staged the game, so an UNMEASURED row is no reason to wait."""
    lr = rules(r)
    hist = history(read_rows(os.path.join(root, "live", "runs.jsonl")))
    items = [it for it in fx.items() if only is None or it["id"] == only]
    return candidates(items, fx.proofs, hist, now, 0 if only else lr["unmeasured_retry_s"], game)


def run_round(fx, root, r, now=None, max_items=None, run=L.run, only=None):
    """One sitting. -> the round's summary row (also appended to <root>/live/rounds.jsonl)."""
    now = time.time() if now is None else now
    lr = rules(r)
    os.makedirs(os.path.join(root, "live"), exist_ok=True)
    summary = {"at": L.iso(now), "runs": []}

    def done(why):
        summary["why"] = why
        with open(os.path.join(root, "live", "rounds.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(summary, sort_keys=True) + "\n")
        return summary

    started = fx.game_started()
    if started is None:
        return done("no running game")
    sick = fx.canary(root, r, now) if hasattr(fx, "canary") else None     # in THIS process: the service's own context
    if sick:
        summary["canary"] = sick
        return done("stopped: %s" % sick[:300])
    todo, counts = plan(fx, root, r, now, only, L.iso(started))
    summary.update(eligible=len(todo), skipped=counts, **({"only": only} if only else {}))
    folded, ran, cap, gated = None, 0, lr["round_max"] if max_items is None else max_items, set()
    for item_id, cid, proof, sha in todo:     # the cap counts runs: a skip never starves the items behind it
        if ran >= cap:
            break
        if (item_id, sha) in gated:     # its gate is the build's, not the clause's: one row says it for all
            summary["skipped"][ITEM_GATED] = summary["skipped"].get(ITEM_GATED, 0) + 1
            continue
        try:
            mods = item_mods(fx, item_id, sha)
        except ValueError as e:
            summary["runs"].append({"item": item_id, "criterion": cid, "outcome": "UNMEASURED", "why": str(e)[:200]})
            continue
        if folded is None:
            folded = fx.folded()
        ran += 1
        text = fx.proofs(item_id)
        trees = live_deploy(text)
        row = run(fx, root, item_id, cid, proof, deploy_args(list(mods) + trees, folded), r, now=time.time(),
                  needs=live_mods(text), site=proof_lines(text, SITE_LINE).get(cid), trees=trees)
        summary["runs"].append({k: row.get(k) for k in ("item", "criterion", "outcome", "why", "sha")})
        if item_gate(row):
            gated.add((item_id, sha))
        if row["outcome"] == "UNMEASURED" and any(row.get("why", "").startswith(s) for s in STOP):
            return done("stopped: %s" % row["why"][:200])
    return done("done")


def deployed(fx, item_id, text, lint=False):
    """`deployed --item`: the proof of a deploy item -> (exit, line). 0 every `live-deploy:` tree is what the game folder
    holds; 1 one is not; 2 it could not measure (no such line, or a plan that did not read). lint reads no game folder, for
    the blind offline check: the line names mods the repo has, and the file has a proof line that runs this."""
    trees = live_deploy(text)
    if not trees:
        return 2, "%s/%s.txt has no live-deploy line" % (PROOFS_DIR, item_id)
    if lint:
        lost = [m for m in trees if not fx.has_mod(m)]
        if lost:
            return 1, "no such mod in the repo: %s" % ", ".join(lost)
        if not [c for c in proof_lines(text).values() if "relentless_live_round.py deployed" in c]:
            return 1, "no live-proof line runs `relentless_live_round.py deployed`"
        return 0, "OK %s names %s" % (item_id, ", ".join(trees))
    rc, plan = fx.deploy_plan(deploy_args(trees, fx.folded()), L.live_rules({})["plan_max_s"])
    why = L.deploy_gap([], rc, plan, trees, fx.folded())
    if why:
        return (2 if why.startswith("the deploy plan") else 1), why
    return 0, "OK the game folder holds %s" % ", ".join(trees)


def census(rows):
    """runs.jsonl rows -> what they spent and why (PROOF_RERUNS_TAME_UNMEASURED_REPEATS). `took_bridge` is the rows that
    held the game (a log exists); `repeats` the UNMEASURED rows that said what their (item, criterion, build) had already
    said, the waste the cap exists to end, so it should fall to near 0 on rows written since the cap."""
    out = {"rows": len(rows), "from": rows[0].get("at") if rows else None, "to": rows[-1].get("at") if rows else None,
           "outcomes": {}, "took_bridge": 0, "took_bridge_verdict": 0, "unmeasured": 0, "repeats": 0}
    causes, items, seen = {}, {}, set()
    for row in rows:
        o = row.get("outcome") or "?"
        out["outcomes"][o] = out["outcomes"].get(o, 0) + 1
        if row.get("log"):
            out["took_bridge"] += 1
            out["took_bridge_verdict"] += o in ("PASS", "FAIL")
        if o != "UNMEASURED":
            continue
        out["unmeasured"] += 1
        key = row.get("cause") or L.cause(row.get("why"))
        causes[key] = causes.get(key, 0) + 1
        one = (row.get("item"), row.get("criterion"), row.get("sha"), key)
        if one in seen:
            out["repeats"] += 1
            items[row.get("item")] = items.get(row.get("item"), 0) + 1
        seen.add(one)
    out["causes"] = sorted(([n, k] for k, n in causes.items()), key=lambda x: (-x[0], x[1]))
    out["repeating_items"] = sorted(([n, k or "?"] for k, n in items.items()), key=lambda x: (-x[0], x[1]))
    return out


def wake_supervisor(root, spawn=subprocess.Popen):
    """The round is over and the game is free: mark it, and start `relentless.py game-next`. The mark is what a running tick
    takes between its steps. Never the round's failure: a wake that does not happen costs the wait for the next tick."""
    try:
        os.makedirs(os.path.join(root, "store"), exist_ok=True)
        with open(os.path.join(root, "store", "game_wake"), "w", encoding="utf-8") as f:
            f.write(L.iso(time.time()))
        spawn(["python3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "relentless.py"), "game-next"],
              env=dict(os.environ, RELENTLESS_ROOT=root), stdin=subprocess.DEVNULL, start_new_session=True)
    except (OSError, ValueError) as e:
        print("wake_supervisor: %s" % e)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("eligible", help="what a round would try now, and the counts of what it would skip")
    p = sub.add_parser("round", help="one sitting: run every due criterion that has a proof, up to --max")
    p.add_argument("--max", type=int, default=None)
    p.add_argument("--item", help="this item only, no unmeasured wait: the supervisor's game phase")
    p = sub.add_parser("deployed", help="the proof of a deploy item: exit 0 its live-deploy trees are in the game folder")
    p.add_argument("--item", required=True)
    p.add_argument("--lint", action="store_true", help="offline: the line names real mods and a proof line runs this")
    p = sub.add_parser("census", help="runs.jsonl sorted by cause: what the rows spent, what repeated")
    p.add_argument("--last", type=int, default=300, help="the newest N rows")
    a = ap.parse_args(argv)
    with open(os.environ.get("RELENTLESS_RULES") or L.RULES, encoding="utf-8") as f:
        r = json.load(f)
    root = os.environ.get("RELENTLESS_ROOT") or "/home/mandrake/rm/relentless"
    if a.cmd == "census":
        path = os.path.join(root, "live", "runs.jsonl")
        if not os.path.exists(path):        # never "no rows": this instrument cannot see
            print("UNMEASURED: no %s" % path, file=sys.stderr)
            return 2
        print(json.dumps(census(read_rows(path)[-a.last:]), indent=1, sort_keys=True))
        return 0
    fx = RoundFx(seat=r.get("seat") or "BENCH")
    if a.cmd == "deployed":
        code, line = deployed(fx, a.item, fx.proofs(a.item), a.lint)
        print(line)
        return code
    if a.cmd == "eligible":
        started = fx.game_started()     # the round's own view: what this game already said stays skipped
        todo, counts = plan(fx, root, r, time.time(), game=L.iso(started) if started else None)
        print(json.dumps({"eligible": [list(t[:3]) for t in todo], "skipped": counts}, indent=1, sort_keys=True))
        return 0
    os.makedirs(os.path.join(root, "live"), exist_ok=True)
    with open(os.path.join(root, "live", "round.lock"), "w") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("a round is running")
            return 0
        print(json.dumps(run_round(fx, root, r, max_items=a.max, only=a.item), indent=1, sort_keys=True), flush=True)
    wake_supervisor(root)       # outside round.lock: the proof it starts takes that lock
    return 0


if __name__ == "__main__":
    sys.exit(main())
