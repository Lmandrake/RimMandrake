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
             on the smallest list that holds the item's mods, then exits. The bridge is released the moment it ends.

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
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

GAME = "game"
DEFAULTS = {"enabled": False, "pool_needs": ["deploy", "game-up", "bridge"], "stage_max_s": 3600, "stage_tries": 2,
            "prove_every_s": 900, "renew_s": 1200,
            # a cold load's bound, sized to the list that loads (rimworld-load-round: 13 mods ~22 s, the full ~316 ~15-25
            # min): base + per mod, from the live ModsConfig.xml; unread, the full list's
            "load_base_s": 180, "load_per_mod_s": 6, "load_unknown_s": 2400,
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
            # RELENTLESS_GAME_HOLD_UNSTICK_IDLE_LIVE_ITER: a live-iterating worker that has not held the bridge for its item this
            # long is working offline, not on the game; its hold lapses so the next item may prove (ATMOSBASE held the
            # game 47 min, bridge free, ten items waiting, 2026-11-03)
            "live_idle_s": 1200}
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
    "a read-only command that exits 0 when the clause holds and 1 when it does not. Batch: one proof per clause, every "
    "clause in one file, so one sitting proves them all. If a clause is not on the item's ledger criteria, add it to "
    "infrastructure/state/live_proofs/<ID>.criteria as `A2 L1: what is observed` (L1 minimal-list read, L2 behaviour on a "
    "quicktest map). The supervisor leases the bridge, deploys and restarts only when your offline proof is green on the "
    "same sha, then reruns the live proofs blind. Never a flyer's flight; never fullscreen or focus the game; the minimal "
    "mod list (all five DLC) when it is enough.",
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
    words = " ".join([title or ""] + [lines[c] for c in k.get("clauses") or []])
    if re.search(flyer_re, words, re.I):
        return "flyer: a flyer's flight is never live-tested without the owner present"
    return None


def other_active(states, item):
    for s in states:
        if s["item"] != item and s["status"] == GAME and (s.get("game") or {}).get("phase") in ACTIVE:
            return s["item"]
        if s["item"] != item and s["status"] == "running" and s.get("live_iter"):
            return s["item"]        # a worker iterating on the running game is its one live user
    return None


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
    """The game items waiting in phase final, oldest first: [(final_since, item)]."""
    return sorted(((s["game"].get("final_since") or 0), s["item"]) for s in states
                  if s["status"] == GAME and (s.get("game") or {}).get("phase") == "final")


def final_split(rows, owed, clauses, started):
    """-> (final clauses, waiting) where waiting is True when every non-final clause PASSed and every final clause
    either PASSed or read FINAL_WAIT on the game that started at `started` (so this game cannot verify it)."""
    finals = [k for k in clauses if owed.get(k) == FINAL_LEVEL]
    if not finals:
        return finals, False
    small_ok = all((rows.get(k) or {}).get("outcome") == "PASS" for k in clauses if k not in finals)
    waits = [k for k in finals if (rows.get(k) or {}).get("outcome") == "UNMEASURED"
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
            e["reload_needed"][item] = reload_why[:300]
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
                  "offline_green": {"sha": sha, "at": now, "nonce": (st.get("check") or {}).get("nonce")}}
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


def outcomes(rows, item, sha, clauses):
    """runs.jsonl rows -> {clause: deciding row} on `sha` (relentless_live_round.history's rule)."""
    import relentless_live_round
    h = relentless_live_round.history(rows)
    return {c: h[(item, c, sha)] for c in clauses if (item, c, sha) in h}


RAN_DUD = re.compile(r"the proof (exited \d+: it did not measure|timed out)")


