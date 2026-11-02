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
            "prove_every_s": 900, "renew_s": 1200}
CLAUSE = re.compile(r"^[A-Z]{1,3}\d{1,3}$")
PROOFS_DIR = "infrastructure/state/live_proofs"
# UNMEASURED reasons (relentless_live.run's own words) that only a deploy or a restart can change
RESTAGE = ("not deployed", "no running game to test", "the game started")
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
    return None


def enter(store, st, sha, now):
    """Under the store lock: an offline PASS on `sha` for an item that owes game clauses. The PASS is the green offline
    proof the lease rule asks for, on this same sha."""
    k = st["contract"]["game"]
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


def stage_prompt(st, r, sha):
    i, g = st["item"], st["gen"]
    rc = "python3 src/RimMandrake/rimflow/relentless.py"
    return "\n".join([
        "You are Relentless's STAGING worker for item %s, generation %d. The supervisor holds the game bridge for you as "
        "seat %s and releases it the moment you exit. Your one job: the running game must run the build at %s, so the "
        "supervisor can rerun this item's live proofs blind. You do NOT run or judge the proofs." % (i, g, r["seat"], sha),
        "1. Deploy: `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod <Mod>` for each mod that %s changed (plan "
        "first, read it, then --apply). Load `rimworld-deploy` first." % sha,
        "2. The game must start after the deploy: restart it on the smallest mod list that holds those mods "
        "(`rimworld-load-round`: modlist_swap.py; all five DLC always). Stamp each change with "
        "`./game --idle-ok --why \"relentless staging %s\" down|loading|up`." % i,
        "3. When the game is up on a map the proofs can read: `%s game-ready --item %s --gen %d \"what you deployed and "
        "which list\"`, then exit. Stopped: `%s snag --item %s --gen %d --class game_stage \"what stopped you\"`, exit."
        % (rc, i, g, rc, i, g),
        "Never fullscreen or focus the game. Never a flyer's flight. Never touch a canonical world save "
        "(infrastructure/state/CANONICAL_SAVE.md). Never `rimflow bridge take/release` or any ledger write on this "
        "item: the supervisor owns both. Foreground commands, timeouts under 540 s, no subagents.",
        "", "--- live proofs it will rerun ---", st.get("_proofs_text", "")[:3000]])


# ---------------------------------------------------------------- effects (mixed into relentless.Effects)

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

    def game_running(self):
        import relentless_live
        return relentless_live.Fx(seat=self.r["seat"]).game_started() is not None

    def bridge_idle(self, purpose):
        r = self.rimflow("bridge", "idle", "--for", purpose)
        return None if r.returncode == 0 else ((r.stdout or "") + (r.stderr or "")).strip()[-300:]

    def bridge_take(self, purpose):
        r = self.rimflow("bridge", "take", "--idle-ok", "--for", purpose)
        return None if r.returncode == 0 else ((r.stderr or "") + (r.stdout or "")).strip()[-300:]

    def bridge_release(self):
        r = self.rimflow("bridge", "release", "--mine")
        return None if r.returncode == 0 else ((r.stderr or "") + (r.stdout or "")).strip()[-300:]

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


# ---------------------------------------------------------------- the step

def _save(store, item, fn):
    with store.lock():
        st = store.load(item)
        if st["status"] != GAME:
            return None
        fn(st)
        store.save(st)
        return st


def _back(store, fx, sup, r, item, klass, why, now, acts):
    """The game phase ends with work to do offline: release what we hold, and the item goes back to a worker."""
    with store.lock():
        st = store.load(item)
        if st["status"] != GAME:
            return
        sup.fail(store, st, klass, why, r, now)
    acts.append({"do": klass, "item": item, "why": why[:200]})
    fx.ledger_note(item, "relentless game phase: %s: %s" % (klass, why))


def _hold(store, fx, item, why, now, acts):
    def f(st):
        st["status"] = "held"
        st["hold"] = {"why": why, "kind": "game", "delivered": False, "at": now}
    _save(store, item, f)
    acts.append({"do": "game_held", "item": item, "why": why[:200]})


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
        if led["state"] in ("built", "validated") and same_sha(led["built_sha"], sha):
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
        _save(store, item, lambda s: s["game"].update(phase="prove"))
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
            return _back(store, fx, sup, r, item, "game_fail", "; ".join(
                "%s FAIL on the running game (%s)" % (k, v.get("log") or v.get("why")) for k, v in fails), now, acts)
        if len(rows) == len(g["clauses"]) and all(v.get("outcome") == "PASS" for v in rows.values()):
            return      # the last verify moves the ledger to done; the next tick finishes it
        lane = [v for v in rows.values() if v.get("outcome") == "SKIPPED"]
        if lane:
            return _hold(store, fx, item, "game phase: %s" % lane[0].get("why"), now, acts)
        refused = [v for v in rows.values() if v.get("outcome") == "REFUSED"]
        if refused:
            return _back(store, fx, sup, r, item, "game_refused", refused[0].get("why") or "refused", now, acts)
        since = max(g.get("staged_at") or 0, g["entered_at"])
        stale = [v for v in rows.values() if v.get("outcome") == "UNMEASURED" and row_at(v) >= since
                 and any((v.get("why") or "").startswith(w) for w in RESTAGE)]
        if stale or not fx.game_running():
            if g["stages"] >= c["stage_tries"]:
                return _hold(store, fx, item, "game phase: %d staging(s) and the build still is not running: %s"
                             % (g["stages"], (stale[0].get("why") if stale else "no running game")), now, acts)
            _save(store, item, lambda s: s["game"].update(phase="stage"))
            g = store.load(item)["game"]
        else:
            if (g.get("proved_at") or 0) >= since and now - g["proved_at"] < c["prove_every_s"]:
                return      # a round ran since the last staging and measured nothing: the bridge was busy, try later
            why = _lease_why(store, fx, r, item, sha, led)
            if why:
                acts.append({"do": "game_waits", "item": item, "why": why})
                return
            pid = fx.prove_launch(item)
            _save(store, item, lambda s: s["game"].update(phase="proving", prove_pid=pid, proved_at=now))
            acts.append({"do": "game_prove", "item": item, "pid": pid})
            return

    if g["phase"] == "stage":
        why = _lease_why(store, fx, r, item, sha, led)
        if why:
            acts.append({"do": "game_waits", "item": item, "why": why})
            return
        took = fx.bridge_take("relentless staging %s: deploy and restart for its live proofs" % item)
        if took:
            acts.append({"do": "game_waits", "item": item, "why": "bridge: %s" % took})
            return
        unit = sup.unit_name("stage", item, st["gen"]) + "-s%d" % (g["stages"] + 1)
        desc = sup.run_desc(store, r, unit, now)

        def f(s):
            s["run"] = desc
            s["game"].update(phase="staging", staged_at=now, taken_at=now, stages=s["game"]["stages"] + 1,
                             ready=None, snag=None)
        st = _save(store, item, f)
        if st is None:
            fx.bridge_release()
            return
        st["_proofs_text"] = fx.proofs_at(item, sha)
        why = fx.launch(st, desc, stage_prompt(st, r, sha), r["pilot_agent"], st["clone"] or fx.books, c["stage_max_s"],
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
        st = _save(store, item, lambda s: s["game"].update(phase="prove", released=gave is None))
        acts.append({"do": "game_staged", "item": item, "released": gave is None})
        if st and st["game"].get("snag"):
            sn = st["game"]["snag"]
            return _back(store, fx, sup, r, item, sn.get("class") or "game_stage", sn.get("detail") or "", now, acts)
        return


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
