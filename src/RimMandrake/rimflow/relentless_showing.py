#!/usr/bin/env python3
"""relentless_showing.py -- the showing stage: an item waiting only on the owner's look is staged BEFORE he is asked
(OWNER_REVIEW_BUILD_SHOWS_READY_BEFORE_ASKED).

The owner, 2026-11-05: "Sloppy. For all the items waiting for human review, please have them pre-build anything needed
for the live showing." Then: "That's a general policy for Relentless Pipeline." He had asked for a live session; the one
item ready for his look (DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS) had nothing staged, and a helper built a review map from
scratch while he waited, racing Relentless's own staging for the bridge.

  trigger   wants(): an open item whose only remaining criterion is his look -- the ledger routes it to him (needs=owner,
            owner_queue.is_his), or every outstanding criterion is a look clause (an L4 "he looks", a cosmetic gate such as
            "nothing ships before his look"). A Designer first-touch pass is a sign-off, not a showing: never enrolled.
  build     one showing worker (the game lane's bridge discipline: the supervisor takes the bridge with `--idle-ok`, which
            refuses under an OWNER or Conductor hold, and only while no game phase holds the game; released the moment it
            ends) writes under SHOW_DIR/<ITEM>/:
              showing.json  {item, sha, route, save, mods, stations: [{n, label, shows, judge, capture}], minutes, built_by}
              captures      one zoomed capture per station
            An art item takes the review-sheet route instead (route "sheet": art_sheet.py with its prereview, no bridge).
  judge     a blind judge, a unit that did not build it, reads the captures and writes judge.json {judged_by, sha,
            verdict pass|fail, stations: {n: note}}. Nothing reaches the owner unread.
  never     a flyer's flight (relentless_live.flyer_word on its title, question and owed criteria): JOINT SESSION, by rule,
            never built -- the owner: never live-test a flyer's flight without him. The sheet route is no flight, so stays.
  blocked   blockers(): an open item of the same family (SUBJECT words, one a word-prefix of the other) or naming one of
            its defNames, with an OWNER note of the past 14 days, is not built yet: the showing waits for it.
  ready     status() == READY only with a complete manifest at the item's current sha, the deployed mod unchanged since,
            and a pass from the judge this supervisor launched. A new sha or a changed deployed mod makes it STALE, and it
            is built again.

The state (one row per enrolled item: phase, run, tries) is the store's showings.json; the reading owner_queue and
RUNNING NOW show is the same file's "items" (state, save, minutes, dir).
"""
import hashlib
import json
import os
import re
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SHOW_DIR = os.environ.get("RELENTLESS_SHOWINGS_DIR") or "/mnt/d/ClaudeWork/rimmandrake/showings"
SHOW_DIR_WIN = r"D:\ClaudeWork\rimmandrake\showings"
MANIFEST = "showing.json"
JUDGE = "judge.json"
STATE = "showings.json"

READY, STALE, OWED, BUILDING, JUDGING, INCOMPLETE, UNJUDGED, FAILED, HELD, BLOCKED, JOINT = (
    "READY TO SHOW", "STALE", "OWED", "BUILDING", "JUDGING", "INCOMPLETE", "UNJUDGED", "JUDGE FAILED", "HELD", "BLOCKED",
    "JOINT SESSION")
OWNER_NOTE_DAYS = 14
DEFAULTS = {"enabled": False, "build_max_s": 3600, "judge_max_s": 1800, "tries": 2, "renew_s": 1200,
            "builder_agent": "rm-testpilot", "judge_agent": "rm-judge"}
# the look clauses: an L4 that says he looks, or a gate that holds shipping on his look
LOOK = re.compile(r"\b(he|owner|owner's|his|the owner)\s+(looks?|look at|sees?|eyes|judges?|signs? off)\b|\bhis (own )?(look|eyes)\b|"
                  r"\bowner'?s? (live )?(look|review|eyes)\b|before his look|nothing ships before", re.I)
# the art route: a picture to judge, not a build to walk. Narrow on purpose: "plank art" on a drawbridge is a live build,
# and "facing" is no art word (every building has one): REEL_NOZZLE_FIX_COUPLER_HIDES_UNDERNEATH's "south facing" reel
# took the sheet route, though its look is a laid hose on a map
ART = re.compile(r"\b(sprites?|textures?|reskins?|redraws?|art sheet|art candidates|review sheet)\b", re.I)
ART_ID = re.compile(r"(^|_)(ART|SPRITES?|TEXTURES?|RESKIN)(_|$)")
# a look at the thing in place: never a sheet, whatever the art words say
IN_PLACE = re.compile(r"\b(in[- ]game|live|on (the|a) map|laid|placed|layering)\b", re.I)
# a defName the ledger text names: the precise half of "the same subject"
DEFNAME = re.compile(r"\b(?:RM|RSW|RUT)_[A-Za-z0-9_]*[A-Za-z0-9]")


