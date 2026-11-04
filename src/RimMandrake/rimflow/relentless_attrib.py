#!/usr/bin/env python3
"""relentless_attrib.py — blame before rebuild (REWORK_GATE_BUILD_BLAME_BEFORE_REBUILD).

Spec: design/RimMandrake/test_tolerance_gpt_advice_2026-11-04.md, "Give attribution an explicit decision owner" and its
closing rule: an unresolved validation preserves the candidate, creates the right diagnostic or repair work, prevents
automatic rebuilding, and cannot close until the original obligations have adequate evidence. Owner ruling (standing
rulings, last section): broken tests are expected; an inability to measure is reported up, never read as broken work;
a false close is still worse than a wait.

Before this, every failed validation was a strike and a new builder: 5 of 30 game_fail items changed code for
generations against a broken site or harness (live churn triage 2026-11-04), and STEVE_DISK_MEASURE_ONLY_FORTY_GIGS_LEFT
went through five builders because the checker's box could not ssh. The supervisor now enforces, not a prompt:

  - a VALIDATION ending (GATED) with no PRODUCT attribution earns no strike, no gen bump, no approach change and no
    builder. The candidate sha is kept; the item waits (`blocked`, st["wait"] kind attribution) and a short READ-ONLY
    diagnostic lease (the help/consult machinery, mode "diagnose") attributes it with evidence:
        PRODUCT     the work violates an obligation it was observed against -> the existing strike path, a builder
        PROOF       the proof cannot show the obligation          -> proof-only repair on the same sha, never code
        CONTRACT    the set contract or binding is wrong           -> the same proof-only repair road
        HARNESS / SITE / CHECKER   the instrument is broken        -> one incident per shared fault (relentless_incident),
                    the item waits on the repair item with its candidate, released only by evidence
        DEPENDENCY  an unmet predecessor                            -> waits on it, no staffing until it lands
  - two endings attribute themselves (mechanical): a refused or bad live-proof line (game_contract, game_refused) is
    CONTRACT. A Marker's structured defects are NOT PRODUCT by themselves (a defect line carries no target and no
    measurement validity: "SSH denied" is a defect line too); they go to the diagnostician like any other FAIL.
  - a candidate that left origin/main (live_broken) is no product evidence either: held for the seat to re-land.
  - a known unmet predecessor (DEPENDENCY) wins over PRODUCT: the item waits, no builder is staffed against a world
    the predecessor has not built; the PRODUCT finding stays on the record and the same candidate is re-validated.
  - a diagnosis that cannot be had (no answer, no consult machinery) holds the item for the seat; it never falls back
    to a builder.
  - release (relentless_block.sweep -> release) is an evidence event: the repair's ledger block ends AND the incident's
    fixtures pass. The item resumes with the SAME candidate (a check, or its game phase with the old live rows voided),
    so nothing closes on the evidence that could not be read, and nothing is rebuilt that was never shown broken.
Worker endings (snags, worker_lost, late, circling) and the proof road (PROOF_ENDS) are unchanged.
"""
import re
import time

TARGETS = ("PRODUCT", "PROOF", "HARNESS", "SITE", "CONTRACT", "CHECKER", "DEPENDENCY")
INSTRUMENTS = ("HARNESS", "SITE", "CHECKER")
PROOF_ROAD = ("PROOF", "CONTRACT")
# validation endings: the supervisor read a check or a game, no worker said what broke
GATED = ("game_fail", "game_unmeasured", "game_proof_unmeasured", "game_contract", "game_refused", "checker_lost",
         "blind_fail", "live_broken", "close_refused")
MECH_CONTRACT = ("game_contract", "game_refused")
PROOF_OWED = "proof_owed"      # the proof road an attribution of PROOF or CONTRACT takes (relentless.PROOF_ENDS)
WAIT_ATTRIB, WAIT_INSTRUMENT, WAIT_DEPENDENCY = "attribution", "instrument", "dependency"
DIAGNOSE = "diagnose"
INSTRUMENT_SNAG = "instrument"     # relentless.INSTRUMENT: a worker's own classification
ID_RX = re.compile(r"^[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+$")


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def mechanical(klass, st):
    """-> the target an ending attributes by itself, or None when it needs a diagnosis. Never PRODUCT: a strike is
    earned only by a diagnosis that names the obligation, the observation and why the instrument was sound."""
    if klass in MECH_CONTRACT:
        return "CONTRACT"
    return None


