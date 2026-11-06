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

import hashlib
import json
import os
import re
import time

import relentless_wall

BOOK = "reach_gaps.json"
# CHECKBOX_BUILD_BUILDER_TOOLCHAIN (redesign_final.md WP-02): a class whose ticket closed while its probe still fails gets a
# SUCCESSOR ticket, never a note and a wait forever (six classes held 23 items behind done tickets on 2026-11-06). Named by
# ordinal: rimflow namecheck refuses a trailing number. Past the last ordinal the last name is reused: reach_ticket reopens it.
SUCCESSOR_WORDS = ("SECOND", "THIRD", "FOURTH", "FIFTH", "SIXTH", "SEVENTH", "EIGHTH", "NINTH", "TENTH", "ELEVENTH", "TWELFTH")
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


def adapters_for(r, texts):
    """-> the seed adapters of EVERY reach_classes row whose match finds the texts, in rules order (CHECKER_REACH_FIX_
    STORE_STILL_DARK gen 3: KUQY's text named the store and git history; classify() took the store row alone)."""
    blob = "\n".join(t for t in texts if t)
    known = relentless_wall.adapters(r)
    out = []
    for c in classes(r):
        if c.get("match") and re.search(c["match"], blob, re.I):
            out += [a for a in c.get("adapters") or [] if a in known and a not in out]
    return out


def _union(first, more, cap):
    out = [x for x in first or []]
    out += [x for x in more or [] if x not in out]
    return out[:cap]


def _paths_of(texts):
    out = []
    for t in texts:
        for m in relentless_wall._THROUGH_WORD.finditer(t or ""):
            p = os.path.normpath(relentless_wall._host(m.group(0)))
            if p not in out and p != "/":
                out.append(p)
    return out


def granted(r, grants, p):
    """-> the box grant (the proposal's, or every box's relentless_box.json default) whose rules grant_covers regex names
    path p, else None. CHECKER_REACH_FIX_STORE_DARK_SECOND: KUQY's store proposal failed the coverage gate twice on the
    mirror's .git, though every box already held that history (git_history). Bad rules data covers nothing."""
    gcov = r.get("grant_covers")
    if not isinstance(gcov, dict) or not isinstance(p, str):
        return None
    held = [g for g in list(grants or []) if isinstance(g, str)] + relentless_wall.default_grants()
    for g in dict.fromkeys(held):
        rx = gcov.get(g)
        if g not in relentless_wall.GRANTS or not isinstance(rx, str):
            continue
        try:
            if re.search(rx, p):
                return g
        except re.error:
            continue
    return None


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


def dark(r, texts):
    """-> the paths `texts` name that no reach repair can ever show: strictly under a read_through root (scratch the wall
    binds read only when named), yet withheld there by design (never_through, never_through_rx), and covered by no
    supervisor adapter. CHECKER_REACH_FIX_STORE_STILL_DARK gen 7: RA_S03_WALL_MEASURE_DID_IT_HELP's proof reads the seed
    bank under relentless_agent (the evaluation keys); its store repair passed the probe, the same sha was blind again,
    and the store class filed a ticket, then a successor, for a gap no repair may open. Such a gap is the proof's binding,
    not the box: the item goes back to its builder (back()). The store, ~/.ssh and the other reach_never roots are not
    read_through roots, so they stay the classes' to repair through their adapters."""
    prof = relentless_wall.profile(r) or {}
    roots = [x.rstrip("/") for x in prof.get("read_through") or [] if isinstance(x, str)]
    cover = [c.rstrip("/") for a in relentless_wall.adapters(r).values() for c in a.get("covers") or []
             if isinstance(c, str)]
    out = []
    for p in _paths_of(texts):
        if not any(p.startswith(x + "/") for x in roots) or relentless_wall.through_reachable(p, prof):
            continue
        if any(p == c or p.startswith(c + "/") for c in cover) or p in out:
            continue
        out.append(p)
    return out


def back_why(gone, what):
    return ("the proof needs %s, which the wall withholds by design (never_through / never_through_rx) and no supervisor "
            "adapter covers: no reach repair can give the Judge these eyes, so the binding goes back to its builder. Rebind "
            "(proof only, the code stays): read it through a supervisor offbox adapter (relentless_rules.json "
            "offbox_adapters; add one if none fits) or prove it from what the box shows. The Judge said: %s"
            % (", ".join(gone[:6]), (what or "")[:300]))


