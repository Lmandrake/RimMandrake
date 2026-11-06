#!/usr/bin/env python3
"""relentless_breakers.py — loop breakers that redirect work instead of demanding novelty
(CHURN_BREAKER_BUILD_RETRY_NEEDS_A_WARRANT; spec design/RimMandrake/test_tolerance_gpt_advice_2026-11-04.md rank 3,
"Make loop breakers redirect work" and "Give each role the history").

Owner 2026-11-03: broken tests are expected; inability to measure is reported up (standing_rulings.md).

The moves, all here so relentless.py carries hooks only:
  - RETRY WARRANT. Every worker sent after a failed attempt owes one `learn "WARRANT: <what changed, or the transient
    hypothesis that makes this attempt informative> | <the result that would change the decision>"` before `finish`.
    The warrant is kept whole on the attempt record, so the next role reads why the retry was worth it. A rebuild that
    changes nothing in the work (only the environment moved) says so in the one structured form, `WARRANT: UNCHANGED:
    <what in the environment changed> | ...`: the record carries `unchanged: True`, and only that lets Relentless pass
    `implemented --no-code` for a ledger-only candidate (relentless_game.no_code_rebuild). Prose never does.
  - SAME SIGNATURE, NEW CODE. A failure signature (class plus normalised detail; a live FAIL's failing clauses) that
    recurs on `signature_builds_hold` (3) different builds, i.e. after two product changes, HOLDS the item (kind
    `signature`): automatic rebuilding is suspended and the hold says to compare product, proof and binding. An unhold
    starts the count over from that point.
  - ONE INCIDENT PER CAPABILITY. A capability failure (the instrument, the box, the bridge, the checker could not
    measure; `capability_classes` and CAPABILITY_RX) with the same signature on `incident_items` (3) different items
    inside `incident_window_s` opens ONE incident in incidents.json (linked to relentless_incident's instrument_incidents.json
    when they share an item: one fault, one row in `relentless.py incidents`). Its first item is the probe; every other affected
    item, and any later item failing on it, waits out of the line (lease skips it). It is told once (tell). It is released
    by evidence, never a tick: the probe's next ending is a candidate or a different signature (a lost process or a wait
    says nothing either way), or an operator runs
    `relentless.py incident-release --key K --evidence "..."`.
  - KNOWN UNMET PREDECESSOR is relentless_block's: a structured ledger block, no worker until its event. Not repeated.
  - HISTORY. A classification and a warrant reach each role whole: ending_history and the help prompts
    print them untruncated (attributions_view); the blind checker still sees none of it.
"""
import json
import re

SHA_RX = re.compile(r"\b[0-9a-f]{7,64}\b")
NUM_RX = re.compile(r"\d+(?:[.:]\d+)*")
WS_RX = re.compile(r"\s+")
LIVE_FAIL_RX = re.compile(r"(?:^|;\s*)(\S+) FAIL on the running game")
WARRANT_RX = re.compile(r"^\s*WARRANT:\s*(\S.{4,}?)\s*\|\s*(\S.{4,})$", re.S)
UNCHANGED_RX = re.compile(r"^UNCHANGED:\s*(\S.*)$", re.S)     # the changed half of a no-change rebuild's warrant
CAPABILITY_RX = re.compile(r"unmeasured|unreach|sandbox|harness|bridge|interop|capabilit|checker_lost|tool_missing|ssh")
CAPABILITY_CLASSES = ("game_unmeasured", "game_proof_unmeasured", "checker_lost", "unmeasured")
SILENT_ENDS = ("worker_lost", "worker_stale", "checker_lost")    # the supervisor saw a process vanish: no evidence either way
NO_WARRANT_ENDS = ("circling",)      # the consult's options are the warrant: the next brief carries them
SIG_LEN = 160
INCIDENTS = "incidents.json"


# ---------------------------------------------------------------- signatures

def signature(klass, detail):
    """-> a stable key for one kind of failure: the class plus its detail with ids, numbers and spacing washed out. A
    live FAIL is keyed by its failing clauses alone (the rest of its line names the run)."""
    klass = (klass or "snag").lower()
    clauses = sorted(set(LIVE_FAIL_RX.findall(detail or "")))
    if klass == "game_fail" and clauses:
        return "%s|%s" % (klass, ",".join(clauses))
    first = ((detail or "").strip().splitlines() or [""])[0].lower()
    norm = WS_RX.sub(" ", NUM_RX.sub("#", SHA_RX.sub("<sha>", first))).strip()[:SIG_LEN]
    return "%s|%s" % (klass, norm)


def builds_by_signature(attempts, since=0):
    """-> {signature: [the builds it ended on, oldest first]}. A build is the finish sha the ending stood on; None is
    the code the item started from. Waits, blocks, proof-only ends and records that are not endings do not count."""
    seen, sha = {}, None
    for a in (attempts or [])[since:]:
        end = a.get("end")
        if end == "finish":
            sha = a.get("sha")
            continue
        if (not end or end in ("owner_call", "blocked", "unmeasured") + SILENT_ENDS or a.get("wait")
                or end.startswith("proof_")):
            continue
        builds = seen.setdefault(signature(end, a.get("detail")), [])
        if sha not in builds:
            builds.append(sha)
    return seen