def record(targets, evidence, now, by, sha, **kw):
    rec = {"targets": list(targets), "evidence": (evidence or "")[:2000], "at": now, "by": by, "sha": sha}
    rec.update({k: v for k, v in kw.items() if v})
    return rec


def gate(store, st, klass, detail, r, now, sup):
    """From fail(), under the lock, before any count moves. -> an attribution record for fail() to go on with (PRODUCT),
    or "routed"/"gated" when fail() must stop here."""
    sha = (st.get("candidate") or {}).get("sha")
    if not sha:
        return None         # no candidate: a worker's ending, the old road
    if klass == "live_broken" and "left origin/main" in (detail or ""):
        # the candidate is gone from main: no observed violation, nothing a builder should be struck for; the seat
        # re-lands it (or files the work again), the record keeps the sha
        withhold(store, st, klass, detail, r, now, sup, diagnose=False)
        return "gated"
    m = mechanical(klass, st)
    if m in PROOF_ROAD:
        rec = record([m], detail, now, "mechanical", sha)
        st["attribution"] = rec
        sup.fail(store, st, PROOF_OWED, "%s (%s, attributed %s: repair the proof or its binding, not the code)"
                 % ((detail or "")[:1600], klass, m), r, now, attributed=rec)
        return "routed"
    withhold(store, st, klass, detail, r, now, sup)
    return "gated"


def withhold(store, st, klass, detail, r, now, sup, diagnose=True):
    """Under the lock. The run (a checker, a live round, a staging) still settles through `stopping`, which lands here on
    `blocked` with the wait: no gen, no strike, no return, no approach; the candidate stays exactly as it was."""
    resume = "game" if st["status"] == sup.relentless_game.GAME else "candidate"
    st["status"] = "stopping"
    st["stopping_since"] = now
    st["wait"] = {"kind": WAIT_ATTRIB, "class": klass, "detail": (detail or "")[:2000], "since": now,
                  "sha": st["candidate"]["sha"], "resume": resume}
    st["last_fail"] = {"class": klass, "detail": (detail or "")[:2000], "at": now}
    store.attempt(st["item"], {"at": iso(now), "gen": st["gen"], "end": klass, "detail": (detail or "")[:600],
                               "gated": WAIT_ATTRIB, "sha": st["candidate"]["sha"]})
    store.learn(st["item"], "- %s gen %d %s withheld: no strike until it is attributed: %s"
                % (iso(now), st["gen"], klass, (detail or "")[:600]))
    if not diagnose:
        no_diagnosis(st, "the candidate left origin/main: re-land it, then unhold to re-check the same sha", now, sup)
    elif not r.get("circling"):
        no_diagnosis(st, "no consult machinery (rules.circling unset) to attribute it", now, sup)
    elif sup.help_pending(st):
        st["wait"]["help_after"] = True       # a circling consult is out: the diagnosis follows it (help_over)
    else:
        want(store, st, now)


def want(store, st, now):
    """A diagnostic consult. Not a circling consult: no round, no cool-down, no failed approach needed."""
    st["help"] = {"status": "wanted", "why": "attribute %s: %s" % (st["wait"]["class"], st["wait"]["detail"][:400]),
                  "by": "attribution", "at": now, "tries": 0, "gen": st["gen"], "round": st.get("help_round") or 0,
                  "mode": DIAGNOSE}
    store.journal({"at": iso(now), "do": "help_wanted", "item": st["item"], "by": "attribution"})


def no_diagnosis(st, why, now, sup):
    """Under the lock. Nobody could attribute it: the seat decides; a builder never inherits an unattributed failure."""
    sup.relentless_strikes.hold(st, "validation ending %s on %s is unattributed (%s): attribute it with `relentless.py "
                                "attribute --item %s --target ...` or unhold to re-check the same sha"
                                % (st["wait"]["class"], st["wait"]["sha"][:12], why, st["item"]), WAIT_ATTRIB, now)
    if st["status"] == "blocked":
        st["status"] = "held"