def _hand_over(store, fx, book, name, item, now, acts):
    """The class repair `item` owned or waited on goes on without it: its first waiter takes the repair over (a ticket's
    blocks are already on the ticket; a probe's waiters were blocked on `item`, so they move to the new owner)."""
    ent = book.get(name) or {}
    waiters = [w for w in ent.get("waiters") or [] if w != item]
    if ent.get("owner") != item:
        if ent:
            ent["waiters"] = waiters
        return
    if not waiters:
        book[name] = dict(ent, status="back", owner=None, waiters=[], back_at=now, last_back=item)
        return
    new, rest = waiters[0], waiters[1:]
    book[name] = dict(ent, owner=new, waiters=rest, since=now, last_back=item)
    if ent.get("status") == "ticket":
        return
    book[name]["status"] = "probe"
    for w in [new] + rest:
        with store.lock():
            cur = store.load(w)
            if not cur or cur["status"] != "blocked" or (cur.get("wait") or {}).get("kind") != WAIT:
                continue
            cur["wait"] = dict(cur["wait"], on=new, attributed_at=now)
            if cur.get("reach"):
                cur["reach"]["status"] = "probe" if w == new else "waiting"
                cur["reach"]["on"] = None if w == new else new
            if w != new:
                cur["block_pending"] = {"kind": "item", "on": [new], "class": "reach",
                                        "detail": "waits on the %s reach repair, now owned by %s" % (name, new)}
            store.save(cur)
        if fx is not None:
            fx.ledger_unblock(w, "reach repair %s: %s went back to its builder; %s owns the repair now" % (name, item, new))
    acts.append({"do": "reach_handed_over", "item": item, "class": name, "to": new})


def propose(r, cls, proposals, unreached, what, store_root=None):
    """-> {adapters, paths, refused, by}. The Judge's --propose lines first; none, and the class's seed."""
    known = relentless_wall.adapters(r)
    said = [str(x).strip() for x in proposals or [] if str(x).strip()][:PROPOSE_MAX]
    ads = [x for x in said if x in known]
    grants = [x for x in said if x in relentless_wall.GRANTS and x not in known]
    paths = _paths_of([x for x in said if x not in known and x not in grants])
    by = "judge" if said else "seed"
    asked = list(grants)
    # the classes' grants ride along with what the Judge said: it names what it lacks, not how the box is made
    for g in list(cls.get("grants") or []) + grants_for(r, list(unreached or []) + [what or ""]):
        if g in relentless_wall.GRANTS and g not in grants:
            grants.append(g)
    if not said:
        ads = _union([x for x in cls.get("adapters") or [] if x in known],
                     adapters_for(r, list(unreached or []) + [what or ""]), relentless_wall.OFFBOX_MAX)
        paths = _paths_of(list(unreached or []) + [what or ""]) if cls.get("paths") else []
    # a path a held box grant already shows is no bind (a bound mirror .git would carry refs past the candidate)
    shown = {p: g for p, g in ((p, granted(r, grants, p)) for p in paths) if g}
    paths = [p for p in paths if p not in shown]
    if said and not ads and not asked and all(refused(p, r, store_root) for p in paths):
        # CHECKER_REACH_FIX_WINDOWS_BUILD_STILL_DARK gen 3: the Judge named only what no repair opens (the live folder);
        # proposing nothing filed a ticket at once, so the class seed adapters stand in for the refused proposal. A path
        # a box grant shows (STORE_DARK_SECOND) is no repair either: the seed stands in for it too.
        ads = [x for x in cls.get("adapters") or [] if x in known]
        by = "judge+seed" if ads else by
    bad = {}
    for p in list(paths):
        why = refused(p, r, store_root)
        if why:
            bad[p] = why
            paths.remove(p)
    bad.update({x: "not a supervisor offbox adapter" for x in said if x not in known and x not in grants
                and not _paths_of([x])})
    out = {"adapters": ads[:relentless_wall.OFFBOX_MAX], "paths": paths[:relentless_wall.THROUGH_MAX], "refused": bad,
           "by": by, "grants": grants}
    if shown:
        out["granted"] = shown
    return out


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
    if prop.get("by") != "judge":     # a seed rides with every class its text names; a Judge's own list stands as said
        prop["adapters"] = _union(prop.get("adapters"), adapters_for(r, texts), relentless_wall.OFFBOX_MAX)
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
    and stayed blind on ~/rm/scratch). It judges every proposal that READS (an adapter or a path); an adapter that declares
    no `covers` covers nothing (gen 5: proc_cwds reads, covers no root, and spent the re-check again). A path counts as
    covered under an adapter's covers or under a proposal path the wall would bind. A proposal that reads nothing is left
    to the nothing-to-probe branch, where a closed ticket's one re-check is its probe."""
    if not prop.get("adapters") and not prop.get("paths"):
        return []
    known = relentless_wall.adapters(r)
    ads = [known[a] for a in prop.get("adapters") or [] if a in known]
    prof = relentless_wall.profile(r) or {}
    masks = [m.rstrip("/") for m in list(prof.get("deny_children") or []) + list(prof.get("deny") or [])]
    cover = [c.rstrip("/") for a in ads for c in a.get("covers") or [] if isinstance(c, str)]
    cover += [p.rstrip("/") for p in prop.get("paths") or [] if relentless_wall.through_reachable(p, prof)]
    cover += relentless_wall.read_always(prof)     # every box shows them (gen 5: the D: mirror's game inventory)
    out = []
    for p in _paths_of(texts):
        if not any(p == m or p.startswith(m + "/") for m in masks):
            continue
        if granted(r, prop.get("grants"), p):
            continue
        if not any(p == c or p.startswith(c + "/") for c in cover) and p not in out:
            out.append(p)
    return out