def cfg(r):
    c = dict(DEFAULTS)
    c.update((r or {}).get("showings") or {})
    return c


def look_clause(c):
    """One criterion {"id","level","text"} is a look clause: L4 naming his look, or a cosmetic gate on it."""
    t = c.get("text") or ""
    return bool(LOOK.search(t)) and (c.get("level") == "L4" or "before his look" in t.lower() or "nothing ships" in t.lower())


def only_look_left(it):
    """Every outstanding criterion is a look clause (and at least one is owed)."""
    owed = [c for c in (getattr(it, "criteria", None) or []) if c.get("id") in (getattr(it, "outstanding", None) or [])]
    return bool(owed) and all(look_clause(c) for c in owed)


def wants(iid, it, is_his, first_touch):
    """-> the trigger in words, or None. is_his: owner_queue.is_his(it, ...) already read; first_touch(iid): a sign-off."""
    if it is None or not getattr(it, "open", False) or first_touch(iid):
        return None
    if only_look_left(it):
        return "only a look clause is owed"
    if is_his:
        return "needs=owner"
    return None


def family(iid):
    """The item's subject words: SUBJECT of SUBJECT_INTENT_TWIST (model.parse_name), else the id without a legacy _N."""
    import model
    got = model.parse_name(iid)
    if got:
        return tuple(got[0])
    return tuple(re.sub(r"_\d+$", "", iid or "").split("_"))


def same_family(a, b):
    """One family is a word-prefix of the other: DRAWBRIDGE and DRAWBRIDGE_UP are one, REEL_NOZZLE and REEL_HOSE are
    not. The first id word alone (PIPE, WATER, REEL) joined every pipe, water and reel item."""
    fa, fb = family(a), family(b)
    n = min(len(fa), len(fb))
    return n > 0 and fa[:n] == fb[:n]


def named_defs(*texts):
    return {m.group(0) for t in texts for m in DEFNAME.finditer(t or "")}


def crit_texts(it):
    return [c.get("text") or "" for c in (getattr(it, "criteria", None) or [])
            if c.get("id") in (getattr(it, "outstanding", None) or [])]


def flyer(it, question, lr):
    """-> why this item's showing is never pre-built, or None: its title, question or owed criteria name a flyer's flight
    (relentless_live.flyer_word, the live lane's own test). The standing ruling, not a ledger block: never live-test a
    flyer's flight without him; a showing of one is a joint session."""
    import relentless_live
    hit = relentless_live.flyer_word(lr, getattr(it, "title", "") or "", ("question", question or ""),
                                     *[("criterion", t) for t in crit_texts(it)])
    return "the %s names %r: a flyer's flight is shown only with him present, never pre-built" % hit if hit else None


def _ts(e):
    try:
        return time.mktime(time.strptime((e.get("ts") or "")[:19], "%Y-%m-%dT%H:%M:%S")) - time.timezone
    except (ValueError, TypeError):
        return None


def blockers(iid, it, items, evs, now, waits_on_look=lambda i: False, days=OWNER_NOTE_DAYS):
    """-> (on, why) when the showing may not be built, else None. 2026-11-05: DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS was
    shown on its 10-22 ask while his 11-03 build spec (on DRAWBRIDGE_UP_FIX_RAISED_LOOKS_LOWERED) had never been built.
    A showing is built only when every open successor or child, and every OWNER note of the past `days` naming the
    subject, is built: an open item is not built, so an OWNER note on an open item of the subject (other than one itself
    waiting only on his look) blocks it; so does his note on this item after its build, a ledger block, an open
    superseding item, or an open item it caused."""
    if getattr(it, "blocked", False):
        return (getattr(it, "blocked_on", None) or "?", "blocked in the ledger: %s" % (getattr(it, "blocked_reason", None) or ""))
    sup = getattr(it, "superseded_by", None)
    if sup and getattr(items.get(sup), "open", False):
        return (sup, "superseded by %s, still open" % sup)
    for oid, o in sorted(items.items()):
        if oid != iid and getattr(o, "open", False) and getattr(o, "caused_by", None) == iid and not waits_on_look(oid):
            return (oid, "its child %s is open" % oid)
    built_at = getattr(it, "built_at", None) or ""
    mine = named_defs(getattr(it, "title", ""), *[c.get("text") for c in getattr(it, "criteria", None) or []])
    for e in reversed(evs or []):
        if e.get("seat") != "OWNER" or e.get("event") not in ("note", "file"):
            continue
        at = _ts(e)
        if at is None or now - at > days * 86400:
            continue
        oid = e.get("id") or ""
        if oid == iid:
            if built_at and (e.get("ts") or "") > built_at and e.get("event") == "note":
                return (iid, "his note of %s postdates its build" % e["ts"][:10])
            continue
        o = items.get(oid)
        if o is None or not getattr(o, "open", False) or waits_on_look(oid):
            continue
        if same_family(oid, iid):
            return (oid, "his %s note on %s (same subject) is not built yet" % (e.get("ts", "")[:10], oid))
        shared = mine & named_defs(e.get("text"), getattr(o, "title", ""), *crit_texts(o)) if mine else None
        if shared:
            return (oid, "his %s note on %s (names %s) is not built yet" % (e.get("ts", "")[:10], oid, sorted(shared)[0]))
    return None


