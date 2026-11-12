#!/usr/bin/env python3
"""relentless_game.py -- Relentless's second mode: an item that needs the running game (RELENTLESS_LIVE_BUILD_ONE_AGENT_TWO_MODES).

Owner, 2026-11-02: "I gut says equip the same agent to understand appropriate use of resources." Conductor's ruling: ONE
Relentless, two modes. Design and gap analysis: design/RimMandrake/relentless_live_mode_2026-11-02.md.

The worker is the same worker. It works offline first and names, in its contract, the clauses that truly need the game
(`contract --game A2,B3 --game-why ...`), each with a `live-proof <crit>: <cmd>` line in
infrastructure/state/live_proofs/<ID>.txt. The blind checker passes the offline proof as for any item. Then, instead of
`close`, the supervisor puts the item in status `game` and walks it through:

  implement  `rimflow implemented --sha` on the PASSED sha: the game clauses become owed criteria at their live levels
             (from infrastructure/state/live_proofs/<ID>.criteria at that sha when the item's own criteria lack them);
  prove      the BLIND live check: relentless_live_round.py round --item <ID>, which reruns each proof line through
             relentless_live.run (deploy check, flyer refusal, bridge take --idle-ok and release at once, `verify` on the
             built sha). No worker notes reach it. All PASS: the ledger's last verify makes the item done. A FAIL goes
             back to an offline worker with the live finding. Not deployed, or no game: stage;
  stage      the one step that changes the game: the supervisor takes the bridge (`bridge take --idle-ok`, which keeps
             his OWNER hold and `./bridge` override) and launches ONE staging worker that deploys and restarts the game
             on the smallest list that holds the item's mods, then exits. The bridge is released the moment it ends,
             or once the game it staged has been UP stage_idle_s (staged_idle): a worker still alive then holds the
             game for nothing. A clause whose proof ran and measured nothing on this game and build goes back to a
             worker at once (blocked_here): the round will not rerun it until the build or the game changes.

  final      PROOF_TIERS_WIDEN_SMALL_LIST_FIRST_ALWAYS (owner 2026-11-02: "small mod lists should always be the way to
             test until a final verification pass on the whole huge mod list"): every clause but a GREEN-FULL one is
             proved on the smallest list that holds the item's mods; a GREEN-FULL clause is the FINAL verification on the
             whole list. An item whose other clauses all PASS and whose final clauses read "final verification waits for
             the full list" waits here, holding nothing; a newer game gets one try; when final_batch_min items wait (or
             the oldest has waited final_wait_s) the oldest stages ONE full-list load that carries them all.

The lease rule, enforced here and nowhere else: no bridge for an item whose offline proof is not green on the same sha
(unless its contract says why none is possible), whose game clauses lack a proof line, that names flight, or while
another item holds a game phase. One live user at a time.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time
try:                                    # whole text, never a silent cut (RIMMANDRAKE_STORE_TEXT_WHOLE_NO_CUTS)
    from . import fulltext
except ImportError:
    import fulltext  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless_expedite  # noqa: E402
import relentless_envcause  # noqa: E402
NO_VERDICT = ("UNMEASURED", "NOT_ADMITTED")     # relentless_live.NO_VERDICT: a NOT_ADMITTED row routes as it did before

GAME = "game"
READING_TTL_S = 30
DEFAULTS = {"enabled": False, "pool_needs": ["deploy", "game-up", "bridge"], "stage_max_s": 3600, "stage_tries": 2,
            "prove_every_s": 900, "renew_s": 1200,
            # STAGING_REWIRE_PYTHON_NOT_AN_LLM: the staging unit runs relentless_stage.py, not an LLM (false: the old
            # pilot_agent staging worker, the stage prompt as its brief)
            "stage_python": True,
            # LIGHTSPEED_REWIRE_ROUND_AS_TESTQ_CLIENT: a clause with no live-tier goes to SteveDesktop on the tier its
            # mods name (relentless_live_round.inferable); false keeps it on Archmagi's round
            "steve_infer": True,
            # a cold load's bound is NOT set here: it is Utils/load_policy.json's process_to_bridge_deadline_s for the
            # list that loads (BRIDGE_DEADLINES_UNIFY_ONE_ABSOLUTE_POLICY), and passing it restages only on stall
            # evidence, never on the clock alone (load_bound, load_stall_evidence)
            # stage_tries stagings that leave no running build are a HARNESS failure, never the owner's: put down, and
            # staged again after harness_retry_s x the count, at most harness_retry_max_s
            "harness_retry_s": 1800, "harness_retry_max_s": 14400,
            # owner 2026-11-02, to save game loads: an item that needs a reload waits up to batch_wait_s while another
            # game item has not yet been tried on the RUNNING game; the reload then deploys every waiting item at once
            "batch_wait_s": 1800,
            # PROOF_TIERS_WIDEN_SMALL_LIST_FIRST_ALWAYS: one full-list load (15-25 min) verifies a batch of final clauses
            "final_batch_min": 4, "final_wait_s": 8 * 3600,
            # a clause whose proof ran and measured nothing this many times on one build goes back to a worker
            "unmeasured_back": 2,
            # RELENTLESS_DIAGNOSE_REPRO_MISS_AS_GAME_FAIL: a defect-repro proof that ran on its site and missed this many
            # times on one build holds the item as not reproduced (no builder: no code change makes a defect appear)
            "repro_miss_limit": 2,
            # RELENTLESS_GAME_HOLD_UNSTICK_IDLE_LIVE_ITER: a live-iterating worker that has not held the bridge for its item this
            # long is working offline, not on the game; its hold lapses so the next item may prove (ATMOSBASE held the
            # game 47 min, bridge free, ten items waiting, 2026-11-03)
            "live_idle_s": 1200,
            # LIVE_SLOTS_MEASURE_NOT_REFUSE_IN_SLOT: a staging whose game has been UP this long since a start after the
            # staging began has done its load; a worker still alive then holds the game for nothing (ART_OVERRIDE's
            # staging held the bridge 18:20-19:20Z, 2026-11-03, while 40 game items waited)
            "stage_idle_s": 600}
CLAUSE = re.compile(r"^[A-Z]{1,3}\d{1,3}$")
PROOFS_DIR = "infrastructure/state/live_proofs"
# UNMEASURED reasons (relentless_live.run's own words) that only a deploy or a restart can change
# "reload needed": relentless_live asks for one when the same cause stopped a criterion repeat_unmeasured times on one game
RESTAGE = ("not deployed", "no running game to test", "the game started", "not in the running load", "reload needed")
SESSIONS = "live_sessions.json"
FINAL_LEVEL = "GREEN-FULL"      # relentless_live.FINAL
FINAL_WAIT = "final verification waits for the full list"      # relentless_live.FINAL_WAIT: a row's why, never a restage
ACTIVE = ("staging", "proving")

BRIEF = [
    "RESOURCES: the running game is scarce. ONE live user at a time, and a cold load costs minutes to a quarter hour. "
    "Prove everything you can offline first: unit tests, def and patch validation (validate_patch.py), offline DLL tests "
    "of geometry and arithmetic (sweep the whole space in Python, then port), log and save reads. Only a clause that "
    "truly needs the running game goes live, and you never drive the game yourself: name those clauses with "
    "`contract ... --game A2,B3 --game-why \"why only the game can show it\"` (or `--no-offline \"why no offline proof "
    "is possible\"`), and give each one line in infrastructure/state/live_proofs/<ID>.txt: `live-proof A2: <command>`, "
    "a read-only command that exits 0 when the clause holds, 1 when it does not, and 2 with `UNMEASURED: <reason>` on "
    "one line when it could not ask; literal text, no `$`, no poll loop (advance with B.ticks); the rules and their "
    "reasons are in skills/live-debugging-proof-harness/references/lightspeed-authoring.md. Batch: one proof per clause, every "
    "clause in one file, so one sitting proves them all. If a clause is not on the item's ledger criteria, add it to "
    "infrastructure/state/live_proofs/<ID>.criteria as `A2 L1: what is observed` (L1 minimal-list read, L2 behaviour on a "
    "quicktest map). The supervisor leases the bridge, deploys and restarts only when your offline proof is green on the "
    "same sha, then reruns the live proofs blind. Never a flyer's flight; never fullscreen or focus the game; the minimal "
    "mod list (all five DLC) when it is enough. A proof that measures one EXACT list (a tier-makeup bar, a perf toll) "
    "adds `live-tier: <tier>` (every clause) or `live-tier A1: <tier>` (a src/RimMandrake/Utils/modset_builder.py tier, "
    "`--list`): that clause runs on SteveDesktop through testq, which loads the tier as the whole list and records what "
    "ran (owner by card 2026-11-05: SteveDesktop is the exact-tier host); Archmagi's list is never swapped for it.",
    "An item that IS a deploy (nothing to change, only trees to put in the game folder): you never --apply and need no "
    "game. Commit that .txt with `live-deploy: ModA, ModB` and `live-proof A1: python3 "
    "src/RimMandrake/rimflow/relentless_live_round.py deployed --item <ID>`, the .criteria line `A1 L1: the game folder "
    "holds these trees`, and `contract --proof \"python3 src/RimMandrake/rimflow/relentless_live_round.py deployed --item "
    "<ID> --lint\" --game A1 --game-why ...`, then `finish` on that commit. The staging worker applies them.",
]


def cfg(r):
    out = dict(DEFAULTS)
    out.update((r or {}).get("game") or {})
    return out


def pool_needs(r):
    """The extra `needs` values the pool takes when the game mode is on."""
    c = cfg(r)
    return list(c["pool_needs"]) if c["enabled"] else []


def parse_game(clauses, why, no_offline):
    """CLI words -> the contract's `game` block, or None when none was given. Raises ValueError on a half block."""
    if not clauses and not why and not no_offline:
        return None
    ids = [c.strip() for c in re.split(r"[,\s]+", clauses or "") if c.strip()]
    bad = [c for c in ids if not CLAUSE.match(c)]
    if not ids or bad:
        raise ValueError("--game names criterion ids like A2,B3 (got %r)" % (clauses,))
    if not (why or "").strip():
        raise ValueError("--game needs --game-why: why only the running game can show these clauses")
    out = {"clauses": sorted(set(ids)), "why": why.strip()}
    if (no_offline or "").strip():
        out["no_offline"] = no_offline.strip()
    return out


def owes(st, sha):
    """The item's contract names game clauses not yet proved on `sha`."""
    g = (st.get("contract") or {}).get("game")
    return bool(g and g.get("clauses")) and (st.get("game") or {}).get("passed_sha") != sha


def checker_lines(contract):
    g = (contract or {}).get("game")
    if not g:
        return []
    return ["GAME CLAUSES %s are proved later, on the running game, by rerunning their lines in "
            "infrastructure/state/live_proofs/<ID>.txt; you cannot run them here. Judge the offline proof as always, "
            "then read each of those lines: a missing line, or one that would stay green while its clause was broken "
            "(it reads nothing the clause names, or cannot exit 1), is WEAK. %s"
            % (", ".join(g["clauses"]), ("The contract says no offline proof is possible: %s. Check that is true; if an "
                                         "offline proof was possible, WEAK." % g["no_offline"]) if g.get("no_offline")
                                        else "")]


def proof_lines(text):
    import relentless_live_round
    return relentless_live_round.proof_lines(text)


def gate(st, title, proofs_text, flyer_re, other):
    """-> why this item may not have the bridge now, or None. Pure.
    other: the id of another item in an active game phase, or None."""
    g = st.get("game") or {}
    k = (st.get("contract") or {}).get("game") or {}
    if other:
        return "one live user at a time: %s holds the game phase" % other
    green = g.get("offline_green") or {}
    if green.get("sha") != g.get("sha") and not k.get("no_offline"):
        return "no green offline proof on %s" % g.get("sha")
    lines = proof_lines(proofs_text)
    lacking = [c for c in k.get("clauses") or [] if c not in lines]
    if lacking:
        return "no live-proof line for %s" % ", ".join(lacking)
    import relentless_live
    lr = dict(relentless_live.DEFAULTS, flyer_re=flyer_re)
    if relentless_live.flyer_word(lr, title, *[("proof", lines[c]) for c in k.get("clauses") or []]):
        return "flyer: a flyer's flight is never live-tested without the owner present"
    return None


def other_active(states, item):
    for s in states:
        if s["item"] != item and s["status"] == GAME and (s.get("game") or {}).get("phase") in ACTIVE:
            return s["item"]
        if s["item"] != item and s["status"] == "running" and s.get("live_iter"):
            return s["item"]        # a worker iterating on the running game is its one live user
        if s["item"] != item and s["status"] == "retiring" and s.get("release_bridge"):
            return s["item"]        # a dropped item's staging worker not yet settled still drives the game
    return expedited_ahead(states, item) if item is not None else None


def busy(store, item):
    """other_active, or a showing build that holds the game (relentless_showing): the bridge it holds is Relentless's
    own, so a staging or a proof round would take it again and restart the game under the showing being built."""
    import relentless_broker
    return other_active(store.states(), item) or showing_live(store) or relentless_broker.busy(store)


def showing_live(store):
    """-> "showing <ITEM>" while a showing build holds the bridge, else None."""
    try:
        with open(store.p("showings.json"), encoding="utf-8") as f:
            rows = (json.load(f) or {}).get("rows") or {}
    except (OSError, ValueError, AttributeError):
        return None
    for iid, row in sorted(rows.items()):
        if isinstance(row, dict) and row.get("phase") == "build" and row.get("bridge"):
            return "showing %s" % iid
    return None


def expedited_ahead(states, item):
    """An expedited item waiting its turn on the game goes next: nothing behind it starts. It stops no one (owner's card
    2026-11-03: "leaves the live game alone"), and one put down on a retry holds nothing; its 4 h expiry bounds the rest."""
    mine = next((s.get("expedite") for s in states if s["item"] == item), None)
    best = None
    for s in states:
        e, g = s.get("expedite"), s.get("game") or {}
        if (s["item"] != item and e and s["status"] == GAME and g.get("phase") in ("prove", "stage", "final")
                and not g.get("retry_at") and (not mine or relentless_expedite.rank(e) < relentless_expedite.rank(mine))
                and (best is None or relentless_expedite.rank(e) < relentless_expedite.rank(best["expedite"]))):
            best = s
    return best["item"] if best else None


def untried(states, item, started):
    """Another game item waiting to prove that has not been tried on the game that started at `started`: the running
    game may serve it without a load, so it goes before a reload (owner 2026-11-02: "To save game loads")."""
    for s in states:
        g = s.get("game") or {}
        if (s["item"] != item and s["status"] == GAME and g.get("phase") == "prove" and not g.get("waits_reload")
                and (g.get("proved_at") or 0) < started):
            return s["item"]
    return None


def batch(states, item, now, full=False):
    """The other game items waiting for a reload: the one staging deploys them all. A full-list staging also carries
    every item waiting in phase final (its one load verifies them all)."""
    return [s for s in states if s["item"] != item and s["status"] == GAME
            and ((s.get("game") or {}).get("waits_reload") or ((s.get("game") or {}).get("phase") == "stage"
                                                               and not (s["game"].get("retry_at") or 0) > now)
                 or (full and (s.get("game") or {}).get("phase") == "final"))]


def finals_waiting(states):
    """The game items waiting in phase final, expedited (by relentless_expedite.rank) then oldest first:
    [(final_since, item)]. The expedited order is expedited_ahead's: ordered by age instead, an older expedited final
    heads the queue while a better-ranked one is ahead of it in busy(), and neither ever stages (Codex cd905b #1)."""
    rows = [s for s in states if s["status"] == GAME and (s.get("game") or {}).get("phase") == "final"]
    rows.sort(key=lambda s: (not s.get("expedite"), relentless_expedite.rank(s["expedite"]) if s.get("expedite") else (0, 0),
                             s["game"].get("final_since") or 0, s["item"]))
    return [(s["game"].get("final_since") or 0, s["item"]) for s in rows]


def final_split(rows, owed, clauses, started):
    """-> (final clauses, waiting) where waiting is True when every non-final clause PASSed and every final clause
    either PASSed or read FINAL_WAIT on the game that started at `started` (so this game cannot verify it)."""
    finals = [k for k in clauses if owed.get(k) == FINAL_LEVEL]
    if not finals:
        return finals, False
    small_ok = all((rows.get(k) or {}).get("outcome") == "PASS" for k in clauses if k not in finals)
    waits = [k for k in finals if (rows.get(k) or {}).get("outcome") in NO_VERDICT
             and (rows[k].get("why") or "").startswith(FINAL_WAIT) and (not started or row_at(rows[k]) >= started)]
    rest_ok = all(k in waits or (rows.get(k) or {}).get("outcome") == "PASS" for k in finals)
    return finals, bool(small_ok and waits and rest_ok)


def session_note(store, started, item, served=False, reload_why=None, mods=None, now=None):
    """store/live_sessions.json, one entry per game process (keyed by its start): the items it served, the reloads its
    workers proved they need, and the loads it saved (each item served beyond the first would have cost its own)."""
    if not started:
        return None
    now = time.time() if now is None else now
    p = store.p(SESSIONS)
    with store.lock():
        try:
            with open(p, encoding="utf-8") as f:
                book = json.load(f)
        except (OSError, ValueError):
            book = {}
        e = book.setdefault(str(int(started)), {"started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
                                                "served": [], "reload_needed": {}, "loads_saved": 0})
        if mods:
            e["modsconfig_mods"] = mods
        if served and item not in e["served"]:
            e["served"].append(item)
        if reload_why:
            e["reload_needed"][item] = reload_why
        e["loads_saved"] = max(0, len(e["served"]) - 1)
        e["last"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
        for k in sorted(book, key=lambda k: int(k))[:-50]:
            book.pop(k)
        tmp = p + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(book, f, indent=1, sort_keys=True)
        os.replace(tmp, p)
    return e


def enter(store, st, sha, now):
    """Under the store lock: an offline PASS on `sha` for an item that owes game clauses. The PASS is the green offline
    proof the lease rule asks for, on this same sha."""
    k = st["contract"]["game"]
    st.pop("live_iter", None)
    st["status"] = GAME
    st["game"] = {"sha": sha, "phase": "implement", "clauses": list(k["clauses"]), "stages": 0, "entered_at": now,
                  "offline_green": {"sha": sha, "at": now, "nonce": (st.get("check") or {}).get("nonce"),
                                    "contract": contract_print(st.get("contract"))}}
    store.save(st)


def contract_print(contract):
    """The contract's fingerprint as the Judge read it. reach_ok is left out: it says the box may be passed, not what is proved."""
    import hashlib
    k = {a: b for a, b in (contract or {}).items() if a != "reach_ok"}
    return hashlib.sha256(json.dumps(k, sort_keys=True, default=str).encode()).hexdigest()[:16]


def green_stands(st, attempts=()):
    """-> why the Judge's PASS already on the candidate's sha still stands, or None. Pure. A candidate that a hold, an
    unhold or a lifted wait sent back to the Judge on a sha it already passed (offline_green), with game clauses still
    owed and the contract as it read it, would only pay a Judge to say PASS again (PASS3_FLOOD_FIX_REJUDGE_GREEN_SHA, 4 such
    re-checks on 2026-11-05): it goes to its game step instead. The contract moved since (a fingerprint, or for an older
    green a contract row in `attempts` after it) or a CONTRACT binding found since: the Judge reads it afresh."""
    sha = (st.get("candidate") or {}).get("sha")
    green = (st.get("game") or {}).get("offline_green") or {}
    if not sha or green.get("sha") != sha or not owes(st, sha):
        return None
    if green.get("contract"):
        if green["contract"] != contract_print(st.get("contract")):
            return None
    else:
        since = int(green.get("at") or 0)     # a row keeps whole seconds: one in green's own second may follow it
        if any("contract" in a and row_at(a) >= since for a in attempts):
            return None
    held = st.get("proof_only") or {}
    if held.get("binding") and (held.get("at") or 0) > (green.get("at") or 0):
        return None
    return "the Judge passed %s already (%s): its game clauses are owed, not another check" % (
        sha[:12], time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(green.get("at") or 0)))


