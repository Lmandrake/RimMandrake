#!/usr/bin/env python3
"""fleet_mods.py — the slow half of the owner's Fleet Watch board: receipts, mods worked on lately, the factory line.

FLEETWATCH_PAGE_SHRINK_LESS_BASH_MORE_MODS (owner, by card 2026-11-02): "there should be a lower section that has a
list of all Mods worked on in the past week or so and where they stand. What was done? Each task that contributed to
that mod (one line)." Everything here is computed in Python so the page stays dumb; fleet_refresh.py writes it.

  receipts(...)  one row per item finished today (local day): ✓/✗, the blind check's verdict, one plain sentence of
                 what changed (its main commit's subject), real commit count (ledger-only commits excluded), tokens.
  mods(...)      one doc per mod touched in the last 7 days, grouped by the paths the commits changed under src/
                 (src/<Tier>/<Mod>/...; tooling folders and paths outside src/ -> "Infrastructure & tooling"):
                 closed/open/parked counts, proof state (modcheck record and the last blind check), what is next and
                 what waits on the owner or the game, one line per contributing task.
  factory(...)   the header line: factory ok or not, N/target workers, tokens today.

Inputs (read-only): `git log origin/main --since=7.days --name-only` (one call), the rimflow ledger (model.read),
the Relentless store (~/rm/relentless/store), infrastructure/state/modcheck_status.json, src/*/*/About/About.xml.

    python3 src/RimMandrake/Utils/fleet_mods.py [--days 7]      # prints {"factory":…, "receipts":[…], "mods":[…]}
"""
import argparse
import calendar
import glob
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fleet_watch  # noqa: E402

REPO = fleet_watch.REPO
STORE = os.path.expanduser("~/rm/relentless/store")
MODCHECK = os.path.join(REPO, "infrastructure", "state", "modcheck_status.json")
DAYS = 7
INFRA = "_infra"
INFRA_NAME = "Infrastructure & tooling"
# folders under src/<Tier>/ that are tooling, not a mod the player loads
TOOLING = {"Utils", "rimflow", "_Shared", "arena", "bridgetools", "contracts", "mapsynth", "art_bench", "ideoligion"}
MARKS = re.compile(r"^(?:review marks?|clean marks?|mark\b|marks\b|lesson\b|ledger\b|rebase\b)", re.I)
CLOSED_STATES = ("done",)


# ---------------------------------------------------------------- pure helpers (selftest_fleet_mods.py) ----------
def parse_log(text):
    """`git log --format=@@%H%x09%ct%x09%s --name-only` -> [{sha, at, subject, files}] newest first."""
    out, cur = [], None
    for line in text.splitlines():
        if line.startswith("@@"):
            parts = line[2:].split("\t", 2)
            if len(parts) < 3:
                cur = None
                continue
            cur = {"sha": parts[0], "at": int(parts[1] or 0), "subject": parts[2], "files": []}
            out.append(cur)
        elif line.strip() and cur is not None:
            cur["files"].append(line.strip())
    return out


def real_files(files):
    return [f for f in files if not fleet_watch.LEDGER_ONLY.match(f)]


def mod_of_path(path, mods):
    """'src/RimMandrake/Stillsand/Defs/x.xml' -> 'Stillsand' when Stillsand is a mod folder; design/<Tier>/<Mod>/... too.
    Anything else -> None (infrastructure)."""
    p = path.split("/")
    if len(p) >= 4 and p[0] in ("src", "design") and p[2] in mods:
        return p[2]
    return None