def route(it, question=""):
    """"sheet" for art (the review-sheet route with its prereview), else "save" (a review savegame). An owed look at the
    thing in place (a laid hose, in game) is a save whatever the art words say."""
    iid = getattr(it, "id", "") or ""
    look = " ".join([getattr(it, "title", "") or "", question or ""] + crit_texts(it))
    if IN_PLACE.search(look):
        return "save"
    return "sheet" if ART_ID.search(iid) or ART.search("%s %s" % (getattr(it, "title", "") or "", question or "")) else "save"


def item_sha(it):
    """The sha a showing is built at: the item's built sha, else the last sha its notes cite, else None."""
    return getattr(it, "built_sha", None) or ((getattr(it, "cited_shas", None) or [None])[-1])


def same_sha(a, b):
    """Two shas name one commit: full or abbreviated, never under 7 hex characters (a bare "a" names half the repo)."""
    ok = lambda x: isinstance(x, str) and re.fullmatch(r"[0-9a-f]{7,40}", x)   # noqa: E731
    return bool(ok(a) and ok(b)) and (a.startswith(b) or b.startswith(a))


def item_dir(item, root=None):
    return os.path.join(root or SHOW_DIR, item)


def win_dir(item):
    return "%s\\%s" % (SHOW_DIR_WIN, item)


def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            got = json.load(f)
        return got if isinstance(got, dict) else None
    except (OSError, ValueError):
        return None


def mods_fp(mods, root):
    """A fingerprint of the deployed copies of `mods` (folder names under the game's Mods): relpath, size, mtime of every
    file. A folder that is absent fingerprints as absent, which differs from any deployed one."""
    h = hashlib.sha1()
    for m in sorted({x for x in mods or [] if isinstance(x, str)}):
        d = os.path.join(root, m)
        h.update(("\0mod %s\n" % m).encode())
        if not os.path.isdir(d):
            h.update(b"absent\n")
            continue
        for base, dirs, files in os.walk(d):
            dirs.sort()
            for fn in sorted(files):
                p = os.path.join(base, fn)
                try:
                    s = os.stat(p)
                except OSError:
                    continue
                h.update(("%s %d %d\n" % (os.path.relpath(p, d), s.st_size, s.st_mtime_ns)).encode())
    return h.hexdigest()[:16]