def not_measuring(rows, item, sha, clauses, limit):
    """-> {clause: (rows, newest why)} for each clause whose proof RAN on `sha` and exited neither PASS nor FAIL at least
    `limit` times (OPS_RELENTLESS_LIVE_MEASURE_RESTORE_LRPU: one build re-proved 4x, then reloaded, all UNMEASURED)."""
    out = {}
    for v in rows:
        if (v.get("item") == item and v.get("criterion") in clauses and (v.get("sha") == sha or same_sha(v.get("sha"), sha))
                and v.get("outcome") == "UNMEASURED" and RAN_DUD.search(v.get("why") or "")):
            n, _ = out.get(v["criterion"], (0, ""))
            out[v["criterion"]] = (n + 1, v.get("why") or "")
    return {k: v for k, v in out.items() if limit and v[0] >= limit}


def stage_prompt(st, r, sha, others=()):
    i, g = st["item"], st["gen"]
    rc = "python3 src/RimMandrake/rimflow/relentless.py"
    return "\n".join([
        "You are Relentless's STAGING worker for item %s, generation %d. The supervisor holds the game bridge for you as "
        "seat %s and releases it the moment you exit. Your one job: the running game must run the build at %s, so the "
        "supervisor can rerun this item's live proofs blind. You do NOT run or judge the proofs." % (i, g, r["seat"], sha),
        "1. Deploy: `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod <Mod>` for each mod that %s changed (plan "
        "first, read it, then --apply), and for each mod a `live-mods:` line in the proofs below names (a build that "
        "changed only a proof still needs its mod's tree deployed). Load `rimworld-deploy` first." % sha,
        ("2. FINAL VERIFICATION: the game must start after the deploy on the owner's WHOLE FULL list "
         "(infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml; `rimworld-load-round`: modlist_swap.py restores it), "
         "never a smaller tier: this one load verifies every item's GREEN-FULL clauses at once. Stamp each change with "
         "`./game --idle-ok --why \"relentless final staging %s\" down|loading|up`." % i) if (st.get("game") or {}).get("full") else
        "2. The game must start after the deploy: restart it on the smallest mod list that holds those mods and every "
        "mod a `live-mods:` line in the proofs below names, with their About.xml dependencies "
        "(`rimworld-load-round`: modlist_swap.py; all five DLC always). Never the full list for a GREEN-FULL clause: that "
        "is the batched final verification, staged on its own. Stamp each change with "
        "`./game --idle-ok --why \"relentless staging %s\" down|loading|up`." % i,
        "   Choose the smallest list that proves the item: a cold load is ~22 s on the 13-mod minimal list and 15-25 "
        "minutes on the full one. Wait for it with `./game` polls (each command under 540 s) up to that bound; if you "
        "must exit while it still loads, say so in game-ready: the supervisor waits out the load itself, bounded by "
        "the list's size, and holds no slot while it waits.",
        ("   ONE LOAD FOR ALL: these game items wait for a reload too; deploy each one's build as well (rimworld-deploy) and "
         "choose the smallest list that holds the most of their mods; level your clone to origin/main first (./sync) so "
         "each build is in the tree: %s." % "; ".join(
             "%s at %s" % (o["item"], (o.get("game") or {}).get("sha", "?")[:12]) for o in others)) if others else
        "   No other game item waits for a reload.",
        "3. When the game is up on a map the proofs can read: `%s game-ready --item %s --gen %d \"what you deployed and "
        "which list\"`, then exit. Stopped: `%s snag --item %s --gen %d --class game_stage \"what stopped you\"`, exit."
        % (rc, i, g, rc, i, g),
        "Never fullscreen or focus the game. Never a flyer's flight. Never touch a canonical world save "
        "(infrastructure/state/CANONICAL_SAVE.md). Never `rimflow bridge take/release` or any ledger write on this "
        "item: the supervisor owns both. Foreground commands, timeouts under 540 s, no subagents.",
        "", "--- live proofs it will rerun ---", st.get("_proofs_text", "")[:3000]])


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


def load_bound(c, mods):
    """Seconds a cold load of `mods` mods may take before it counts as failed."""
    return int(c["load_base_s"] + c["load_per_mod_s"] * mods) if mods else int(c["load_unknown_s"])