def reenter(store, st, now, why):
    """Under the store lock: back to the game step on the sha the Judge already passed, its offline green kept."""
    green = dict(st["game"]["offline_green"])
    green.setdefault("contract", contract_print(st.get("contract")))    # green_stands found it unchanged
    st.pop("recheck_at", None)
    st.pop("put_down", None)
    enter(store, st, green["sha"], now)
    st["game"]["offline_green"] = green
    st["game"]["reentered"] = {"at": now, "why": why}
    store.save(st)


def same_sha(a, b):
    """The ledger keeps a short sha, the store the full one."""
    return bool(a and b) and min(len(a), len(b)) >= 7 and (a.startswith(b) or b.startswith(a))


def row_at(row):
    import calendar
    try:
        return calendar.timegm(time.strptime(row.get("at", ""), "%Y-%m-%dT%H:%M:%SZ"))
    except ValueError:
        return 0


def void_rows(root, item, sha, why, now):
    """A void row in <root>/live/runs.jsonl: this item's earlier live rows on `sha` stop counting
    (relentless_live_round.history, not_measuring), because they were read through an instrument since attributed broken
    and repaired, or a person lifted its attribution hold (relentless_attrib.resume)."""
    p = os.path.join(root, "live", "runs.jsonl")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps({"item": item, "sha": sha, "void": True, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "why": (why or "")}) + "\n")


def outcomes(rows, item, sha, clauses):
    """runs.jsonl rows -> {clause: deciding row} on `sha` (relentless_live_round.history's rule)."""
    import relentless_live_round
    h = relentless_live_round.history(rows)
    return {c: h[(item, c, sha)] for c in clauses if (item, c, sha) in h}


RAN_DUD = re.compile(r"the proof (exited -?\d+: it did not measure|timed out)")   # -11: killed by a signal


def with_log(v):
    """A row -> its why, the log first, so the worker it goes back to reads the evidence however short the line is cut."""
    return "%s%s" % ("(%s) " % v["log"] if v.get("log") else "", v.get("why") or "")


def not_measuring(rows, item, sha, clauses, limit):
    """-> {clause: (rows, newest why)} for each clause whose proof RAN on `sha` and exited neither PASS nor FAIL at least
    `limit` times (OPS_RELENTLESS_LIVE_MEASURE_RESTORE_LRPU: one build re-proved 4x, then reloaded, all UNMEASURED)."""
    out = {}
    for v in rows:
        if v.get("void") and v.get("item") == item and same_sha(v.get("sha"), sha):
            out = {}        # read through an instrument since repaired (relentless_attrib.resume): those duds are void
            continue
        if (v.get("item") == item and v.get("criterion") in clauses and (v.get("sha") == sha or same_sha(v.get("sha"), sha))
                and v.get("outcome") == "UNMEASURED" and RAN_DUD.search(v.get("why") or "")):
            n, _ = out.get(v["criterion"], (0, ""))
            out[v["criterion"]] = (n + 1, with_log(v))
    return {k: v for k, v in out.items() if limit and v[0] >= limit}


def repro_misses(rows, item, sha, clauses, since=0):
    """-> {clause: (misses, [their verdict lines, oldest first])}: rows where the clause's defect-repro proof ran on `sha`
    (its site prepared, so the site was the one it asked for) and said it did not reproduce (relentless_live.REPRO_MISS),
    written after `since` (the last not-reproduced hold: a person who lifts it buys fresh tries). A void row resets."""
    import relentless_live
    out = {}
    for v in rows:
        if v.get("void") and v.get("item") == item and same_sha(v.get("sha"), sha):
            out = {}
            continue
        if (v.get("item") == item and v.get("criterion") in clauses and (v.get("sha") == sha or same_sha(v.get("sha"), sha))
                and v.get("outcome") == "UNMEASURED" and v.get("miss")
                and (v.get("why") or "").startswith(relentless_live.REPRO_MISS) and row_at(v) > since):
            n, ws = out.get(v["criterion"], (0, []))
            out[v["criterion"]] = (n + 1, ws + [with_log(v)])
    return out


def fail_detail(k, v):
    """One game_fail clause -> "<k> FAIL on the running game (<log>): <the proof's last verdict line>". The row carries
    the line (relentless_live.run, verdict_line); an older row has it read back from its log."""
    import relentless_live
    line = v.get("verdict_line")
    if line is None and v.get("log"):
        line = relentless_live.last_verdict(v["log"])
    line = (line or "").replace(";", ",")     # relentless_breakers.LIVE_FAIL_RX splits clauses on ";"
    return "%s FAIL on the running game (%s)%s" % (k, v.get("log") or v.get("why"), ": " + line if line else "")


def staged_idle(fx, g, c, now):
    """-> (why, up_seen): why a live staging is over in all but name, or None: the game is UP, started after the staging
    began, and has been SEEN up stage_idle_s since. The staging's step then ends its run (settle) and releases the bridge,
    as at stage_max_s. up_seen is {"started", "at"}: when this supervisor first read THIS process UP (the caller keeps it
    on g). The clock runs from that reading, never from process start: a 25-minute full-list load is LOADING for 25
    minutes, and measured from its start it read idle on its first UP reading (Codex r4 game0 #1)."""
    rd = fx.game_reading() or {}
    started = rd.get("started")
    seen = g.get("up_seen")
    if rd.get("state") != "UP" or not started or started <= (g.get("staged_at") or 0):
        return None, seen
    if not seen or seen.get("started") != started:     # a new process: its clock starts at this reading
        seen = {"started": started, "at": now}
    up = now - seen["at"]
    if up < c["stage_idle_s"]:
        return None, seen
    return "the game it staged has been seen UP %ds (started %s, first seen UP %s, limit %ds): the load is done" % (
        up, time.strftime("%H:%M:%SZ", time.gmtime(started)), time.strftime("%H:%M:%SZ", time.gmtime(seen["at"])),
        c["stage_idle_s"]), seen


def blocked_here(rows, clauses, sha, started, now):
    """-> {clause: why} of the proof-ran-and-measured-nothing clauses, when EVERY clause not yet PASSed is one the round
    will not run again on the game that started at `started` (relentless_live_round.due: a dud or FINAL_WAIT on this
    game and build) and at least one is a dud; else {}. LIVE_SLOTS_MEASURE_NOT_REFUSE_IN_SLOT: the round no longer reruns
    those, so without this the item would sit in prove until some other item reloaded the game."""
    if not started:
        return {}
    import relentless_live
    import relentless_live_round as R
    game = relentless_live.iso(started)
    out = {}
    for k in clauses:
        v = rows.get(k)
        if (v or {}).get("outcome") == "PASS":
            continue
        why = R.due(v, v.get("sha"), now, 0, game, per_game=False) if v else None
        if why not in (R.DUD_HERE, R.WAITS_TIER):
            return {}
        if why == R.DUD_HERE:
            out[k] = with_log(v)
    return out


# ---- exact-tier clauses: SteveDesktop through testq (LANE_TIER_WIRE_A_WHOLE_LIST_LOAD) -------------------------------
# Owner by card 2026-11-05, "What should SteveDesktop spend its time on now? -> Exact-mod-list tests": a clause whose proof
# needs an exact list runs on SteveDesktop, never on Archmagi's game, which keeps its own list. One testq job per
# (item, tier) on the built sha; Steve's admission keeps a tier's train, so riders batch only within a tier.
TESTQ_PY = "src/RimMandrake/Utils/testq/testq.py"
STEVE_BY = "RELENTLESS"
STEVE = "testq"     # runs.jsonl row["source"] of a SteveDesktop verdict
STEVE_WAIT, STEVE_FAIL = "wait", "fail"     # steve_sync's answers: stop here / a FAIL row, the prove phase returns it
STEVE_HEAD = re.compile(r"^(?:exit -?\d+|timed out after \d+ s): ")   # worker.run_proofs's head on a proof row


def tier_clauses(text, clauses, owed=None, inferred=None):
    """-> {tier: [clause]} for the clauses a `live-tier:` line sends to SteveDesktop. ValueError on a malformed line.
    owed: {clause: level}; a GREEN-FULL clause is the full list's final check on Archmagi, never a tier's.
    inferred: (the mods__ tier this build's mods name, the clauses that went back to Archmagi): every other clause
    relentless_live_round.inferable passes goes to that tier (LIGHTSPEED_REWIRE_ROUND_AS_TESTQ_CLIENT)."""
    import relentless_live_round as LR
    tiers = LR.live_tiers(text)
    tier, back = inferred or (None, ())
    out = {}
    for k in clauses:
        level = (owed or {}).get(k)
        t = None if level == FINAL_LEVEL else LR.clause_tier(text, k, tiers)
        if not t and tier and k not in back and LR.inferable(text, k, level, tiers):
            t = tier
        if t:
            out.setdefault(t, []).append(k)
    return out


def is_inferred(tier):
    import relentless_live_round as LR
    return (tier or "").startswith(LR.MODS_TIER)


def steve_inferred(fx, c, item, sha):
    """-> (the mods__ tier for this build, the clauses it gave back to Archmagi) or None: inference off, a fake world
    without it, a build whose modset_builder cannot resolve mods__ names, or mods that cannot be named (that last one
    gives every clause back, with its why, so Archmagi's round runs them and steve_sync never asks again)."""
    if not (c.get("steve_infer") and c.get("enabled")) or not hasattr(fx, "infer_tier") or not fx.sha_infers(sha):
        return None
    back = set(fx.steve_fell_back(item, sha))
    tier, why = fx.infer_tier(item, sha)
    if not tier:
        fx.steve_fallback(item, sha, ["*"], "no inferred tier: %s" % why)
        return None
    return tier, back


def steve_unmeasured(detail):
    """A proof exit 1 that is an inability, not a miss (relentless_live's EXIT1_HARNESS / EXIT1_RELOAD, read over the
    log tail the row carries): the reason, or None for a real FAIL."""
    import relentless_live as L
    # the worker's row is "exit 1: <the log's tail>": the head is the worker's, the lines are the proof's
    for line in STEVE_HEAD.sub("", detail or "", count=1).splitlines():
        if L.EXIT1_HARNESS.search(line) or L.EXIT1_RELOAD.search(line.strip()):
            return line.strip()
    return None


def steve_rows(job, res, item, sha, clauses, now):
    """A counted testq result -> ({clause: runs.jsonl row} for each clause it judged PASS or FAIL, {clause: why} for
    the rest). A result whose load was not the tier judges nothing (tier_load.py: exact false)."""
    tier = res.get("tier") or {}
    byid = {r.get("row"): r for r in res.get("rows") or [] if r.get("chain") == "proofs"}
    rows, unmeasured = {}, {}
    for k in clauses:
        v = byid.get(k)
        if res.get("outcome") != "DONE" or not tier.get("exact"):
            unmeasured[k] = (tier.get("why") or "%s/%s: %s" % (res.get("outcome"), res.get("cause"), res.get("note") or ""))
            continue
        if not v or v.get("verdict") not in ("PASS", "FAIL"):
            unmeasured[k] = (v or {}).get("detail") or "no row for %s in %s" % (k, res.get("attempt"))
            continue
        inability = v["verdict"] == "FAIL" and steve_unmeasured(v.get("detail"))
        if inability:
            unmeasured[k] = inability
            continue
        rows[k] = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "item": item, "criterion": k,
                   "sha": sha, "outcome": v["verdict"], "verdict": v["verdict"], "source": STEVE, "job": job["id"],
                   "attempt": res.get("attempt"), "tier": job_tier(job), "running": len(res.get("running") or []),
                   "proof_exit": 0 if v["verdict"] == "PASS" else 1,
                   "why": ("SteveDesktop %s, tier %s exact (%d running mods): %s"
                           % (res.get("attempt"), job_tier(job), len(res.get("running") or []),
                              (v.get("detail") or "")))}
    return rows, unmeasured


def steve_cost(root, jb, rec, item, sha, tier, judged, dud, now):
    """One proof cost row (proof_cost.py) per clause a counted testq job answered, PASS/FAIL or not: its wait is the
    job's submission to this read of its result (an upper bound by the poll interval); SteveDesktop's bridge time is not
    seen from here, so held/staging/proving read None. A job read again on a later tick (a dud whose resubmission
    waits) writes nothing twice: one row per (job, clause). Never raises."""
    import proof_cost
    sub = jb.get("submitted")
    marks = {"start": sub if isinstance(sub, (int, float)) else None, "ended": now, "held_unknown": True}
    jid = (rec.get("job") or {}).get("id")
    try:
        done = {r.get("clause") for r in proof_cost.read(os.path.join(root, proof_cost.LEDGER))
                if r.get("source") == "testq" and jid and r.get("job") == jid}
    except Exception:       # noqa: BLE001  an unread ledger writes the row (a duplicate beats a lost one)
        done = set()
    out = []
    for k in sorted((set(judged) | set(dud)) - done):
        outcome = judged[k]["outcome"] if k in judged else "UNMEASURED"
        try:
            tok = proof_cost.staging_tokens(root, item)
        except Exception:   # noqa: BLE001  an unread spend record is an UNMEASURED cost
            tok = {"tokens": None}
        tokens = tok.pop("tokens", None)
        out.append(proof_cost.record(root, "testq", item, k, sha, tier, outcome, marks, tokens=tokens,
                                     why=dud.get(k), job=jid, **tok))
    return out


def job_tier(job):
    p = job.get("profile") or ""
    return p.split(":", 1)[1] if p.startswith("tier:") else None


def steve_sync(store, fx, r, item, g, sha, now, acts):
    """The game phase's exact-tier half, every tick of prove and stage: submit each tier's open clauses as one testq job,
    read the finished job through fault_monitor.gate (quarantine or hold: no verdict, it waits or resubmits), verify each
    PASS/FAIL per criterion and write its runs.jsonl row; a result that measured nothing resubmits, up to steve_tries,
    then holds. -> True when the step must stop here: every clause still open is a tier clause (nothing for Archmagi's
    game to do), the item was held, or the lane refused: STEVE_WAIT; FAIL when a clause's row is a FAIL (the prove
    phase returns the item); else None (Archmagi serves the rest, the round skips these)."""
    c = cfg(r)
    led = fx.game_ledger(item) or {}
    try:
        inferred = steve_inferred(fx, c, item, sha)
        if inferred and "*" in inferred[1]:
            inferred = None
        tiers = tier_clauses(fx.proofs_at(item, sha), g["clauses"], led.get("owed"), inferred)
    except ValueError as e:
        _hold(store, fx, item, "game phase: live-tier: %s" % e, now, acts)
        return STEVE_WAIT
    if not tiers:
        return None
    import relentless_live_round
    rows = outcomes(fx.game_rows(), item, sha, g["clauses"])
    jobs = dict(g.get("testq") or {})
    for tier in sorted(tiers):
        open_ = [k for k in tiers[tier] if not relentless_live_round.decides(rows.get(k))]
        jb = dict(jobs.get(tier) or {})
        if not open_:
            continue
        if jb.get("sha") and jb["sha"] != sha and not same_sha(jb["sha"], sha):
            jb = {}     # a job for an older build says nothing of this one; its tries were that build's
        got = fx.testq_job(jb["job"]) if jb.get("job") else {"state": None}
        state, verdict = got["state"], (got.get("gate") or (None, None))
        if state in ("pending", "running") or (state == "done" and verdict[0] == "hold"):
            acts.append({"do": "game_steve_wait", "item": item, "tier": tier, "job": jb["job"], "state": state})
            continue
        if state == "done" and verdict[0] == "count":
            rec = got["rec"]
            judged, dud = steve_rows(rec["job"], rec["result"], item, sha, open_, now)
            for k, row in sorted(judged.items()):
                level = (led.get("owed") or {}).get(k) or "L1"
                why = fx.steve_verify(item, k, level, sha, row["outcome"].lower(), "testq %s on SteveDesktop" % row["attempt"],
                                      "relentless-steve: tier %s, %s" % (tier, rec["job"]["id"]))
                if why:
                    dud[k] = "the verdict %s did not land: %s" % (row["outcome"], why)
                    continue
                fx.game_row_append(row)
            # after the verify: a verdict that did not land is a dud, never a measured cost row
            steve_cost(store.root, jb, rec, item, sha, tier, {k: v for k, v in judged.items() if k not in dud}, dud, now)
            acts.append({"do": "game_steve_result", "item": item, "tier": tier, "job": jb["job"],
                         "judged": sorted(judged), "unmeasured": sorted(dud)})
            if not dud:
                jobs[tier] = dict(jb, finished=now)
                continue
            jb["last_why"] = "; ".join("%s: %s" % (k, w) for k, w in sorted(dud.items()))
            open_ = sorted(dud)
        elif state == "quarantined" or (state == "done" and verdict[0] == "quarantine"):
            jb["last_why"] = "testq %s ran inside a SteveDesktop fault window: quarantined, never counted" % jb["job"]
            jb["tries"] = max(0, (jb.get("tries") or 1) - 1)    # the host's fault, not the clause's: not a try
            jb["quarantined"] = (jb.get("quarantined") or 0) + 1
            if jb["quarantined"] > c.get("steve_quarantines", 4):    # a host that keeps faulting: a person looks
                jobs[tier] = jb
                _save(store, item, lambda s: s["game"].update(testq=jobs))
                _hold(store, fx, item, "game phase: SteveDesktop faulted under %d jobs for %s on tier %s (fault_monitor "
                      "quarantine): %s" % (jb["quarantined"], ",".join(open_), tier, jb["last_why"]), now, acts)
                return STEVE_WAIT
        elif state == "cancelled":
            jb["last_why"] = "testq %s was cancelled" % jb["job"]
        if (jb.get("tries") or 0) >= c.get("steve_tries", 3) and is_inferred(tier):
            # an inferred tier is our guess at the list, not the proof's ask: Archmagi's round runs these clauses as it
            # did before Lightspeed, never a hold (relentless_live_round.fell_back skips them no more)
            jobs[tier] = dict(jb, fell_back=now)
            fx.steve_fallback(item, sha, open_, "SteveDesktop measured nothing in %d jobs on %s: %s"
                              % (jb["tries"], tier, jb.get("last_why") or "?"))
            acts.append({"do": "game_steve_fallback", "item": item, "tier": tier, "clauses": open_})
            for k in open_:
                tiers[tier].remove(k)
            continue
        if (jb.get("tries") or 0) >= c.get("steve_tries", 3):
            jobs[tier] = jb
            _save(store, item, lambda s: s["game"].update(testq=jobs))
            _hold(store, fx, item, "game phase: SteveDesktop measured nothing for %s on tier %s in %d jobs: %s"
                  % (",".join(open_), tier, jb["tries"], jb.get("last_why") or "?"), now, acts)
            return STEVE_WAIT
        job, why = fx.testq_submit(item, sha, tier, open_, fx.steve_deploy(item, sha))
        if why:
            _save(store, item, lambda s: s["game"].update(testq=jobs))
            _waits(store, fx, item, "testq: submit of tier %s refused: %s" % (tier, why), now, acts)
            return STEVE_WAIT
        jobs[tier] = dict(jb, job=job, sha=sha, clauses=open_, tries=(jb.get("tries") or 0) + 1, submitted=now)
        acts.append({"do": "game_steve_submit", "item": item, "tier": tier, "job": job, "clauses": open_})
    _save(store, item, lambda s: s["game"].update(testq=jobs))
    rows = outcomes(fx.game_rows(), item, sha, g["clauses"])
    steve = {k for ks in tiers.values() for k in ks}
    open_all = [k for k in g["clauses"] if not relentless_live_round.decides(rows.get(k))]
    if any(v.get("outcome") == "FAIL" for v in rows.values()):
        return STEVE_FAIL
    return STEVE_WAIT if open_all and all(k in steve for k in open_all) else None


