#!/usr/bin/env python3
"""relentless_reachfix.py - a blind Judge fixes its own eyes (BLIND_JUDGE_BUILD_FIXES_OWN_EYES, owner 2026-11-05).

Owner: "The JUDGE is the one who can't measure something, so the JUDGE should fix it. His incentive is to be fair, so it's
not reward hacking." and "It should only file a ticket if it is unable to make the fix itself."

Before this, an UNMEASURED verdict set a 30-minute clock and the same sha was checked again; two blind checks held the item,
and every unhold bought two more Markers (JAM_CLASS_BUILD_OPS_DETECTOR_PER_CLASS: 11 checks, churn diagnosis
D:\\ClaudeWork\\rimmandrake\\conductor\\churn_diagnosis_2026-11-05.md). Now the first blind verdict ends the checking:

  on_blind()   under the lock, at the verdict. The gap is classed (relentless_rules.json reach_classes). The Judge's own
               `verdict UNMEASURED ... --propose NAME|PATH` is the repair (else the class's seed adapters / the paths its
               --unreached names). The first item blind on a class OWNS the repair; another item blind on a class whose
               repair is open WAITS on it (blocked, a ledger dependency on the owner). No clock, no re-check.
  sweep()      every tick, out of the lock. The owner's proposal is PROBED from inside the Judge's wall (Fx.reach_probe:
               each path read in a unit with the Marker's systemd properties, each adapter run and read non-empty).
               Pass: the supervisor applies it as its own overlay (contract.offbox += adapters, the paths bound read only
               at the next launch, contract.reach_ok stamped so the box fingerprint moves) and the UNCHANGED sha is checked
               once more; the waiters each probe their own proposal next. Fail, or blind again on the repaired sha: then,
               and only then, a ticket is filed (the class's `ticket`), and owner and waiters block on it; a closed ticket
               re-probes, and only a pass releases.

A repair may also carry box GRANTS (relentless_wall.GRANTS, a reach_classes row's `grants`, or a Judge's --propose by
name): git_history makes the Marker's next box with a read-only git history at the candidate, for proofs that run git
inside the box (CHECKER_REACH_BUILD_GIT_AND_GH_ADAPTERS gen 3: adapters alone left six Judges blind). A stored proposal
gains the grants its blind text earns when it re-probes (refreshed()).

A repair only ADDS read access: a path under reach_never, never_through or never_through_rx is refused before any probe,
an adapter must already be a supervisor offbox adapter (no Judge-written argv ever runs), and nothing here touches the
proof, the verdict logic or the product sha.
"""
from __future__ import annotations

import json
import os
import re
import time

import relentless_wall

BOOK = "reach_gaps.json"
WAIT = "reach"          # st["wait"]["kind"]: relentless_attrib.release leaves it alone; this module moves it
PROPOSE_MAX = 8


def on(r):
    return bool(r.get("reach_repair", True))


def classes(r):
    return [c for c in r.get("reach_classes") or [] if isinstance(c, dict) and c.get("class")]


def classify(r, texts):
    """-> the first reach_classes row whose `match` finds any of `texts`, else the catch-all `other` row."""
    blob = "\n".join(t for t in texts if t)
    for c in classes(r):
        if c.get("match") and re.search(c["match"], blob, re.I):
            return c
    return {"class": "other", "adapters": [], "paths": True,
            "ticket": r.get("reach_other_ticket", "CHECKER_REACH_FIX_OTHER_STILL_DARK")}


def grants_for(r, texts):
    """-> the box grants (relentless_wall.GRANTS) of EVERY reach_classes row whose match finds the texts: a grant changes
    how the box is made, so a /proc text that also says git gets the git history its in-box proof runs."""
    blob = "\n".join(t for t in texts if t)
    out = []
    for c in classes(r):
        if c.get("match") and re.search(c["match"], blob, re.I):
            out += [g for g in c.get("grants") or [] if g in relentless_wall.GRANTS and g not in out]
    return out


def _paths_of(texts):
    out = []
    for t in texts:
        for m in relentless_wall._THROUGH_WORD.finditer(t or ""):
            p = os.path.normpath(relentless_wall._host(m.group(0)))
            if p not in out and p != "/":
                out.append(p)
    return out