def is_diagnose(st):
    return ((st or {}).get("help") or {}).get("mode") == DIAGNOSE


def help_over(store, st, word, now, sup):
    """From help_over, under the lock, after the consult ended with `word`."""
    w = st.get("wait") or {}
    if w.get("kind") != WAIT_ATTRIB or st["status"] in ("held",) + sup.ENDED:
        return
    if not is_diagnose(st):
        if w.pop("help_after", None):
            want(store, st, now)
        return
    # the wait is still an attribution's, so no `attribute` routed it: answered or not, nobody attributed it
    no_diagnosis(st, "the diagnostic consult %s: %s" % (word, (st["help"].get("end") or "no attribution")[:200]), now, sup)


def prompt(st, text, attempts, nonce, r):
    rc = "python3 src/RimMandrake/rimflow/relentless.py"
    w, i = st["wait"], st["item"]
    rows = ["  %s gen %s ended %s%s: %s" % (a.get("at"), a.get("gen"), a.get("end"), " (withheld)" if a.get("gated") else "",
                                            (a.get("detail") or "")[:300]) for a in attempts[-12:] if a.get("end")]
    return "\n".join([
        "You are the DIAGNOSTICIAN for one failed validation. You attribute it; you fix nothing. Your cwd is a clean tree "
        "at origin/main. Read anything: the logs named below, the proof, the code at %s, the checker's words, "
        "infrastructure/state/facts/instrument_traps.md, the open repair items (`rimflow show`). No code edits, no push. "
        "The one ledger write you may make is filing a repair item (`rimflow namecheck`, then `rimflow file <NAME> --for "
        "BENCH`), or reusing the open one that already names this fault." % w["sha"],
        "Broken tests are expected; an inability to measure is not broken work, and a false close is worse than a wait. "
        "Attribute to PRODUCT only when the work itself was observed violating an obligation it was checked against.",
        "Then run exactly one of these and stop:",
        "  %s attribute --item %s --nonce %s --target PRODUCT --obligation \"the clause\" --observed \"what the mod did, "
        "from the log\" --why-product \"why the instrument is sound here\" --evidence \"the log line\"" % (rc, i, nonce),
        "  %s attribute --item %s --nonce %s --target PROOF|CONTRACT --evidence \"why the proof or its binding cannot show "
        "the clause\"   (a proof-only repair on the same sha, never code)" % (rc, i, nonce),
        "  %s attribute --item %s --nonce %s --target HARNESS|SITE|CHECKER --repair <REPAIR_ITEM> --component \"the "
        "tool/site and its version\" --fixture-good \"a command on which the repaired instrument measures and prints "
        "FIXTURE_VERDICT: PASS, exit 0\" --fixture-bad \"one on which it measures and prints FIXTURE_VERDICT: FAIL, exit "
        "non-zero (a fixture that dies in setup prints no verdict and releases nothing)\" --evidence \"the line showing the instrument, not the work, broke\"" % (rc, i, nonce),
        "  %s attribute --item %s --nonce %s --target DEPENDENCY --on <PREDECESSOR> --evidence \"what it waits for\""
        % (rc, i, nonce),
        "Mixed? Repeat --target (PRODUCT with HARNESS goes to a builder and links the incident; PRODUCT with DEPENDENCY "
        "waits on the predecessor first; the evidence for each part goes in --evidence). File the repair item in the "
        "SUPERVISOR's ledger (`rimflow file` from this tree publishes nothing): an id it has never seen is refused.",
        "", "Ending: %s at %s" % (w["class"], w["sha"]), "Detail: %s" % w["detail"],
        "Contract: %s" % (st.get("contract") or {}), "", "--- endings on record ---"] + rows + ["", "--- item ---", text])