def item_ids(subject, known):
    """Item ids named in a commit subject that the ledger knows."""
    return [t for t in dict.fromkeys(re.findall(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b", subject)) if t in known]


def mod_by_name(item, mods_upper):
    """An item id whose leading segments spell a mod folder (LEANINGSCRUB_STALL_1 -> LeaningScrub; longest wins)."""
    segs = item.split("_")
    best = None
    for k in range(1, len(segs)):
        name = "".join(segs[:k])
        if name in mods_upper:
            best = mods_upper[name]
    return best


def plain_subject(subject):
    """'ITEM_X: exact-step speed proof + engine-law test' -> 'Exact-step speed proof + engine-law test.'"""
    s = re.sub(r"^(?:[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+[,:]?\s*)+", "", subject).strip()
    s = re.sub(r"\b[0-9a-f]{7,40}\b", "", s)
    s = s.lstrip("+-*· ").strip()
    s = fleet_watch.de_id(" ".join(s.split())).strip(" ;,")
    if not s:
        return ""
    s = s[0].upper() + s[1:]
    s = fleet_watch.short(s, 120)
    return s if s.endswith(("…", ".", "!", "?", ")")) else s + "."


def outcome(commits_of_item):
    """The item's main commit (most real files, not a review/lesson mark) as one plain sentence; "" if none."""
    best = None
    for c in commits_of_item:
        n = len(real_files(c["files"]))
        if not n or MARKS.match(re.sub(r"^[A-Z0-9_]+[:,]\s*", "", c["subject"])):
            continue
        if best is None or n > best[0]:
            best = (n, c)
    return plain_subject(best[1]["subject"]) if best else ""


def day_label(at):
    return time.strftime("%-d %b", time.localtime(at)) if at else ""


def local_midnight(now):
    t = time.localtime(now)
    return int(time.mktime((t.tm_year, t.tm_mon, t.tm_mday, 0, 0, 0, 0, 0, -1)))


# ---------------------------------------------------------------- inputs --------------------------------------------
def mod_folders():
    """{folder: display name} for every src/<Tier>/<Mod>/ that is not tooling; a display name two folders share gets
    its tier added."""
    out, tier = {}, {}
    for d in sorted(glob.glob(os.path.join(REPO, "src", "*", "*", ""))):
        name = os.path.basename(d.rstrip("/"))
        if name in TOOLING or name.startswith(".") or not os.path.isdir(d):
            continue
        disp = name
        try:
            with open(os.path.join(d, "About", "About.xml"), encoding="utf-8", errors="replace") as f:
                m = re.search(r"<name>([^<]+)</name>", f.read())
            if m:
                disp = re.sub(r"^(?:RimMandrake|RimUtinni|RimStarWars|Jawa)\s*:\s*", "", m.group(1).strip())
        except OSError:
            if not glob.glob(os.path.join(d, "*")):
                continue
        out[name] = disp[:1].upper() + disp[1:]
        tier[name] = os.path.basename(os.path.dirname(d.rstrip("/")))
    seen = {}
    for k, v in out.items():
        seen.setdefault(v, []).append(k)
    for v, ks in seen.items():
        if len(ks) > 1:
            for k in ks:
                out[k] = "%s (%s)" % (v, tier[k])
    return out


def git_log(days):
    return fleet_watch.sh("git", "log", "origin/main", "--since=%d.days" % days, "--format=@@%H%x09%ct%x09%s",
                          "--name-only")


def ledger():
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
    import model  # noqa: E402
    evs = model.read()
    return evs, model.replay(evs)


def relentless_states():
    out = {}
    for p in glob.glob(os.path.join(STORE, "items", "*", "state.json")):
        try:
            with open(p) as f:
                s = json.load(f)
        except (OSError, ValueError):
            continue
        out[s.get("item") or os.path.basename(os.path.dirname(p))] = s
    return out


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def close_at(item, evs):
    """Epoch of the item's last close event, or None."""
    for i in reversed(item.history or []):
        e = evs[i] if 0 <= i < len(evs) else {}
        if e.get("event") == "close":
            return _epoch(e.get("ts"))
    return None


def _epoch(ts):
    try:
        return int(calendar.timegm(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")))
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- derivations ---------------------------------------
def verdict_of(rs):
    c = (rs or {}).get("check")
    return c.get("verdict") if isinstance(c, dict) else None


def receipts(now, commits_by_item, rel, world, evs, detached_done=()):
    """Rows (status Done/Ended) for items finished since local midnight: Relentless done_at today, plus finished
    detached helper rows passed in. Each carries a `receipt` the page renders without thinking."""
    since = local_midnight(now)
    out = {}
    for item, s in rel.items():
        if s.get("status") != "done" or (s.get("done_at") or 0) < since:
            continue
        v = verdict_of(s)
        out[item] = {"item": item, "status": "Done", "glyph": "✓" if v != "FAIL" else "✗",
                     "finished_at": int(s["done_at"]), "started": int(s.get("enrolled_at") or s["done_at"]),
                     "relentless": True, "ga": "g%s·a%s" % (s.get("gen"), s.get("attempts")),
                     "receipt": {"ok": v != "FAIL", "check": v,
                                 "outcome": outcome(commits_by_item.get(item, [])),
                                 "commits": sum(1 for c in commits_by_item.get(item, []) if real_files(c["files"])),
                                 "tokens": s.get("spent") or None}}
    for r in detached_done:
        if r["item"] in out or (r.get("finished_at") or 0) < since:
            continue
        it = world.items.get(r["item"])
        runs = [x for x in (getattr(it, "runs", None) or []) if "blind-check" in str(getattr(x, "config", ""))]
        v = {"pass": "PASS", "fail": "FAIL"}.get(str(getattr(runs[-1], "result", "")).lower()) if runs else None
        ok = r["status"] == "Done" and v != "FAIL"
        out[r["item"]] = dict(r, glyph="✓" if ok else "✗", receipt={
            "ok": ok, "check": v, "outcome": outcome(commits_by_item.get(r["item"], [])),
            "commits": r.get("commit_count") or 0, "tokens": r.get("tokens")})
    return sorted(out.values(), key=lambda r: -r["finished_at"])


def attribute(log, known, mods):
    """-> (by_item {item: [commit]}, item_mods {item: set(mod or INFRA)}, mod_last {mod: epoch}, item_last)"""
    by_item, item_mods, mod_last, item_last = {}, {}, {}, {}
    for c in log:
        files = real_files(c["files"])
        if not files:
            continue
        touched = {mod_of_path(f, mods) or INFRA for f in files}
        for m in touched:
            mod_last[m] = max(mod_last.get(m, 0), c["at"])
        for i in item_ids(c["subject"], known):
            by_item.setdefault(i, []).append(c)
            item_mods.setdefault(i, set()).update(touched)
            item_last[i] = max(item_last.get(i, 0), c["at"])
    for i, ms in item_mods.items():  # an item that touched a mod is that mod's, not also infra's
        if len(ms) > 1:
            ms.discard(INFRA)
    return by_item, item_mods, mod_last, item_last


PARKED_REL = ("held", "blocked", "retired")
NEXT_REL = ("running", "candidate", "game", "queued")


def task_mark(it, rs):
    if it is not None and it.state in CLOSED_STATES:
        return "✓"
    if parked(it, rs):
        return "⏸"
    return "○"


def parked(it, rs):
    return bool(it is not None and (getattr(it, "held", False) or getattr(it, "blocked", False))) or \
        (rs or {}).get("status") in PARKED_REL


def waits_on(it, rs):
    """'you' / 'the game' / '' for an open item."""
    if it is None:
        return ""
    if it.needs == "owner" or getattr(it, "blocked_kind", None) == "owner" or (rs or {}).get("hold") == "owner":
        return "you"
    if (rs or {}).get("status") == "game" or getattr(it, "blocked_kind", None) == "live":
        return "the game"
    return ""


def proof_line(mod, mc, blind, now, days):
    """'blind check PASS 2 Nov · modcheck not run in 7d' — both instruments, each with its date."""
    parts = []
    if blind:
        parts.append("blind check %s %s" % (blind[1], day_label(blind[0])))
    e = mc.get(mod)
    if e and now - (e.get("ts") or 0) <= days * 86400:
        parts.append("modcheck %s %s" % (e.get("status"), day_label(e["ts"])))
    else:
        parts.append("modcheck not run in %dd" % days)
    return " · ".join(parts)


def mods(now, log, world, evs, rel, mc, folders, days=DAYS):
    """One doc per mod (plus the infra block) touched in the window, newest activity first."""
    known = world.items
    by_item, item_mods, mod_last, item_last = attribute(log, known, folders)
    upper = {k.upper(): k for k in folders}
    window = now - days * 86400
    groups = {}
    for i, ms in item_mods.items():
        for m in ms:
            groups.setdefault(m, set()).add(i)
    # open items named for a mod count toward it even with no commit yet (they are its queue)
    named_open = {}
    for iid, it in known.items():
        if not it.open:
            continue
        m = mod_by_name(iid, upper)
        if m and m in mod_last:
            named_open.setdefault(m, set()).add(iid)
    docs = []
    for m, last in mod_last.items():
        if last < window:
            continue
        items = groups.get(m, set())
        closed_week = [i for i in items if known[i].state in CLOSED_STATES and (close_at(known[i], evs) or 0) >= window]
        open_all = {i for i in items | named_open.get(m, set()) if known[i].open}
        parked_n = [i for i in open_all if parked(known[i], rel.get(i))]
        open_n = len(open_all) - len(parked_n)
        blind = None
        for i in items:
            s = rel.get(i) or {}
            c = s.get("check") if isinstance(s.get("check"), dict) else None
            if c and c.get("verdict") and (c.get("verdict_at") or c.get("at") or 0) >= window:
                at = int(c.get("verdict_at") or c.get("at"))
                if blind is None or at > blind[0]:
                    blind = (at, c["verdict"])
        nxt, waits = "", []
        cand = sorted(open_all, key=lambda i: (len(item_mods.get(i, ())) > 3,
                                               NEXT_REL.index(rel[i]["status"]) if rel.get(i, {}).get("status") in NEXT_REL
                                               else 9, {"doing": 0, "built": 1, "validated": 1, "ready": 2}.get(known[i].state, 3),
                                               -(item_last.get(i) or 0), i))
        for i in cand:
            if not parked(known[i], rel.get(i)):
                nxt = fleet_watch.title_short(known[i].title or i, 48)
                break
        for i in cand:
            w = waits_on(known[i], rel.get(i))
            if w:
                waits.append("waits on %s: %s" % (w, fleet_watch.title_short(known[i].title or i, 40)))
        tasks = []
        for i in sorted(items, key=lambda i: -(item_last.get(i) or 0)):
            it = known[i]
            tasks.append({"mark": task_mark(it, rel.get(i)), "title": fleet_watch.title_short(it.title or i, 48),
                          "date": day_label(close_at(it, evs) if it.state in CLOSED_STATES else item_last.get(i))})
        name = INFRA_NAME if m == INFRA else folders.get(m, m)
        docs.append({"id": m, "name": name, "infra": m == INFRA, "last_at": int(last),
                     "closed": len(closed_week), "open": open_n, "parked": len(parked_n),
                     "counts": "%d closed this week · %d open · %d parked" % (len(closed_week), open_n, len(parked_n)),
                     "proof": "" if m == INFRA else proof_line(m, mc, blind, now, days),
                     "next": nxt, "waits": waits[:3], "tasks": tasks[:25], "more": max(0, len(tasks) - 25)})
    docs.sort(key=lambda d: (d["infra"], -d["last_at"]))
    for n, d in enumerate(docs):
        d["order"] = n
    return docs


def factory(now, store=STORE):
    """Header facts: factory ok or the plain reason it is not, running/target workers, Relentless tokens today (UTC)."""
    st = load_json(os.path.join(store, "staffing.json"), {})
    br = load_json(os.path.join(store, "breaker.json"), {})
    integ = load_json(os.path.join(store, "integrity.json"), {})
    why = ""
    if not st:
        why = "no staffing reading"
    elif now - (st.get("t") or 0) > 15 * 60:
        why = "silent %dm" % int((now - (st.get("t") or 0)) / 60)
    elif (br.get("until") or 0) > now:
        why = "paused after repeated failures"
    elif integ.get("blocked"):
        why = "blocked by a damage check"
    elif st.get("alarmed"):
        why = "alarm raised"
    return {"ok": not why, "why": why, "running": st.get("running"), "target": st.get("target"),
            "tokens_today": st.get("spent_today"), "at": int(now)}


def gather(now, days=DAYS, detached_done=()):
    log = parse_log(git_log(days))
    evs, world = ledger()
    rel = relentless_states()
    mc = load_json(MODCHECK, {})
    folders = mod_folders()
    by_item = attribute(log, world.items, folders)[0]
    for r in detached_done:
        it = world.items.get(r["item"])
        if it is not None:
            r.setdefault("title", it.title)
    rec = receipts(now, by_item, rel, world, evs, detached_done)
    for r in rec:
        it = world.items.get(r["item"])
        r.setdefault("title", (it.title if it else "") or r["item"])
    return {"factory": factory(now), "receipts": rec, "mods": mods(now, log, world, evs, rel, mc, folders, days)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=DAYS)
    a = ap.parse_args()
    print(json.dumps(gather(int(time.time()), a.days), indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