def complete(man, saves=None, item=None):
    """Why the manifest is not a complete showing, or None. saves: the game's Saves folder, where a review save's
    <save>.rws must be (None: not checked)."""
    if not man:
        return "no %s" % MANIFEST
    if item is not None and man.get("item") != item:
        return "the manifest is %r's, not %s's" % (man.get("item"), item)
    if (man.get("route") or "save") not in ("save", "sheet"):
        return "route %r is neither save nor sheet" % man.get("route")
    if not isinstance(man.get("sha"), str) or not man["sha"].strip():
        return "no sha: a showing names the build it shows"
    st = man.get("stations") or []
    if not isinstance(st, list) or not st:
        return "no stations"
    for s in st:
        if not isinstance(s, dict) or not all(isinstance(s.get(k), (str, int)) and s.get(k) for k in ("n", "label", "shows", "judge", "capture")) \
                or not isinstance(s["capture"], str):
            return "station %s lacks one of n, label, shows, judge, capture" % (s.get("n") if isinstance(s, dict) else s)
        if man.get("_dir") and not os.path.isfile(os.path.join(man["_dir"], s["capture"])):
            return "station %s: capture %s not on disk" % (s["n"], s["capture"])
    ns = [str(x["n"]) for x in st]
    if len(set(ns)) != len(ns):
        return "station numbers repeat (%s): each needs its own judge note" % ", ".join(ns)
    if (man.get("route") or "save") == "save" and not (isinstance(man.get("save"), str) and man["save"]):
        return "no save name"
    if (man.get("route") or "save") == "save" and not (isinstance(man.get("mods"), list) and man["mods"]
                                                       and all(isinstance(x, str) and x for x in man["mods"])):
        return "no mods: a review save names the deployed mods it was built on, or nothing can say it went stale"
    if (man.get("route") or "save") == "save" and not man.get("deployed"):
        return "no deployed fingerprint: the builder records `relentless_showing.py fp <mods>` after its last deploy"
    if (man.get("route") or "save") == "save" and saves and not os.path.isfile(os.path.join(saves, "%s.rws" % man["save"])):
        return "save %s.rws is not in the game's Saves folder" % man["save"]
    if man.get("route") == "sheet" and not (isinstance(man.get("sheet"), str) and man["sheet"]
                                            and isinstance(man.get("prereview"), str) and man["prereview"]):
        return "the sheet route names no sheet and prereview"
    if man.get("route") == "sheet" and not (man["prereview"].startswith("/") and os.path.isfile(man["prereview"])):
        return "prereview %s is not a file on disk (a WSL path)" % man["prereview"]
    if man.get("route") == "sheet" and not (man["sheet"].startswith("/") and os.path.isfile(man["sheet"])):
        return "sheet %s is not a file on disk (a WSL path: a served url can change after the judge read it)" % man["sheet"]
    if not man.get("built_by"):
        return "no built_by"
    return None


def status(man, judge, sha, deployed_fp, judge_unit, saves=None, item=None):
    """-> (state, why). man: showing.json (with _dir), judge: judge.json, sha: the item's sha now, deployed_fp: mods_fp of
    the manifest's mods now, judge_unit: the unit the supervisor launched to judge it."""
    if not man:
        return OWED, "nothing built"
    if man.get("sha") is not None and not isinstance(man.get("sha"), str):
        return INCOMPLETE, "sha %r is not a string" % (man.get("sha"),)
    if not same_sha(man.get("sha"), sha) and (man.get("sha") or sha):
        return STALE, "built at %s, the item is at %s" % ((man.get("sha") or "?")[:10], (sha or "?")[:10])
    if man.get("deployed") and deployed_fp and man["deployed"] != deployed_fp:
        return STALE, "the deployed mod changed since the showing was built"
    gap = complete(man, saves, item)
    if gap:
        return INCOMPLETE, gap
    if not judge:
        return UNJUDGED, "no blind judge yet"
    if not judge_unit or judge.get("judged_by") != judge_unit or judge.get("judged_by") == man.get("built_by"):
        return UNJUDGED, "the judge on file is not the blind judge this supervisor launched"
    if not isinstance(judge.get("sha"), str) or not same_sha(judge["sha"], man.get("sha")):
        return STALE, "judged at another sha (or none)"
    if judge.get("verdict") != "pass":
        return FAILED, str(judge.get("why") or "the judge did not pass it")
    notes = judge.get("stations") if isinstance(judge.get("stations"), dict) else {}
    unread = [str(x["n"]) for x in man["stations"] if not str(notes.get(str(x["n"])) or "").strip()]
    if unread:
        return UNJUDGED, "the judge left station(s) %s without a note" % ", ".join(unread)
    return READY, "save %s" % man.get("save") if man.get("save") else "sheet %s" % man.get("sheet")


def stations(man):
    st = (man or {}).get("stations")
    return st if isinstance(st, list) else []


def minutes(man):
    m = (man or {}).get("minutes")
    return m if isinstance(m, (int, float)) and m > 0 else 2 + len(stations(man))


# ---------------------------------------------------------------- the briefs