def fill(r, name, prop, texts):
    """-> the proposal with the seed adapters that cover what it leaves uncovered (CHECKER_REACH_FIX_CLONES_STILL_DARK gen
    9: DESSICATED_CORPSES_JUDGE_THE_ONES_HE_MISSED's Judge proposed [proc_cwds, relentless_live_evidence, rm_pool_state],
    named the bench seat clone, and the coverage gate filed this ticket though the clones seed's seat_clone_state covers
    bench). Only seed adapters (the class row's and every row the texts match) whose `covers` hold a gap join; at
    OFFBOX_MAX the proposal's own adapters that cover nothing named make room, last first. No gap filled: unchanged."""
    gaps = uncovered(r, prop, texts)
    if not gaps:
        return prop
    known = relentless_wall.adapters(r)
    row = next((c for c in classes(r) if c["class"] == name), {})
    seed = _union([x for x in row.get("adapters") or [] if x in known], adapters_for(r, texts), 64)

    def covers(a, ps):
        cv = [c.rstrip("/") for c in (known.get(a) or {}).get("covers") or [] if isinstance(c, str)]
        return [p for p in ps if any(p == c or p.startswith(c + "/") for c in cv)]
    have = list(prop.get("adapters") or [])
    add = []
    for a in seed:
        if a not in have and covers(a, [g for g in gaps if not any(covers(b, [g]) for b in add)]):
            add.append(a)
    if not add:
        return prop
    named = [p for p in _paths_of(texts)]
    while len(have) + len(add) > relentless_wall.OFFBOX_MAX:
        idle = [a for a in have if not covers(a, named)]
        if not idle:
            break
        have.remove(idle[-1])
    out = (have + add)[:relentless_wall.OFFBOX_MAX]
    by = prop.get("by") or "seed"
    return dict(prop, adapters=out, by=by if by.endswith("+seed") or by == "seed" else by + "+seed",
                filled=[a for a in add if a in out])


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


def worker_owes(r, st, blind):
    """-> the reach_classes row when the blind gap is evidence the WORKER owes (`worker_owes`, e.g. gpt_review: a review it
    never wrote, which no adapter or read path can make), else None. Such a gap opens no repair: it goes back to the worker
    (CHECKER_REACH_FIX_WINDOWS_BUILD_STILL_DARK gen 7, FOUNDRY_BACKSTOP_REPAIR_CURSOR_HIDES_INPUT)."""
    chk = st.get("_blind_check") or {}
    what = (st.get("blind") or {}).get("what") or blind or ""
    cls = classify(r, [what] + list(chk.get("unreached") or []))
    return cls if cls.get("worker_owes") else None


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
    gone = dark(r, [what] + list(chk.get("unreached") or []))
    if gone:
        # no repair opens it: the binding goes back to the builder (relentless.unmeasured runs the return)
        acts = []
        for name in sorted(book):
            _hand_over(store, None, book, name, item, now, acts)
        save(store, book)
        st["reach"] = dict(prev, status="back", at=now, dark=gone[:6], sha=sha)
        st.pop("wait", None)
        st.pop("block_pending", None)
        st["_reach_back"] = back_why(gone, what)
        return ("blind check at %s: UNMEASURED (Marker said %s) on what no reach repair may open (%s): no repair, no "
                "ticket; the binding goes back to its builder: %s" % (sha, said, ", ".join(gone[:6]), what[:300]))
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