def refused(p, r, store_root=None):
    """-> why a read path may not be added, or None. Add-only stays add-only: the store, transcripts, memory, credentials
    and the worker run folders stay dark whatever a Judge proposes."""
    prof = relentless_wall.profile(r) or {}
    p = os.path.normpath(relentless_wall._host(p))
    if not relentless_wall._SAFE.match(p):
        return "not a plain absolute path"
    never = list(r.get("reach_never") or []) + list(prof.get("never_through") or []) + ([store_root] if store_root else [])
    for n in never:
        if p == n.rstrip("/") or p.startswith(n.rstrip("/") + "/") or n.startswith(p.rstrip("/") + "/"):
            return "under %s, which no reach repair opens" % n
    rx = prof.get("never_through_rx")
    if rx and re.search(rx, p):
        return "matches never_through_rx (a worker's progress, handoff or transcript)"
    return None


def propose(r, cls, proposals, unreached, what, store_root=None):
    """-> {adapters, paths, refused, by}. The Judge's --propose lines first; none, and the class's seed."""
    known = relentless_wall.adapters(r)
    said = [str(x).strip() for x in proposals or [] if str(x).strip()][:PROPOSE_MAX]
    ads = [x for x in said if x in known]
    grants = [x for x in said if x in relentless_wall.GRANTS and x not in known]
    paths = _paths_of([x for x in said if x not in known and x not in grants])
    by = "judge" if said else "seed"
    if not said:
        ads = [x for x in cls.get("adapters") or [] if x in known]
        paths = _paths_of(list(unreached or []) + [what or ""]) if cls.get("paths") else []
    elif not ads and not grants and all(refused(p, r, store_root) for p in paths):
        # CHECKER_REACH_FIX_WINDOWS_BUILD_STILL_DARK gen 3: the Judge named only what no repair opens (the live folder);
        # proposing nothing filed a ticket at once, so the class seed adapters stand in for the refused proposal
        ads = [x for x in cls.get("adapters") or [] if x in known]
        by = "judge+seed" if ads else by
    # the classes' grants ride along with what the Judge said: it names what it lacks, not how the box is made
    for g in list(cls.get("grants") or []) + grants_for(r, list(unreached or []) + [what or ""]):
        if g in relentless_wall.GRANTS and g not in grants:
            grants.append(g)
    bad = {}
    for p in list(paths):
        why = refused(p, r, store_root)
        if why:
            bad[p] = why
            paths.remove(p)
    bad.update({x: "not a supervisor offbox adapter" for x in said if x not in known and x not in grants
                and not _paths_of([x])})
    return {"adapters": ads[:relentless_wall.OFFBOX_MAX], "paths": paths[:relentless_wall.THROUGH_MAX], "refused": bad,
            "by": by, "grants": grants}


def grants(st):
    """The box grants a passed repair makes the Marker's next box with (relentless_wall.make_box)."""
    rp = st.get("reach") or {}
    if rp.get("status") != "applied":
        return []
    return [g for g in (rp.get("proposal") or {}).get("grants") or [] if g in relentless_wall.GRANTS]


def refreshed(r, st):
    """-> the item's stored proposal with the grants its blind text earns under today's rules: a proposal stored before a
    grant existed (the six items blind on git after gen 1's adapters) gains it when its ticket closes and it re-probes."""
    rp = st.get("reach") or {}
    prop = dict(rp.get("proposal") or {})
    texts = [rp.get("still_blind"), (st.get("blind") or {}).get("what")]
    row = [c for c in classes(r) if c["class"] == rp.get("class")]
    add = list((row[0].get("grants") or []) if row else []) + grants_for(r, texts)
    have = list(prop.get("grants") or [])
    for g in add:
        if g in relentless_wall.GRANTS and g not in have:
            have.append(g)
    prop["grants"] = have
    return prop