def build_prompt(item, why, rt, sha, d, unit, question=""):
    win = win_dir(item)
    head = ["You are Relentless's SHOWING builder for %s (OWNER_REVIEW_BUILD_SHOWS_READY_BEFORE_ASKED). The owner, "
            "2026-11-05: \"For all the items waiting for human review, please have them pre-build anything needed for "
            "the live showing.\" This item waits only on his look (%s). What he will judge: %s" % (item, why, question or "(its ledger title)"),
            "Build its showing at sha %s. Write everything to %s (WSL %s). You build; you never judge your own work."
            % ((sha or "HEAD")[:12], win, d)]
    if rt == "sheet":
        body = ["Route: ART. Use the review-sheet route (skill rimworld-review-sheets): build the sheet with art_sheet.py "
                "and its prereview (skill rimworld-art-evaluation). No bridge, no game.",
                "Write %s/%s: {\"item\": \"%s\", \"sha\": \"<sha>\", \"route\": \"sheet\", \"sheet\": \"<the sheet's WSL path>\", "
                "\"prereview\": \"<WSL path>\", \"stations\": [{\"n\": 1, \"label\": \"...\", \"shows\": \"what it shows\", "
                "\"judge\": \"what he judges\", \"capture\": \"<file in this dir>\"}], \"minutes\": <to show it>, "
                "\"built_by\": \"%s\"}." % (d, MANIFEST, item, unit)]
    else:
        body = ["Route: REVIEW SAVEGAME. The supervisor holds the bridge for you as RELENTLESS: never `rimflow bridge take`/"
                "`release`. Deploy the item's mods (deploy_custom_mods.py --mod <m>, plan, then --apply) and restart on the "
                "smallest list that holds them (skills rimworld-deploy, rimworld-load-round, rimbridge, rimworld-live-review).",
                "Build ONE map: every station numbered and labelled, packed close, hostiles killed unless they are a "
                "station (memory review-maps-numbered-dense). Save it as Showing_%s. Take a zoomed capture of every "
                "station into %s (at most 1500 px a side)." % (item, d),
                "Write %s/%s: {\"item\": \"%s\", \"sha\": \"<sha you built>\", \"route\": \"save\", \"save\": \"Showing_%s\", "
                "\"mods\": [<game Mods folder names you deployed>], \"deployed\": \"<the output of `python3 "
                "src/RimMandrake/rimflow/relentless_showing.py fp <those folder names>` run after your last deploy>\", "
                "\"stations\": [{\"n\": 1, \"label\": \"...\", \"shows\": "
                "\"what it shows\", \"judge\": \"what he judges\", \"capture\": \"<file in this dir>\"}], \"minutes\": <to "
                "show it>, \"built_by\": \"%s\"}. Also stations.md: number -> what it shows -> what he judges."
                % (d, MANIFEST, item, item, unit)]
    tail = ["Never a flyer's flight, never a capture of one, never fullscreen or focus the game.",
            "No ledger writes, no commits. A blocker you cannot pass: write %s/blocked.txt with one line why, and exit." % d,
            "Never write judge.json. Exit when the manifest is written."]
    return "\n\n".join(head + body + tail)


def judge_prompt(item, d, unit):
    return "\n\n".join([
        "You are Relentless's BLIND showing judge for %s. You did not build it. Nothing reaches the owner unread." % item,
        "Read %s/%s. View EVERY station capture it names (crop to the subject, at most 1500 px a side). For each station "
        "judge: does the capture show what `shows` says, is it labelled with its number, and can the owner judge `judge` "
        "from it? Hostiles on the map that are not a station fail it." % (d, MANIFEST),
        "Write %s/%s: {\"judged_by\": \"%s\", \"sha\": \"<the manifest's sha>\", \"verdict\": \"pass\"|\"fail\", "
        "\"why\": \"<one line>\", \"stations\": {\"1\": \"<note>\", ...}}. Pass only when every station passes. No ledger "
        "writes, no game, no commits." % (d, JUDGE, unit)])


# ---------------------------------------------------------------- the supervisor's pass

def load_state(store):
    got = read_json(store.p(STATE)) or {}
    got.setdefault("rows", {})
    got.setdefault("items", {})
    return got


def save_state(store, s):
    store._write(store.p(STATE), json.dumps(s, indent=1, sort_keys=True))