def stale(fx, r, name, ent, sha):
    """-> the class ticket's closed sha when the candidate `sha` does not hold it, else None. A Judge blind at a sha cut
    before the fix that gives it eyes is blind by its base, not by the box: no repair or reopen helps, a rebase does
    (REAPER_SELFTEST_FIX_BLIND_IN_EVERY_BOX: OPS_TMP_DRAIN_RESTORE_JVCO's 65315ab8e7 predated 21832017e8 and reopened
    it, 2026-11-06). An unanswered ancestry (None) proves nothing: the old road stands."""
    contains = getattr(fx, "contains", None)
    if not sha or contains is None:
        return None
    fix = (fx.item_state(ent.get("ticket") or _ticket_of(r, name)) or {}).get("closed_sha")
    return fix if fix and contains(sha, fix) is False else None


def stale_why(name, ticket, fix, sha):
    return ("the Judge was blind at %s, a candidate cut before %s's fix %s, which is what gives it eyes on the %s reach: "
            "rebase onto origin/main (it holds %s), rerun the proof, and finish on the new sha; no reach repair or reopen "
            "is owed" % ((sha or "?")[:10], ticket, fix[:10], name, fix[:10]))


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


def sweep(store, fx, r, now, acts, iso, back=None):
    """Not under the lock. Probe each open repair; pass applies and re-checks once, fail files the ticket. `back(store,
    st, why, r, now)`, under the lock: an owner blind on what no repair opens (dark()) goes back to its builder."""
    if not on(r):
        return
    book = load(store)
    for name in sorted(book):
        ent = book.get(name) or {}
        owner, status = ent.get("owner"), ent.get("status")
        if status not in ("probe", "ticket", "failed") or not owner:
            continue
        st = store.load(owner)
        if not st or st["status"] != "blocked" or (st.get("wait") or {}).get("kind") != WAIT:
            ent["status"] = "orphan"
            save(store, book)
            continue
        rp = st.get("reach") or {}
        gone = dark(r, [rp.get("still_blind"), (st.get("blind") or {}).get("what")])
        if gone and back is not None:
            why = back_why(gone, rp.get("still_blind") or (st.get("blind") or {}).get("what"))
            with store.lock():
                cur = store.load(owner)
                if not cur or cur["status"] != "blocked" or (cur.get("wait") or {}).get("kind") != WAIT:
                    continue
                cur.pop("wait", None)
                cur.pop("block_pending", None)
                cur["reach"] = dict(cur.get("reach") or {}, status="back", at=now, dark=gone[:6])
                back(store, cur, why, r, now)
            if status == "ticket":
                fx.ledger_unblock(owner, "reach repair %s: no repair opens %s; the binding went back to its builder"
                                  % (name, ", ".join(gone[:6])))
            _hand_over(store, fx, book, name, owner, now, acts)
            for other in sorted(book):
                if other != name:
                    _hand_over(store, fx, book, other, owner, now, acts)
            save(store, book)
            store.journal({"at": iso(now), "do": "reach_back", "item": owner, "class": name, "dark": gone[:6]})
            acts.append({"do": "reach_back", "item": owner, "class": name, "dark": gone[:6]})
            continue
        fix = stale(fx, r, name, ent, rp.get("sha") or (st.get("candidate") or {}).get("sha"))
        if fix and back is not None:
            why = stale_why(name, ent.get("ticket") or _ticket_of(r, name), fix, rp.get("sha"))
            with store.lock():
                cur = store.load(owner)
                if not cur or cur["status"] != "blocked" or (cur.get("wait") or {}).get("kind") != WAIT:
                    continue
                cur.pop("wait", None)
                cur.pop("block_pending", None)
                cur["reach"] = dict(cur.get("reach") or {}, status="stale", at=now, fix=fix)
                back(store, cur, why, r, now)
            if status == "ticket":
                fx.ledger_unblock(owner, "reach repair %s: the candidate predates the fix %s; back to its builder"
                                  % (name, fix[:10]))
            _hand_over(store, fx, book, name, owner, now, acts)
            save(store, book)
            store.journal({"at": iso(now), "do": "reach_stale", "item": owner, "class": name, "fix": fix})
            acts.append({"do": "reach_stale", "item": owner, "class": name, "fix": fix})
            continue
        prop = refreshed(r, st)
        if status == "ticket":
            led = fx.item_state(ent["ticket"]) or {}
            event = "%s:%s:%s" % (led.get("state"), led.get("closed_sha"), led.get("event"))
            if led.get("state") != "done":
                continue
            fp = box_fingerprint()
            if ent.get("probed_event") == event and ent.get("probed_box") == fp:
                # probed at this close, on this box, and it failed: the done ticket is no repair, so a successor is
                file_successor(store, fx, r, book, name, owner, ent.get("why") or "its probe failed after the close",
                               now, acts, iso)
                continue
            ent["probed_event"] = event     # a new close, or the box itself changed since (relentless_box.json): probe once
            ent["probed_box"] = fp
            prop = reseed(r, name, prop)
        if status == "failed":
            file_ticket(store, fx, r, book, name, owner, ent.get("why"), now, acts, iso)
            continue
        why = None
        texts = [rp.get("still_blind"), (st.get("blind") or {}).get("what")]
        prop = fill(r, name, prop, texts)
        gaps = uncovered(r, prop, texts)
        if gaps:
            # it would read, but nothing in it reaches what the Judge named: the re-check would be blind again
            good, why = False, "the proposal (adapters %s) does not cover %s" % (prop.get("adapters") or "-", gaps[:6])
            moved, pwhy = split(store, fx, r, book, name, owner, st, prop, gaps, why, now, acts, iso)
            if moved:
                continue
            if pwhy:
                why += "; and the rest of the repair failed its probe too: " + pwhy[:300]
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
                if not cur or cur["status"] != "blocked" or (cur.get("wait") or {}).get("kind") != WAIT:
                    continue
                _apply(cur, prop, name, now, "probe passed: %s" % (why or "")[:200])
                store.attempt(owner, {"at": iso(now), "gen": cur["gen"], "end": "reach_repaired", "class": name,
                                      "detail": ("probe passed: %s" % why)[:600], "sha": rp.get("sha")})
                store.save(cur)
            if status == "ticket":
                fx.ledger_unblock(owner, "reach repair %s: %s closed and the probe passes" % (name, ent["ticket"]))
            waiters = list(ent.get("waiters") or [])
            book[name] = dict({k: v for k, v in ent.items() if k not in ("ok_prop", "split_owner")}, status="ok",
                              owner=None, waiters=[], ok_at=now, last_owner=owner)
            save(store, book)
            for w in waiters:
                release_waiter(store, fx, w, name, now, iso, prop=prop, owner=owner, r=r)
            store.journal({"at": iso(now), "do": "reach_repaired", "item": owner, "class": name, "waiters": waiters})
            acts.append({"do": "reach_repaired", "item": owner, "class": name, "waiters": waiters})
            continue
        if status == "ticket":      # the ticket closed and the probe still fails: a successor, never a wait on a done ticket
            file_successor(store, fx, r, book, name, owner, why, now, acts, iso)
            continue
        file_ticket(store, fx, r, book, name, owner, why, now, acts, iso)
    orphans(store, fx, book, now, acts, iso, r)


