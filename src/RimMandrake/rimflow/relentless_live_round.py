#!/usr/bin/env python3
"""relentless_live_round.py -- one game-up sitting of the live tier: every built item that has a written proof for a
live criterion it owes gets relentless_live.run(), several per sitting (RA_S09_LIVE_WIRE_ONE_REAL_LEAF).

    python3 src/RimMandrake/rimflow/relentless_live_round.py eligible        # what a round would try, and why not the rest
    python3 src/RimMandrake/rimflow/relentless_live_round.py round [--max 6]

The supervisor (relentless.py tick, live_tick) starts `round` detached, at most one at a time, every live.round_every_s.

WHERE A PROOF COMES FROM: a line in infrastructure/state/live_proofs/<ID>.txt, one per criterion:

    live-proof A2: python3 src/RimMandrake/Utils/live_log_check.py --absent RUT_PaleMoss

A proof that needs mods its build did not change (a harness item, a proof over another mod) names them on one line, so
the round runs it on any game holding them and their About.xml dependencies, and UNMEASURED ("not in the running load",
which the game phase restages) on any other (PROOF_TIERS_WIDEN_SMALL_LIST_FIRST_ALWAYS):

    live-mods: Graffiti, SacredGraffiti

A criterion at level GREEN-FULL is the FINAL verification on the whole full list: it runs only when that tier is up.

Not the item's prose: the Marker's box leaves infrastructure/state/items out (walls.marker.tree_exclude), so a proof kept
there could never be checked blind. The prose keeps the why; the .txt holds only the lines.

Nothing here turns a criterion's English into a proof: a guessed proof would pass criteria nobody proved. A criterion with
no line is counted as `no proof` in `eligible` and waits for one.

A round, in order:
  1. no running game -> one rounds.jsonl row and nothing else (no bridge, no plan);
  2. candidates: built/validated, built sha, an owed criterion at a live level with a live-proof line, of any owner and
     any mod (FlowWorks and Gimme Some Slack included: FOUNDRY retired 2026-11-02, owner by card, and its acceptance
     sweeps became this lane);
  3. history (live/runs.jsonl): a criterion already PASS, FAIL or REFUSED on the same built sha is not run again (a FAIL
     stands until a new build; a refusal of a criterion cut on the ledger stands until its prose holds it whole);
     UNMEASURED retries after live.unmeasured_retry_s;
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


LIVE_MODS = re.compile(r"^\s*(?:[-*]\s+)?`?live-mods\s*:\s*(?P<mods>[^`]*)`?\s*$")


def live_mods(text):
    """A live_proofs file -> the mod folders its `live-mods:` lines name (every line, in order, no repeats)."""
    out = []
    for line in (text or "").splitlines():
        m = LIVE_MODS.match(line)
        if m:
            out += [x for x in re.split(r"[\s,]+", m.group("mods")) if x and x not in out]
    return out


TERMINAL = ("PASS", "FAIL", "REFUSED")


def history(rows):
    """runs.jsonl rows -> {(item, criterion, sha): the row that decides}: a terminal row (PASS, FAIL, REFUSED) stands for
    its build whatever came after it; otherwise the newest row."""
    out = {}
    for row in rows:
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
        for cid in owed:
            if cid not in proofs:
                skip("no proof")
                continue
            last = hist.get((it["id"], cid, it["built_sha"]))
            if last and last.get("cut") and not crit[cid].get("cut"):
                last = None     # refused while cut on the ledger; its prose now holds it whole: run it
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
    if any(m in folded for m in mods):
        return " ".join(["--compose biomes"] + ["--with %s" % m for m in mods if m not in folded])
    return " ".join("--mod %s" % m for m in mods)


def mod_gap(fx, sha, text, running=True):
    """What a run of this build would find missing from the game, asked BEFORE a game slot is spent
    (LIVE_MODLIST_ENFORCE_BEFORE_SLOT: 6 of 28 live runs were HORRORS 'UtinniPatches not enabled in ModsConfig',
    GRAFFITI 'not in the running load', DRAWBRIDGE a stale FlowWorks DLL). The build's mods plus its `live-mods:` are
    planned once (deploy_custom_mods.py, read only). -> {"mods", "off": {folder: flag} (NOT DEPLOYED / not enabled in
    ModsConfig), "dll": [stale or missing DLLs in the game folder], "running": why the RUNNING load lacks them or None,
    "error": why the plan could not be read or None}. running=False skips the bridge read (no game, or a staging)."""
    out = {"mods": [], "off": {}, "dll": [], "running": None, "error": None}
    try:
        mods = sorted(set(fx.mods_of(sha)) | set(live_mods(text)))
    except ValueError as e:
        out["error"] = str(e)[:200]
        return out
    out["mods"] = mods
    if not mods:
        return out
    rc, plan = fx.deploy_plan(deploy_args(mods, fx.folded()), L.live_rules({}).get("plan_max_s", 300))
    if rc not in (0, 1):
        out["error"] = "the deploy plan failed (exit %s): %s" % (rc, (plan or "")[-200:])
        return out
    _covered, drift, off = L.plan_sections(plan)
    out["off"] = off
    out["dll"] = sorted({"%s/%s" % (sec, e) if not e.startswith(sec + "/") else e
                         for sec, flag, e in drift if flag != "H" and e.lower().endswith(".dll")})
    if running:
        out["running"] = fx.running_load_gap(mods)
    return out


class RoundFx(L.Fx):
    """relentless_live.Fx plus what a round needs: every item, one plan per args, the lane and the compose manifest."""

    def __init__(self, *a, **kw):
        L.Fx.__init__(self, *a, **kw)
        self._plans = {}

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

    def mods_of(self, sha):
        return sorted({m for m, _ in L.game_files(self.touched(sha), self.shippable)})


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
    todo, counts = plan(fx, root, r, now, only, L.iso(started))
    summary.update(eligible=len(todo), skipped=counts, **({"only": only} if only else {}))
    folded, ran, cap = None, 0, max_items or lr["round_max"]
    for item_id, cid, proof, sha in todo:     # the cap counts runs: a skip never starves the items behind it
        if ran >= cap:
            break
        try:
            mods = fx.mods_of(sha)
        except ValueError as e:
            summary["runs"].append({"item": item_id, "criterion": cid, "outcome": "UNMEASURED", "why": str(e)[:200]})
            continue
        if folded is None:
            folded = fx.folded()
        ran += 1
        text = fx.proofs(item_id)
        row = run(fx, root, item_id, cid, proof, deploy_args(mods, folded), r, now=time.time(),
                  needs=live_mods(text), site=proof_lines(text, SITE_LINE).get(cid))
        summary["runs"].append({k: row.get(k) for k in ("item", "criterion", "outcome", "why", "sha")})
        if row["outcome"] == "UNMEASURED" and any(row.get("why", "").startswith(s) for s in STOP):
            return done("stopped: %s" % row["why"][:200])
    return done("done")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("eligible", help="what a round would try now, and the counts of what it would skip")
    p = sub.add_parser("round", help="one sitting: run every due criterion that has a proof, up to --max")
    p.add_argument("--max", type=int, default=None)
    p.add_argument("--item", help="this item only, no unmeasured wait: the supervisor's game phase")
    a = ap.parse_args(argv)
    with open(os.environ.get("RELENTLESS_RULES") or L.RULES, encoding="utf-8") as f:
        r = json.load(f)
    root = os.environ.get("RELENTLESS_ROOT") or "/home/mandrake/rm/relentless"
    fx = RoundFx(seat=r.get("seat") or "BENCH")
    if a.cmd == "eligible":
        todo, counts = plan(fx, root, r, time.time())
        print(json.dumps({"eligible": [list(t[:3]) for t in todo], "skipped": counts}, indent=1, sort_keys=True))
        return 0
    os.makedirs(os.path.join(root, "live"), exist_ok=True)
    with open(os.path.join(root, "live", "round.lock"), "w") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("a round is running")
            return 0
        print(json.dumps(run_round(fx, root, r, max_items=a.max, only=a.item), indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