def tick(store, fx, r, now, acts, sup):
    """One pass: settle ended runs, read every enrolled item's state, start at most one build and one judge.

    fx needs: showing_items() -> [(iid, item, why, question)], launch/alive/bridge_take/bridge_release, showing_clone()
    -> (clone path or None, why), and mods_root; bridge_reading and saves_root when it has them. sup: relentless
    (unit_name, run_desc, settle). Switched off, it only winds its own runs down."""
    c = cfg(r)
    if not hasattr(fx, "showing_items"):     # a test's bare fixture has no ledger to enrol from
        return None
    if not c["enabled"]:
        return _wind_down(store, fx, acts)
    s = load_state(store)
    rows, items = s["rows"], {}
    import relentless_live
    lr = relentless_live.live_rules(r)
    enrolled = fx.showing_items()
    live = {x[0] for x in enrolled}
    import relentless_jobs      # the Mods walk is a detached job's (RELENTLESS_SHRINK_TICK_SLOW_PHASES_DETACHED)
    fpr = relentless_jobs.ModsFp(store, getattr(fx, "mods_root", None), relentless_jobs.launcher(store, "mods_fp"))
    for iid in [k for k in rows if k not in live]:
        row = rows[iid]     # no longer waiting on his look: its run stops, its bridge goes back, its row goes
        if fx.alive(row.get("run")):
            fx.stop(row["run"], True)
            acts.append({"do": "showing_stopped", "item": iid, "why": "no longer waiting on his look"})
            continue        # settled on a later pass, once it is dead
        if row.get("bridge"):
            fx.bridge_release()
        rows.pop(iid)       # its files stay for the record
    for iid, it, why, q, blk in enrolled:
        row = rows.setdefault(iid, {"phase": None, "tries": 0, "enrolled": now, "why": why})
        d = item_dir(iid, getattr(fx, "show_root", None))
        run = row.get("run")
        rt = route(it, q)
        fly = flyer(it, q, lr) if rt == "save" else None
        if row.get("phase") == "build" and fx.alive(run):
            gone = _lost_bridge(fx, row)
            stop = fly or ("on %s: %s" % blk if blk else None) or gone
            if stop:    # a flyer, a new blocker or a lost bridge stops a running build now, not at its renewal
                fx.stop(run, True)
                acts.append({"do": "showing_stopped", "item": iid, "why": stop})
                items[iid] = {"state": HELD, "why": "stopping: %s" % stop, "dir": win_dir(iid)}
                if gone:
                    row["bridge"] = False
                row["tries"] = max(0, row.get("tries", 0) - 1)      # stopped, not failed: the try is given back
                continue
        if row.get("phase") in ("build", "judge") and run:
            if fx.alive(run) and now - run.get("at", now) < c["%s_max_s" % row["phase"]]:
                items[iid] = {"state": BUILDING if row["phase"] == "build" else JUDGING, "dir": win_dir(iid)}
                if row.get("bridge") and now - row.get("taken_at", now) >= c["renew_s"]:    # a hold with no event lapses
                    lost = fx.bridge_take("relentless showing %s (renew)" % iid)
                    if not lost:
                        row["taken_at"] = now
                    else:       # someone else holds it now (his OWNER hold, the Conductor): the build stops at once
                        fx.stop(run, True)
                        row["bridge"] = False
                        acts.append({"do": "showing_stopped", "item": iid, "why": "bridge: %s" % str(lost)})
                continue
            if fx.alive(run):
                fx.stop(run, True)
                continue
            if row["phase"] == "build" and row.get("bridge"):
                fx.bridge_release()
                row["bridge"] = False
            acts.append({"do": "showing_%s_ended" % row["phase"], "item": iid})
            if row["phase"] == "judge":
                unit = row.pop("judge_run_unit", None) or run.get("unit")
                if read_json(os.path.join(d, JUDGE)):
                    row["judged"] = unit
                else:       # a judge that wrote nothing is judged again, at most `tries` times
                    row["judge_tries"] = row.get("judge_tries", 0) + 1
            row["phase"], row["run"] = None, None
        man = read_json(os.path.join(d, MANIFEST))
        if man is not None:
            man["_dir"] = d
        jd = read_json(os.path.join(d, JUDGE))
        fp = fpr(man["mods"]) if man and isinstance(man.get("mods"), list) and man["mods"] else None
        sha_now = item_sha(it) or (row.get("built_sha") is None and (man or {}).get("sha")) or None
        state, swhy = status(man, jd, sha_now, fp, row.get("judged"), getattr(fx, "saves_root", None), iid)  # no ledger sha: the HEAD it was built at stands
        if state == READY and row.get("judge_digest") and row["judge_digest"] != digest(d, man, getattr(fx, "saves_root", None)):
            state, swhy = STALE, "the showing changed after its blind judge read it"
        if man and state not in (STALE, INCOMPLETE) and (man.get("route") or "save") != rt:
            state, swhy = STALE, "built for the %s route; its owed look now needs the %s route" % (man.get("route") or "save", rt)
        if fly:         # by rule, before any build: no flyer showing is staged without him
            state, swhy = JOINT, fly
        elif blk:       # never READY TO SHOW on a build his later word has not reached
            state, swhy = BLOCKED, "on %s: %s" % blk
        elif os.path.isfile(os.path.join(d, "blocked.txt")) and state != READY:
            state, swhy = HELD, open(os.path.join(d, "blocked.txt"), encoding="utf-8", errors="replace").read().strip()
        if state == STALE and (row.get("built_sha") != item_sha(it) or
                               ("route" in swhy and row.get("route_reset") != rt) or
                               ("deployed mod changed" in swhy and row.get("deploy_reset") != fp)):
            row["tries"] = 0         # a new build, a new deploy of its mod, or a new route earns new tries, once each
            row["deploy_reset"] = fp
            row["route_reset"] = rt
        if state not in (READY, HELD, JOINT, BLOCKED) and row["tries"] >= c["tries"] and state != UNJUDGED:
            state, swhy = HELD, "%d showing builds did not make it ready: %s" % (row["tries"], swhy)
        elif state == UNJUDGED and row.get("judge_tries", 0) >= c["tries"]:
            state, swhy = HELD, "%d blind judges wrote no verdict" % row["judge_tries"]
        if state == UNJUDGED and row.get("judged"):      # a judge.json not by its own blind judge: judged again
            row.pop("judged")
            row["judge_tries"] = row.get("judge_tries", 0) + 1
        row.update(state=state, why_state=swhy)
        items[iid] = {"state": state, "why": swhy, "blocked_on": blk[0] if blk else None, "dir": win_dir(iid), "save": (man or {}).get("save"),
                      "sheet": (man or {}).get("sheet"), "minutes": minutes(man) if man else None,
                      "stations": len(stations(man)), "route": rt}
    s["items"] = items
    try:
        why = fpr.close()
    except Exception as e:  # noqa: BLE001  no fresh answer asked for: the next pass walks inline what the cache lacks
        why = "%s: %s" % (type(e).__name__, e)
    if why:
        acts.append({"do": "error", "item": None, "why": "mods_fp job: %s" % str(why)})
    s["mods_fp"] = {"hits": fpr.hits, "inline": fpr.inline}
    _start(store, fx, r, c, s, enrolled, now, acts, sup)
    s["at"] = now
    save_state(store, s)
    return s