def gap_class(r, gaps, visited):
    """-> the reach_classes row (or the catch-all `other`) whose match finds the uncovered `gaps`, skipping every class in
    `visited`; None when the only home left is one already visited."""
    blob = "\n".join(gaps)
    for c in classes(r):
        if c["class"] not in visited and c.get("match") and re.search(c["match"], blob, re.I):
            return c
    other = classify(r, [])
    return other if other["class"] not in visited else None


def split(store, fx, r, book, name, owner, st, prop, gaps, why, now, acts, iso):
    """CHECKER_REACH_FIX_GIT_DARK_SECOND: the git class's owner NIGHTLY_COP_FIX_RED_AQJSGV_CFVH also named
    /home/mandrake/rm/arena (gone from the host with the arena trial) and the D: mirror's bundle_textures. No git repair
    covers those, so every probe of the git class failed on them and eight items blind on git history alone waited
    behind two tickets. The gaps are the owner's own: the rest of the repair (adapters, grants, covered paths) is probed
    without them, only while someone waits; a pass releases the class's waiters with it and moves the owner alone to the class its gaps name
    (gap_class, never one it was already split from), where it is probed afresh. -> (moved, why the rest failed)."""
    ent = book[name]
    if not ent.get("waiters"):      # no one waits behind the owner's gaps: its class ticket is its own (selftest row 8c)
        return False, None
    rp = st.get("reach") or {}
    visited = list(rp.get("split_from") or []) + [name]
    dest = gap_class(r, gaps, visited)
    if dest is None:
        return False, None
    rest = dict(prop, paths=[p for p in prop.get("paths") or [] if p not in gaps])
    if not (rest.get("adapters") or rest.get("paths") or rest.get("grants")):
        return False, None
    good, pwhy = fx.reach_probe(r, rest.get("paths") or [], rest.get("adapters") or [],
                                {"sha": rp.get("sha") or "", "repo": fx.books, "item": owner}, store.root,
                                grants=rest.get("grants") or [])
    if not good:
        return False, pwhy
    dn = dest["class"]
    with store.lock():
        cur = store.load(owner)
        if not cur or cur["status"] != "blocked" or (cur.get("wait") or {}).get("kind") != WAIT:
            return False, None
        dent = book.get(dn) or {}
        cur["reach"] = dict(cur.get("reach") or {}, **{"class": dn, "split_from": visited, "proposal": prop,
                                                       "split_why": why[:300]})
        cur.pop("block_pending", None)
        if dent.get("owner") and dent["owner"] != owner and dent.get("status") in ("probe", "ticket", "failed"):
            on = dent["ticket"] if dent.get("status") == "ticket" and dent.get("ticket") else dent["owner"]
            cur["reach"]["status"] = "ticket" if on != dent["owner"] else "waiting"
            _wait(cur, on, dn, now, "its uncovered paths %s wait on the %s reach repair owned by %s"
                  % (gaps[:6], dn, dent["owner"]), ledger_on=on)
            dent.setdefault("waiters", [])
            if owner not in dent["waiters"]:
                dent["waiters"].append(owner)
            book[dn] = dent
        else:
            cur["reach"]["status"] = "probe"
            _wait(cur, owner, dn, now, "")
            book[dn] = dict({k: dent[k] for k in ("successors",) if k in dent}, owner=owner, status="probe", since=now,
                            waiters=[w for w in dent.get("waiters") or [] if w != owner])
        store.attempt(owner, {"at": iso(now), "gen": cur["gen"], "end": "reach_split", "class": name, "to": dn,
                              "detail": ("the %s repair passed its probe without %s: %s" % (name, gaps[:6], pwhy))[:600]})
        store.save(cur)
    waiters = list(ent.get("waiters") or [])
    book[name] = dict(ent, status="ok", owner=None, waiters=[], ok_at=now, last_owner=None, ok_prop=rest,
                      split_owner=owner)
    save(store, book)
    if ent.get("status") == "ticket":
        fx.ledger_unblock(owner, "reach repair %s: %s closed and the probe passes without this item's own gaps %s, "
                          "which move to the %s class" % (name, ent.get("ticket"), gaps[:6], dn))
    for w in waiters:
        release_waiter(store, fx, w, name, now, iso, prop=rest, owner=owner, r=r)
    store.journal({"at": iso(now), "do": "reach_split", "item": owner, "class": name, "to": dn, "gaps": gaps[:6],
                   "waiters": waiters})
    acts.append({"do": "reach_split", "item": owner, "class": name, "to": dn, "waiters": waiters})
    return True, None