def same_signature_hold(attempts, klass, detail, r, since=0):
    """-> the hold reason when this ending's signature has now ended `signature_builds_hold` different builds, else
    None. Called after the ending's attempt record is written."""
    limit = r.get("signature_builds_hold", 3)
    if not limit:
        return None
    sig = signature(klass, detail)
    builds = builds_by_signature(attempts, since).get(sig, [])
    if len(builds) < limit:
        return None
    return ("same failure signature on %d builds (%s): %s. Automatic rebuilding is suspended: compare the product, the "
            "proof and the binding (what each build changed, what the proof measures, what the clause is bound to) "
            "before another build; unhold with the hypothesis that rules two of them out"
            % (len(builds), ", ".join((b or "start")[:10] for b in builds), sig))


# ---------------------------------------------------------------- the retry warrant

def owe_warrant(st, klass, time_not_work=False):
    """In fail(): the next worker of a failed attempt owes a warrant. A wait on time is not a failed approach."""
    if time_not_work or klass in NO_WARRANT_ENDS:
        return
    st["warrant_owed"] = {"after": klass, "gen": st["gen"]}


def take_warrant(st, text, gen, at):
    """In learn(): -> the warrant record when `text` is one and one is owed, else None."""
    m = WARRANT_RX.match(text or "")
    if not m or not st.get("warrant_owed"):
        return None
    w = {"changed": m.group(1).strip(), "decides": m.group(2).strip(), "gen": gen, "at": at,
         "after": st.pop("warrant_owed")["after"]}
    if UNCHANGED_RX.match(w["changed"]):
        w["unchanged"] = True       # the explicit claim no_code_rebuild reads; no wording of prose stands for it
    st["warrant"] = w
    return w


def warrant_refusal(st):
    """In finish(): -> the refusal text while a warrant is owed, else None."""
    w = st.get("warrant_owed")
    if not w:
        return None
    return ("this attempt is a retry after %s and owes its warrant: `learn \"WARRANT: <what changed since the last "
            "attempt, or the transient hypothesis that makes this one informative> | <the result that would change the "
            "decision>\"` before finishing" % w["after"])


BRIEF = ("RETRY WARRANT: this is a retry after a failed attempt. Before you edit, record `learn \"WARRANT: <what "
         "changed since the last attempt (code, proof, binding, environment) or the transient hypothesis that makes "
         "another attempt informative> | <the result that would change the decision>\"`; `finish` is refused until "
         "you do. A rebuild that changes nothing in the work (only the environment moved) writes \"WARRANT: UNCHANGED: "
         "<what in the environment changed> | ...\" and commits only the ledger or item note. If nothing relevant changed and no result would change the decision, do not retry: `snag` with "
         "that, or `help`.")


# ---------------------------------------------------------------- cross-item capability incidents

def is_capability(klass, r):
    klass = (klass or "").lower()
    return klass in r.get("capability_classes", CAPABILITY_CLASSES) or bool(CAPABILITY_RX.search(klass))