def _wind_down(store, fx, acts):
    """The stage switched off: no run of it outlives the switch. A live one is stopped, a dead one's bridge goes back."""
    if not os.path.isfile(store.p(STATE)):
        return None
    s = load_state(store)
    changed = False
    for iid, row in list(s["rows"].items()):
        if fx.alive(row.get("run")):
            fx.stop(row["run"], True)
            acts.append({"do": "showing_stopped", "item": iid, "why": "the showing stage is off"})
            continue
        if row.get("bridge"):
            fx.bridge_release()
        s["rows"].pop(iid)
        changed = True
    if changed:
        s["items"] = {k: v for k, v in s["items"].items() if k in s["rows"]}
        save_state(store, s)
    return None


def digest(d, man, saves=None):
    """What the judge read: the bytes of the manifest and of every capture (small files). A change after the pass voids
    it."""
    h = hashlib.sha1()
    local = [(man or {}).get(k) for k in ("sheet", "prereview")]
    local = [p for p in local if isinstance(p, str) and p.startswith("/")]     # the sheet route's own files, when local
    for fn in [MANIFEST] + [x["capture"] for x in stations(man) if isinstance(x, dict) and isinstance(x.get("capture"), str)] + local:
        h.update(("\0%s\n" % fn).encode())
        try:
            with open(os.path.join(d, fn), "rb") as f:
                h.update(f.read())
        except OSError:
            h.update(b"absent")
    sv = (man or {}).get("save")
    if saves and isinstance(sv, str) and sv:      # the save itself: megabytes, so its size and mtime
        try:
            st = os.stat(os.path.join(saves, "%s.rws" % sv))
            h.update(("\0save %d %d" % (st.st_size, st.st_mtime_ns)).encode())
        except OSError:
            h.update(b"\0save absent")
    return h.hexdigest()[:16]