def brief_line(at):
    """The builder's or proof worker's brief: what the last ending was blamed on, and what that leaves to do."""
    ts = at.get("targets") or []
    if "PRODUCT" in ts:
        return ("ATTRIBUTED PRODUCT (%s): the work was observed violating an obligation; fix the product, not the proof. "
                "Obligation: %s. Observed: %s. Evidence: %s%s" % (at.get("by"), at.get("obligation") or "-",
                                                                   at.get("observed") or "-", at.get("evidence", "")[:600],
                "" if ts == ["PRODUCT"] else ". The %s part is tracked on %s; do not work round it"
                % ("/".join(t for t in ts if t != "PRODUCT"), at.get("repair") or at.get("on") or "its repair item")))
    return ("ATTRIBUTED %s (%s): the code at %s was not shown broken; repair the proof or its binding so it can show the "
            "obligation, and leave the code as it is. Evidence: %s" % ("+".join(ts), at.get("by"), (at.get("sha") or "")[:12],
                                                                       at.get("evidence", "")[:600]))


def validate(targets, a):
    """CLI args -> (targets, fields) or ValueError: what each target must carry."""
    ts = []
    for t in targets or []:
        t = (t or "").strip().upper()
        if t not in TARGETS:
            raise ValueError("--target must be one of %s (got %r)" % ("|".join(TARGETS), t))
        if t not in ts:
            ts.append(t)
    if not ts:
        raise ValueError("give at least one --target")
    if not (a.get("evidence") or "").strip():
        raise ValueError("--evidence is required: the line that decides it")
    if "PRODUCT" in ts and not all((a.get(k) or "").strip() for k in ("obligation", "observed", "why_product")):
        raise ValueError("PRODUCT needs --obligation, --observed and --why-product: an observed violation, not a guess")
    if any(t in INSTRUMENTS for t in ts):
        rep = (a.get("repair") or "").strip()
        if not ID_RX.match(rep):
            raise ValueError("%s needs --repair <REPAIR_ITEM> (a filed id)" % "/".join(t for t in ts if t in INSTRUMENTS))
        if "PRODUCT" not in ts and not ((a.get("fixture_good") or "").strip() and (a.get("fixture_bad") or "").strip()):
            raise ValueError("an instrument wait needs --fixture-good and --fixture-bad: the release check")
    if "DEPENDENCY" in ts and not ID_RX.match((a.get("on") or "").strip()):
        raise ValueError("DEPENDENCY needs --on <PREDECESSOR> (a filed id)")
    if "DEPENDENCY" in ts and any(t in INSTRUMENTS for t in ts):
        raise ValueError("one wait at a time: attribute the DEPENDENCY now; the instrument is diagnosed again when the "
                         "re-validation after it runs")
    return ts


def answer(store, item, nonce, targets, a, r, now, sup, known=None):
    """`relentless.py attribute`: the diagnostician's (nonce) or an operator's (nonce None, on an item that waits or is
    held for attribution) return. Recorded and routed under one lock. -> the route taken."""
    ts = validate(targets, a)
    if known is not None:       # a wait on an id the ledger lacks would fail its block write on every tick
        for k in ("repair", "on"):
            v = (a.get(k) or "").strip()
            if v and not known(v):
                raise ValueError("--%s %s has never been filed: file the repair item first" % (k, v))
    with store.lock():
        st = store.load(item)
        if st is None:
            raise ValueError("%s is not enrolled" % item)
        w = st.get("wait") or {}
        held = st["status"] == "held" and (st.get("hold") or {}).get("kind") == WAIT_ATTRIB
        if nonce is not None:
            h = st.get("help") or {}
            if (h.get("status") != "running" or h.get("nonce") != nonce or h.get("expired") or h.get("answered_at")
                    or not is_diagnose(st)):
                raise sup.Fenced("%s: no diagnosis is waiting for that nonce" % item)
            h["answered_at"] = now
            by = "diagnose unit %s" % ((h.get("run") or {}).get("unit") or "?")
        else:
            by = "operator"
        if w.get("kind") != WAIT_ATTRIB or not (st["status"] in ("blocked", "stopping") or held):
            raise ValueError("%s is not waiting for an attribution (%s)" % (item, st["status"]))
        if held:
            st["hold"] = None
            st["status"] = "blocked"
        rec = record(ts, a.get("evidence"), now, by, w["sha"], obligation=a.get("obligation"), observed=a.get("observed"),
                     why_product=a.get("why_product"), repair=a.get("repair"), on=a.get("on"),
                     component=a.get("component"), ending=w["class"])
        st["attribution"] = rec
        store.attempt(item, {"at": iso(now), "gen": st["gen"], "attributed": ts, "by": by, "ending": w["class"],
                             "sha": w["sha"], "evidence": rec["evidence"][:600]})
        route = _route(store, st, ts, a, rec, r, now, sup)
        store.journal({"at": iso(now), "do": "attributed", "item": item, "targets": ts, "route": route})
        store.save(st)
    return route