STAGE_AGENT = "python_stager"   # relentless.Effects.launch runs relentless_stage.py in the unit for this agent


def game_companion_owed(fx, builds):
    """[(item, sha)] riding one load -> the shas whose JawaBench companion the game folder does not hold (fx
    .game_companion), in order, or None. Every rider counts, not the lead alone (COMPANION_DEPLOY_LIVE_ROUND_FORGETS:
    FW_PROOF_TOOLS_HARDEN_READ_GAPS rode HOSE_SITE_FIX_TERRAIN_WONT_READ_BACK's load and read STALE)."""
    if not hasattr(fx, "game_companion"):
        return None
    owed = []
    for item, sha in builds:
        got = fx.game_companion(item, sha)
        if got and got not in owed:
            owed.append(got)
    return owed or None


def stage_plan(st, c, sha, others, enable, dlls, trees, remedy, deploy_args=None, companion=None, menu=None,
               without=()):
    """What relentless_stage.py does for this staging (STAGING_REWIRE_PYTHON_NOT_AN_LLM), the stage prompt's steps as
    data. deploy: deploy_custom_mods.py argument strings, the build's mod folders (never a packageId: those are enabled,
    not deployed) with the stale-DLL ones and the lane fix's, then the `live-deploy:` trees. deploy_args: folders -> one
    argument string (GameFx.game_deploy_args: a folded biome folder plans through --compose biomes).
    companion: the built shas whose JawaBench companion the game folder lacks (game_companion_owed), or None: the
    stager builds and deploys one JawaBench holding them all in the shutdown window (LIVEROUND_COMPANION_DEPLOY_OLD_DLL_
    BLAMED; COMPANION_DEPLOY_LIVE_ROUND_FORGETS)."""
    import relentless_live_round as R
    folders = sorted({m for m in enable if not R.is_package(m)} | set(dlls) | set((remedy or {}).get("mods") or []))
    args = (deploy_args or (lambda ms: " ".join("--mod %s" % m for m in ms)))
    deploy = ([args(folders)] if folders else []) + ([trees[1]] if trees and trees[1] else [])
    return {"item": st["item"], "gen": st["gen"], "sha": sha, "full": bool((st.get("game") or {}).get("full")),
            "enable": sorted(enable), "deploy": deploy, "riders": [o["item"] for o in others],
            "remedy_cmds": list((remedy or {}).get("cmds") or []), "max_s": c["stage_max_s"],
            **({"companion": list(companion)} if companion else {}), **menu_plan(menu, without)}


def menu_plan(menu, without=()):
    """staging_menu() -> the stage plan's keys for it: menu_cmds (run at the main menu, before any game), for a
    live-toggle item `toggle` {"mod", "side"}, and `without`: the mods the load must lack (the toggle's without side and
    `without`, the batch's live-without mods: without_set), which the stager takes off with modlist_swap.py --disable.
    {} when there is none."""
    menu = menu or {}
    out = {"menu_cmds": list(menu["cmds"])} if menu.get("cmds") else {}
    off = set(without or ())
    if menu.get("toggle"):
        out["toggle"] = {"mod": menu["toggle"], "side": menu["side"]}
        if menu["side"] == "without":
            off.add(menu["toggle"])
    if off:
        out["without"] = sorted(off)
    return out


def staging_menu(fx, item, sha, stages, others=()):
    """-> {"cmds": [live-menu commands of the item and its riders, {toggle} filled], "toggle": mod or None, "side":
    with|without or None}, or raises ValueError (a malformed live-toggle, or {toggle} with no side). The side is the
    item's own: its stagings alternate, so a pair of loads comes from two stagings (STAGING_MENU_FIX_ALWAYS_PARKS_ON_MAPS)."""
    import relentless_live_round as LR
    text = fx.proofs_at(item, sha) or ""
    mod = LR.live_toggle(text)
    side = LR.toggle_side(stages) if mod else None
    cmds = LR.menu_cmds(text, side)
    for o in others:
        for cmd in LR.menu_cmds(fx.proofs_at(o["item"], (o.get("game") or {}).get("sha")) or ""):
            if cmd not in cmds:
                cmds.append(cmd)
    return {"cmds": cmds, "toggle": mod, "side": side}


def menu_ok(fx, o):
    """False when rider `o`'s live-menu lines cannot be filled (a {toggle} with no side): the rider's defect never holds
    the item it would ride with; it stages alone and its own staging holds it."""
    import relentless_live_round as LR
    try:
        LR.menu_cmds(fx.proofs_at(o["item"], (o.get("game") or {}).get("sha")) or "")
        return True
    except ValueError:
        return False


def menu_bound(fx, item, sha):
    """True when the item's proofs carry a live-menu or live-toggle line: they measure only on a load whose staging ran
    those menu commands (on this item's side), so a game another load started can never serve them
    (GAMEENV_FIX_PROOFSITE_7B433874_ITEMS_WAIT: PLANET_ATMOSPHERE_CLOUD_COST_1 tried two full-list games, said "rides a
    later load" on both, and was routed as a proof-or-site defect). A malformed line is bound too: its staging holds it."""
    import relentless_live_round as LR
    text = fx.proofs_at(item, sha) or ""
    try:
        return bool(LR.live_menu(text) or LR.live_toggle(text))
    except ValueError:
        return True


def stage_tries(c, g):
    """The stagings an item gets before it is a harness failure: a live-toggle item's pair needs one load per side, so
    it gets stage_tries per side."""
    return c["stage_tries"] * (2 if g.get("toggle") else 1)


def toggles(fx, o):
    """True when rider `o`'s proofs ask for a with/without pair: it never rides another item's load (its side is its own)."""
    import relentless_live_round as LR
    try:
        return bool(LR.live_toggle(fx.proofs_at(o["item"], (o.get("game") or {}).get("sha")) or ""))
    except ValueError:
        return True


def stage_prompt(st, r, sha, others=(), enable=(), dlls=(), trees=None, remedy=None, companion=None, menu=None,
                 without=()):
    """trees: `live-deploy:` mods riding this load -> (folders, deploy_custom_mods.py args covering them), or None.
    remedy: the lane's own fix of an environment cause (_env_fix): {"mods": to deploy and load, "cmds": producers}."""
    i, g = st["item"], st["gen"]
    rc = "python3 src/RimMandrake/rimflow/relentless.py"
    en = "python3 src/RimMandrake/Utils/modlist_swap.py --enable %s --apply" % " ".join(enable)
    dis = "python3 src/RimMandrake/Utils/modlist_swap.py --disable %s --apply" % " ".join(without)
    return "\n".join([
        "You are Relentless's STAGING worker for item %s, generation %d. The supervisor holds the game bridge for you as "
        "seat %s and releases it the moment you exit. Your one job: the running game must run the build at %s, so the "
        "supervisor can rerun this item's live proofs blind. You do NOT run or judge the proofs." % (i, g, r["seat"], sha),
        "1. Deploy: `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod <Mod>` for each mod that %s changed (plan "
        "first, read it, then --apply), and for each mod folder a `live-mods:` line in the proofs below names (a build that "
        "changed only a proof still needs its mod's tree deployed). Load `rimworld-deploy` first." % sha,
        ("   DEPLOY ITEM: the supervisor owes the game these trees whole though no commit changed them: %s. You are the one "
         "allowed to write them: `python3 src/RimMandrake/Utils/deploy_custom_mods.py %s` (the plan), read it, then the same "
         "with --apply, with the game DOWN when a DLL differs." % (", ".join(trees[0]), trees[1])) if trees else
        "   DEPLOY ITEM: none; deploy only the mods named above.",
        ("2. FINAL VERIFICATION: the game must start after the deploy on the owner's WHOLE FULL list "
         "(infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml; `rimworld-load-round`: modlist_swap.py restores it), "
         "never a smaller tier: this one load verifies every item's GREEN-FULL clauses at once. Stamp each change with "
         "`./game --idle-ok --why \"relentless final staging %s\" down|loading|up`." % i) if (st.get("game") or {}).get("full") else
        "2. The game must start after the deploy: restart it on the smallest mod list that holds those mods and every "
        "mod a `live-mods:` line in the proofs below names, with their About.xml dependencies "
        "(`rimworld-load-round`: modlist_swap.py; all five DLC always). An entry with a dot is a packageId, a workshop "
        "or game-folder mod: never deploy it, enable it (`modlist_swap.py --enable <packageId>` adds its dependency "
        "closure across the workshop and the game's Mods folder). Never the full list for a GREEN-FULL clause: that "
        "is the batched final verification, staged on its own. Stamp each change with "
        "`./game --idle-ok --why \"relentless staging %s\" down|loading|up`." % i,
        "   Choose the smallest list that proves the item: a cold load is ~22 s on the 13-mod minimal list and 15-25 "
        "minutes on the full one. Wait for it with `./game` polls (each command under 540 s) up to that bound; if you "
        "must exit while it still loads, say so in game-ready: the supervisor waits out the load itself, bounded by "
        "the list's size, and holds no slot while it waits.",
        ("   MOD LIST: the next load must hold %s and their dependencies (owner 2026-10-24: the list is ours to change; all "
         "five DLC stay on). The supervisor already ran `%s`; after any list swap, and again with the game down right "
         "before the launch, run it once more: a swap drops them, and a load without them measures nothing."
         % (", ".join(enable), en)) if enable else "   MOD LIST: no mod of these builds needs enabling.",
        ("   MOD LIST WITHOUT: the next load must LACK %s (a live-without line or a live-toggle's without side; "
         "STAGING_REMOVAL_FIX_ONLY_KNOWS_ADDITION). The supervisor already ran `%s`; run it again after every list swap "
         "and every --enable, and once more with the game down right before the launch (it takes off the active mods "
         "that need them too), then parse the live ModsConfig.xml: snag if any of them is still active."
         % (", ".join(without), dis)) if without else "   MOD LIST WITHOUT: no mod must be kept off this load.",
        ("   SHUTDOWN WINDOW: with the game DOWN and before the launch, deploy %s (`deploy_custom_mods.py --mod <Mod> "
         "--apply`): the game folder holds a stale DLL for each, and a DLL cannot be written while the game runs."
         % ", ".join(dlls)) if dlls else "   SHUTDOWN WINDOW: no stale DLL in the game folder for these mods.",
        ("   COMPANION: in the same shutdown window run `python3 src/RimMandrake/bridgetools/build.py --gm --apply` from a "
         "clean clone whose HEAD is on origin/main and holds %s (./sync levels it): the proofs call JawaBench tools and "
         "the game folder's DLL does not hold those builds." % ", ".join(c[:12] for c in companion))
        if companion else "   COMPANION: not owed.",
        ("   ONE LOAD FOR ALL: these game items wait for a reload too; deploy each one's build as well (rimworld-deploy) and "
         "choose the smallest list that holds the most of their mods; level your clone to origin/main first (./sync) so "
         "each build is in the tree: %s." % "; ".join(
             "%s at %s" % (o["item"], (o.get("game") or {}).get("sha", "?")[:12]) for o in others)) if others else
        "   No other game item waits for a reload.",
        ("   LANE FIX (an earlier read measured nothing for an environment reason: %s): deploy %s (plan, read, --apply) "
         "and hold them in this load%s." % ((remedy.get("why") or ""), ", ".join(remedy.get("mods") or []) or "nothing more",
                                            "; then, with the game up, run each producer once and keep its exit and last "
                                            "lines for game-ready: %s" % " ; ".join("`%s`" % c for c in remedy["cmds"])
                                            if remedy.get("cmds") else "")) if remedy else
        "   LANE FIX: none.",
        ("   TOGGLE: this staging is the %s side of a with/without pair on %s: the list must %s it (check the live "
         "ModsConfig.xml after every swap; snag if it %s)." % (menu["side"], menu["toggle"],
                                                               "hold" if menu["side"] == "with" else "lack",
                                                               "lacks it" if menu["side"] == "with" else "holds it"))
        if (menu or {}).get("toggle") else "   TOGGLE: none.",
        ("   MAIN MENU STEP: the moment the load reaches the main menu and BEFORE you start or load any game, run each "
         "of these once and keep its exit and last lines for game-ready (a non-zero exit is the proof's business, not "
         "a stop): %s" % " ; ".join("`%s`" % x for x in menu["cmds"])) if (menu or {}).get("cmds") else
        "   MAIN MENU STEP: none.",
        "3. When the game is up and the main menu step (if any) has run: `%s game-ready --item %s --gen %d \"what you "
        "deployed and which list\"`, then exit. Stopped: `%s snag --item %s --gen %d --class game_stage \"what stopped "
        "you\"`, exit." % (rc, i, g, rc, i, g),
        "Never fullscreen or focus the game. Never a flyer's flight. Never touch a canonical world save "
        "(infrastructure/state/CANONICAL_SAVE.md). Never `rimflow bridge take/release` or any ledger write on this "
        "item: the supervisor owns both. Foreground commands, timeouts under 540 s, no subagents.",
        "", "--- live proofs it will rerun ---", st.get("_proofs_text", "")])


# ---------------------------------------------------------------- effects (mixed into relentless.Effects)

def live_mod_count():
    """The active mods of the live ModsConfig.xml (what the running game loaded when it started after the swap), or None."""
    utils = os.path.join(os.path.dirname(HERE), "Utils")
    if utils not in sys.path:
        sys.path.insert(0, utils)
    try:
        import modlist_swap
        got = modlist_swap.mods(modlist_swap.LIVE)
    except Exception:  # noqa: BLE001  an unread list is the full list's bound, never a crash in the tick
        return None
    return len(got) if got else None


def _load_policy():
    utils = os.path.join(os.path.dirname(HERE), "Utils")
    if utils not in sys.path:
        sys.path.insert(0, utils)
    import load_policy
    return load_policy


def load_bound(c, mods):
    """The ONE policy's supervisory deadline (seconds) for a cold load of `mods` mods; unread is the full list's. Past
    it the ATTEMPT is over, but the game is restaged (restarted) only on stall evidence (load_stall_evidence)."""
    return int(_load_policy().profile_for(mods)["process_to_bridge_deadline_s"])


# belt_watchdog signals that are EVIDENCE of a stall (Not Responding, CPU idle, a frozen or looping Player.log, a
# modal wedge, a dead process). Its "bridge" signal is NOT: past the warn threshold it fires on the clock alone.
STALL_EVIDENCE_SIGNALS = ("game", "player_log", "modals")
# load_stall_evidence's answer when belt_watchdog itself cannot read: a broken instrument, not "no evidence"
STALL_BLIND = "BLIND stall probe: "


def stall_evidence(sigs):
    """belt_watchdog Sig list -> 'name: detail' of the first evidence signal at STALLED or worse, else None."""
    import belt_watchdog as bw
    for s in sigs:
        if s.name in STALL_EVIDENCE_SIGNALS and bw.RANK.get(s.level, 0) >= bw.RANK[bw.STALLED]:
            return "%s %s: %s" % (s.level, s.name, s.detail)
    return None


def mod_gap_why(gap):
    """relentless_live_round.mod_gap -> why the game cannot serve the build without a reload, or None. A plan that could
    not be read blocks nothing here: the run reports it with its own row."""
    gap = gap or {}
    parts = []
    if gap.get("off"):
        parts.append("the live ModsConfig/game folder lacks %s"
                     % ", ".join("%s (%s)" % kv for kv in sorted(gap["off"].items())))
    if gap.get("dll"):
        parts.append("stale DLL in the game folder: %s" % ", ".join(gap["dll"][:5]))
    if gap.get("running"):
        parts.append(gap["running"])
    return ("modlist gate: " + "; ".join(parts)) if parts else None


LEDGER_ONLY = ("infrastructure/state/ledger/", "infrastructure/state/items/", "infrastructure/state/queue/")  # cli._LEDGER_ONLY


def _paths_of(fx, sha):
    """-> the paths `sha` changes (relentless.Effects.touched), or None when the fx cannot say (a fake without it)."""
    f = getattr(fx, "touched", None)
    if not callable(f):
        return None
    try:
        return f(sha)
    except Exception:       # noqa: BLE001 - an unreadable sha is no rebuild claim: the cli's own gate decides
        return None


def no_code_rebuild(st, sha, touched):
    """-> the `implemented --no-code` words for a rebuild that changed nothing, or None. All of: the candidate `sha` is the
    build's (st["candidate"]), it touches only the ledger and item prose (`touched`, its paths), and the warrant recorded
    for that generation carries `unchanged: True` (relentless_breakers.take_warrant: `WARRANT: UNCHANGED: ...`, never a
    reading of prose: "nothing in the work changed except the cooldown fix" matched the old substring). cli then checks
    the interval: the item's recorded build is under `sha`, its files unchanged, no later commit naming the item touches
    more than the ledger (_carried_work), so this carries a build forward and never stands for one.
    RELENTLESS_NOCODE_REBUILD_IMPLEMENTED_REFUSED: GIZKA_STOWAWAY_UNMEASURED_ROWS_1 gen 8 re-anchored its stale build on
    today's main with an item note only (ad2549a17d, warrant "nothing in the work changed; the environment did"), and
    `implemented` refused it as ledger-only, so a finished item went back as proof_owed."""
    cand, w = st.get("candidate") or {}, st.get("warrant") or {}
    if not touched or not all(p.startswith(LEDGER_ONLY) for p in touched):
        return None
    if not cand.get("sha") or not (cand["sha"].startswith(sha) or sha.startswith(cand["sha"])):
        return None
    if w.get("gen") is None or w.get("gen") != cand.get("gen") or w.get("unchanged") is not True:
        return None
    return ("gen %s rebuild, ledger-only; warrant: %s" % (w["gen"], w["changed"]))


def enable_set(gaps):
    """Every mod folder the next load must hold: [relentless_live_round.mod_gap] -> sorted folders (the build's mods and
    its live-mods of each item riding the load)."""
    return sorted({m for g in gaps for m in (g or {}).get("mods") or []})


def without_set(gaps, menu=None):
    """Every mod the next load must LACK: the live-without mods of each item riding it, plus a live-toggle's without
    side (STAGING_REMOVAL_FIX_ONLY_KNOWS_ADDITION: staging used to only enable, so a without-proof ran on whatever list
    was up)."""
    off = {m for g in gaps for m in (g or {}).get("without") or []}
    if (menu or {}).get("toggle") and menu.get("side") == "without":
        off.add(menu["toggle"])
    return sorted(off)


def dll_mods(gaps):
    """The mod folders with a stale DLL in the game folder, deployed in the shutdown window before the launch."""
    return sorted({d.split("/")[0] for g in gaps for d in (g or {}).get("dll") or []})