def box_fingerprint(cfg=None):
    """-> a short hash of relentless_box.json: what every box carries. A change re-probes a class parked on a done ticket."""
    cfg = relentless_wall.box_config() if cfg is None else cfg
    return hashlib.sha256(json.dumps(cfg, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:16]


def successor_id(name, ent):
    """-> the class's next ticket: CHECKER_REACH_FIX_<CLASS>_DARK_<ORDINAL>, one ordinal per successor already filed."""
    n = len(ent.get("successors") or [])
    word = SUCCESSOR_WORDS[min(n, len(SUCCESSOR_WORDS) - 1)]
    return "CHECKER_REACH_FIX_%s_DARK_%s" % (re.sub(r"[^A-Z0-9]+", "_", str(name).upper()).strip("_") or "OTHER", word)


def file_successor(store, fx, r, book, name, owner, why, now, acts, iso):
    """The class's ticket is done and its probe still fails: file the successor, note the predecessor once, and move the
    owner's and waiters' blocks onto it. -> the successor id, or None when it did not land (the next sweep retries)."""
    ent = book[name]
    old = ent.get("ticket") or _ticket_of(r, name)
    new = successor_id(name, ent)
    text = ("Successor of %s, which closed while the %s reach probe still fails for %s and %d waiter(s): %s. Give the "
            "Marker a way to read it (relentless_box.json for what every box carries, an offbox adapter, or a read path "
            "the wall may bind); closing this re-probes and releases the waiting items."
            % (old, name, owner, len(ent.get("waiters") or []), (why or "")[:300]))
    if not file_ticket(store, fx, r, book, name, owner, why, now, acts, iso, ticket=new, text=text):
        return None
    ent = book[name]
    ent.setdefault("successors", []).append({"ticket": new, "after": old, "at": now})
    ent.pop("probed_event", None)
    save(store, book)
    if new != old:
        fx.ledger_note(old, "relentless: %s closed, but the %s reach probe still fails; successor filed: %s" % (old, name, new))
    acts.append({"do": "reach_successor", "item": owner, "class": name, "ticket": new, "after": old})
    return new


def file_ticket(store, fx, r, book, name, owner, why, now, acts, iso, ticket=None, text=None):
    """The fallback, and only after the item's own repair failed its probe: one ticket per class; owner and waiters block
    on it in the ledger. `ticket`/`text`: a successor's (file_successor). -> True when it landed."""
    ent = book[name]
    ticket = ticket or _ticket_of(r, name)
    bad = fx.reach_ticket(ticket, text or "Relentless could not repair its own %s reach: the Judge's proposal for %s failed its "
                          "probe from inside the wall (%s). Give the Marker a way to read it (an offbox adapter in "
                          "relentless_rules.json or a read path the wall may bind); closing this re-probes and releases "
                          "the waiting items." % (name, owner, (why or "")[:300]))
    if bad:
        acts.append({"do": "reach_ticket_failed", "item": owner, "why": bad})
        return False
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
    return True


def release_waiter(store, fx, item, name, now, iso, prop=None, owner=None, r=None):
    """The class's repair passed its probe on the owner: the waiter gets the same overlay and its sha is checked once.
    Blind again after it, and the applied-then-blind route files the class ticket. It never becomes a second owner:
    the book is the sweep's, and a waiter promoted under it was lost when the sweep saved its own copy."""
    with store.lock():
        cur = store.load(item)
        if not cur or cur["status"] != "blocked" or (cur.get("wait") or {}).get("kind") != WAIT:
            return False
        if prop is None:
            prop = (cur.get("reach") or {}).get("proposal") or {}
        else:
            # the owner's passed repair, PLUS this waiter's own adapters and grants (CHECKER_REACH_FIX_STORE_STILL_DARK
            # gen 3: KUQY got IWIV's store proposal alone and was blind again on the git history its own text named).
            # Its own read paths stay out: they were never probed.
            mine = refreshed(r, cur) if r is not None else ((cur.get("reach") or {}).get("proposal") or {})
            prop = dict(prop, adapters=_union(prop.get("adapters"), mine.get("adapters"), relentless_wall.OFFBOX_MAX),
                        grants=_union(prop.get("grants"), [g for g in mine.get("grants") or []
                                                           if g in relentless_wall.GRANTS], len(relentless_wall.GRANTS)))
        cur["reach"] = dict(cur.get("reach") or {}, sha=(cur.get("candidate") or {}).get("sha"))
        _apply(cur, prop, name, now, "the %s repair passed its probe on %s" % (name, owner or "its owner"))
        store.attempt(item, {"at": iso(now), "gen": cur["gen"], "end": "reach_waiter_released", "class": name,
                             "owner": owner, "sha": cur["reach"]["sha"]})
        store.save(cur)
    fx.ledger_unblock(item, "reach repair %s passed its probe on %s; this item's sha is checked once" % (name, owner))
    return True


def orphans(store, fx, book, now, acts, iso, r=None):
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
                if not cur or cur["status"] != "blocked" or (cur.get("wait") or {}).get("kind") != WAIT:
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
        prop = ent.get("ok_prop") or ((last or {}).get("reach") or {}).get("proposal")    # ok_prop: a split's (split)
        if release_waiter(store, fx, st["item"], w["class"], now, iso, prop=prop, owner=ent.get("last_owner"), r=r):
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