def _route(store, st, ts, a, rec, r, now, sup):
    import relentless_incident
    w = st["wait"]
    item = st["item"]
    if "DEPENDENCY" in ts:      # a known unmet predecessor: never staffed, PRODUCT or not (the record keeps PRODUCT)
        return _wait(st, ts, rec, WAIT_DEPENDENCY, a["on"].strip(), now)
    if any(t in INSTRUMENTS for t in ts):
        relentless_incident.link(store, a["repair"].strip(), item, w["sha"], now, a.get("component"), rec["evidence"],
                                 {"good": a.get("fixture_good"), "bad": a.get("fixture_bad")},
                                 [t for t in ts if t in INSTRUMENTS], waits="PRODUCT" not in ts)
    if "PRODUCT" in ts:     # an observed violation: the builder, with the strike it earned
        st.pop("wait", None)
        detail = "%s | attributed PRODUCT: %s observed %s (%s)" % (w["detail"][:1200], rec.get("obligation"),
                                                                    rec.get("observed"), rec["evidence"][:400])
        sup.fail(store, st, w["class"], detail, r, now, attributed=rec)
        if w.get("live"):
            st["live_iter"] = w["live"]
        return "builder"
    if any(t in INSTRUMENTS for t in ts):
        return _wait(st, ts, rec, WAIT_INSTRUMENT, a["repair"].strip(), now)
    st.pop("wait", None)        # PROOF / CONTRACT: the proof road on the same candidate, never the code
    sup.fail(store, st, PROOF_OWED, "%s | attributed %s: %s" % (w["detail"][:1200], "+".join(ts), rec["evidence"][:600]),
             r, now, attributed=rec)
    return "proof"


def _wait(st, ts, rec, kind, on, now):
    w = st["wait"]
    w.update(kind=kind, on=on, incident=on if kind == WAIT_INSTRUMENT else None, attributed_at=now)
    st["block_pending"] = {"kind": "item", "on": [on], "class": kind,
                           "detail": "attributed %s at %s: %s" % ("+".join(ts), w["sha"][:12], rec["evidence"][:400])}
    return "wait:" + on


def snag_incident(store, st, ons, detail, now):
    """Under the lock: a worker's `snag --class instrument --on <repair>`. The worker's own work is unfinished, so the
    item resumes as a fresh lease of the queue when the repair closes; the incident records it beside the items the
    diagnostician sent there, so one fault has one record."""
    import relentless_incident
    rep = (ons or [None])[0]
    if not rep:
        return
    relentless_incident.link(store, rep, st["item"], None, now, None, detail, None, ["worker_snag"])
    st["wait"] = {"kind": WAIT_INSTRUMENT, "class": INSTRUMENT_SNAG, "detail": (detail or "")[:2000], "since": now,
                  "sha": None, "resume": "queued", "on": rep, "incident": rep}


def _same(cw, w):
    """The exact wait this sweep read, not a later one on the same item (a fence across the unlocked fixture run)."""
    return all(cw.get(k) == w.get(k) for k in ("kind", "on", "sha", "since", "attributed_at"))


def _refuse(store, fx, item, w, event, now, why, note, acts):
    if w.get("refused_event") != event:
        with store.lock():
            cur = store.load(item)
            fresh = cur is not None and _same(cur.get("wait") or {}, w)
            if fresh:
                cur["wait"]["refused_event"] = event
                store.save(cur)
        if fresh:
            store.journal({"at": iso(now), "do": "alarm", "item": item, "why": why[:400]})
            fx.ledger_note(item, note)
    acts.append({"do": "incident_refused" if w.get("incident") else "dependency_refused", "item": item, "on": w["on"],
                 "why": why[:200]})
    return False