def reseed(r, name, prop):
    """A closed ticket is usually a rules change: the class's seed adapters as the rules ship NOW join the stored proposal
    (CHECKER_REACH_FIX_CLONES_STILL_DARK: the clones class gained seat_clone_state after its owner's empty seed failed)."""
    row = next((c for c in classes(r) if c["class"] == name), {})
    known = relentless_wall.adapters(r)
    have = list(prop.get("adapters") or [])
    add = [x for x in row.get("adapters") or [] if x in known and x not in have]
    return dict(prop, adapters=(have + add)[:relentless_wall.OFFBOX_MAX]) if add else prop


def uncovered(r, prop, texts):
    """-> the masked paths the blind texts name that the proposal covers nowhere (CHECKER_REACH_FIX_CLONES_STILL_DARK gen 3:
    a probe asks only whether the repair READS; SCRATCH_CLONES_PRUNE_LANDED_DEAD_WEIGHT got seat_clone_state, which reads,
    and stayed blind on ~/rm/scratch). Opt-in: it judges only a proposal with an adapter that declares `covers`. A path
    counts as covered under an adapter's covers or under a proposal path the wall would bind."""
    known = relentless_wall.adapters(r)
    ads = [known[a] for a in prop.get("adapters") or [] if a in known]
    if not any(isinstance(a.get("covers"), list) for a in ads):
        return []
    prof = relentless_wall.profile(r) or {}
    masks = [m.rstrip("/") for m in list(prof.get("deny_children") or []) + list(prof.get("deny") or [])]
    cover = [c.rstrip("/") for a in ads for c in a.get("covers") or [] if isinstance(c, str)]
    cover += [p.rstrip("/") for p in prop.get("paths") or [] if relentless_wall.through_reachable(p, prof)]
    out = []
    for p in _paths_of(texts):
        if not any(p == m or p.startswith(m + "/") for m in masks):
            continue
        if not any(p == c or p.startswith(c + "/") for c in cover) and p not in out:
            out.append(p)
    return out


def load(store):
    try:
        with open(store.p(BOOK), encoding="utf-8") as f:
            b = json.load(f)
        return b if isinstance(b, dict) else {}
    except (OSError, ValueError):
        return {}