class GameFx(object):
    """What the game mode asks of the world. Needs self.rimflow, self.books, self.base (relentless.Effects has them)."""

    def proofs_at(self, item, sha, ext=".txt"):
        r = subprocess.run(["git", "show", "%s:%s/%s%s" % (sha, PROOFS_DIR, item, ext)], cwd=self.books,
                           capture_output=True, text=True, timeout=60)
        return r.stdout if r.returncode == 0 else ""

    def game_implement(self, item, sha, criteria_text, live=None, why=None, no_code=None):
        args = ["implemented", item, "--sha", sha, "--why", why or "relentless: blind offline PASS; the game clauses stay owed"]
        if no_code:     # a ledger-only rebuild whose warrant says the work did not change (no_code_rebuild)
            args += ["--no-code", no_code]
        tmp = None
        if criteria_text.strip():
            tmp = os.path.join(self.base, "live", "%s.criteria" % item)
            os.makedirs(os.path.dirname(tmp), exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(criteria_text)
            args += ["--criteria-file", tmp]
        if live:
            args += ["--live", live]
        r = self.rimflow(*args, timeout=180)
        return None if r.returncode == 0 else (r.stderr or r.stdout)

    def game_ledger(self, item):
        """-> {state, built_sha, owed: {criterion: level}} from the ledger, or None."""
        import model
        it = model.replay(model.read()).items.get(item)
        if it is None:
            return None
        crit = {c["id"]: c["level"] for c in it.criteria or []}
        return {"state": it.state, "built_sha": it.built_sha, "title": it.title or "",
                "owed": {c: crit.get(c) for c in it.outstanding or []},
                "criteria": {c["id"]: dict(c) for c in it.criteria or []},      # owner_looks reads their words
                "passed": {p["criterion"]: p["level"] for p in it.passed or []}}     # met since this build

    def game_rows(self):
        import relentless_live_round
        return relentless_live_round.read_rows(os.path.join(self.base, "live", "runs.jsonl"))

    def game_reading(self):
        """-> {"state": "UP"|"LOADING"|"DOWN"|None, "started": epoch|None, "mods": n|None, "evidence": str}.
        UP: the process runs and the bridge listens; LOADING: it runs, the bridge does not yet; None: no reading taken
        (never read as "no game": that is what held ten items on the owner). Each read is tasklist, netstat and
        powershell over the Windows boundary, ~50 s of a tick across its game items, and no step restarts the game in
        line (a staging is a detached worker): one reading serves READING_TTL_S."""
        hit = getattr(self, "_game_read", None)
        if hit and time.monotonic() - hit[0] < READING_TTL_S:
            return dict(hit[1])
        import probe
        import relentless_live
        m = probe.measure(use_cache=False)
        started = relentless_live.Fx(seat=self.r["seat"]).game_started() if m.get("running") else None
        got = {"state": m.get("implies"), "started": started, "mods": live_mod_count(),
               "evidence": m.get("evidence") or ""}
        self._game_read = (time.monotonic(), got)
        return dict(got)

    def load_stall_evidence(self):
        """-> 'LEVEL signal: detail' when belt_watchdog sees evidence of a stall in a loading game, None when it sees
        none, STALL_BLIND + why when the probe itself fails. A blind probe is never 'no evidence' and never a kill: the
        caller ends the attempt as a harness failure and leaves the game loading (LOAD_WAIT_FIX_BLIND_PROBE_WAITS_FOREVER)."""
        try:
            _load_policy()
            import belt_watchdog
            return stall_evidence(belt_watchdog.gather(bridge=False))
        except Exception as e:  # noqa: BLE001  reported up as blind, never read as no evidence
            return "%s%s: %s" % (STALL_BLIND, type(e).__name__, str(e))

    def bridge_reading(self):
        """-> {"holder", "purpose", "since"} of the bridge lock as the ledger reads now."""
        import model
        w = model.replay(model.read())
        return {"holder": w.bridge_holder, "purpose": w.bridge_purpose or "", "since": w.bridge_since}

    def bridge_idle(self, purpose):
        r = self.rimflow("bridge", "idle", "--for", purpose)
        return None if r.returncode == 0 else ((r.stdout or "") + (r.stderr or "")).strip()

    def bridge_take(self, purpose):
        r = self.rimflow("bridge", "take", "--idle-ok", "--for", purpose)
        return None if r.returncode == 0 else ((r.stderr or "") + (r.stdout or "")).strip()

    def bridge_release(self):
        r = self.rimflow("bridge", "release", "--mine")
        return None if r.returncode == 0 else ((r.stderr or "") + (r.stdout or "")).strip()

    def game_preflight(self, item, lines, sites=None):
        """relentless_live.preflight on the ledger and books as a live run would read them: [{cid, why, fp, kind}]."""
        import relentless_live
        return relentless_live.preflight(relentless_live.Fx(books=self.books, seat=self.r["seat"]),
                                         relentless_live.live_rules(self.r), item, lines, sites)

    def game_carry(self, item, sha):
        """relentless_live.carry on the books: (newer sha, why) when only a rebuilt shared assembly made `sha` stale."""
        import relentless_live
        try:
            return relentless_live.carry(relentless_live.Fx(books=self.books, seat=self.r["seat"]), sha, item)
        except ValueError:
            return None

    def game_carry_blockers(self, item, sha):
        """relentless_live.carry_blockers on the books: [(path, commit)] that stopped a carry from `sha`."""
        import relentless_live
        try:
            return relentless_live.carry_blockers(relentless_live.Fx(books=self.books, seat=self.r["seat"]), sha, item)
        except ValueError:
            return []

    def refusal_print(self, item, criterion, why, proof):
        """A runs.jsonl refusal -> relentless_live.fingerprint over the criterion's whole text as the ledger reads now."""
        import relentless_live
        it = relentless_live.Fx(books=self.books, seat=self.r["seat"]).item(item) or {}
        text = ({c["id"]: c for c in it.get("criteria") or []}.get(criterion) or {}).get("text") or ""
        return relentless_live.fingerprint(criterion, why, proof, text)

    def _mods_text(self, item, sha):
        """The live_proofs text whose `live-mods:`/`live-deploy:` lines a staging enables and deploys: the books' current
        file, the one the live run itself reads (relentless_live_round.round: fx.proofs), else the build's. Read at the
        build's sha, a name corrected on main after the build kept refusing every staging the run would have passed
        (WATER_DEPTH_RESKIN_HE_LOOKS_FIRST held 2026-11-05 on 15d414c's 'RimMandrake.FlowWorks', main said FlowWorks)."""
        return self._round_fx().proofs(item) or self.proofs_at(item, sha)

    def game_mod_gap(self, item, sha, running=True):
        """relentless_live_round.mod_gap for the build at `sha`, read as a live run would read it."""
        import relentless_live_round
        return relentless_live_round.mod_gap(self._round_fx(), sha, self._mods_text(item, sha), running, item)

    def game_own_mods(self, item, sha):
        """The mod folders the build at `sha` itself changed (relentless_live_round.item_mods), no `live-mods:` rider: the
        mods whose name in a staging's stop makes it the build's defect (_stage_stop). Raises ValueError as item_mods does."""
        import relentless_live_round
        return relentless_live_round.item_mods(self._round_fx(), item, sha)

    def game_names_check(self, item, sha):
        """relentless_names over the item's live_proofs text (_mods_text) -> (refusal or None, [advice: warn only],
        [inferred: the needs the gate adds to its load]). A live-without the planned load holds (or that names no mod)
        is a refusal too, before any slot (LIVE_NEEDS_ENFORCE_ABSENCE_NOW_EXPLICIT)."""
        import relentless_live_round
        import relentless_names
        text = self._mods_text(item, sha)
        index = relentless_names.default_index()
        chk = relentless_names.check(relentless_live_round.live_mods(text), index)
        def read(p):
            try:
                with open(os.path.join(self.books, p), encoding="utf-8", errors="replace") as f:
                    return f.read()
            except OSError:
                return ""
        scripts = relentless_names.gather_scripts(text, read)
        saves = relentless_names.gather_saves(text, lambda p: read(p)[:262144])  # cut-ok: a search window for save names
        why = relentless_names.refusal(chk["refused"])
        try:
            build = sorted(relentless_live_round.item_mods(self._round_fx(), item, sha))
            nd = relentless_names.needs(text, scripts, chk["mods"], build, index, saves=saves)
        except (ValueError, OSError):
            return why, [], []
        clash = relentless_names.without_conflict(nd)
        return ("; ".join(x for x in (why, clash) if x) or None), nd["warn"], nd["add"]

    def game_batch_gap(self, builds):
        """relentless_live_round.batch_gap: every [(item, sha)] riding one load, for one deploy plan."""
        import relentless_live_round
        return relentless_live_round.batch_gap(self._round_fx(), [(s, self._mods_text(i, s), i) for i, s in builds])

    def game_deploy_args(self, folders):
        """Mod folders -> one deploy_custom_mods.py argument string (relentless_live_round.deploy_args)."""
        import relentless_live_round as R
        return R.deploy_args(folders, self._round_fx().folded())

    def game_companion(self, item, sha):
        """`sha` when the item owes the game its JawaBench DLL (a `live-companion:` line, or a build touching the
        companion's sources) and the game folder's copy does not hold it (FRESH, or a clean build of a descendant:
        companion_identity cover); else None. The stager builds one companion holding every owed sha
        (COMPANION_DEPLOY_LIVE_ROUND_FORGETS: an exact source hash per built sha cannot be met by a batch)."""
        import relentless_live as L
        import relentless_live_round as R
        fx = self._round_fx()
        try:
            owes = R.companion_line(self._mods_text(item, sha)) or L.companion_touched(fx, sha, item)
        except (ValueError, OSError):
            return None
        if not owes:
            return None
        v = fx.companion(sha) or {}
        return sha if v.get("want") and v.get("state") != "FRESH" else None

    def game_trees(self, builds):
        """Every `live-deploy:` mod of [(item, sha)] riding one load -> (folders, deploy_custom_mods.py args), or None."""
        import relentless_live_round as R
        got = sorted({m for i, s in builds for m in R.live_deploy(self._mods_text(i, s))})
        return (got, R.deploy_args(got, self._round_fx().folded())) if got else None

    # exact-tier clauses go to SteveDesktop (LANE_TIER_WIRE_A_WHOLE_LIST_LOAD) -----------------------------------------
    def _testq(self):
        d = os.path.join(self.books, "src", "RimMandrake", "Utils", "testq")
        if d not in sys.path:
            sys.path.insert(0, d)
        import fault_monitor
        import testq
        return testq, fault_monitor

    def steve_deploy(self, item, sha):
        """The mods an exact-tier job deploys on SteveDesktop: those the build changed, and its `live-deploy:` trees."""
        import relentless_live_round as R
        text = self._mods_text(item, sha)
        got = sorted(R.item_mods(self._round_fx(), item, sha))
        # live-mods trees too: an inferred tier loads them, so SteveDesktop must hold them at this build
        return got + [m for m in R.folders(R.live_mods(text)) if m not in got]

    # inferred tiers (LIGHTSPEED_REWIRE_ROUND_AS_TESTQ_CLIENT) ---------------------------------------------------------
    def sha_infers(self, sha):
        import relentless_live_round as R
        return R.sha_infers(self.books, sha)

    def infer_tier(self, item, sha):
        """-> (the mods__ tier this build's proofs need, None) or (None, why): the build's mods and the file's
        live-mods/live-deploy, each named once (relentless_names.check: a folded source is its composed mod), as
        packageIds (a repo folder by its About.xml, a packageId as written)."""
        import relentless_live_round as R
        import relentless_names as N
        fx = self._round_fx()
        try:
            names = list(R.item_mods(fx, item, sha)) + R.live_mods(self._mods_text(item, sha))
        except ValueError as e:
            return None, "the build's mods do not read: %s" % e
        index = fx.names_index()
        chk = N.check(sorted(set(names)), index)
        if chk["refused"]:
            return None, "names refused: %s" % R._refusal(chk["refused"])
        pid_of = {v: k for k, v in index.repo_pids.items()}
        pids = []
        for m in chk["mods"]:
            pid = pid_of.get(m) or (m.lower() if R.is_package(m) else None)
            if not pid:
                return None, "no packageId for %s" % m
            pids.append(pid)
        return R.mods_tier(pids)

    def _fallback_path(self):
        import relentless_live_round as R
        return os.path.join(self.base, R.FALLBACK)

    def steve_fell_back(self, item, sha):
        import relentless_live_round as R
        v = R.read_fallback(self.base).get(item) or {}
        return list(v.get("clauses") or []) if v.get("sha") and same_sha(v["sha"], sha) else []

    def steve_fallback(self, item, sha, clauses, why):
        """Give clauses of this build back to Archmagi's round (relentless_live_round.read_fallback reads it)."""
        import relentless_live_round as R
        got = R.read_fallback(self.base)
        old = got.get(item) or {}
        keep = list(old.get("clauses") or []) if old.get("sha") and same_sha(old["sha"], sha) else []
        got[item] = {"sha": sha, "clauses": sorted(set(keep) | set(clauses)), "why": why,
                     "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        p = self._fallback_path()
        os.makedirs(os.path.dirname(p), exist_ok=True)
        tmp = p + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(got, f, indent=1, sort_keys=True)
        os.replace(tmp, p)

    def testq_submit(self, item, sha, tier, clauses, deploy):
        """testq.py submit: one exact-tier job on lane stevedesktop -> (job id, None), or (None, why it refused). A
        same request still pending or running answers with that job (testq.same_request), so a resubmit never doubles."""
        argv = ["python3", os.path.join(self.books, TESTQ_PY), "submit", item, "--proofs", ",".join(clauses),
                "--profile", "tier:" + tier, "--lane", "stevedesktop", "--purpose", "fix", "--by", STEVE_BY,
                "--sha", sha, "--for-item", item]
        for m in deploy:
            argv += ["--deploy", m]
        try:
            r = subprocess.run(argv, cwd=self.books, capture_output=True, text=True, timeout=240,
                               stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            return None, "testq.py submit timed out"
        for line in reversed((r.stdout or "").strip().splitlines()):
            try:
                o = json.loads(line)
            except ValueError:
                continue
            if isinstance(o, dict) and o.get("job"):
                return o["job"], None
        return None, ((r.stdout or "") + (r.stderr or "")).strip() or "exit %d, no job" % r.returncode

    def testq_job(self, job):
        """-> {"state": pending|running|done|quarantined|cancelled|None, "rec": the record or None, "gate":
        fault_monitor.gate's (verdict, why) for a done record}. Only a gate of `count` lets a result decide anything."""
        T, FM = self._testq()
        state = T.where(job)
        if state is None and os.path.exists(T.q("quarantined", job + ".json")):
            state = "quarantined"
        rec = T.read_json(T.q(state, job + ".json")) if state else None
        gate = None
        if state == "done" and rec:
            windows, fstate = FM.load()
            gate = FM.gate(rec, windows, fstate)
        return {"state": state, "rec": rec, "gate": gate}

    def steve_verify(self, item, criterion, level, sha, result, evidence, config):
        """rimflow verify for one clause SteveDesktop measured -> None, or why it did not land."""
        v = self.rimflow("verify", item, "--criterion", criterion, "--level", level, "--sha", sha, "--result", result,
                         "--config", fulltext.fit(config, 300), "--evidence", fulltext.fit(evidence, 300),
                         "--why", "relentless exact tier: SteveDesktop through testq, the tier loaded whole and checked")
        return None if v.returncode == 0 else ((v.stderr or v.stdout) or "")

    def game_row_append(self, row):
        p = os.path.join(self.base, "live", "runs.jsonl")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")

    def _round_fx(self):
        """One per Effects, so per tick: the same plan is read once a tick. modlist_enable forgets it, the plan reads
        ModsConfig."""
        if getattr(self, "_round", None) is None:
            import relentless_live_round
            self._round = relentless_live_round.RoundFx(books=self.books, seat=self.r["seat"])
        return self._round

    def modlist_enable(self, mods):
        """modlist_swap.py --enable <mods> --apply on the live ModsConfig.xml -> None, or why it could not."""
        self._round = self._game_read = None
        r = subprocess.run(["python3", os.path.join(self.books, "src/RimMandrake/Utils/modlist_swap.py"), "--enable",
                            *mods, "--apply"], cwd=self.books, capture_output=True, text=True, timeout=180,
                           stdin=subprocess.DEVNULL)
        return None if r.returncode == 0 else ((r.stdout or "") + (r.stderr or "")).strip()

    def modlist_disable(self, mods):
        """modlist_swap.py --disable <mods> --apply on the live ModsConfig.xml -> None, or why it could not."""
        self._round = self._game_read = None
        r = subprocess.run(["python3", os.path.join(self.books, "src/RimMandrake/Utils/modlist_swap.py"), "--disable",
                            *mods, "--apply"], cwd=self.books, capture_output=True, text=True, timeout=180,
                           stdin=subprocess.DEVNULL)
        return None if r.returncode == 0 else ((r.stdout or "") + (r.stderr or "")).strip()

    def prove_launch(self, item):
        import model
        import relentless
        os.makedirs(os.path.join(self.base, "live"), exist_ok=True)
        with open(os.path.join(self.base, "live", "round.out"), "a", encoding="utf-8") as out:
            p = subprocess.Popen(["python3", os.path.join(HERE, "relentless_live_round.py"),
                                  "round", "--item", item], cwd=self.books,
                                 env=dict(model.bridge_holder.process_env(), RELENTLESS_ROOT=self.base,
                                          PATH=relentless.windows_path(os.environ.get("PATH", ""))),
                                 stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
        return p.pid

    def prove_alive(self, pid):
        return self.live_round_alive(pid)

    def broker_launch(self):
        """Start the game broker's job (relentless_broker.job), detached, with prove_launch's environment."""
        import model
        import relentless
        os.makedirs(os.path.join(self.base, "live"), exist_ok=True)
        with open(os.path.join(self.base, "live", "broker.out"), "a", encoding="utf-8") as out:
            subprocess.Popen(["python3", os.path.join(HERE, "relentless_broker.py"), "job"],
                             cwd=self.books, env=dict(model.bridge_holder.process_env(), RELENTLESS_ROOT=self.base,
                                                      PATH=relentless.windows_path(os.environ.get("PATH", ""))),
                             stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
        return None


# ---------------------------------------------------------------- holds that outlived their user

def names_item(purpose, item):
    """True when the bridge purpose names `item` as a whole id: `ART` is not in `staging CART` (Codex r4 game0 #2; a
    substring match kept an idle ART's game hold alive on CART's bridge activity)."""
    return bool(item) and re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(item), purpose or "") is not None


def stale_holds(states, now, c, alive, bridge, reading):
    """-> [(item, kind, why)]: every game-phase holder other_active would count that no longer uses the game. Pure but
    for the callables: alive(pid) -> bool; bridge() -> bridge_reading(); reading() -> game_reading(), each asked only
    when a holder needs it. RELENTLESS_GAME_HOLD_UNSTICK_IDLE_LIVE_ITER: other_active held the game for as long as such a holder
    existed, and only that holder's own step (or its worker's reload-needed) could end it, so one idle holder parked
    every other game item ("one live user at a time") for 47 minutes on 2026-11-03.
      proving   its prove pid is dead: the round ended (its rows, if any, are on runs.jsonl for its step to read);
                a broker batch item is not named here: its own step reads the broker job's lock
      live_iter its worker has not held the bridge for this item for live_idle_s, or the game it iterates on is down or
                is a different game than the one that showed the FAIL"""
    out, br, rd = [], None, None
    for s in states:
        g = s.get("game") or {}
        if s["status"] == GAME and g.get("phase") == "proving" and not g.get("broker"):    # a broker batch's
            if not g.get("prove_pid") or not alive(g["prove_pid"]):     # liveness is its job's lock (_broker_holds)
                out.append((s["item"], "proving", "its prove pid %s is not running: the round ended"
                            % g.get("prove_pid")))
        li = s.get("live_iter")
        if s["status"] == "running" and li:
            if rd is None:
                rd = reading() or {}
            if rd.get("state") == "DOWN" or (rd.get("state") == "UP" and rd.get("started") and li.get("started")
                                             and int(rd["started"]) != int(li["started"])):
                out.append((s["item"], "live_iter", "the game that showed its FAIL (started %s) no longer runs: %s"
                            % (li.get("started"), rd.get("state") if rd.get("state") == "DOWN"
                               else "started %s" % rd.get("started"))))
                continue
            if br is None:
                br = bridge() or {}
            if br.get("holder") and names_item(br.get("purpose"), s["item"]):
                out.append((s["item"], "seen", now))       # it drives the game now: the idle clock starts again
                continue
            seen = li.get("bridge_seen") or li.get("at") or now
            if now - seen >= c["live_idle_s"]:
                out.append((s["item"], "live_iter", "its worker has not held the bridge for it in %d s (limit %d s): "
                            "it works offline" % (now - seen, c["live_idle_s"])))
    return out


def lapse_holds(store, fx, r, now, acts):
    """Each tick, before any item steps: free the game from every holder stale_holds names, and journal why."""
    c = cfg(r)
    states = store.states()
    if not any(((s.get("game") or {}).get("phase") == "proving" and s["status"] == GAME)
               or (s["status"] == "running" and s.get("live_iter")) for s in states):
        return
    stale = stale_holds(states, now, c, fx.prove_alive, getattr(fx, "bridge_reading", lambda: {}),
                        getattr(fx, "game_reading", lambda: {}))
    for item, kind, why in stale:
        if kind == "seen":
            with store.lock():
                st = store.load(item)
                if st.get("live_iter"):
                    st["live_iter"]["bridge_seen"] = why
                    store.save(st)
            continue
        with store.lock():
            st = store.load(item)
            if kind == "proving":
                if st["status"] != GAME or (st.get("game") or {}).get("phase") != "proving":
                    continue
                st["game"]["phase"] = "prove"
            else:
                li = st.pop("live_iter", None)
                if st["status"] != "running" or li is None:
                    continue
                st["live_lapsed"] = dict(li, lapsed_at=now, why=why)
                store.learn(item, "- %s: the game hold lapsed (%s); the game is free for the next item. Work offline; "
                            "a live iteration needs the game again through a game phase" % (
                                time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), why))
            store.save(st)
        store.journal({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "do": "game_hold_released",
                       "item": item, "kind": kind, "why": why})
        acts.append({"do": "game_hold_released", "item": item, "kind": kind, "why": why})


# ---------------------------------------------------------------- the step

def _save(store, item, fn):
    with store.lock():
        st = store.load(item)
        if st["status"] != GAME:
            return None
        fn(st)
        store.save(st)
        return st


def _back(store, fx, sup, r, item, klass, why, now, acts, live=None):
    """The game phase ends with work to do: release what we hold, and the item goes back to a worker. `live`: the game
    that showed the FAIL still runs its build, so the worker iterates on it until it proves a reload is needed."""
    with store.lock():
        st = store.load(item)
        if st["status"] != GAME:
            return
        gated = sup.fail(store, st, klass, why, r, now) == "gated"
        if gated:       # unattributed (relentless_attrib): the candidate waits for its diagnosis, no worker yet
            st["wait"]["live"] = live
        elif live:
            st["live_iter"] = live
        store.save(st)
    acts.append({"do": klass, "item": item, "why": why, **({"gated": True} if gated else {})})
    fx.ledger_note(item, "relentless game phase: %s%s: %s" % (klass, " (withheld for attribution, no strike)" if gated
                                                              else "", why))


ENV_KEEP = 40      # environment causes kept per item (tried and routed): every clause of an item and its stale builds


def _keep(book, got):
    """got: cause key -> value (a time, or [the fix's time, the row's own time]); the newest ENV_KEEP are kept."""
    out = dict(book or {})
    out.update(got)
    return dict(sorted(out.items(), key=lambda kv: kv[1] if isinstance(kv[1], list) else [kv[1]])[-ENV_KEEP:])


def _t(v):
    return v if isinstance(v, list) else [v, v]


def _load_gate(store, fx, r, item, g, rd, now, acts):
    """A LOADING game, from every road that could restage it (the prove phase's stale rows, and every entry to `stage`:
    a final waiter's batch timer, a lane fix that stages now). -> (True, None): waited or ended the attempt, the tick
    is over; (False, why): stall evidence says this load is dead and a restage may replace it. Before, a final waiter
    whose batch timer ran out entered `stage` while the game read LOADING and restaged it with no bound or evidence
    (Codex r4 game1 #1)."""
    c = cfg(r)
    bound = load_bound(c, rd.get("mods"))
    age = int(now - (rd.get("started") or g.get("staged_at") or g["entered_at"]))   # never 0 for ever
    if age < bound:
        why = "the game is loading: %ds of a %ds bound (%s mods)" % (age, bound, rd.get("mods") or "unread")
        _save(store, item, lambda s: (s.update(put_down={"on": why, "at": now}),
                                      s["game"].update(loading={"started": rd.get("started"), "bound": bound})))
        acts.append({"do": "game_loading", "item": item, "why": why})
        return True, None
    # BRIDGE_DEADLINES_UNIFY_ONE_ABSOLUTE_POLICY: the clock alone never restarts a loading game
    ev = fx.load_stall_evidence()
    msg = _load_policy().deadline_exceeded("cold load of %s mods" % (rd.get("mods") or "unread"), age, bound,
                                           alive=True)       # LOADING = the process runs
    if ev and ev.startswith(STALL_BLIND):
        # a probe that cannot see would wait this load for ever: the deadline ends the ATTEMPT (a counted
        # harness failure and an alarm), and the game, which may still be loading, is left running
        _harness(store, fx, r, item, "%s; the stall probe is blind (%s), so the attempt ends and the game is "
                 "left loading" % (msg, ev[len(STALL_BLIND):]), now, acts)
        _save(store, item, lambda s: s["game"].update(spare_load={"started": rd.get("started")}))
        return True, None
    if not ev:
        why = "%s; no stall evidence (belt_watchdog), so it is waited, not restaged" % msg
        _save(store, item, lambda s: (s.update(put_down={"on": why, "at": now}),
                                      s["game"].update(loading={"started": rd.get("started"), "bound": bound})))
        acts.append({"do": "game_loading_past_deadline", "item": item, "why": why})
        return True, None
    if g.get("spare_load") is not None:     # evidence, not the clock: this load is restaged after all
        _save(store, item, lambda s: s["game"].pop("spare_load", None))
    return False, "%s; stall evidence: %s" % (msg, ev)


def _env(store, fx, r, item, rows, since, now, acts):
    """UNMEASURED_LANE_REWIRE_STOP_REBUILDING_SITES (owner 2026-11-05: "fix class not instance"): a clause that measured
    nothing for an ENVIRONMENT reason (relentless_envcause.classify) never goes back to a builder or starts a generation.
    A cause the lane can fix (deploy a mod the plan omitted, load a tier that holds the item's mods, run the producer a
    proof reads) is fixed by the lane itself ONCE (_env_fix): the next staging deploys and enables its mods and runs its
    producer, and the round re-reads. The same cause read again after a staging that carried the fix, or a cause nothing
    in the lane can fix (the proof's own call, the harness, the proof or its site) that a rerun cannot change, is routed
    ONCE to one fixer (_env_route) and the item waits. -> True when it acted (False: the lane's own roads go on).
    Before: MODCHECK_DONOR_ENVIRONMENTS_1 spent 12 generations because no lane step ever ran `modcheck run Armoury`."""
    import relentless_live_round
    st = store.load(item)
    tried = st.get("env_tried") or {}
    staged = st["game"].get("staged_at") or 0
    try:        # the item's `live-mods:`: a type the load lacks is a load fix on its packageIds (relentless_envcause)
        needs = relentless_live_round.live_mods(fx.proofs_at(item, st["game"].get("sha")))
    except Exception:       # noqa: BLE001  an unreadable proofs file names no mod: the cause still routes, never builds
        needs = []
    envs = []
    for v in rows.values():
        if row_at(v) < since:   # read before this staging: the staged game has not answered yet (Codex r5 game1 #2)
            continue
        if v.get("outcome") == "UNMEASURED" and v.get("harness"):
            continue    # relentless_live's harness row (INFRA streak or box fault) is _harness's restage, never a route
        e = relentless_envcause.classify(v, item, needs)
        if e:
            e["at"], e["decided"] = row_at(v), (relentless_live_round.decides(v)
                                                  or (v.get("why") or "").startswith(relentless_envcause.HARNESS[0]))
            envs.append(e)
    fresh = [e for e in envs if e.fix and e.fp not in tried]
    if fresh and _env_fix(store, item, fresh, now, acts):
        return True
    # a fix that rides the next staging (-> False) never ends the reading: a second, unfixable cause beside it still
    # routes, or the item fell through to _refuse and went back to a builder (Codex r4 game1 #2)
    # the fix's time is the lane clock, a row's is its own: a re-read is a NEWER row after a staging that carried it
    again = [e for e in envs if e.fix and e.fp in tried and staged >= _t(tried[e.fp])[0] and e["at"] > _t(tried[e.fp])[1]
             and not st["game"].get("remedy")]      # a fix not yet run by a confirmed staging was never tried
    stuck = [e for e in envs if not e.fix and e["decided"]]
    if again or stuck:
        _env_route(store, fx, item, again + stuck, now, acts,
                   "the lane fixed it once and the re-read says the same" if again else None)
        return True
    return False


def _env_fix(store, item, envs, now, acts):
    """The lane's one fix: the staging's remedy (stage_prompt LANE FIX) names the mods to deploy and enable and the
    producers to run. A cause the lane already restages for (RESTAGE: not deployed, not in the running load, reload
    needed) rides that staging and its batch wait (-> False); any other is staged now on its voided rows (-> True)."""
    import relentless_live
    st = store.load(item)
    sha = st["game"]["sha"]
    # a mod named by an UNDEPLOYED row is in the build's own mod gap already (game_mod_gap -> enable_set): not again
    mods = sorted({m for e in envs if not (e.why or "").startswith(relentless_live.UNDEPLOYED) for m in e.mods})
    cmds = sorted({e.cmd for e in envs if e.cmd})
    detail = "; ".join(relentless_envcause.line(e) for e in envs)
    rides = all(any((e.why or "").startswith(w) for w in RESTAGE) for e in envs)
    if not rides:
        void_rows(store.root, item, sha, "lane fix: %s" % detail, now)

    def f(s):
        s["env_tried"] = _keep(s.get("env_tried"), {e.fp: [now, e["at"]] for e in envs})
        rem = s["game"].get("remedy") or {}
        s["game"]["remedy"] = {"mods": sorted(set(rem.get("mods") or []) | set(mods)),
                               "cmds": sorted(set(rem.get("cmds") or []) | set(cmds)), "why": detail, "at": now}
        if not rides:
            s["game"].update(phase="stage", stages=0, retry_at=None, ready=None, snag=None, waits_reload=None)
            s["put_down"] = {"on": ("the lane fixes the environment once: %s" % detail), "at": now}
    if _save(store, item, f) is None:
        return True
    store.attempt(item, {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "gen": st["gen"], "end": "game_env_fix",
                         "detail": detail, "sha": sha})
    acts.append({"do": "game_env_fix", "item": item, "why": detail, "mods": mods, "cmds": cmds})
    return not rides


REPAIR_FMT = "GAMEENV_FIX_%s_%s_ITEMS_WAIT"     # rimflow namecheck: subject GAMEENV, intent FIX, <= 44 chars


def repair_id(e):
    """The one repair item for an environment cause: keyed by its kind and fingerprint (relentless_envcause.fp: no paths,
    numbers or times), so every item the same cause stops waits on the same repair (fix the class, not the instance)."""
    return REPAIR_FMT % (e.kind.upper().replace("_OR_", "").replace("_", ""), e.fp[:8].upper())   # PROOFSITE: 7 words max


def _env_route(store, fx, item, envs, now, acts, head=None):
    """Routed ONCE to one fixer that builds (ENV_HOLDS_FIX_ROUTE_TO_BUILDERS): each cause files, joins or reopens its
    repair item (repair_id; filed for the supervisor's seat, needs offline, so a Relentless builder takes it), and the item
    waits `blocked` on it with a dependency wait (relentless_attrib): the ledger block is written by relentless_block.sweep,
    and when the repair CLOSES the item resumes its game phase on the same sha (relentless_attrib.resume), never a builder.
    Before: a game hold the tick delivered to the seat queue, where nobody builds (ART_OVERRIDE_FAMILY_SCRIPT_1 sat held
    overnight on a harness parse bug). Its rows are voided, so the re-read after the fix is fresh; the same cause read
    again after the release routes to the same repair again (reopened if it closed), never a builder or a new gen.
    A filing that fails changes nothing: the rows stand and the next tick routes again."""
    import relentless_attrib
    envs = [e for e in envs if e]
    st = store.load(item)
    if st["status"] != GAME:
        return
    routed = st.get("env_routed") or {}
    seen = [e for e in envs if e.fp in routed]
    detail = "; ".join(relentless_envcause.line(e) for e in envs) or "no row named the cause"
    why = ("game phase: environment, routed once to one fixer, no builder and no new generation%s%s: %s"
           % ("; %s" % head if head else "", "; the same cause again after its route" if seen else "", detail))
    sha = st["game"]["sha"]
    if not envs:        # nothing names a cause: one repair for the unnamed (a dud with no row)
        envs = [relentless_envcause.Env(kind="proof_or_site", fp=relentless_envcause._key("proof_or_site", ""),
                                        criterion=None, why="", mods=[], log=None)]
    repairs = []
    for e in envs:
        rep = repair_id(e)
        if rep in repairs:
            continue
        title = ("Game-lane environment cause (%s) no lane step can fix stops live proofs: %s"
                 % (e.kind, (e.why or "no row named the cause")))
        text = ("relentless: %s at %s waits on this repair (blocked; it resumes its game phase on the same sha when this "
                "closes, no builder is sent to it): %s" % (item, sha[:12], relentless_envcause.line(e)))
        err = fx.env_repair(rep, title, text)
        if err:
            store.journal({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "do": "alarm",
                           "kind": "game_env_route_failed", "item": item, "why": ("%s: %s" % (rep, err))})
            acts.append({"do": "game_env_route_failed", "item": item, "repair": rep, "why": str(err)})
            return
        repairs.append(rep)
    why = ("%s | waits on %s" % (why, ", ".join(repairs)))

    def f(s):
        s["env_routed"] = _keep(s.get("env_routed"), {e.fp: now for e in envs})
        s["status"] = "blocked"
        s["blocked_at"] = now
        s["wait"] = {"kind": relentless_attrib.WAIT_DEPENDENCY, "class": "game_env", "detail": why, "since": now,
                     "sha": sha, "resume": GAME, "on": repairs[0], "incident": None, "attributed_at": now}
        s["block_pending"] = {"kind": "item", "on": list(repairs), "class": "game_env", "detail": why}
        s["put_down"] = {"on": ("waits on %s: %s" % (", ".join(repairs), detail)), "at": now}
    if _save(store, item, f) is None:
        return
    void_rows(store.root, item, sha, "routed: %s" % detail, now)
    store.attempt(item, {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "gen": st["gen"],
                         "end": "game_env_route", "detail": detail, "sha": sha, "repairs": repairs})
    store.journal({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "do": "alarm", "kind": "game_env",
                   "item": item, "repairs": repairs, "why": why})
    acts.append({"do": "game_env_route", "item": item, "repairs": repairs, "why": why})


def _hold(store, fx, item, why, now, acts):
    def f(st):
        st["status"] = "held"
        st["hold"] = {"why": why, "kind": "game", "delivered": False, "at": now}
        st["put_down"] = {"on": why, "at": now}
    _save(store, item, f)
    acts.append({"do": "game_held", "item": item, "why": why})


NOT_REPRODUCED = "not reproduced"


def _not_reproduced(store, fx, item, missed, now, acts):
    """repro_miss_limit misses on one build: a game hold (unhold returns it to the prove phase, with fresh tries), the
    attempt ending `not_reproduced`, and last_fail carrying every miss's verdict line, never only a log path."""
    detail = "; ".join("%s: %d repro misses on its site: %s" % (k, n, " | ".join(ws))
                       for k, (n, ws) in sorted(missed.items()))
    why = "game phase: %s: %s" % (NOT_REPRODUCED, detail)

    def f(st):
        st["status"] = "held"
        st["hold"] = {"why": why, "kind": "game", "delivered": False, "at": now}
        st["put_down"] = {"on": why, "at": now}
        st["last_fail"] = {"class": "not_reproduced", "detail": detail, "at": now}
        st["game"]["missed_at"] = now
    _save(store, item, f)
    store.attempt(item, {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "gen": store.load(item)["gen"],
                         "end": "not_reproduced", "detail": detail})
    acts.append({"do": "game_not_reproduced", "item": item, "why": detail})
    fx.ledger_note(item, ("relentless game phase: held, %s: %s" % (NOT_REPRODUCED, detail)))


FLYER = "flyer:"
OWNER_LOOK = "owner look:"


def owner_looks(led, lines, keys):
    """-> {criterion: why} of `keys` that are his own act (relentless_live.owner_look: a look, a keep, a sign-off, or a
    proof reading OWNER.jsonl). RELENTLESS_FIX_GAME_LANE_OWNER_LOOK_FAILS: WATER_DEPTH_RESKIN_HE_LOOKS_FIRST bound L4
    ("the owner has looked at the one review and kept it") as a game clause and bounced 4 times on a check only he can
    pass. Such a clause is never run on the game; the item goes to him once every game clause has PASSed."""
    import relentless_live
    crit = led.get("criteria") or {}
    out = {}
    for k in sorted(keys):
        why = relentless_live.owner_look(crit.get(k) or {"id": k, "level": (led.get("owed") or {}).get(k)}, lines.get(k))
        if why:
            out[k] = why
    return out


def owner_look_hold(why):
    """This game hold waits on his look: every game clause PASSed and only his act is owed. His to lift, like a flyer's."""
    return (why or "").startswith("game phase: " + OWNER_LOOK)


def _owner_hold(store, fx, item, looks, whys, now, acts):
    """Every game clause PASSed; what is left is his look: held on him (needs=owner, relentless.hold_is_his), its clone
    back, never a game_fail and never a worker round."""
    why = "game phase: %s every game clause PASSed; %s owed, the owner's own act (%s): no game can pass it" % (
        OWNER_LOOK, ", ".join(looks), "; ".join("%s %s" % (k, whys.get(k) or "his look") for k in looks))
    _hold(store, fx, item, why, now, acts)
    acts.append({"do": "game_owner_look", "item": item, "clauses": list(looks)})


def flyer_hold(why):
    """This game hold's words say a flyer's flight, the one game hold only he can lift. Anchored where _hold writes the
    reason: the rest of a why is free text (proof paths, mod names, file names), and "flyer" in it says nothing."""
    return (why or "").startswith("game phase: " + FLYER)


REFUSED_KEEP = 20       # fingerprints kept per item: enough for every clause of an item and its stale builds


def _refuse(store, fx, sup, r, item, klass, why, fp, now, acts):
    """A refusal no game can change (LIVE_REFUSAL_SILENCE_SAME_TEXT_HELD). The first time, the item goes back to a
    worker with the reason, and `fp` (relentless_live.fingerprint: criterion, cause, proof, whole criterion text) is
    kept; the same fp again means the worker changed none of that, so it is held with the reason and takes no game slot
    or worker round again until a person lifts it. Before: GRAFFITI_NORTHSTAR_GREEN_FULL_1 A1 and A2 were refused 35
    times each on one unchanging cut criterion."""
    seen = (store.load(item).get("refused_fps") or {})
    if fp in seen:
        return _hold(store, fx, item, "game phase: refused again unchanged after a return (%s, first %s): %s"
                     % (klass, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(seen[fp])), why), now, acts)

    def keep(s):
        fps = dict(s.get("refused_fps") or {})
        fps[fp] = now
        s["refused_fps"] = dict(sorted(fps.items(), key=lambda kv: kv[1])[-REFUSED_KEEP:])
    _save(store, item, keep)
    return _back(store, fx, sup, r, item, klass, why, now, acts)


RETIERED = "re-tiered"      # relentless_live.owed's word for a ledger criterion older than the .criteria line of its id


def _rerecord(store, fx, item, sha, acts):
    """The ledger holds an older criterion under an id the .criteria file now words otherwise (re-tiered,
    GRAFFITI_NORTHSTAR_GREEN_FULL_1): record the manifest again from that file. Only the supervisor can (`rimflow
    implemented` refuses a worker on an item relentless carries), so a worker sent back for it could change nothing.
    -> None when recorded, else rimflow's refusal."""
    text = fx.proofs_at(item, sha, ".criteria")
    led = fx.game_ledger(item) if hasattr(fx, "game_ledger") else None
    # a manifest replaces the last: each ledger criterion the file does not name is carried over, as close_rerecord
    # does, so a re-record never drops an owed clause (Codex cd905b re-review)
    again = fx.game_implement(item, sha, with_kept(text, (led or {}).get("criteria") or {}),
                              (store.load(item).get("contract") or {}).get("live"))
    acts.append({"do": "game_rerecorded", "item": item, "why": (again or "ok")})
    return again



def with_kept(text, ledger):
    """The `.criteria` text plus one line for each ledger criterion ({id: {level, text}}) it does not name. Pure."""
    named = _criteria_lines(text)
    kept = ["%s %s: %s" % (cid, c.get("level"), (c.get("text") or "").strip())
            for cid, c in sorted(ledger.items()) if cid not in named]
    if not kept:
        return text
    return (text or "").rstrip("\n") + "\n" + "".join(k + "\n" for k in kept)


def _criteria_lines(text):
    """-> {cid: (level, text cut as the ledger keeps it)} of the criterion lines in a .criteria file. Pure."""
    import model
    got = {}
    for line in (text or "").splitlines():
        m = model.CRITERION_LINE_RE.match(line)
        if m:
            got[m.group("cid")] = (m.group("level"), m.group("text").strip()[:model.CRITERION_TEXT_MAX])
    return got


def criteria_moved(text, ledger):
    """-> the ids both the `.criteria` file (`text`) and the ledger manifest (`ledger`: {id: {level, text}}) hold, whose
    level or wording the file now says otherwise (re-tiered). The ledger keeps a text's first CRITERION_TEXT_MAX chars,
    as model does. A line only one side holds is not a re-tier and moves nothing. Pure."""
    lines, ledger = _criteria_lines(text), ledger or {}
    return [cid for cid, (level, words) in sorted(lines.items()) if cid in ledger
            and (ledger[cid].get("level") != level or (ledger[cid].get("text") or "").strip() != words)]


def close_rerecord(store, fx, item, sha, acts):
    """The closing step's twin of _preflight's re-record (CLOSE_RETIER_FIX_LEDGER_STILL_OWES_L1): a non-game item whose
    candidate re-tiers a criterion in live_proofs/<ID>.criteria (L1 -> L0) left the ledger owing the old level, and
    `close` refused it for ever ('still owes A2 L1'). When the file at `sha` re-tiers a ledger criterion, the manifest is
    recorded again from the file, each ledger criterion the file does not name carried over as it stands (a manifest
    replaces the last, and a closing step drops no clause). -> None when nothing moved or the re-record landed, else
    rimflow's refusal."""
    led = fx.game_ledger(item)
    if led is None:
        return None
    text = fx.proofs_at(item, sha, ".criteria")
    ledger = led.get("criteria") or {}
    moved = criteria_moved(text, ledger)
    if not moved:
        return None
    again = fx.game_implement(item, sha, with_kept(text, ledger),
                              (store.load(item).get("contract") or {}).get("live"),
                              why="relentless: blind PASS; the candidate's .criteria re-tiers %s, recorded again "
                                  "before the close" % ", ".join(moved))
    acts.append({"do": "close_rerecorded", "item": item, "moved": moved, "why": (again or "ok")})
    return again

CARRY_MAX = 8      # carries per game entry: a build carried this often is waiting on something else, and goes back


def _carry_origin(store, item, sha):
    """The item's OWN build a carry is computed from: the carried green's origin, else `sha`."""
    return ((store.load(item).get("game") or {}).get("offline_green") or {}).get("carried_from") or sha


def _not_carried(store, fx, item, sha):
    """-> "; not carried: <path (commit)>, ..." naming the non-assembly changes since the item's own build that stopped
    the carry, or "" (OPS_CHURN_DIAGNOSE_PIT_XGUR_QNTR: a stale return naming only the rebuilt DLL told the worker
    nothing it could act on)."""
    if not hasattr(fx, "game_carry_blockers"):
        return ""
    origin = _carry_origin(store, item, sha)
    got = fx.game_carry_blockers(item, origin) or []
    if not got:
        return ""
    return "; not carried: since %s %s" % (origin[:12], ", ".join("%s (%s)" % pc for pc in got[:5]))


def _carry(store, fx, item, sha, now, acts):
    """A stale build whose only later change is another commit's rebuild of a shared assembly (relentless_live.carry):
    the game phase moves to that commit, the Judge's offline green carried with its origin named, the ledger re-recorded
    there. No worker, no strike: the worker it went to could only land a commit that changes nothing
    (OPS_CHURN_DIAGNOSE_SUMP_GSVT_SSCT). -> the new sha, or None (the stale build goes back as before)."""
    g = store.load(item).get("game") or {}
    if g.get("carries", 0) >= CARRY_MAX or not hasattr(fx, "game_carry"):
        return None
    # carry again from the item's OWN build, never from a carried sha: that is another commit, judged on its own sources
    # (SUMP_TAR_FIRE_NETWORK_1: carried 64cfba -> 890c85, GSS_END_HEAPS; CordLayer.cs changed after 890c85, so a carry
    # computed from 890c85 refused and the item went back to a worker who could change nothing)
    origin = _carry_origin(store, item, sha)
    got = fx.game_carry(item, origin)
    if not got:
        return None
    new, why = got
    if new.startswith(sha) or sha.startswith(new):
        return None
    led = fx.game_ledger(item) if hasattr(fx, "game_ledger") else None
    # the carried manifest keeps every ledger criterion the file does not name, as _rerecord does (Codex cd905b round 2)
    if fx.game_implement(item, new, with_kept(fx.proofs_at(item, new, ".criteria"), (led or {}).get("criteria") or {}),
                         (store.load(item).get("contract") or {}).get("live"),
                         why="relentless: carried from %s, %s" % (origin[:12], why)) is not None:
        return None

    def mv(s):
        gg = s["game"]
        green = dict(gg.get("offline_green") or {})
        green.update(sha=new, carried_from=green.get("carried_from") or sha)
        gg.update(sha=new, offline_green=green, carries=gg.get("carries", 0) + 1, proved_at=None,
                  carried={"from": sha, "to": new, "at": now, "why": why})
    _save(store, item, mv)
    acts.append({"do": "game_carried", "item": item, "from": sha[:12], "to": new[:12]})
    fx.ledger_note(item, "relentless game phase: build carried %s -> %s, no worker: %s" % (sha[:12], new[:12], why))
    return new


RECARRY_EVERY_S = 600      # a returned stale build asks carry again at most this often (each ask is a few git calls)


def recarry_returned(store, fx, now, acts):
    """A stale build that went back to a worker and still waits for one (queued) is asked to carry again before any
    worker is sent: the carry it was refused may have been the supervisor's own defect, fixed since. When the Judge's
    green still stands (same sha as the candidate, same contract, clauses owed) and the item's OWN build now carries,
    it re-enters the game phase on that green; the game step's preflight then carries it there (_carry). No worker, and
    the item keeps its returns. OPS_CHURN_DIAGNOSE_SUMP_GSVT_SSCT: SUMP_TAR_FIRE_NETWORK_1 went back at 18:16Z on a
    carry refused by carry_scope's defect; d2ac77bb77 fixed it at 18:43Z and the same carry answered dfc2007c13, but the
    item sat queued for a worker (approach pilot) who could change nothing, and its churn alarm re-rang at 19:07Z."""
    if not hasattr(fx, "game_carry"):
        return
    for item in store.items():
        st = store.load(item) or {}
        g, lf = st.get("game") or {}, st.get("last_fail") or {}
        green = g.get("offline_green") or {}
        if (st.get("status") != "queued" or lf.get("class") != "game_stale_build" or st.get("hold") or st.get("wait")
                or st.get("block_pending") or st.get("run") or st.get("awaiting_ledger") or not green.get("sha")
                or (st.get("candidate") or {}).get("sha") != green["sha"] or not owes(st, green["sha"])
                or green.get("contract") != contract_print(st.get("contract"))
                or now - (st.get("recarry_at") or 0) < RECARRY_EVERY_S):
            continue
        _save(store, item, lambda s: s.update(recarry_at=now))
        origin = green.get("carried_from") or green["sha"]
        got = fx.game_carry(item, origin)
        if not got:
            continue
        why = "returned stale build carries now: %s -> %s, %s" % (origin[:12], got[0][:12], got[1])
        with store.lock():
            cur = store.load(item)
            if cur.get("status") != "queued" or cur.get("run") or (cur.get("last_fail") or {}).get("class") != "game_stale_build":
                continue
            reenter(store, cur, now, why)
            store.attempt(item, {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "gen": cur["gen"],
                                 "routed": "recarried", "sha": green["sha"], "detail": why, "to": GAME})
        acts.append({"do": "game_recarried", "item": item, "from": origin[:12], "to": got[0][:12]})
        fx.ledger_note(item, "relentless game phase: %s; back to the game step, no worker" % why)


def _preflight(store, fx, sup, r, item, lines, now, acts, sha):
    """relentless_live.preflight before a game slot is spent (implement, before a staging load, before a proof round):
    -> True when the item was sent back or held. A stale build goes back to be rebuilt on the newer bytes; a refused
    clause goes back to have its criterion or proof line fixed (LIVE_CUT_CRITERION_ENFORCE_AT_IMPLEMENT,
    LIVE_STALE_HARDEN_CAUGHT_BEFORE_SLOT)."""
    import relentless_live_round
    sites = relentless_live_round.proof_lines(fx.proofs_at(item, sha), relentless_live_round.SITE_LINE)
    bad = fx.game_preflight(item, lines, sites)
    if any(RETIERED in b["why"] for b in bad) and _rerecord(store, fx, item, sha, acts) is None:
        bad = fx.game_preflight(item, lines, sites)
    bad = bad + _names_bad(store, fx, item, sha, acts)
    if any(b["kind"] == "stale" for b in bad) and _carry(store, fx, item, sha, now, acts):
        return True     # the next tick reads the carried build afresh
    if not bad:
        return False
    stale = [b for b in bad if b["kind"] == "stale"]
    first = stale[0] if stale else bad[0]
    klass = "game_stale_build" if stale else "game_contract"
    why = first["why"] + _not_carried(store, fx, item, sha) if stale else "; ".join("%s %s" % (b["cid"], b["why"]) for b in bad)
    fp = first["fp"] if stale else "+".join(sorted(b["fp"] for b in bad))
    _refuse(store, fx, sup, r, item, klass, "live preflight: %s" % why, fp, now, acts)
    return True


def _names_bad(store, fx, item, sha, acts):
    """LIVE_MODS_ENFORCE_ROLL_CALL_BEFORE_BOARDING: the item's `live-mods:`/`live-deploy:` names through the one resolver
    (relentless_names) before any slot -> [a preflight refusal] when one names no mod this machine has (what it looked
    like and the nearest names), else []. Its need inference is advice only: journaled once per build, never written into
    a proof. A fake without game_names_check checks nothing."""
    if not hasattr(fx, "game_names_check"):
        return []
    got = fx.game_names_check(item, sha)
    why, advice, inferred = got[0], got[1], (got[2] if len(got) > 2 else [])
    if (advice or inferred) and ((store.load(item) or {}).get("game") or {}).get("advised") != sha:
        act = {"do": "live_mods_advice", "item": item, "sha": sha,
               "advice": ["%s (%s)" % (a["mod"], a["at"]) for a in advice][:8]}
        if inferred:    # LIVE_NEEDS_ENFORCE_ABSENCE_NOW_EXPLICIT: added to the load by the gate, never to the proof
            act["inferred"] = ["%s (%s %s)" % (a["mod"], a["src"], a["at"]) for a in inferred][:8]
        acts.append(act)
        _save(store, item, lambda s: s.setdefault("game", {}).update(advised=sha))
    if not why:
        return []
    return [{"cid": "live-mods", "why": why, "kind": "refused",
             "fp": "names:" + hashlib.sha1(why.encode("utf-8")).hexdigest()[:12]}]


def _harness(store, fx, r, item, why, now, acts):
    """Stagings that leave no running build are OUR failure (owner: a live problem is not an owner problem): put down,
    the count reset, staged again after a growing wait; an alarm and a ledger note say why. Never _hold."""
    c = cfg(r)
    out = {}

    def f(s):
        gg = s["game"]
        n = gg.get("harness", 0) + 1
        wait = int(min(c["harness_retry_s"] * n, c["harness_retry_max_s"]))
        out.update(n=n, wait=wait)
        gg.update(phase="stage", stages=0, harness=n, retry_at=now + wait, harness_why=why)
        gg.pop("spare_load", None)      # only the blind-probe deadline spares a load; it sets it after this
        s["put_down"] = {"on": ("harness #%d, staged again in %ds: %s" % (n, wait, why)), "at": now}
    if _save(store, item, f) is None:
        return
    store.journal({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "do": "alarm", "kind": "game_harness",
                   "item": item, "why": why})
    acts.append({"do": "game_harness", "item": item, "why": why, "retry_s": out["wait"]})
    fx.ledger_note(item, "relentless game phase: a harness failure, not an owner question (#%d): %s; staged again in %ds"
                   % (out["n"], why, out["wait"]))


STAGE_STOP = "game_stage"


def _stage_stop(store, fx, sup, r, item, detail, now, acts):
    """STAGER_SNAG_REWIRE_BUILDER_WOKEN_FOR_HARNESS: the stager stopped before any proof ran, and the item entered this
    lane through a blind PASS. Only a stop naming the item's own mod goes back to a builder (a strike, a new generation).
    Any other is the environment: restaged (_harness, its growing wait), no worker. The same stop after that restage goes
    to one repair item (_env_route), the item waiting on it, so a stop nothing here can change never loads the game for
    ever. Before: HEAVY_TEXTURES_MEASURE_REAL_VRAM gen 5 went back 2026-11-06 13:55Z for a companion exact-hash gate fixed
    32 minutes later, and the builder could change nothing."""
    st = store.load(item)
    try:
        own = fx.game_own_mods(item, st["game"]["sha"])
    except ValueError:      # mods_of's refusal: an unreadable build names no mod, and no worker could act on the stop
        own = []
    if relentless_envcause.stage_names(detail, own):
        return _back(store, fx, sup, r, item, STAGE_STOP, detail, now, acts)
    e = relentless_envcause.stage_stop(detail)
    _save(store, item, lambda s: s["game"].update(snag=None))
    if e.fp in (st.get("env_tried") or {}):
        _env_route(store, fx, item, [e], now, acts, "the lane restaged once and the stager stopped the same way")
        if store.load(item)["status"] != GAME:
            return
        # the repair could not be filed: _env_route's alarm is out, and the restage below retries it on the next stop
    _save(store, item, lambda s: s.update(env_tried=_keep(s.get("env_tried"), {e.fp: [now, now]})))
    store.attempt(item, {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "gen": st["gen"], "end": "game_env_fix",
                         "detail": ("stager stop, restaged: %s" % detail), "sha": st["game"]["sha"]})
    _harness(store, fx, r, item, "the stager stopped before any proof ran: %s" % detail, now, acts)


def _waits(store, fx, item, why, now, acts):
    """Put down on what it waits for. It holds no place and its clone is parked (relentless.release_parked); a flyer
    waits on the owner himself, so it is held and the ledger asks him: never picked again until he lifts the hold
    (owner 2026-11-02: "put down blocked items once they become blocked and go do something else")."""
    if why.startswith(FLYER):
        return _hold(store, fx, item, "game phase: %s" % why, now, acts)
    _save(store, item, lambda s: s.update(put_down={"on": why, "at": now}))
    acts.append({"do": "game_waits", "item": item, "why": why})


def _reload(store, fx, r, item, rd, why, now, acts):
    """The running game cannot serve this build (mod_gap_why): no prove round. Another untried item gets the running
    game first (bounded); then it stages the one load that enables its mods. A final item stages the full list."""
    c = cfg(r)
    g = store.load(item)["game"]
    first = g.get("waits_reload") or now
    mark = {"game": rd.get("started"), "why": why, "at": now}
    acts.append({"do": "game_mod_gap", "item": item, "why": why})
    other = untried(store.states(), item, rd["started"]) if rd.get("started") and now - first < c["batch_wait_s"] else None
    if other:
        w = "waits for one reload: the running game may serve %s first (%s)" % (other, why)
        _save(store, item, lambda s: (s.update(put_down={"on": w, "at": now}),
                                      s["game"].update(waits_reload=first, mod_gap=mark)))
        return
    if g["stages"] >= stage_tries(c, g):
        _save(store, item, lambda s: s["game"].update(mod_gap=mark))
        return _harness(store, fx, r, item, "%d staging(s) and the game still cannot serve it: %s" % (g["stages"], why),
                        now, acts)
    _save(store, item, lambda s: (s.update(put_down={"on": why, "at": now}),
                                  s["game"].update(phase="stage", mod_gap=mark, waits_reload=None,
                                                   full=True if s["game"].get("final_since") else s["game"].get("full"))))


def step(store, fx, r, item, now, acts, sup):
    """One transition of an item in status `game`. `sup` is relentless (fail, settle, finished, run_desc, unit_name)."""
    st = store.load(item)
    g = st["game"]
    c = cfg(r)
    sha = g["sha"]
    led = fx.game_ledger(item)
    if led is None or led["state"] in ("dropped", "superseded"):
        if g["phase"] == "proving" and not g.get("broker") and g.get("prove_pid") and fx.prove_alive(g["prove_pid"]):
            # its detached proof still drives the game: retiring now would end the item's claim on the live user and
            # let another stage and restart under it (Codex cd905b round 2). It retires once the proof has exited.
            acts.append({"do": "retire_waits_proof", "item": item, "pid": g["prove_pid"]})
            return
        with store.lock():
            cur = store.load(item)
            cur["gen"] += 1
            if g["phase"] == "staging":     # the bridge goes back once its staging worker is settled, never before:
                cur["release_bridge"] = True    # other_active counts it the game's live user until then
            cur["status"] = "retiring"
            cur["stopping_since"] = now
            store.save(cur)
        acts.append({"do": "retire", "item": item})
        return
    if led["state"] == "done" and g["phase"] != "staging":
        _save(store, item, lambda s: s["game"].update(passed_sha=sha, phase="passed"))
        sup.finished(store, fx, item, st["candidate"], now, acts, attempt=True)
        return

    if g["phase"] == "implement":
        recorded = led["state"] in ("built", "validated") and same_sha(led["built_sha"], sha)
        if recorded:
            why = None
        else:
            nc = no_code_rebuild(st, sha, _paths_of(fx, sha))
            why = fx.game_implement(item, sha, fx.proofs_at(item, sha, ".criteria"), (st["contract"] or {}).get("live"),
                                    **({"no_code": nc} if nc else {}))
            led = fx.game_ledger(item) if not why else led
        if why:
            return _back(store, fx, sup, r, item, "game_contract", "rimflow implemented refused: %s" % why, now, acts)
        # a clause already met at this build (a verify event since `implemented`) is not owed, and not missing either:
        # it leaves the game clauses (MODCHECK_DONOR_ENVIRONMENTS_1: A2 passed live, then read as "missing" forever)
        lines = proof_lines(fx.proofs_at(item, sha))
        # his own act (a look, a keep) is no game clause: skipped here, his once the rest pass (owner_hold)
        his = owner_looks(led, lines, set(g["clauses"]) | set(led["owed"]))
        clauses = [k for k in g["clauses"] if k not in his]
        met = [k for k in clauses if k not in led["owed"] and k in (led.get("passed") or {})]
        missing = [k for k in clauses if k not in led["owed"] and k not in met]
        notlive = [k for k in clauses if k in led["owed"] and led["owed"][k] not in LIVE_LEVELS()]
        if missing or notlive:
            return _back(store, fx, sup, r, item, "game_contract",
                         "game clauses not owed at a live level after implemented: missing %s, not live %s; add them to "
                         "%s/%s.criteria" % (missing, notlive, PROOFS_DIR, item), now, acts)
        # a GREEN-FULL clause the criteria file owes with a proof line joins the game clauses (a contract written before
        # PROOF_TIERS_WIDEN_SMALL_LIST_FIRST_ALWAYS names only the small ones), or the item would wait on it forever
        # the live lane refuses a line bash builds at run time or one that mutates the game; caught here it costs a
        # worker round, caught there a live run that measures nothing (OPS_RELENTLESS_LIVE_MEASURE_RESTORE_LRPU: 5 of 40)
        import relentless_live
        lr = relentless_live.live_rules(r)
        bad = [(k, relentless_live.refused_proof(lr, led.get("title"), "", lines[k])) for k in sorted(lines)
               if k in led["owed"] and k not in his]
        bad = [(k, w) for k, w in bad if w and not w.startswith("flyer:")]     # a flyer is put down, not sent back
        if bad:
            return _back(store, fx, sup, r, item, "game_contract", "; ".join(
                "%s/%s.txt %s: %s" % (PROOFS_DIR, item, k, w) for k, w in bad), now, acts)
        finals = [k for k in sorted(led["owed"]) if led["owed"][k] == FINAL_LEVEL and k not in g["clauses"] and k in lines
                  and k not in his]
        # an owed live criterion that joins no game clause (a GREEN-FULL with no proof line, or one at a smaller level
        # the contract never named) is verified by nothing, so the item would wait at the all-PASS return below forever:
        # it goes back for its line or its clause (Codex review, RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN #7)
        stray = [k for k in sorted(led["owed"]) if led["owed"][k] in LIVE_LEVELS() and k not in g["clauses"]
                 and k not in finals and k not in his]
        if stray:
            return _back(store, fx, sup, r, item, "game_contract",
                         "owed live criteria %s join no game clause: a %s one needs `live-proof <id>: <command>` in "
                         "%s/%s.txt; any other is named with `contract --game` (the same --proof)"
                         % (stray, FINAL_LEVEL, PROOFS_DIR, item), now, acts)
        owed_lines = {k: lines[k] for k in clauses + finals if k in lines and k not in met}
        if _preflight(store, fx, sup, r, item, owed_lines, now, acts, sha):
            return
        _save(store, item, lambda s: s["game"].update(
            phase="prove", clauses=[k for k in s["game"]["clauses"] if k not in met and k not in his] + finals,
            owner_clauses=sorted(his)))
        acts.append({"do": "game_implemented", "item": item, "sha": sha})
        return

    if g["phase"] == "proving":
        if g.get("broker") and _broker_holds(store, fx, item, g, now, acts):
            return      # its lines are in the broker's running batch (relentless_broker)
        if not g.get("broker") and g.get("prove_pid") and fx.prove_alive(g["prove_pid"]):
            return
        _save(store, item, lambda s: (s["game"].update(phase="prove"), s["game"].pop("broker", None)))
        g = store.load(item)["game"]

    if g["phase"] == "prove":
        if g.get("broker"):
            if _broker_holds(store, fx, item, g, now, acts):
                return  # queued for the game broker: put down, holding nothing, until a batch runs its lines
            _save(store, item, lambda s: s["game"].pop("broker", None))
            g = store.load(item)["game"]
        his = owner_looks(led, proof_lines(fx.proofs_at(item, sha)), g["clauses"])
        if his:     # a state from before RELENTLESS_FIX_GAME_LANE_OWNER_LOOK_FAILS still names his look as a game clause
            _save(store, item, lambda s: s["game"].update(
                clauses=[k for k in s["game"]["clauses"] if k not in his],
                owner_clauses=sorted(set(s["game"].get("owner_clauses") or []) | set(his))))
            g = store.load(item)["game"]
        built = led.get("built_sha") if same_sha(led.get("built_sha"), sha) else sha
        if steve_sync(store, fx, r, item, g, built, now, acts) == STEVE_WAIT:
            return      # what is still open runs on SteveDesktop through testq: Archmagi's game has nothing to do
        g = store.load(item)["game"]
        rows = outcomes(fx.game_rows(), item, built, g["clauses"])
        import relentless_live
        # LIVE_VERDICT_BUILD_INFRA_NOT_FAIL: only a FAIL verdict (the proof ran after a healthy check) is a strike
        fails = [(k, v) for k, v in rows.items() if v.get("outcome") == "FAIL" and relentless_live.verdict(v) == "FAIL"]
        if fails:
            rd = fx.game_reading()      # still up on the build that failed: the next worker works it live, no reload
            # only on the very game every FAIL ran on (its row's game_started): a game started since may not run the
            # failed build, so no live iteration is granted on it (Codex, ..._TEN_MORE #10)
            same_game = bool(rd.get("started")) and all(
                v.get("game_started") == relentless_live.iso(rd["started"]) for _, v in fails)
            live = ({"started": rd.get("started"), "at": now, "sha": sha, "clauses": [k for k, _ in fails]}
                    if rd.get("state") == "UP" and same_game else None)
            return _back(store, fx, sup, r, item, "game_fail", "; ".join(fail_detail(k, v) for k, v in fails), now,
                         acts, live=live)
        if len(rows) == len(g["clauses"]) and all(v.get("outcome") == "PASS" for v in rows.values()):
            looks = [k for k in g.get("owner_clauses") or [] if k in led["owed"]]
            if looks:
                return _owner_hold(store, fx, item, looks, owner_looks(led, proof_lines(fx.proofs_at(item, sha)), looks),
                                   now, acts)
            return      # the last verify moves the ledger to done; the next tick finishes it
        rd0 = fx.game_reading()
        _finals, waiting = final_split(rows, led["owed"], g["clauses"], rd0.get("started"))
        if waiting:     # otherwise done: only the full-list final verification is owed; it waits for a batched load
            why = "final verification: every other clause PASSed; waits for one full-list load with the batch"
            _save(store, item, lambda s: (s.update(put_down={"on": why, "at": now}),
                                          s["game"].update(phase="final", final_since=s["game"].get("final_since") or now,
                                                           final_game=rd0.get("started"), waits_reload=None,
                                                           full=None)))
            acts.append({"do": "game_final_wait", "item": item})
            return
        lane = [v for v in rows.values() if v.get("outcome") == "SKIPPED"]
        if lane:
            return _hold(store, fx, item, "game phase: %s" % lane[0].get("why"), now, acts)
        refused = [v for v in rows.values() if v.get("outcome") == "REFUSED"]
        at = [v.get("at") for v in refused]
        if refused and all(RETIERED in (v.get("why") or "") for v in refused):
            # the run read an older ledger criterion: the supervisor re-records it and the next round's row decides.
            # Once per entry to the game lane (st["game"] is new each entry), so a re-record that changed nothing is
            # refused as before instead of spending a round each time
            if g.get("rerecorded_for") == at:
                refused = []
            elif not g.get("rerecorded_for") and _rerecord(store, fx, item, sha, acts) is None:
                _save(store, item, lambda s: s["game"].update(rerecorded_for=at, proved_at=None))
                g, refused = store.load(item)["game"], []
        if refused:
            v = refused[0]
            return _refuse(store, fx, sup, r, item, "game_refused", v.get("why") or "refused",
                           fx.refusal_print(item, v.get("criterion"), v.get("why"), v.get("proof")), now, acts)
        import relentless_live_round
        if _env(store, fx, r, item, rows, max(g.get("staged_at") or 0, g["entered_at"]), now, acts):
            return      # an environment cause: the lane fixed it once and re-reads, or routed it once; never a builder
        infra = [v for v in rows.values() if v.get("outcome") == "UNMEASURED" and v.get("harness")
                 and row_at(v) >= max(g.get("staged_at") or 0, g["entered_at"])]
        if infra:       # INFRA on infra_games games: OUR failure, an alarm and a later restage, never a worker strike
            v = infra[0]
            return _harness(store, fx, r, item, "%s %s (%s)" % (v.get("criterion"), v.get("why") or "",
                                                                v.get("log") or ""), now, acts)
        dead = [v for v in rows.values() if v.get("outcome") in NO_VERDICT and relentless_live_round.decides(v)]
        if dead:        # a build no game can run, or a cause that outlived a reload: no stage or proof round can help
            v = dead[0]
            if not v.get("defect") and _carry(store, fx, item, sha, now, acts):
                return      # only a rebuilt shared assembly made it stale: proved on the carried build next round
            return _refuse(store, fx, sup, r, item, "game_proof_unmeasured" if v.get("defect") else "game_stale_build",
                           "%s %s UNMEASURED (%s): %s%s" % (v.get("criterion"), v.get("proof") or "", v.get("log") or "",
                                                            v.get("why") or "", (" [likewise %s: see their logs]" % ", ".join(
                                                                sorted(x.get("criterion") or "?" for x in dead[1:])))
                                                            if dead[1:] else ""),
                           fx.refusal_print(item, v.get("criterion"), v.get("why"), v.get("proof")), now, acts)
        missed = {k: m for k, m in repro_misses(fx.game_rows(), item, built, g["clauses"], g.get("missed_at") or 0).items()
                  if m[0] >= c["repro_miss_limit"]}
        if missed:  # the defect did not appear where its repro asked: a person reads it, no builder is sent
            return _not_reproduced(store, fx, item, missed, now, acts)
        dud = not_measuring(fx.game_rows(), item, built, g["clauses"], c["unmeasured_back"])
        if dud:     # the proof ran and said it measured nothing, again: the proof's or its site's, never a builder's
            return _env_route(store, fx, item, [relentless_envcause.dud(rows.get(k), item) for k in sorted(dud)],
                              now, acts, "the proof ran %s times on this build and measured nothing"
                              % "/".join(str(n) for _, (n, _w) in sorted(dud.items())))
        here = blocked_here(rows, g["clauses"], built, rd0.get("started"), now)
        if here:    # nothing left this game can measure, and a proof ran and measured nothing: routed at once
            return _env_route(store, fx, item, [relentless_envcause.dud(rows.get(k), item) for k in sorted(here)],
                              now, acts, "the proof ran on this game and build and measured nothing; the same game and "
                              "build can only say it again")
        since = max(g.get("staged_at") or 0, g["entered_at"])
        stale = [v for v in rows.values() if v.get("outcome") in NO_VERDICT and row_at(v) >= since
                 and any((v.get("why") or "").startswith(w) for w in RESTAGE)]
        rd = fx.game_reading()
        state = rd.get("state")
        if rd.get("started"):       # a row from an earlier game says nothing of this one: it is tried first
            stale = [v for v in stale if row_at(v) >= rd["started"]]
        if state is None:       # the supervisor could not look: a harness gap, never "no game", never a restart
            return _waits(store, fx, item, "harness: the game cannot be read from the supervisor: %s"
                          % (rd.get("evidence") or "no reading"), now, acts)
        if state == "LOADING":  # a cold load: wait it out, holding nothing, up to the bound of the list that loads
            held, why = _load_gate(store, fx, r, item, g, rd, now, acts)
            if held:
                return
            stale = [{"why": why}]
        if stale and state == "UP" and rd.get("started"):
            # the running game cannot serve this item; before a reload, every other game item gets its try on it, and
            # this one waits (bounded) to ride the one reload with the rest
            first = g.get("waits_reload") or now
            other = untried(store.states(), item, rd["started"]) if now - first < c["batch_wait_s"] else None
            if other:
                why = ("waits for one reload: the running game may serve %s first (%s)"
                       % (other, (stale[0].get("why") or "")))
                _save(store, item, lambda s: (s.update(put_down={"on": why, "at": now}),
                                              s["game"].update(waits_reload=first)))
                acts.append({"do": "game_batch_wait", "item": item, "why": why})
                return
        if stale or state == "DOWN":
            if g["stages"] >= stage_tries(c, g):
                return _harness(store, fx, r, item, "%d staging(s) and the build still is not running: %s"
                                % (g["stages"], (stale[0].get("why") if stale else rd.get("evidence") or "no game")),
                                now, acts)
            _save(store, item, lambda s: s["game"].update(phase="stage"))
            g = store.load(item)["game"]
        else:
            if (g.get("proved_at") or 0) >= since and now - g["proved_at"] < c["prove_every_s"]:
                return      # a round ran since the last staging and measured nothing: the bridge was busy, try later
            brk = _broker_on(store, fx)     # the broker waits for the idle game, so a queued item asks only the gate
            why = _gate_why(store, fx, r, item, sha, led) if brk else _lease_why(store, fx, r, item, sha, led)
            if why:
                return _waits(store, fx, item, why, now, acts)
            if _preflight(store, fx, sup, r, item, _owed_lines(fx, item, sha, g, led), now, acts, sha):
                return      # HEAD may have moved the build's files since implement: caught here, not as a run row
            mg = g.get("mod_gap") or {}     # a running load cannot gain a mod: one reading per game is enough
            gap = (mg.get("why") if rd.get("started") and mg.get("game") == rd["started"]
                   else mod_gap_why(fx.game_mod_gap(item, built)))
            if gap:         # the running game lacks the build's mods: no prove round, a reload that enables them
                return _reload(store, fx, r, item, rd, gap, now, acts)
            if brk and _broker_offer(store, fx, item, sha, g, rd, now, acts):
                return      # LIVELANE_BUILD_GAME_BROKER_PROOF_LINES: a broker fault falls through to its own round
            if brk:     # the fault fallback is the old lane again: it asks the lease (bridge, other users) it had waived
                why = _lease_why(store, fx, r, item, sha, led)
                if why:
                    return _waits(store, fx, item, why, now, acts)
            pid = fx.prove_launch(item)
            _save(store, item, lambda s: (s.pop("put_down", None), s["game"].update(phase="proving", prove_pid=pid,
                                                                                     proved_at=now, waits_reload=None)))
            session_note(store, rd.get("started"), item, served=True, mods=rd.get("mods"), now=now)
            acts.append({"do": "game_prove", "item": item, "pid": pid})
            return

    if g["phase"] == "final":
        rd = fx.game_reading()
        if busy(store, item) is not None:
            return      # one live user at a time; waiting here holds nothing
        if (rd.get("state") == "UP" and rd.get("started") and rd["started"] != g.get("final_game")
                and not menu_bound(fx, item, sha)):     # a menu-time proof needs its own staging
            # a newer game may be the full list already (another item's load, or the owner's): one try, no load
            _save(store, item, lambda s: s["game"].update(phase="prove", staged_at=now, waits_reload=None))
            acts.append({"do": "game_final_try_running", "item": item, "started": rd["started"]})
            return
        queue = finals_waiting(store.states())
        if not queue or queue[0][1] != item:
            return      # the oldest final stages the one load for the batch
        if len(queue) < c["final_batch_min"] and now - queue[0][0] < c["final_wait_s"] and not st.get("expedite"):
            return
        _save(store, item, lambda s: s["game"].update(phase="stage", full=True, stages=0))
        acts.append({"do": "game_final_stage", "item": item, "batch": [q[1] for q in queue]})
        g = store.load(item)["game"]

    if g["phase"] == "stage":
        if (g.get("retry_at") or 0) > now:
            return      # put down on a harness failure until its retry: it holds no place, the bridge is free
        built0 = led.get("built_sha") if same_sha(led.get("built_sha"), sha) else sha
        if not g.get("full") and steve_sync(store, fx, r, item, g, built0, now, acts) in (STEVE_WAIT, STEVE_FAIL):
            # every open clause is an exact tier: SteveDesktop's, so no Archmagi staging, no list swap (owner by card
            # 2026-11-05); the item waits in prove for testq. A Steve FAIL stages nothing either: prove returns it
            if store.load(item)["status"] == "game":
                _save(store, item, lambda s: s["game"].update(phase="prove"))
            return
        g = store.load(item)["game"]
        rd = fx.game_reading()
        spare = g.get("spare_load")
        if spare is not None and rd.get("state") == "LOADING" and (spare.get("started") is None
                                                                   or spare.get("started") == rd.get("started")):
            # the attempt ended on a blind stall probe, not on evidence: the clock alone never restarts that load, so
            # the prove phase reads it again (and ends the attempt again, counted, while the probe stays blind)
            _save(store, item, lambda s: s["game"].update(phase="prove"))
            acts.append({"do": "game_spare_load", "item": item, "started": rd.get("started")})
            return
        if spare is not None:
            _save(store, item, lambda s: s["game"].pop("spare_load", None))
            g = store.load(item)["game"]
        if rd.get("state") is None:     # unread, as on the prove road: a harness gap, never a launch (Codex r5 game1 #1)
            return _waits(store, fx, item, "harness: the game cannot be read from the supervisor: %s"
                          % (rd.get("evidence") or "no reading"), now, acts)
        if rd.get("state") == "LOADING" and _load_gate(store, fx, r, item, g, rd, now, acts)[0]:
            return      # every road into a staging meets the load bound and the stall evidence, not only the prove one
        if rd.get("state") == "UP" and rd.get("started"):
            # another item's load may already run this build (owner 2026-11-02, "To save game loads"): an item that has
            # no row from the running game tries it before it stages a load of its own (BIOME_TIER_CLEANUP_1 read DOWN
            # while CONTAGION's staging restarted the game, and would have staged a third load untried)
            built = led.get("built_sha") if same_sha(led.get("built_sha"), sha) else sha
            seen = [v for v in outcomes(fx.game_rows(), item, built, g["clauses"]).values() if row_at(v) >= rd["started"]]
            if not seen and busy(store, item) is None and (g.get("mod_gap") or {}).get("game") != rd["started"] \
                    and not g.get("remedy") and not menu_bound(fx, item, sha):
                # a lane fix, or a live-menu/live-toggle proof, needs its own staging: the running game says the same
                _save(store, item, lambda s: s["game"].update(phase="prove", staged_at=rd["started"], waits_reload=None))
                acts.append({"do": "game_try_running", "item": item, "started": rd["started"]})
                return
        why = _lease_why(store, fx, r, item, sha, led)
        if why:
            return _waits(store, fx, item, why, now, acts)
        if _preflight(store, fx, sup, r, item, _owed_lines(fx, item, sha, g, led), now, acts, sha):
            return      # a staging is a game load: never spent on a build no game can run or a clause a run refuses
        why = _clone(store, fx, r, st, now, acts, sup)
        if why:
            return _waits(store, fx, item, "clone: " + why, now, acts)
        st = store.load(item)
        others = [o for o in batch(store.states(), item, now, full=bool(g.get("full"))) if _rides_ok(fx, r, o)]
        if not g.get("full"):   # the full list already holds them
            others += stranded_riders(fx, r, store.states(), item, now)
        try:        # STAGING_MENU_FIX_ALWAYS_PARKS_ON_MAPS: a with/without item stages alone, and never rides
            mine = toggles(fx, {"item": item, "game": {"sha": sha}})
            others = [] if mine else [o for o in others if not toggles(fx, o) and menu_ok(fx, o)]
            if mine and g.get("full"):  # the full list holds the mod: its without side can never load
                raise ValueError("a live-toggle pair cannot stage on the full list (final verification)")
            menu = staging_menu(fx, item, sha, g["stages"], others)
        except ValueError as e:     # a malformed live-toggle or a {toggle} with no side: no load can serve it
            return _hold(store, fx, item, "game phase: the live_proofs file's live-menu/live-toggle: %s" % e, now, acts)
        built = led.get("built_sha") if same_sha(led.get("built_sha"), sha) else sha
        gaps = [fx.game_batch_gap([(item, built)] + [(o["item"], o["game"]["sha"]) for o in others
                                                     if (o.get("game") or {}).get("sha")])]
        bad = sorted({x["item"] for x in gaps[0].get("refused") or [] if x.get("pos")})
        if bad:     # a rider whose names resolve nowhere drops itself only; its own preflight sends it back
            acts.append({"do": "game_rider_names_refused", "item": item, "riders": bad,
                         "why": "; ".join(x["why"] for x in gaps[0]["refused"] if x.get("pos"))})
            others = [o for o in others if o["item"] not in bad]
        split = sorted({x["item"] for x in gaps[0].get("split") or []})
        if split:   # needs X / live-without X: never one load; the rider stages on a load of its own later
            acts.append({"do": "game_rider_without_split", "item": item, "riders": split,
                         "why": "; ".join(x["why"] for x in gaps[0]["split"])})
            others = [o for o in others if o["item"] not in split]
        if bad or split:    # the dropped riders' mods and menu steps leave with them (Codex cd905b re-review)
            gaps = [fx.game_batch_gap([(item, built)] + [(o["item"], o["game"]["sha"]) for o in others
                                                         if (o.get("game") or {}).get("sha")])]
            try:
                menu = staging_menu(fx, item, sha, g["stages"], others)
            except ValueError as e:
                return _hold(store, fx, item, "game phase: the live_proofs file's live-menu/live-toggle: %s" % e, now, acts)
        # every rider's own lane fix rides with it: a passenger marked staged without its remedy run would read its next
        # identical environment failure as a failed fix and hold (Codex, ..._TEN_MORE #9)
        remedy = merged_remedy([g.get("remedy")] + [(o.get("game") or {}).get("remedy") for o in others]) or {}
        want = sorted(set(enable_set(gaps)) | set(remedy.get("mods") or []))
        if menu["toggle"]:      # the pair's side: the mod on top of the list, or kept off it (the stager checks)
            low = menu["toggle"].lower()
            want = sorted(set(w for w in want if w.lower() != low) | ({menu["toggle"]} if menu["side"] == "with" else set()))
            acts.append({"do": "game_toggle_side", "item": item, "mod": menu["toggle"], "side": menu["side"]})
        if want and not g.get("full"):      # the full list's own staging restores FULL.LATEST, then enables on top
            why = fx.modlist_enable(want)
            if why and others:
                # a rider's names are the rider's defect, never this item's hold (OPS_CHURN_DIAGNOSE_PLAYER_YGLE_IHKT:
                # PLAYER_START_SITE_1 was held on riders' Utils/bridgetools/BiomesShell, TITANIC on a rider's
                # RimMandrake.FlowWorks): the item's own mods are tried alone, and it stages alone if they enable
                gaps = [fx.game_batch_gap([(item, built)])]
                remedy = merged_remedy([g.get("remedy")]) or {}
                alone = sorted(set(enable_set(gaps)) | set(remedy.get("mods") or []))
                menu = staging_menu(fx, item, sha, g["stages"])     # its riders' menu steps leave with them
                acts.append({"do": "game_modlist_riders_dropped", "item": item, "riders": [o["item"] for o in others],
                             "why": why})
                others = []
                want = alone
                why = fx.modlist_enable(want) if want else None
            if why:     # no restart path holds these mods: held with the reason, never a load that cannot serve it
                store.journal({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "do": "alarm",
                               "kind": "game_modlist", "item": item, "why": why})
                fx.ledger_note(item, "relentless game phase: held, the next load cannot hold its mods: %s" % why)
                return _hold(store, fx, item, "game phase: modlist_swap.py --enable %s refused: %s"
                             % (" ".join(want), why), now, acts)
            acts.append({"do": "game_modlist_enable", "item": item, "mods": want})
        off = without_set(gaps, menu)
        if off and not g.get("full") and hasattr(fx, "modlist_disable"):
            # STAGING_REMOVAL_FIX_ONLY_KNOWS_ADDITION: a load that must LACK a mod is made, never hoped for (the
            # stager takes them off again after its own swap: the plan's `without`)
            why = fx.modlist_disable(off)
            if why:
                fx.ledger_note(item, "relentless game phase: held, the next load cannot lack %s: %s" % (", ".join(off), why))
                return _hold(store, fx, item, "game phase: modlist_swap.py --disable %s refused: %s"
                             % (" ".join(off), why), now, acts)
            acts.append({"do": "game_modlist_disable", "item": item, "mods": off})
        gap = fx.clone_gap(st["clone"])     # checked again at the launch: QUICKTEST_POLICY_NRE_FULLLIST_1 launched without
        if gap:                             # claude_bounded.sh; the bridge is never taken for a stage that cannot start
            return _waits(store, fx, item, "clone: %s lacks %s; the next prepare makes it again" % (st["clone"], gap),
                          now, acts)
        took = fx.bridge_take("relentless staging %s: deploy and restart for its live proofs" % item)
        if took:
            acts.append({"do": "game_waits", "item": item, "why": "bridge: %s" % took})
            return
        unit = sup.unit_name("stage", item, st["gen"]) + "-s%d" % (g["stages"] + 1)
        desc = sup.run_desc(store, r, unit, now)

        def f(s):
            s.pop("put_down", None)
            s["run"] = desc
            s["game"].update(toggle=menu["toggle"], side=menu["side"])     # stage_tries reads it; show says the side
            s["game"].update(phase="staging", staged_at=now, taken_at=now, up_seen=None, stages=s["game"]["stages"] + 1,
                             ready=None, snag=None, waits_reload=None, batch=[o["item"] for o in others])
            # this staging carries the remedy; it is spent only when the staging confirms game-ready (settle below),
            # never at launch: a staging that died before running it would leave the fix unapplied and its next
            # identical row read as "fixed once" (Codex r4 game1 #3)
            if s["game"].get("remedy"):
                s["game"]["remedy_carried"] = s["game"].pop("remedy")
        st = _save(store, item, f)
        if st is None:
            fx.bridge_release()
            return
        st["_proofs_text"] = fx.proofs_at(item, sha)
        trees = fx.game_trees([(item, built)] + [(o["item"], o["game"]["sha"]) for o in others
                                                 if (o.get("game") or {}).get("sha")])
        comp = game_companion_owed(fx, [(item, built)] + [(o["item"], o["game"]["sha"]) for o in others
                                                          if (o.get("game") or {}).get("sha")])
        agent = r["pilot_agent"]
        if c.get("stage_python", True):     # the prompt rides as the python stager's fallback brief only
            agent = STAGE_AGENT
            st["_stage_plan"] = stage_plan(st, c, sha, others, want, dll_mods(gaps), trees, remedy,
                                           getattr(fx, "game_deploy_args", None), companion=comp, menu=menu,
                                           without=off)
        why = fx.launch(st, desc, stage_prompt(st, r, sha, others, want, dll_mods(gaps), trees, remedy, comp, menu,
                                               without=off), agent,
                        st["clone"], c["stage_max_s"], {"RELENTLESS_ROOT": store.root, "RELENTLESS_GEN": str(st["gen"])})
        if why:
            fx.bridge_release()
            _save(store, item, lambda s: (s["game"].update(phase="stage", **({"remedy": g["remedy"]} if g.get("remedy") else {})),
                                          s["game"].pop("remedy_carried", None)))
            acts.append({"do": "game_stage_launch_failed", "item": item, "why": why})
            return
        for o in others:        # this staging carries each rider's remedy too, spent as the item's is
            if (o.get("game") or {}).get("remedy"):
                _save(store, o["item"], lambda s: s["game"].__setitem__("remedy_carried", s["game"].pop("remedy")))
        acts.append({"do": "game_stage", "item": item, "unit": unit})
        return

    if g["phase"] == "staging":
        run = st.get("run")
        done, seen = staged_idle(fx, g, c, now) if fx.alive(run) and not g.get("ready") else (None, g.get("up_seen"))
        if seen != g.get("up_seen"):
            _save(store, item, lambda s: s["game"].update(up_seen=seen))
        if done:
            acts.append({"do": "game_stage_idle", "item": item, "why": done})
        if fx.alive(run) and now - g["staged_at"] < c["stage_max_s"] and not g.get("ready") and not done:
            if now - g.get("taken_at", 0) >= c["renew_s"]:      # a hold with no event for 45 min is anyone's
                if not fx.bridge_take("relentless staging %s (renew)" % item):
                    _save(store, item, lambda s: s["game"].update(taken_at=now))
            return
        # settle's stop/force/quarantine clock runs from the first stop, never from staged_at: a staging ended at
        # stage_max_s (or by staged_idle) is already past stop_quarantine_s from staged_at, and was quarantined
        # unstopped on the first tick ("unit ... would not die", ART_OVERRIDE_FAMILY_SCRIPT_1 19:22:51Z, 2026-11-03)
        stop_since = g.get("stop_since")
        if stop_since is None and fx.alive(run):
            stop_since = now
            _save(store, item, lambda s: s["game"].update(stop_since=now))
        if not sup.settle(store, fx, r, item, "run", stop_since if stop_since is not None else now, now, acts):
            return
        gave = fx.bridge_release()       # at once, however staging ended
        st = _save(store, item, lambda s: s["game"].update(phase="prove", released=gave is None, full=None,
                                                          stop_since=None))
        rode = []
        ran = bool(st and st["game"].get("ready")) and not (st and st["game"].get("snag"))

        def spend(s):       # a remedy is spent only by a staging that confirmed game-ready; else it waits for the next
            carried = s["game"].pop("remedy_carried", None)
            if carried and not ran:
                s["game"]["remedy"] = merged_remedy([s["game"].get("remedy"), carried])
        if st:
            st = _save(store, item, spend) or st

        def ride(s):
            spend(s)
            if s["game"].get("phase") in ("prove", "stage", "final"):
                s["game"].update(phase="prove", staged_at=now, waits_reload=None)
                rode.append(s["item"])
        for o in g.get("batch") or []:      # the items that rode this reload try the new game, none stages its own
            _save(store, o, ride)
        acts.append({"do": "game_staged", "item": item, "released": gave is None, "batch": rode})
        if st and st["game"].get("snag"):
            sn = st["game"]["snag"]
            if (sn.get("class") or STAGE_STOP) == STAGE_STOP:
                return _stage_stop(store, fx, sup, r, item, sn.get("detail") or "", now, acts)
            return _back(store, fx, sup, r, item, sn["class"], sn.get("detail") or "", now, acts)
        return


def _clone(store, fx, r, st, now, acts, sup):
    """The stage runs in the item's own clone, verified and made again when it was released while the item waited
    (BLUEDESERT_FLORA_PLANT_REFUSAL_1 launched in a parked-away path: "missing claude_bounded.sh"). Never the books:
    the books are the supervisor's. -> None, or why it cannot have one now."""
    item = st["item"]
    if not st.get("clone"):
        path = fx.clone_path(item, len(st.get("quarantined") or []))
        _save(store, item, lambda s: s.update(clone=path))
        st = store.load(item)
    if not fx.clone_present(st["clone"]):
        hold = sup.make_room(store, fx, r, now, acts)
        if hold:
            return hold
        acts.append({"do": "clone_try", "by": "check"})
    return fx.prepare(st)


def _owed_lines(fx, item, sha, g, led):
    """The game clauses still owed on the ledger -> {clause: its live-proof line at `sha`}."""
    lines = proof_lines(fx.proofs_at(item, sha))
    return {k: lines[k] for k in g["clauses"] if k in lines and k in (led.get("owed") or {})}


def merged_remedy(rems):
    """Several lane fixes (_env_fix's remedy) as one: mods and producer commands unioned, the whys joined. None if none."""
    rems = [x for x in rems if x]
    if not rems:
        return None
    return {"mods": sorted({m for x in rems for m in x.get("mods") or []}),
            "cmds": sorted({c for x in rems for c in x.get("cmds") or []}),
            "why": "; ".join(x.get("why") or "" for x in rems if x.get("why")),
            "at": max(x.get("at") or 0 for x in rems)}


def _rides_ok(fx, r, o):
    """A batched item rides this staging only past its own gate and preflight (flyer, proof lines, changed files),
    read without side effects: one that fails is left to stage on its own step, which refuses or sends it back."""
    import relentless_live
    og = o.get("game") or {}
    led = fx.game_ledger(o["item"])
    if led is None or led["state"] in ("dropped", "superseded", "done") or not og.get("sha"):
        return False
    if gate(o, led.get("title"), fx.proofs_at(o["item"], og["sha"]), relentless_live.live_rules(r)["flyer_re"], None):
        return False
    return not fx.game_preflight(o["item"], _owed_lines(fx, o["item"], og["sha"], og, led))


# PROOFYIELD_REPAIR_THREE_OF_THIRTEEN_MEASURED: a built item whose last row says its mods are not on the game (HOSTILE_FLORA,
# LORE_STAGES, FLAME_STATUES: one NOT_ADMITTED row a load, for days) had nobody to stage them: eligible() takes proposed/
# ready only, and 357 built bridge items had no store record. A staging is the one thing that deploys and enables, so a
# few of them ride each one; the next cron round then proves them. A rotating few, so one rider's gap starves none.
STRANDED_RIDERS = 4
STRANDED_ADMIT = ("deploy_gap", "running_load")     # relentless_live.ADMIT: the causes a staging can end
STRANDED_FROM = (None, "queued", "held", "blocked", "done", "retired")      # no worker or phase is moving its build


def stranded_riders(fx, r, states, item, now):
    """-> rider dicts ({"item", "game": {"sha"}, "stranded": True}) for built items a load would serve, at most
    STRANDED_RIDERS, in `others`' shape. Read only. A flyer, a refused preflight or a build the ledger moved past is left."""
    if not hasattr(fx, "game_rows"):
        return []
    import relentless_live
    import relentless_live_round as LR
    status = {s["item"]: s["status"] for s in states}
    shas = {}
    for (i, _c, sha), row in LR.history(fx.game_rows()).items():
        if (row.get("outcome") == relentless_live.NOT_ADMITTED and row.get("admit") in STRANDED_ADMIT and sha and i != item
                and status.get(i) in STRANDED_FROM):
            shas.setdefault(i, set()).add(sha)
    names = sorted(shas)
    start = int(now // 3600) % len(names) if names else 0
    lr, out = relentless_live.live_rules(r), []
    for i in (names[start:] + names[:start])[:STRANDED_RIDERS * 3]:     # each look replays the ledger: a staging is in a tick
        if len(out) >= STRANDED_RIDERS:
            break
        led = fx.game_ledger(i)
        built = (led or {}).get("built_sha")
        sha = next((x for x in sorted(shas[i]) if same_sha(built, x)), None)
        if not sha or led.get("state") not in relentless_live.TESTABLE:
            continue
        # the books' current file, the one the live run reads: lightspeed_wire wrote these items' lines long after the build
        text = (getattr(fx, "_mods_text", None) or fx.proofs_at)(i, built) or ""
        lines = proof_lines(text)
        owed = {k: lines[k] for k in led.get("owed") or {} if k in lines}
        if LR.live_menu(text) or LR.live_toggle(text):      # measures only on a staging of its own: it never rides
            continue
        if not owed or relentless_live.flyer_word(lr, led.get("title"), *[("proof", v) for v in owed.values()]):
            continue
        if fx.game_preflight(i, owed):
            continue
        out.append({"item": i, "game": {"sha": built}, "stranded": True})
    return out


def _lease_why(store, fx, r, item, sha, led):
    import relentless_live
    other = busy(store, item)
    why = gate(store.load(item), led.get("title"), fx.proofs_at(item, sha), relentless_live.live_rules(r)["flyer_re"],
               other)
    return why or fx.bridge_idle("relentless game phase %s" % item)


def _gate_why(store, fx, r, item, sha, led):
    """_lease_why without the game's other users: what bars the item itself (flyer, no proof line)."""
    import relentless_live
    return gate(store.load(item), led.get("title"), fx.proofs_at(item, sha), relentless_live.live_rules(r)["flyer_re"],
                None)


# ---------------------------------------------------------------- the game broker (relentless_broker)

def _broker_on(store, fx):
    try:
        import relentless_broker
        return relentless_broker.active(store, fx)
    except Exception:  # noqa: BLE001  no broker: the lane as it was
        return False


def _broker_offer(store, fx, item, sha, g, rd, now, acts):
    """Queue the item's lines and put it down. -> False on a fault (recorded): the caller launches its own round."""
    import relentless_broker
    try:
        at = relentless_broker.offer(store, item, sha, g["clauses"], rd.get("started"), now)
        why = "queued for the game broker: %d clause(s)" % len(g["clauses"])
        _save(store, item, lambda s: (s.update(put_down={"on": why, "at": now}), s["game"].update(
            broker={"queued_at": at, "game": rd.get("started")}, waits_reload=None)))
        acts.append({"do": "game_broker_queued", "item": item, "clauses": len(g["clauses"])})
        return True
    except Exception as e:  # noqa: BLE001  a broker fault falls back to the item's own prove round
        relentless_broker.fault(store, "offer", e)
        return False


def _broker_holds(store, fx, item, g, now, acts):
    """True while the broker still owns the item's turn (queued, or in a running batch). False when the turn is over or
    the broker is off or faulted: the item then walks the tree as before."""
    import relentless_broker
    try:
        if not relentless_broker.active(store, fx):
            return False
        if g["phase"] == "proving":
            relentless_broker.reconcile(store, now, acts)   # an abandoned batch is marked lost (and journalled) first
        held = (not relentless_broker.over(store, item, g, now) if g["phase"] == "proving"
                else relentless_broker.waiting(store, item, g))
        if not held:
            relentless_broker.forget(store, item)
        return held
    except Exception as e:  # noqa: BLE001
        relentless_broker.fault(store, "settle", e)
        return False


def LIVE_LEVELS():
    import relentless_live
    return relentless_live.LIVE_LEVELS


# ---------------------------------------------------------------- what the staging worker may call

def ready(store, item, gen, note, now=None):
    now = time.time() if now is None else now
    with store.lock():
        st = store.load(item)
        if not staging(st, gen):
            raise ValueError("%s gen %d is not staging (now %s)" % (item, gen, (st or {}).get("status")))
        st["game"]["ready"] = {"at": now, "note": (note or "")}
        st["last_beat"] = now
        store.save(st)


def staging(st, gen):
    return bool(st) and st["status"] == GAME and st["gen"] == gen and (st.get("game") or {}).get("phase") == "staging"


if __name__ == "__main__":
    print(json.dumps(DEFAULTS, indent=1))