class GameFx(object):
    """What the game mode asks of the world. Needs self.rimflow, self.books, self.base (relentless.Effects has them)."""

    def proofs_at(self, item, sha, ext=".txt"):
        r = subprocess.run(["git", "show", "%s:%s/%s%s" % (sha, PROOFS_DIR, item, ext)], cwd=self.books,
                           capture_output=True, text=True, timeout=60)
        return r.stdout if r.returncode == 0 else ""

    def game_implement(self, item, sha, criteria_text, live=None):
        args = ["implemented", item, "--sha", sha, "--why", "relentless: blind offline PASS; the game clauses stay owed"]
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
        return None if r.returncode == 0 else (r.stderr or r.stdout)[-400:]

    def game_ledger(self, item):
        """-> {state, built_sha, owed: {criterion: level}} from the ledger, or None."""
        import model
        it = model.replay(model.read()).items.get(item)
        if it is None:
            return None
        crit = {c["id"]: c["level"] for c in it.criteria or []}
        return {"state": it.state, "built_sha": it.built_sha, "title": it.title or "",
                "owed": {c: crit.get(c) for c in it.outstanding or []}}

    def game_rows(self):
        import relentless_live_round
        return relentless_live_round.read_rows(os.path.join(self.base, "live", "runs.jsonl"))

    def game_reading(self):
        """-> {"state": "UP"|"LOADING"|"DOWN"|None, "started": epoch|None, "mods": n|None, "evidence": str}.
        UP: the process runs and the bridge listens; LOADING: it runs, the bridge does not yet; None: no reading taken
        (never read as "no game": that is what held ten items on the owner)."""
        import probe
        import relentless_live
        m = probe.measure(use_cache=False)
        started = relentless_live.Fx(seat=self.r["seat"]).game_started() if m.get("running") else None
        return {"state": m.get("implies"), "started": started, "mods": live_mod_count(),
                "evidence": m.get("evidence") or ""}

    def bridge_reading(self):
        """-> {"holder", "purpose", "since"} of the bridge lock as the ledger reads now."""
        import model
        w = model.replay(model.read())
        return {"holder": w.bridge_holder, "purpose": w.bridge_purpose or "", "since": w.bridge_since}

    def bridge_idle(self, purpose):
        r = self.rimflow("bridge", "idle", "--for", purpose)
        return None if r.returncode == 0 else ((r.stdout or "") + (r.stderr or "")).strip()[-300:]

    def bridge_take(self, purpose):
        r = self.rimflow("bridge", "take", "--idle-ok", "--for", purpose)
        return None if r.returncode == 0 else ((r.stderr or "") + (r.stdout or "")).strip()[-300:]

    def bridge_release(self):
        r = self.rimflow("bridge", "release", "--mine")
        return None if r.returncode == 0 else ((r.stderr or "") + (r.stdout or "")).strip()[-300:]

    def game_preflight(self, item, lines, sites=None):
        """relentless_live.preflight on the ledger and books as a live run would read them: [{cid, why, fp, kind}]."""
        import relentless_live
        return relentless_live.preflight(relentless_live.Fx(books=self.books, seat=self.r["seat"]),
                                         relentless_live.live_rules(self.r), item, lines, sites)

    def refusal_print(self, item, criterion, why, proof):
        """A runs.jsonl refusal -> relentless_live.fingerprint over the criterion's whole text as the ledger reads now."""
        import relentless_live
        it = relentless_live.Fx(books=self.books, seat=self.r["seat"]).item(item) or {}
        text = ({c["id"]: c for c in it.get("criteria") or []}.get(criterion) or {}).get("text") or ""
        return relentless_live.fingerprint(criterion, why, proof, text)

    def prove_launch(self, item):
        import relentless
        os.makedirs(os.path.join(self.base, "live"), exist_ok=True)
        with open(os.path.join(self.base, "live", "round.out"), "a", encoding="utf-8") as out:
            p = subprocess.Popen(["python3", os.path.join(self.books, "src/RimMandrake/rimflow/relentless_live_round.py"),
                                  "round", "--item", item], cwd=self.books,
                                 env=dict(os.environ, RELENTLESS_ROOT=self.base,
                                          PATH=relentless.windows_path(os.environ.get("PATH", ""))),
                                 stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
        return p.pid

    def prove_alive(self, pid):
        return self.live_round_alive(pid)


# ---------------------------------------------------------------- holds that outlived their user

def stale_holds(states, now, c, alive, bridge, reading):
    """-> [(item, kind, why)]: every game-phase holder other_active would count that no longer uses the game. Pure but
    for the callables: alive(pid) -> bool; bridge() -> bridge_reading(); reading() -> game_reading(), each asked only
    when a holder needs it. RELENTLESS_GAME_HOLD_UNSTICK_IDLE_LIVE_ITER: other_active held the game for as long as such a holder
    existed, and only that holder's own step (or its worker's reload-needed) could end it, so one idle holder parked
    every other game item ("one live user at a time") for 47 minutes on 2026-11-03.
      proving   its prove pid is dead: the round ended (its rows, if any, are on runs.jsonl for its step to read)
      live_iter its worker has not held the bridge for this item for live_idle_s, or the game it iterates on is down or
                is a different game than the one that showed the FAIL"""
    out, br, rd = [], None, None
    for s in states:
        g = s.get("game") or {}
        if s["status"] == GAME and g.get("phase") == "proving":
            if not g.get("prove_pid") or not alive(g["prove_pid"]):
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
            if br.get("holder") and s["item"] in (br.get("purpose") or ""):
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
                st["live_lapsed"] = dict(li, lapsed_at=now, why=why[:300])
                store.learn(item, "- %s: the game hold lapsed (%s); the game is free for the next item. Work offline; "
                            "a live iteration needs the game again through a game phase" % (
                                time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), why))
            store.save(st)
        store.journal({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "do": "game_hold_released",
                       "item": item, "kind": kind, "why": why[:300]})
        acts.append({"do": "game_hold_released", "item": item, "kind": kind, "why": why[:200]})


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
        sup.fail(store, st, klass, why, r, now)
        if live:
            st["live_iter"] = live
        store.save(st)
    acts.append({"do": klass, "item": item, "why": why[:200]})
    fx.ledger_note(item, "relentless game phase: %s: %s" % (klass, why))