def save(store, book):
    tmp = store.p(BOOK + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(book, f, indent=1, sort_keys=True)
    os.replace(tmp, store.p(BOOK))


def paths(st):
    """The read paths a passed repair binds at the Marker's next launch (re-checked against the rules there)."""
    rp = st.get("reach") or {}
    return list((rp.get("proposal") or {}).get("paths") or []) if rp.get("status") == "applied" else []


def _wait(st, kind_on, cls, now, detail, ledger_on=None):
    st["status"] = "blocked"
    st["blocked_at"] = now
    st["wait"] = {"kind": WAIT, "on": kind_on, "class": cls, "attributed_at": now}
    if ledger_on:
        st["block_pending"] = {"kind": "item", "on": [ledger_on], "class": "reach", "detail": detail[:600]}


def on_blind(store, st, r, now, said, blind):
    """Under the lock, after unmeasured() counted the blindness. -> the ledger line. The item stops being checked."""
    item, sha = st["item"], (st.get("candidate") or {}).get("sha")
    chk = st.get("_blind_check") or {}
    what = (st.get("blind") or {}).get("what") or blind or ""
    prev = st.get("reach") or {}
    book = load(store)
    if prev.get("status") == "applied" and prev.get("sha") == sha:
        # the probe passed and the Judge is still blind on the same sha: the repair did not give it its eyes
        cls = prev["class"]
        st["reach"] = dict(prev, status="failed", at=now, still_blind=what[:300])
        ent = book.setdefault(cls, {})
        ent.update(owner=item, status="failed", since=now, why="its repair passed the probe, yet the Judge is still blind: "
                   + what[:250])
        save(store, book)
        _wait(st, item, cls, now, "", None)
        return ("blind again at %s after its %s repair passed its probe: Relentless cannot fix this itself, so it files %s "
                "and waits on it: %s" % (sha, cls, _ticket_of(r, cls), what[:300]))
    cls = classify(r, [what] + list(chk.get("unreached") or []))
    prop = propose(r, cls, chk.get("proposals"), chk.get("unreached"), what, store.root)
    name = cls["class"]
    ent = book.get(name) or {}
    owner = ent.get("owner")
    if owner and owner != item and ent.get("status") in ("probe", "ticket", "failed"):
        st["reach"] = {"class": name, "proposal": prop, "sha": sha, "status": "waiting", "on": owner, "at": now}
        _wait(st, owner, name, now, "the Judge could not reach the evidence (%s): it waits on %s, which owns the %s reach "
              "repair" % (what[:300], owner, name), ledger_on=owner)
        book.setdefault(name, ent).setdefault("waiters", [])
        if item not in ent["waiters"]:
            ent["waiters"].append(item)
        save(store, book)
        return ("blind check at %s: UNMEASURED (Marker said %s); no re-check. The %s gap's repair is %s's, so this item "
                "waits on it: %s" % (sha, said, name, owner, what[:300]))
    st["reach"] = {"class": name, "proposal": prop, "sha": sha, "status": "probe", "at": now}
    book[name] = {"owner": item, "status": "probe", "since": now, "waiters": [w for w in ent.get("waiters") or []
                                                                             if w != item]}
    save(store, book)
    _wait(st, item, name, now, "", None)
    return ("blind check at %s: UNMEASURED (Marker said %s); no re-check. This item owns the %s reach repair (%s "
            "proposal: adapters %s, read paths %s%s); it is probed from inside the Judge's wall, then the same sha is "
            "checked once: %s" % (sha, said, name, prop["by"], prop["adapters"] or "-", prop["paths"] or "-",
                                  "; refused %s" % prop["refused"] if prop["refused"] else "", what[:300]))


def _ticket_of(r, name):
    for c in classes(r):
        if c["class"] == name and c.get("ticket"):
            return c["ticket"]
    return r.get("reach_other_ticket", "CHECKER_REACH_FIX_OTHER_STILL_DARK")


def _apply(st, prop, name, now, how):
    """Under the lock: the supervisor's own add-only overlay; the product sha and the proof stay as they are."""
    k = st.get("contract")
    if k is not None:
        have = relentless_wall.offbox_cmds(k)
        k["offbox"] = (have + [x for x in prop.get("adapters") or [] if x not in have])[:relentless_wall.OFFBOX_MAX]
        k["reach_ok"] = ("reach repair %s (%s): adapters %s, read paths %s, box grants %s" % (
            name, how, prop.get("adapters") or "-", prop.get("paths") or "-", prop.get("grants") or "-"))[:400]
        if not k["offbox"]:
            k.pop("offbox")
    st["reach"] = dict(st.get("reach") or {}, proposal=prop, status="applied", applied_at=now)
    st.pop("wait", None)
    st.pop("block_pending", None)
    st["blind"] = None
    st.pop("recheck_at", None)
    st["status"] = "candidate"


def sweep(store, fx, r, now, acts, iso):
    """Not under the lock. Probe each open repair; pass applies and re-checks once, fail files the ticket."""
    if not on(r):
        return
    book = load(store)
    for name, ent in sorted(book.items()):
        owner, status = ent.get("owner"), ent.get("status")
        if status not in ("probe", "ticket", "failed") or not owner:
            continue
        st = store.load(owner)
        if not st or st["status"] != "blocked" or (st.get("wait") or {}).get("kind") != WAIT:
            ent["status"] = "orphan"
            save(store, book)
            continue
        rp = st.get("reach") or {}
        prop = refreshed(r, st)
        if status == "ticket":
            led = fx.item_state(ent["ticket"]) or {}
            event = "%s:%s:%s" % (led.get("state"), led.get("closed_sha"), led.get("event"))
            if led.get("state") != "done" or ent.get("probed_event") == event:
                continue
            ent["probed_event"] = event
            prop = reseed(r, name, prop)
        if status == "failed":
            file_ticket(store, fx, r, book, name, owner, ent.get("why"), now, acts, iso)
            continue
        why = None
        gaps = uncovered(r, prop, [rp.get("still_blind"), (st.get("blind") or {}).get("what")])
        if gaps:
            # it would read, but nothing in it reaches what the Judge named: the re-check would be blind again
            good, why = False, "the proposal (adapters %s) does not cover %s" % (prop.get("adapters") or "-", gaps[:6])
        elif not prop.get("adapters") and not prop.get("paths") and not prop.get("grants"):
            # nothing to probe: a closed ticket is the repair, and the one re-check is its probe (blind again -> ticket)
            good = status == "ticket"
            why = ("%s closed; nothing to probe from here, so the one re-check is the probe" % ent.get("ticket") if good
                   else "the Judge proposed nothing Relentless may apply%s" % (
                       " (refused: %s)" % prop.get("refused") if prop.get("refused") else ""))
        else:
            good, why = fx.reach_probe(r, prop.get("paths") or [], prop.get("adapters") or [],
                                       {"sha": rp.get("sha") or "", "repo": fx.books, "item": owner}, store.root,
                                       grants=prop.get("grants") or [])
        if good:
            with store.lock():
                cur = store.load(owner)
                if cur["status"] != "blocked" or (cur.get("wait") or {}).get("kind") != WAIT:
                    continue
                _apply(cur, prop, name, now, "probe passed: %s" % (why or "")[:200])
                store.attempt(owner, {"at": iso(now), "gen": cur["gen"], "end": "reach_repaired", "class": name,
                                      "detail": ("probe passed: %s" % why)[:600], "sha": rp.get("sha")})
                store.save(cur)
            if status == "ticket":
                fx.ledger_unblock(owner, "reach repair %s: %s closed and the probe passes" % (name, ent["ticket"]))
            waiters = list(ent.get("waiters") or [])
            book[name] = dict(ent, status="ok", owner=None, waiters=[], ok_at=now, last_owner=owner)
            save(store, book)
            for w in waiters:
                release_waiter(store, fx, w, name, now, iso, prop=prop, owner=owner)
            store.journal({"at": iso(now), "do": "reach_repaired", "item": owner, "class": name, "waiters": waiters})
            acts.append({"do": "reach_repaired", "item": owner, "class": name, "waiters": waiters})
            continue
        if status == "ticket":      # the ticket closed and the probe still fails: it keeps waiting, said once per close
            fx.ledger_note(ent["ticket"], "relentless: %s closed, but the %s reach probe still fails, so %s and %d "
                           "waiter(s) stay blocked: %s" % (ent["ticket"], name, owner, len(ent.get("waiters") or []), why))
            save(store, book)
            continue
        file_ticket(store, fx, r, book, name, owner, why, now, acts, iso)
    orphans(store, fx, book, now, acts, iso)


def file_ticket(store, fx, r, book, name, owner, why, now, acts, iso):
    """The fallback, and only after the item's own repair failed its probe: one ticket per class; owner and waiters block
    on it in the ledger."""
    ent = book[name]
    ticket = _ticket_of(r, name)
    bad = fx.reach_ticket(ticket, "Relentless could not repair its own %s reach: the Judge's proposal for %s failed its "
                          "probe from inside the wall (%s). Give the Marker a way to read it (an offbox adapter in "
                          "relentless_rules.json or a read path the wall may bind); closing this re-probes and releases "
                          "the waiting items." % (name, owner, (why or "")[:300]))
    if bad:
        acts.append({"do": "reach_ticket_failed", "item": owner, "why": bad})
        return
    ent.update(status="ticket", ticket=ticket, ticket_at=now, why=(why or "")[:300])
    save(store, book)
    for it in [owner] + list(ent.get("waiters") or []):
        with store.lock():
            cur = store.load(it)
            if not cur or cur["status"] != "blocked" or (cur.get("wait") or {}).get("kind") != WAIT:
                continue
            cur["wait"]["on"] = ticket
            cur["block_pending"] = {"kind": "item", "on": [ticket], "class": "reach",
                                    "detail": "the Judge's %s reach repair failed its probe: %s" % (name, (why or "")[:300])}
            if cur.get("reach"):
                cur["reach"]["status"] = "ticket"
            store.save(cur)
    store.journal({"at": iso(now), "do": "reach_ticket", "item": owner, "class": name, "ticket": ticket})
    acts.append({"do": "reach_ticket", "item": owner, "class": name, "ticket": ticket, "why": (why or "")[:200]})


def release_waiter(store, fx, item, name, now, iso, prop=None, owner=None):
    """The class's repair passed its probe on the owner: the waiter gets the same overlay and its sha is checked once.
    Blind again after it, and the applied-then-blind route files the class ticket. It never becomes a second owner:
    the book is the sweep's, and a waiter promoted under it was lost when the sweep saved its own copy."""
    with store.lock():
        cur = store.load(item)
        if not cur or cur["status"] != "blocked" or (cur.get("wait") or {}).get("kind") != WAIT:
            return False
        if prop is None:
            prop = (cur.get("reach") or {}).get("proposal") or {}
        cur["reach"] = dict(cur.get("reach") or {}, sha=(cur.get("candidate") or {}).get("sha"))
        _apply(cur, prop, name, now, "the %s repair passed its probe on %s" % (name, owner or "its owner"))
        store.attempt(item, {"at": iso(now), "gen": cur["gen"], "end": "reach_waiter_released", "class": name,
                             "owner": owner, "sha": cur["reach"]["sha"]})
        store.save(cur)
    fx.ledger_unblock(item, "reach repair %s passed its probe on %s; this item's sha is checked once" % (name, owner))
    return True


def orphans(store, fx, book, now, acts, iso):
    """A reach-blocked item the book does not hold (promoted to a probe the book lost, or waiting on a finished owner):
    on a class whose repair is open it joins that repair's waiters; on one that passed it gets the passed overlay.
    -> the ids moved."""
    moved = []
    for st in store.states():
        w = st.get("wait") or {}
        if st["status"] != "blocked" or w.get("kind") != WAIT:
            continue
        ent = book.get(w.get("class")) or {}
        if ent.get("owner") == st["item"] or st["item"] in (ent.get("waiters") or []):
            continue
        if ent.get("status") in ("probe", "ticket", "failed") and ent.get("owner"):
            on = ent["ticket"] if ent.get("status") == "ticket" and ent.get("ticket") else ent["owner"]
            with store.lock():
                cur = store.load(st["item"])
                if cur["status"] != "blocked" or (cur.get("wait") or {}).get("kind") != WAIT:
                    continue
                cur["wait"] = dict(cur["wait"], on=on, attributed_at=now)
                cur["reach"] = dict(cur.get("reach") or {}, status="ticket" if on != ent["owner"] else "waiting")
                cur["block_pending"] = {"kind": "item", "on": [on], "class": "reach",
                                        "detail": "waits on the %s reach repair owned by %s" % (w["class"], ent["owner"])}
                store.save(cur)
            ent.setdefault("waiters", []).append(st["item"])
            save(store, book)
            moved.append(st["item"])
            acts.append({"do": "reach_orphan_waits", "item": st["item"], "class": w["class"], "on": on})
            continue
        if ent.get("status") != "ok":
            continue
        last = store.load(ent["last_owner"]) if ent.get("last_owner") else None
        prop = ((last or {}).get("reach") or {}).get("proposal")
        if release_waiter(store, fx, st["item"], w["class"], now, iso, prop=prop, owner=ent.get("last_owner")):
            moved.append(st["item"])
            acts.append({"do": "reach_orphan_released", "item": st["item"], "class": w["class"]})
    return moved


def adopt(store, st, r, now):
    """Under the lock: a held `unmeasured` item, or a blind candidate, from before this rule, moved to its reach repair.
    -> the line, or None when it is not one."""
    hold = st.get("hold") or {}
    if not (st.get("candidate") or {}).get("sha") or not (
            (st["status"] == "held" and hold.get("kind") == "unmeasured") or (st["status"] == "candidate" and st.get("blind"))):
        return None
    blind = st.get("blind") or {}
    st["hold"] = None
    st["_blind_check"] = {}
    try:
        return on_blind(store, st, r, now, blind.get("said") or "UNMEASURED", blind.get("what") or hold.get("why") or "")
    finally:
        st.pop("_blind_check", None)