def release(store, fx, st, now, acts):
    """From relentless_block.sweep (not under the lock), a `blocked` item with a wait whose ledger block no longer
    holds. -> True when the item moved. Evidence only: the repair or predecessor CLOSED (state done; dropped,
    superseded or a bare unblock is no evidence), then for an incident its fixtures; no clock releases anything."""
    import relentless_incident
    item, w = st["item"], st.get("wait") or {}
    if w.get("kind") not in (WAIT_INSTRUMENT, WAIT_DEPENDENCY):
        return False        # attribution: the diagnostician or the seat moves it
    led_on = fx.item_state(w["on"]) or {}
    # the evidence event is this close: its last ledger event, so a reopen and a new close (even on the same sha) is a
    # new event, and a tick is not
    event = "%s:%s:%s:%s" % (w["on"], led_on.get("state") or "?", led_on.get("closed_sha") or "-",
                             led_on.get("event") if led_on.get("event") is not None else "-")
    if led_on.get("state") != "done":
        return _refuse(store, fx, item, w, event, now,
                       "%s %s is %s, not closed: %s keeps waiting" % ("repair" if w.get("incident") else "predecessor",
                                                                    w["on"], led_on.get("state"), item),
                       "relentless: %s waits on %s, which is %s without closing; the candidate keeps waiting: "
                       "re-attribute it or file a new item" % (item, w["on"], led_on.get("state")), acts)
    if w.get("incident"):
        ok, why = relentless_incident.check(store, w["incident"], fx.run_fixture, now, event,
                                            need_fixtures=bool(w.get("sha")))
        if not ok:
            return _refuse(store, fx, item, w, event, now, "incident %s: %s" % (w["incident"], why),
                           "relentless: the repair %s ended but its fixtures refuse it, so %s keeps waiting with its "
                           "candidate: %s" % (w["incident"], item, why), acts)
    else:
        why = "%s done" % w["on"]
    # the fixtures took time: the close they judged must still be the close that stands (a reopen meanwhile, even one
    # that leaves this wait untouched, voids them)
    now_on = fx.item_state(w["on"], fresh=True) or {}
    if (now_on.get("state"), now_on.get("closed_sha"), now_on.get("event")) != \
            (led_on.get("state"), led_on.get("closed_sha"), led_on.get("event")):
        return False
    with store.lock():
        cur = store.load(item)
        if cur is None or cur["status"] != "blocked" or not _same(cur.get("wait") or {}, w) or cur.get("block_pending"):
            return False
        sha = cur["wait"]["sha"]
        resume(store, cur, now, "released: %s" % why)
        store.save(cur)
        if w.get("incident"):
            relentless_incident.released(store, w["incident"], item, now)
    store.journal({"at": iso(now), "do": "released", "item": item, "on": w["on"], "sha": sha, "to": cur["status"]})
    acts.append({"do": "released", "item": item, "on": w["on"], "to": cur["status"]})
    return True


def resume(store, st, now, why):
    """Under the lock. The same candidate is validated again from where it waited; the game's old rows on this sha are
    voided first, or the round would read their FAIL again (relentless_live_round.history)."""
    w = st.pop("wait")
    sha = w["sha"]
    if w["resume"] == "queued" or not sha:      # a worker's snag: its unfinished work goes back to the line
        store.attempt(st["item"], {"at": iso(now), "gen": st["gen"], "end": "released", "detail": why[:600], "to": "queued"})
        st["status"] = "queued"
        st["returned_at"] = now
        st["not_before"] = 0
        return
    store.attempt(st["item"], {"at": iso(now), "gen": st["gen"], "end": "released", "detail": why[:600], "sha": sha,
                               "to": w["resume"]})
    if w["resume"] == "game" and (st.get("contract") or {}).get("game") and (st.get("candidate") or {}).get("sha") == sha:
        import relentless_game
        relentless_game.void_rows(store.root, st["item"], sha, why, now)
        relentless_game.enter(store, st, sha, now)
        return
    st["status"] = "candidate"
    st["check"] = None
    st.pop("recheck_at", None)
    st.pop("blind", None)