def _start(store, fx, r, c, s, enrolled, now, acts, sup):
    rows = s["rows"]
    building = any(x.get("phase") == "build" for x in rows.values())  # one build at a time, of either route
    judging = any(x.get("phase") == "judge" for x in rows.values())
    by_id = {iid: (it, why, q) for iid, it, why, q, _blk in enrolled}
    for iid in sorted(by_id, key=lambda i: rows[i].get("enrolled", 0)):
        row, (it, why, q) = rows[iid], by_id[iid]
        if row.get("phase"):
            continue
        state = row.get("state")
        if state == UNJUDGED and not judging and not row.get("judged"):
            d = item_dir(iid, getattr(fx, "show_root", None))
            row["judge_digest"] = digest(d, read_json(os.path.join(d, MANIFEST)), getattr(fx, "saves_root", None))
            unit = sup.unit_name("showj", iid, row.get("tries", 0) * 10 + row.get("judge_tries", 0))
            judging = _launch(store, fx, r, c, s, row, iid, unit, "judge", judge_prompt(iid, item_dir(iid, getattr(fx, "show_root", None)), unit),
                              c["judge_agent"], c["judge_max_s"], now, acts, sup) or judging
            continue
        if state not in (OWED, STALE, INCOMPLETE, FAILED) or building or row.get("tries", 0) >= c["tries"]:
            if state in (OWED, STALE, INCOMPLETE, FAILED) and building:
                acts.append({"do": "showing_waits", "item": iid, "why": "another showing builds"})
            continue
        rt = route(it, q)
        if rt == "save":
            if relentless_game().other_active(store.states(), None):
                acts.append({"do": "showing_waits", "item": iid, "why": "a game phase holds the game"})
                building = True
                continue
            took = fx.bridge_take("relentless showing %s: review savegame for the owner's look" % iid)
            if took:        # an OWNER or Conductor hold refuses this take: nothing deploys or restarts under it
                acts.append({"do": "showing_waits", "item": iid, "why": "bridge: %s" % took})
                building = True
                continue
            row["bridge"], row["taken_at"] = True, now
        unit = sup.unit_name("show", iid, row.get("starts", row.get("tries", 0)))     # starts: a given-back try never reuses a unit name
        d = item_dir(iid, getattr(fx, "show_root", None))
        os.makedirs(d, exist_ok=True)
        for stale in (MANIFEST, JUDGE, "blocked.txt"):      # a rebuild starts clean: an old pass never reads ready
            try:
                os.remove(os.path.join(d, stale))
            except OSError:
                pass
        row.pop("judged", None)
        row["judge_tries"] = 0          # a new build earns its own blind judges
        row["built_sha"] = item_sha(it)
        ok = _launch(store, fx, r, c, s, row, iid, unit, "build", build_prompt(iid, why, rt, item_sha(it), d, unit, q),
                     c["builder_agent"], c["build_max_s"], now, acts, sup)
        if ok:
            row["tries"] = row.get("tries", 0) + 1
            row["starts"] = row.get("starts", row["tries"] - 1) + 1
            building = True
        elif row.get("bridge"):
            fx.bridge_release()
            row["bridge"] = False


def _launch(store, fx, r, c, s, row, iid, unit, phase, prompt, agent, max_s, now, acts, sup):
    clone, why = fx.showing_clone()
    if not clone:
        acts.append({"do": "showing_waits", "item": iid, "why": "clone: %s" % why})
        return False
    desc = sup.run_desc(store, r, unit, now)
    row.update(phase=phase, run=desc)
    if phase == "judge":
        row["judge_run_unit"] = unit
    save_state(store, s)        # the run is on disk before the unit exists
    why = fx.launch({"item": iid, "clone": clone, "gen": row.get("tries", 0)}, desc, prompt, agent, clone, max_s,
                    {"RELENTLESS_ROOT": store.root, "RELENTLESS_SHOWING": iid, "RELENTLESS_SHOWING_UNIT": unit})
    if why:
        row.update(phase=None, run=None)
        row.pop("judge_run_unit", None)
        acts.append({"do": "showing_launch_failed", "item": iid, "phase": phase, "why": why})
        return False
    acts.append({"do": "showing_%s" % phase, "item": iid, "unit": unit})
    s["items"].setdefault(iid, {"dir": win_dir(iid)})["state"] = BUILDING if phase == "build" else JUDGING
    return True


def _lost_bridge(fx, row):
    """-> why the bridge this build took is no longer Relentless's, or None. The ledger read each pass a build runs: an
    OWNER or Conductor take between renewals must stop it at once."""
    if not row.get("bridge") or not hasattr(fx, "bridge_reading"):
        return None
    holder = (fx.bridge_reading() or {}).get("holder")
    return None if holder == "RELENTLESS" else "bridge now held by %s" % (holder or "nobody")


def relentless_game():
    import relentless_game as g
    return g


def reading(root):
    """{item: {state, save, minutes, dir, ...}} from a Relentless root's showings.json; {} when absent."""
    got = read_json(os.path.join(root, "store", STATE)) if root else None
    return (got or {}).get("items") or {}


def main(argv):
    """`fp <Mods folder>...`: the deployed fingerprint a showing builder writes into its manifest."""
    if len(argv) < 2 or argv[0] != "fp":
        print("usage: relentless_showing.py fp <Mods folder name>...")
        return 2
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
    import game_paths
    print(mods_fp(argv[1:], game_paths.LOCAL_MODS))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))