def _hold(store, fx, item, why, now, acts):
    def f(st):
        st["status"] = "held"
        st["hold"] = {"why": why, "kind": "game", "delivered": False, "at": now}
        st["put_down"] = {"on": why[:200], "at": now}
    _save(store, item, f)
    acts.append({"do": "game_held", "item": item, "why": why[:200]})


FLYER = "flyer:"
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


def _preflight(store, fx, sup, r, item, lines, now, acts, sha):
    """relentless_live.preflight before a game slot is spent (implement, before a staging load, before a proof round):
    -> True when the item was sent back or held. A stale build goes back to be rebuilt on the newer bytes; a refused
    clause goes back to have its criterion or proof line fixed (LIVE_CUT_CRITERION_ENFORCE_AT_IMPLEMENT,
    LIVE_STALE_HARDEN_CAUGHT_BEFORE_SLOT)."""
    import relentless_live_round
    bad = fx.game_preflight(item, lines, relentless_live_round.proof_lines(fx.proofs_at(item, sha),
                                                                           relentless_live_round.SITE_LINE))
    if not bad:
        return False
    stale = [b for b in bad if b["kind"] == "stale"]
    first = stale[0] if stale else bad[0]
    klass = "game_stale_build" if stale else "game_contract"
    why = first["why"] if stale else "; ".join("%s %s" % (b["cid"], b["why"]) for b in bad)
    fp = first["fp"] if stale else "+".join(sorted(b["fp"] for b in bad))
    _refuse(store, fx, sup, r, item, klass, "live preflight: %s" % why, fp, now, acts)
    return True


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
        gg.update(phase="stage", stages=0, harness=n, retry_at=now + wait, harness_why=why[:300])
        s["put_down"] = {"on": ("harness #%d, staged again in %ds: %s" % (n, wait, why))[:200], "at": now}
    if _save(store, item, f) is None:
        return
    store.journal({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "do": "alarm", "kind": "game_harness",
                   "item": item, "why": why[:300]})
    acts.append({"do": "game_harness", "item": item, "why": why[:200], "retry_s": out["wait"]})
    fx.ledger_note(item, "relentless game phase: a harness failure, not an owner question (#%d): %s; staged again in %ds"
                   % (out["n"], why, out["wait"]))