def load(store):
    try:
        with open(store.p(INCIDENTS), encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def save(store, d):
    store._write(store.p(INCIDENTS), json.dumps(d, indent=1, sort_keys=True))


def note(store, item, klass, detail, r, now):
    """Under the lock, in fail(). Records a capability ending; releases an incident whose probe ended otherwise; opens
    one when `incident_items` items share a signature in the window. -> the incident key it opened, else None."""
    d = load(store)
    changed = False
    sig = signature(klass, detail) if is_capability(klass, r) else None
    window = r.get("incident_window_s", 86400)
    for key, inc in list(d.items()):
        if inc.get("open") and inc.get("probe") == item and key != sig and klass not in SILENT_ENDS:
            release(store, d, key, "the probe %s ended %s instead" % (item, klass), now)
            changed = True
        elif not inc.get("open") and now - inc.get("last", 0) >= window:      # a cause silent for the window is forgotten
            del d[key]
            changed = True
    opened = None
    if sig:
        inc = d.setdefault(sig, {"items": {}, "open": False})
        inc["items"] = {i: t for i, t in inc["items"].items() if now - t < window or inc["open"]}
        inc["items"][item] = now
        inc["last"] = now
        changed = True
        if not inc["open"] and len(inc["items"]) >= r.get("incident_items", 3):
            first = min(inc["items"], key=lambda i: (inc["items"][i], i))
            inc.update({"open": True, "opened": now, "probe": first, "told": False, "why": (detail or "")[:600],
                        "class": klass})
            store.journal({"at": _iso(now), "do": "incident_open", "key": sig, "items": sorted(inc["items"]),
                           "probe": first})
            opened = sig
        if inc["open"]:     # opened now, or a later item joined it: either may share an item with a diagnosed fault
            _link_instrument(store, sig, inc, now)
    if changed:
        save(store, d)
    return opened


def _link_instrument(store, sig, inc, now):
    """Under the lock: an instrument incident (relentless_incident, a diagnosed fault with a repair item) already holding
    one of these items is the same fault. Link both ways: one fault, one book (INCIDENT_STORES_UNIFY_TWO_BOOKS_ONE_FAULT)."""
    import relentless_incident as RI
    incs = RI.load(store)
    hit = sorted(k for k, v in incs.items() if v.get("status") != RI.RELEASED
                 and set(inc["items"]) & {i for i, w in (v.get("items") or {}).items() if not w.get("released_at")})
    if not hit:
        return None
    fresh = [k for k in hit if sig not in (incs[k].get("capability") or [])]
    for k in fresh:
        incs[k]["capability"] = sorted(set(incs[k].get("capability") or []) | {sig})
    if fresh:
        RI.save(store, incs)
    if not inc.get("repair"):       # the first diagnosis that explains it stands
        inc["repair"] = hit[0]
        store.journal({"at": _iso(now), "do": "incident_linked", "key": sig, "repair": hit[0]})
    return inc["repair"]


def probe_passed(store, item, now):
    """In _take_receipt(), under the lock: the probe reached a candidate, so the capability works again."""
    d = load(store)
    hit = [k for k, inc in d.items() if inc.get("open") and inc.get("probe") == item]
    for key in hit:
        release(store, d, key, "the probe %s reached a candidate" % item, now)
    if hit:
        save(store, d)


def release(store, d, key, evidence, now):
    inc = d.pop(key, None)
    if inc is not None:
        store.journal({"at": _iso(now), "do": "incident_released", "key": key, "evidence": evidence,
                       "items": sorted(inc.get("items") or {})})
    return inc


def release_by_hand(store, key, evidence, now):
    """`relentless.py incident-release`: an operator's repair, with its evidence. -> the incident, or ValueError."""
    if not (evidence or "").strip():
        raise ValueError("incident-release takes the evidence that the capability works again (--evidence)")
    with store.lock():
        d = load(store)
        if key not in d:
            raise ValueError("no incident %r; open ones: %s" % (key, ", ".join(k for k, v in d.items() if v.get("open")) or "none"))
        inc = release(store, d, key, evidence, now)
        save(store, d)
    return inc


def waits(store, item, d=None):
    """-> the open incident key `item` waits behind (it is affected and is not the probe), else None."""
    for key, inc in (load(store) if d is None else d).items():
        if inc.get("open") and item in (inc.get("items") or {}) and inc.get("probe") != item:
            return key
    return None


PROBE_GONE = ("held", "blocked", "done", "retired")


def tell(store, fx, now, acts):
    """Each tick: a probe that left the line (held, blocked, ended) hands the probe to the next affected item, or with
    none left the incident ends; an open incident not yet told reaches the Conductor once."""
    with store.lock():
        d = load(store)
        moved = False
        for key, inc in list(d.items()):
            if not inc.get("open"):
                continue
            gone = lambda i: (store.load(i) or {"status": "done"})["status"] in PROBE_GONE     # noqa: E731
            if not gone(inc.get("probe")):
                continue
            left = sorted((i for i in inc["items"] if not gone(i)), key=lambda i: (inc["items"][i], i))
            if left:
                store.journal({"at": _iso(now), "do": "incident_probe", "key": key, "from": inc.get("probe"), "to": left[0]})
                inc["probe"] = left[0]
            else:
                release(store, d, key, "no affected item is left in line to probe it", now)
            moved = True
        if moved:
            save(store, d)
    said = []
    for key, inc in load(store).items():
        if not inc.get("open") or inc.get("told"):
            continue
        text = ("INCIDENT: %d items failed on one capability (%s); they wait behind one probe (%s) and come back when it "
                "passes or `relentless.py incident-release --key '%s' --evidence ...`. Last: %s"
                % (len(inc["items"]), key, inc.get("probe"), key, (inc.get("why") or "")[:300]))
        if inc.get("repair"):
            text += (" | the same fault is diagnosed: repair item %s; its close with fixtures that hold releases this "
                     "too; one book: `relentless.py incidents`" % inc["repair"])
        fail = fx.conductor_alarm(text)
        if fail:
            acts.append({"do": "alarm_retry", "why": "incident: %s" % fail})
            continue
        said.append((key, inc.get("opened")))
        acts.append({"do": "incident_told", "key": key})
    if said:
        with store.lock():      # fail() may have written the file meanwhile: mark on a fresh read
            d = load(store)
            for key, born in said:
                if key in d and d[key].get("opened") == born:     # released and reopened meanwhile: a new incident, untold
                    d[key]["told"] = True
            save(store, d)


# ---------------------------------------------------------------- the history each role sees

def attributions_view(attempts):
    """-> whole lines for every classification and warrant on record, oldest first: what a diagnosis,
    a fresh pair of eyes or the next builder must not lose to a cut at 140 characters."""
    out = []
    for a in attempts or []:
        if a.get("classified"):
            out.append("gen %s classified it %s: %s" % (a.get("gen"), a["classified"], a.get("evidence") or ""))
        elif a.get("warrant"):
            w = a["warrant"]
            out.append("gen %s retry warrant: changed: %s | decides: %s" % (a.get("gen"), w.get("changed"), w.get("decides")))
    return out


def _iso(t):
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))