def _waits(store, fx, item, why, now, acts):
    """Put down on what it waits for. It holds no place and its clone is parked (relentless.release_parked); a flyer
    waits on the owner himself, so it is held and the ledger asks him: never picked again until he lifts the hold
    (owner 2026-11-02: "put down blocked items once they become blocked and go do something else")."""
    if why.startswith(FLYER):
        return _hold(store, fx, item, "game phase: %s" % why, now, acts)
    _save(store, item, lambda s: s.update(put_down={"on": why[:200], "at": now}))
    acts.append({"do": "game_waits", "item": item, "why": why})


def step(store, fx, r, item, now, acts, sup):
    """One transition of an item in status `game`. `sup` is relentless (fail, settle, finished, run_desc, unit_name)."""
    st = store.load(item)
    g = st["game"]
    c = cfg(r)
    sha = g["sha"]
    led = fx.game_ledger(item)
    if led is None or led["state"] in ("dropped", "superseded"):
        if g["phase"] == "staging":
            fx.bridge_release()
        with store.lock():
            cur = store.load(item)
            cur["gen"] += 1
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
            why = fx.game_implement(item, sha, fx.proofs_at(item, sha, ".criteria"), (st["contract"] or {}).get("live"))
            led = fx.game_ledger(item) if not why else led
        if why:
            return _back(store, fx, sup, r, item, "game_contract", "rimflow implemented refused: %s" % why, now, acts)
        missing = [k for k in g["clauses"] if k not in led["owed"]]
        notlive = [k for k in g["clauses"] if k in led["owed"] and led["owed"][k] not in LIVE_LEVELS()]
        if missing or notlive:
            return _back(store, fx, sup, r, item, "game_contract",
                         "game clauses not owed at a live level after implemented: missing %s, not live %s; add them to "
                         "%s/%s.criteria" % (missing, notlive, PROOFS_DIR, item), now, acts)
        # a GREEN-FULL clause the criteria file owes with a proof line joins the game clauses (a contract written before
        # PROOF_TIERS_WIDEN_SMALL_LIST_FIRST_ALWAYS names only the small ones), or the item would wait on it forever
        lines = proof_lines(fx.proofs_at(item, sha))
        # the live lane refuses a line bash builds at run time or one that mutates the game; caught here it costs a
        # worker round, caught there a live run that measures nothing (OPS_RELENTLESS_LIVE_MEASURE_RESTORE_LRPU: 5 of 40)
        import relentless_live
        lr = relentless_live.live_rules(r)
        bad = [(k, relentless_live.refused_proof(lr, led.get("title"), "", lines[k])) for k in sorted(lines)
               if k in led["owed"]]
        bad = [(k, w) for k, w in bad if w and not w.startswith("flyer:")]     # a flyer is put down, not sent back
        if bad:
            return _back(store, fx, sup, r, item, "game_contract", "; ".join(
                "%s/%s.txt %s: %s" % (PROOFS_DIR, item, k, w) for k, w in bad), now, acts)
        finals = [k for k in sorted(led["owed"]) if led["owed"][k] == FINAL_LEVEL and k not in g["clauses"] and k in lines]
        owed_lines = {k: lines[k] for k in list(g["clauses"]) + finals if k in lines}
        if recorded and any("re-tiered" in b["why"] for b in fx.game_preflight(item, owed_lines)):
            # the ledger holds an older criterion under the id (GRAFFITI_NORTHSTAR_GREEN_FULL_1): record the manifest
            # again from the .criteria file before anything is judged against it
            again = fx.game_implement(item, sha, fx.proofs_at(item, sha, ".criteria"), (st["contract"] or {}).get("live"))
            acts.append({"do": "game_rerecorded", "item": item, "why": (again or "ok")[:200]})
        if _preflight(store, fx, sup, r, item, owed_lines, now, acts, sha):
            return
        _save(store, item, lambda s: s["game"].update(phase="prove", clauses=list(s["game"]["clauses"]) + finals))
        acts.append({"do": "game_implemented", "item": item, "sha": sha})
        return

    if g["phase"] == "proving":
        if g.get("prove_pid") and fx.prove_alive(g["prove_pid"]):
            return
        _save(store, item, lambda s: s["game"].update(phase="prove"))
        g = store.load(item)["game"]

    if g["phase"] == "prove":
        built = led.get("built_sha") if same_sha(led.get("built_sha"), sha) else sha
        rows = outcomes(fx.game_rows(), item, built, g["clauses"])
        fails = [(k, v) for k, v in rows.items() if v.get("outcome") == "FAIL"]
        if fails:
            rd = fx.game_reading()      # still up on the build that failed: the next worker works it live, no reload
            live = ({"started": rd.get("started"), "at": now, "sha": sha, "clauses": [k for k, _ in fails]}
                    if rd.get("state") == "UP" and rd.get("started") else None)
            return _back(store, fx, sup, r, item, "game_fail", "; ".join(
                "%s FAIL on the running game (%s)" % (k, v.get("log") or v.get("why")) for k, v in fails), now, acts,
                live=live)
        if len(rows) == len(g["clauses"]) and all(v.get("outcome") == "PASS" for v in rows.values()):
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
        if refused:
            v = refused[0]
            return _refuse(store, fx, sup, r, item, "game_refused", v.get("why") or "refused",
                           fx.refusal_print(item, v.get("criterion"), v.get("why"), v.get("proof")), now, acts)
        import relentless_live_round
        dead = [v for v in rows.values() if v.get("outcome") == "UNMEASURED" and relentless_live_round.decides(v)]
        if dead:        # a build no game can run, or a cause that outlived a reload: no stage or proof round can help
            v = dead[0]
            return _refuse(store, fx, sup, r, item, "game_proof_unmeasured" if v.get("defect") else "game_stale_build",
                           "%s %s UNMEASURED (%s): %s" % (v.get("criterion"), v.get("proof") or "", v.get("log") or "",
                                                          v.get("why") or ""),
                           fx.refusal_print(item, v.get("criterion"), v.get("why"), v.get("proof")), now, acts)
        dud = not_measuring(fx.game_rows(), item, built, g["clauses"], c["unmeasured_back"])
        if dud:     # the proof ran and said it measured nothing, again: a proof defect, no reload fixes it
            return _back(store, fx, sup, r, item, "game_unmeasured", "; ".join(
                "%s: the proof ran %d times on this build and measured nothing (%s)" % (k, n, why[:160])
                for k, (n, why) in sorted(dud.items())), now, acts)
        since = max(g.get("staged_at") or 0, g["entered_at"])
        stale = [v for v in rows.values() if v.get("outcome") == "UNMEASURED" and row_at(v) >= since
                 and any((v.get("why") or "").startswith(w) for w in RESTAGE)]
        rd = fx.game_reading()
        state = rd.get("state")
        if rd.get("started"):       # a row from an earlier game says nothing of this one: it is tried first
            stale = [v for v in stale if row_at(v) >= rd["started"]]
        if state is None:       # the supervisor could not look: a harness gap, never "no game", never a restart
            return _waits(store, fx, item, "harness: the game cannot be read from the supervisor: %s"
                          % (rd.get("evidence") or "no reading"), now, acts)
        if state == "LOADING":  # a cold load: wait it out, holding nothing, up to the bound of the list that loads
            bound = load_bound(c, rd.get("mods"))
            age = int(now - (rd.get("started") or g.get("staged_at") or g["entered_at"]))   # never 0 for ever
            if age < bound:
                why = "the game is loading: %ds of a %ds bound (%s mods)" % (age, bound, rd.get("mods") or "unread")
                _save(store, item, lambda s: (s.update(put_down={"on": why, "at": now}),
                                              s["game"].update(loading={"started": rd.get("started"), "bound": bound})))
                acts.append({"do": "game_loading", "item": item, "why": why})
                return
            stale = [{"why": "the game still loads %ds after it started (bound %ds for %s mods)"
                      % (age, bound, rd.get("mods") or "unread")}]
        if stale and state == "UP" and rd.get("started"):
            # the running game cannot serve this item; before a reload, every other game item gets its try on it, and
            # this one waits (bounded) to ride the one reload with the rest
            first = g.get("waits_reload") or now
            other = untried(store.states(), item, rd["started"]) if now - first < c["batch_wait_s"] else None
            if other:
                why = ("waits for one reload: the running game may serve %s first (%s)"
                       % (other, (stale[0].get("why") or "")[:120]))
                _save(store, item, lambda s: (s.update(put_down={"on": why[:200], "at": now}),
                                              s["game"].update(waits_reload=first)))
                acts.append({"do": "game_batch_wait", "item": item, "why": why[:200]})
                return
        if stale or state == "DOWN":
            if g["stages"] >= c["stage_tries"]:
                return _harness(store, fx, r, item, "%d staging(s) and the build still is not running: %s"
                                % (g["stages"], (stale[0].get("why") if stale else rd.get("evidence") or "no game")),
                                now, acts)
            _save(store, item, lambda s: s["game"].update(phase="stage"))
            g = store.load(item)["game"]
        else:
            if (g.get("proved_at") or 0) >= since and now - g["proved_at"] < c["prove_every_s"]:
                return      # a round ran since the last staging and measured nothing: the bridge was busy, try later
            why = _lease_why(store, fx, r, item, sha, led)
            if why:
                return _waits(store, fx, item, why, now, acts)
            if _preflight(store, fx, sup, r, item, _owed_lines(fx, item, sha, g, led), now, acts, sha):
                return      # HEAD may have moved the build's files since implement: caught here, not as a run row
            pid = fx.prove_launch(item)
            _save(store, item, lambda s: (s.pop("put_down", None), s["game"].update(phase="proving", prove_pid=pid,
                                                                                     proved_at=now, waits_reload=None)))
            session_note(store, rd.get("started"), item, served=True, mods=rd.get("mods"), now=now)
            acts.append({"do": "game_prove", "item": item, "pid": pid})
            return

    if g["phase"] == "final":
        rd = fx.game_reading()
        if other_active(store.states(), item) is not None:
            return      # one live user at a time; waiting here holds nothing
        if rd.get("state") == "UP" and rd.get("started") and rd["started"] != g.get("final_game"):
            # a newer game may be the full list already (another item's load, or the owner's): one try, no load
            _save(store, item, lambda s: s["game"].update(phase="prove", staged_at=now, waits_reload=None))
            acts.append({"do": "game_final_try_running", "item": item, "started": rd["started"]})
            return
        queue = finals_waiting(store.states())
        if not queue or queue[0][1] != item:
            return      # the oldest final stages the one load for the batch
        if len(queue) < c["final_batch_min"] and now - queue[0][0] < c["final_wait_s"]:
            return
        _save(store, item, lambda s: s["game"].update(phase="stage", full=True, stages=0))
        acts.append({"do": "game_final_stage", "item": item, "batch": [q[1] for q in queue]})
        g = store.load(item)["game"]

    if g["phase"] == "stage":
        if (g.get("retry_at") or 0) > now:
            return      # put down on a harness failure until its retry: it holds no place, the bridge is free
        rd = fx.game_reading()
        if rd.get("state") == "UP" and rd.get("started"):
            # another item's load may already run this build (owner 2026-11-02, "To save game loads"): an item that has
            # no row from the running game tries it before it stages a load of its own (BIOME_TIER_CLEANUP_1 read DOWN
            # while CONTAGION's staging restarted the game, and would have staged a third load untried)
            built = led.get("built_sha") if same_sha(led.get("built_sha"), sha) else sha
            seen = [v for v in outcomes(fx.game_rows(), item, built, g["clauses"]).values() if row_at(v) >= rd["started"]]
            if not seen and other_active(store.states(), item) is None:
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

        others = batch(store.states(), item, now, full=bool(g.get("full")))

        def f(s):
            s.pop("put_down", None)
            s["run"] = desc
            s["game"].update(phase="staging", staged_at=now, taken_at=now, stages=s["game"]["stages"] + 1,
                             ready=None, snag=None, waits_reload=None, batch=[o["item"] for o in others])
        st = _save(store, item, f)
        if st is None:
            fx.bridge_release()
            return
        st["_proofs_text"] = fx.proofs_at(item, sha)
        why = fx.launch(st, desc, stage_prompt(st, r, sha, others), r["pilot_agent"], st["clone"], c["stage_max_s"],
                        {"RELENTLESS_ROOT": store.root, "RELENTLESS_GEN": str(st["gen"])})
        if why:
            fx.bridge_release()
            _save(store, item, lambda s: s["game"].update(phase="stage"))
            acts.append({"do": "game_stage_launch_failed", "item": item, "why": why[:200]})
            return
        acts.append({"do": "game_stage", "item": item, "unit": unit})
        return

    if g["phase"] == "staging":
        run = st.get("run")
        if fx.alive(run) and now - g["staged_at"] < c["stage_max_s"] and not g.get("ready"):
            if now - g.get("taken_at", 0) >= c["renew_s"]:      # a hold with no event for 45 min is anyone's
                if not fx.bridge_take("relentless staging %s (renew)" % item):
                    _save(store, item, lambda s: s["game"].update(taken_at=now))
            return
        if not sup.settle(store, fx, r, item, "run", g["staged_at"], now, acts):
            return
        gave = fx.bridge_release()       # at once, however staging ended
        st = _save(store, item, lambda s: s["game"].update(phase="prove", released=gave is None, full=None))
        rode = []

        def ride(s):
            if s["game"].get("phase") in ("prove", "stage", "final"):
                s["game"].update(phase="prove", staged_at=now, waits_reload=None)
                rode.append(s["item"])
        for o in g.get("batch") or []:      # the items that rode this reload try the new game, none stages its own
            _save(store, o, ride)
        acts.append({"do": "game_staged", "item": item, "released": gave is None, "batch": rode})
        if st and st["game"].get("snag"):
            sn = st["game"]["snag"]
            return _back(store, fx, sup, r, item, sn.get("class") or "game_stage", sn.get("detail") or "", now, acts)
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


def _lease_why(store, fx, r, item, sha, led):
    import relentless_live
    other = other_active(store.states(), item)
    why = gate(store.load(item), led.get("title"), fx.proofs_at(item, sha), relentless_live.live_rules(r)["flyer_re"],
               other)
    return why or fx.bridge_idle("relentless game phase %s" % item)


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
        st["game"]["ready"] = {"at": now, "note": (note or "")[:600]}
        st["last_beat"] = now
        store.save(st)


def staging(st, gen):
    return bool(st) and st["status"] == GAME and st["gen"] == gen and (st.get("game") or {}).get("phase") == "staging"


if __name__ == "__main__":
    print(json.dumps(DEFAULTS, indent=1))
