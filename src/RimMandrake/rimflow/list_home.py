#!/usr/bin/env python3
"""list_home.py: the kept list of old tickets by home. No model, no tokens. It launches, closes and drops nothing.

Item RIMMANDRAKE_GROUP_OLD_TICKETS_BY_HOME_AND_KEEP_THE_LIST_FOR_GOOD; page
design/specs/2026-11-23-old-tickets-by-home/boundary.md; selftest selftest_list_home.py. Why: the owner, 2026-11-23, wants
the old tickets grouped by mod, pipeline repair and other kinds once, and the list kept on the ledger.

    python3 src/RimMandrake/rimflow/list_home.py counts             each home with its count, and the no-home count
    python3 src/RimMandrake/rimflow/list_home.py list [--home HOME] each home, its groups, its tickets (one home: --home)
    python3 src/RimMandrake/rimflow/list_home.py no-home            the open list tickets that have no home
    python3 src/RimMandrake/rimflow/list_home.py json               the whole view, for a program
    python3 src/RimMandrake/rimflow/list_home.py offer [--by-mod]   the tickets the Workshop Pipeline may hand to a lane or
                                                                    to Codex: not parked (a block that holds, a dated
                                                                    wait ahead) and not one mod's work (mod_work.of); the
                                                                    rest are counted by mod (--by-mod: and listed)
    python3 src/RimMandrake/rimflow/list_home.py place [--apply]   the rule homes of the old tickets with no test and no
                                                                    home (rule_home); --apply writes them in one act
                                                                    (the lane's tick writes them too: list_dispatch)
    exit 0 read; 2 could not look (the ledger or the page's ticket set could not be read)

The write is `rimflow home <ID> --home H --group G --flag F [--reason R]`, or `rimflow home --from <rows.tsv>` (ID, HOME,
GROUP, FLAG, REASON, a tab between). A home is mod:<folder>, pipeline:<part>, game:<need>, machine:<name> or unplaced.
The set is the one the Maturation Pipeline page counts: open ledger items that are not mod work (maturation_nonmod).
"""
import argparse
import collections
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

KINDS = ("mod", "pipeline", "game", "machine", "fix")   # fix:<Mod>: a correction of a passed version that moves no bar (conductor_stops sort --to lane)
UNPLACED = "unplaced"
FLAGS = ("LOOKS CURRENT", "LOOKS OVERTAKEN", "CANNOT TELL")
CLOSED = ("done", "dropped", "superseded")
GROUP_RX = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NAME_RX = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
MOD_ROOTS = ("src/RimMandrake", "src/RimStarWars", "src/RimUtinni", "design/concepts")


def fields(home, group, flag, reason=None):
    """-> ({"home", "group", "flag", "reason"}, None) or (None, the fault and its repair)."""
    home, group, flag = (str(v or "").strip() for v in (home, group, flag))
    reason = " ".join(str(reason or "").split()) or None
    kind, _c, name = home.partition(":")
    if home != UNPLACED and (kind not in KINDS or not NAME_RX.match(name)):
        return None, ("the home %r is not mod:<folder>, pipeline:<part>, game:<need>, machine:<name>, fix:<mod folder> or unplaced "
                      "(a name has no spaces)" % home)
    if not GROUP_RX.match(group):
        return None, "the group %r is not a lower-case slug (for example pipe-art)" % group
    if flag not in FLAGS:
        return None, "the flag %r is not one of %s" % (flag, ", ".join(FLAGS))
    if flag == "LOOKS OVERTAKEN" and not reason:
        return None, "LOOKS OVERTAKEN needs a reason: the ruling, item or change that overtook it"
    if home == UNPLACED and not reason:
        return None, "unplaced needs a reason: why no home fits"
    return {"home": home, "group": group, "flag": flag, "reason": reason}, None


def read_rows(text, known):
    """rows-file text, known(id) -> bool -> ([(id, fields)], [faults])."""
    out, bad, seen = [], [], set()
    for n, ln in enumerate(text.splitlines(), 1):
        if not ln.strip() or ln.startswith("#"):
            continue
        f = [x.strip() for x in ln.split("\t")]
        if not 4 <= len(f) <= 5:
            bad.append("line %d: %d fields; ID, HOME, GROUP, FLAG, REASON with a tab between are wanted" % (n, len(f)))
            continue
        got, why = fields(f[1], f[2], f[3], f[4] if len(f) == 5 else None)
        if why:
            bad.append("line %d: %s: %s" % (n, f[0], why))
        elif f[0] in seen:
            bad.append("line %d: %s has two rows" % (n, f[0]))
        elif not known(f[0]):
            bad.append("line %d: %s has never been filed" % (n, f[0]))
        else:
            out.append((f[0], got))
        seen.add(f[0])
    return out, bad


def same(cur, new):
    return bool(cur) and all(cur.get(k) == new[k] for k in ("home", "group", "flag", "reason"))



# ---- homes by rule (the Conductor, 2026-11-26: design/specs/2026-11-26-testless-tickets/conductor_decisions.md, Q1) ----

RULE_FLAG = "CANNOT TELL"       # a rule placed it; nobody read the prose


def _own_home(it):
    h = (getattr(it, "home", None) or {}).get("home") if getattr(it, "home", None) else None
    return h if h and h != UNPLACED else None


# A fresh-reader ticket (fresh_reader.py) has no home and no cause, so the lane keyed it on its own id: a bundle of one
# by its form (measured 2026-11-26 and 27: 71 of the 73 `item:` bundles that ended were fresh-reader tickets). Its home
# is the area of the files it names, so the reads of one area fold into one bundle (work_bundle.read_fold). Item
# RIMMANDRAKE_FILL_BUNDLES_BY_HOME_HOLD_MEDIAN_ONE_TODAY; page design/specs/2026-11-24-work-bundles/boundary.md.
READ_AREAS = (("src/RimMandrake/rimflow/", "pipeline:read-rimflow"), ("src/RimMandrake/Utils/", "pipeline:read-utils"))
READ_OTHER = "pipeline:read-other"


def reader_home(it):
    """-> the home of a fresh-reader ticket by the area of its first file (READ_AREAS, else READ_OTHER), or None for any
    other ticket or a reader title that names no file. Pure."""
    import fresh_reader as FR
    t = it.get("title") if isinstance(it, dict) else getattr(it, "title", None)
    if not str(t or "").startswith(FR.PREFIX):
        return None
    paths = FR.parse_title(t)[0]
    if not paths:
        return None
    return next((h for pre, h in READ_AREAS if paths[0].startswith(pre)), READ_OTHER)


def rule_home(it, items, reading, words):
    """-> (home, group, reason) of a ticket with no home of its own, by the first rule that places it, or None.
    (1) the nearest ancestor in its chain of causes (caused_by) that has a real home: its mod by mod_work (reading),
    else its own home that is not unplaced; (2) the mod that its id or title names (list_dispatch.mod_of over `words`,
    the word rule of the lane's switches and holds). Pure over its inputs; a loop in the chain ends the walk."""
    seen = {getattr(it, "id", None)}
    pid, n = getattr(it, "caused_by", None), 0
    while pid and pid not in seen and pid in items:
        seen.add(pid)
        n += 1
        p = items[pid]
        r = reading(p)
        h = ("mod:%s" % r["mod"]) if isinstance(r, dict) and r.get("mod") else _own_home(p)
        if h:
            return h, "by-rule-cause", "by rule: the home of its cause %s, %d hop(s) up its chain of causes" % (pid, n)
        pid = getattr(p, "caused_by", None)
    import list_dispatch as LD
    m = LD.mod_of(getattr(it, "id", None), getattr(it, "title", None), words)
    if m:
        return ("mod:%s" % m, "by-rule-name", "by rule: its id or title names the mod %s (list_dispatch.mod_of, the word "
                "rule of the lane's switches and holds)" % m)
    return None


def place_rows(items, reading, words, before):
    """-> [(id, fields)] of the rule homes: each open ticket with no home of its own (unplaced counts as one), no test
    (list_shape.needs_shape_run), filed before `before` (shape_from, an epoch), and not one mod's work, that rule_home
    places. A ticket whose mod reading could not be made is never a row."""
    import list_shape as LS
    out = []
    for i in sorted(items):
        x = items[i]
        if getattr(x, "state", None) in CLOSED or getattr(x, "home", None):
            continue
        sf = LS.facts(x)
        if not LS.needs_shape_run(sf) or sf.get("filed") is None or sf["filed"] >= before:
            continue
        r = reading(x)
        if not isinstance(r, dict) or r.get("unreadable") or r.get("mod"):
            continue
        got = rule_home(x, items, reading, words)
        if got:
            f, _why = fields(got[0], got[1], RULE_FLAG, got[2])
            if f:
                out.append((i, f))
    return out


def write_rows(rows, why, publish=True, tmpdir=None, runner=None):
    """Write `rows` ([(id, fields)]) in one `rimflow home --from` act. -> (rc, output); rc 0 written, 4 written and not
    landed yet (ledger_landing), else refused."""
    import subprocess
    import tempfile
    if not rows:
        return 0, "home: no row"
    if tmpdir is None:
        import list_dispatch as LD
        tmpdir = LD.sdir()
    fd, path = tempfile.mkstemp(prefix="rule_homes_", suffix=".tsv", dir=tmpdir)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        for i, h in rows:
            f.write("\t".join([i, h["home"], h["group"], h["flag"], h.get("reason") or ""]) + "\n")
    argv = [sys.executable, os.path.join(HERE, "cli.py"), "home", "--from", path, "--seat", "BENCH", "--why", why]
    if publish:
        argv.append("--publish")
    env = dict(os.environ, RIMFLOW_SEAT="BENCH")
    for k in ("CLAUDE_SESSION_ID", "CLAUDE_CODE_SESSION_ID"):
        env.pop(k, None)
    try:
        import time_budget
        r = (runner or subprocess.run)(argv, cwd=REPO, env=env, capture_output=True, text=True,
                                       timeout=time_budget.RIMFLOW_S, stdin=subprocess.DEVNULL, errors="replace")
        return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return 99, "%s: %s" % (type(e).__name__, e)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


PLACE_WHY = ("pipeline act: homes by rule for old tickets with no test and no home (the Conductor's decision of "
             "2026-11-26, design/specs/2026-11-26-testless-tickets/conductor_decisions.md question 1; list_home.rule_home)")


def place_main(apply=False, before=None, words=None, reading=None, publish=True):
    """-> the count of homes written (0 for a dry run). Prints each row."""
    import model as LM
    import list_dispatch as LD
    import list_shape as LS
    if before is None:
        frm = LD.load_cfg().get("shape_from")
        if not frm:
            print("no shape_from in list_dispatch.json: no ticket is old, so none is placed")
            return 0
        before = LS._epoch(frm)
    if words is None:
        words = LD._mods()
    if reading is None:
        import mod_work as MW
        modset = MW.mods()
        reading = lambda it: MW.reading(it, modset, LM.ITEMS)  # noqa: E731
    w = LM.replay()
    rows = place_rows(w.items, reading, words, before)
    for i, h in rows:
        print("%s\t%s\t%s" % (i, h["home"], h["reason"]))
    print("place: %d rule home(s)%s" % (len(rows), "" if apply else " (dry run: --apply writes them)"))
    if not apply or not rows:
        return 0
    rc, out = write_rows(rows, PLACE_WHY, publish=publish)
    print(out)
    if rc not in (0, 4):
        raise RuntimeError("rimflow home --from refused (exit %d): %s" % (rc, out))
    return len(rows)

# ---- the view -------------------------------------------------------------------------------------------------------

def open_homes(items, ids):
    """-> {id: home dict or None} of the ids that are open."""
    return {i: items[i].home for i in ids if items[i].state not in CLOSED}


def view(homes):
    """{id: home dict or None} -> {"total", "homes": {home: {"count", "flags", "groups": {group: [ids]}}}, "no_home"}."""
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    flags = collections.defaultdict(collections.Counter)
    for i, h in sorted(homes.items()):
        if h:
            by[h["home"]][h["group"]].append(i)
            flags[h["home"]][h["flag"]] += 1
    out = {}
    for h in sorted(by, key=lambda h: (h.partition(":")[0], -sum(map(len, by[h].values())), h)):
        g = by[h]
        out[h] = {"count": sum(map(len, g.values())), "flags": dict(flags[h]),
                  "groups": {k: g[k] for k in sorted(g, key=lambda k: (-len(g[k]), k))}}
    return {"total": len(homes), "homes": out, "no_home": sorted(i for i, h in homes.items() if not h)}


def planned_mod(name):
    return not any(os.path.isdir(os.path.join(REPO, r, name)) for r in MOD_ROOTS)


def _flags(f):
    return ", ".join("%s %d" % (k.lower(), f[k]) for k in FLAGS if f.get(k))


def lines(v, planned=planned_mod, only=None, tickets=True, info=None):
    info = info or {}
    out = []
    for h, d in v["homes"].items():
        if only and h != only:
            continue
        kind, _c, name = h.partition(":")
        out.append("%s%s: %d (%s)" % (h, " [planned: no folder of this name]" if kind == "mod" and planned(name) else "",
                                      d["count"], _flags(d["flags"])))
        if tickets:
            for g, ids in d["groups"].items():
                out.append("    %s: %d" % (g, len(ids)))
                out += ["        %s%s" % (i, info.get(i, "")) for i in ids]
    if not only:
        kinds = collections.Counter()
        for h, d in v["homes"].items():
            kinds[h.partition(":")[0]] += d["count"]
        out.append("total open list tickets: %d; %s; no home: %d" % (
            v["total"], ", ".join("%s %d" % kv for kv in sorted(kinds.items())), len(v["no_home"])))
        if tickets:
            out += ["    no home: %s" % i for i in v["no_home"]]
    return out


def read():
    """-> ({id: home or None}, {id: item}) of the open list tickets. Raises when it could not look."""
    import list_pipeline as LP
    import maturation_nonmod as N
    import maturation_now as MN
    croot = os.path.join(REPO, "design", "concepts")
    mods = [f for f in sorted(os.listdir(croot)) if not f.startswith("_") and os.path.isdir(os.path.join(croot, f))
            and (os.path.exists(os.path.join(croot, f, "version", "VERSION.json"))
                 or MN.read_json(os.path.join(croot, f, "stage.json"))[0] is not None)]
    stores = N.read_stores(MN.live_facts(mods), mods)
    if stores["items"] is None:
        raise RuntimeError("the ledger could not be read (%s)" % stores["causes"])
    sec = N.section(stores, time.time(), spend=MN.read_spend, stage=LP.stage_of)
    return open_homes(stores["items"], list(sec["stage_of"])), stores["items"]


class _World(object):
    """The one field priority.block_holds reads of a world: its items."""
    def __init__(self, items):
        self.items = items


def parked(items, it, now):
    """-> why `it` is parked (a block that holds, or a dated wait still ahead), else None. A parked ticket goes to no lane
    and to no Codex run: list_dispatch.py reads the same block and wait and launches nothing on it."""
    import model as LM
    e = LM.iso_epoch(it.wait_until) if getattr(it, "wait_until", None) else None
    if e is not None and e > now:
        return "waits until %s: %s" % (it.wait_until, it.wait_reason or "no reason given")
    if getattr(it, "blocked", None):
        up = os.path.dirname(HERE)
        if up not in sys.path:
            sys.path.insert(0, up)          # priority imports only as rimflow.priority
        from rimflow import priority as PR
        if PR.block_holds(_World(items), it, now):
            return "blocked: %s" % PR.block_line(it)
    return None


def offer(items, ids, modset, reading=None, now=None):
    """-> {"offer": [ids], "mods": {mod: [ids]}, "parked": {id: why}, "blind": {id: cause}} over the open list tickets
    `ids`. A parked ticket (a block that holds, a dated wait ahead) is not offered; a ticket that is one mod's work waits
    for that mod's Maturation Pipeline run; a ticket whose home cannot be read is not offered."""
    import mod_work as MW
    reading = reading or (lambda it: MW.reading(it, modset))
    now = time.time() if now is None else now
    out = {"offer": [], "mods": collections.defaultdict(list), "parked": {}, "blind": {}}
    for i in sorted(ids):
        it = items[i]
        if it.state in CLOSED:
            continue
        why = parked(items, it, now)
        if why:
            out["parked"][i] = why
            continue
        r = reading(it)
        if r.get("unreadable"):
            out["blind"][i] = r["unreadable"]
        elif r.get("mod"):
            out["mods"][r["mod"]].append(i)
        else:
            out["offer"].append(i)
    out["mods"] = dict(out["mods"])
    return out


def offer_lines(o, items, by_mod=False):
    out = ["offered to a lane or to Codex: %d open list tickets (not one mod's work)" % len(o["offer"])]
    for i in o["offer"]:
        out.append("    %s  [%s]  %s" % (i, "check" if items[i].effect else "no check",
                                         " ".join(str(items[i].title or "").split())[:100]))  # cut-ok: terminal display
    n = sum(map(len, o["mods"].values()))
    out.append("kept off, each waits for its mod's Maturation Pipeline run: %d, in %d mods" % (n, len(o["mods"])))
    for m in sorted(o["mods"], key=lambda m: (-len(o["mods"][m]), m)):
        out.append("    %-28s %d" % (m, len(o["mods"][m])))
        if by_mod:
            out += ["        %s" % i for i in o["mods"][m]]
    out.append("parked, not offered (a block that holds or a dated wait ahead): %d" % len(o.get("parked") or {}))
    out += ["    %s: %s" % (i, " ".join(str(w).split())[:160]) for i, w in sorted((o.get("parked") or {}).items())]  # cut-ok: terminal display
    out.append("could not look, not offered: %d" % len(o["blind"]))
    out += ["    %s: %s" % kv for kv in sorted(o["blind"].items())]
    return out


def main(argv=None, read=read):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("counts")
    s = sub.add_parser("list")
    s.add_argument("--home", help="one home, for example mod:FlowWorks")
    sub.add_parser("no-home")
    sub.add_parser("json")
    s = sub.add_parser("offer")
    s.add_argument("--by-mod", action="store_true", help="list the kept-off tickets under each mod")
    s = sub.add_parser("place")
    s.add_argument("--apply", action="store_true", help="write the rule homes (one rimflow home --from act, published)")
    o = ap.parse_args(argv)
    if o.cmd == "place":
        try:
            place_main(apply=o.apply)
        except Exception as e:  # noqa: BLE001 - could not look is never "nothing to place"
            print("UNMEASURED: the rule homes could not be made or written (%s: %s)" % (type(e).__name__, e))
            return 2
        return 0
    try:
        homes, items = read()
    except Exception as e:  # noqa: BLE001 - could not look is never an empty list
        print("UNMEASURED: the list could not be read (%s: %s)" % (type(e).__name__, e))
        return 2
    v = view(homes)
    if o.cmd == "offer":
        import mod_work as MW
        try:
            modset = MW.mods()
        except Exception as e:  # noqa: BLE001 - could not look is never an empty offer
            print("UNMEASURED: the mod folders could not be read (%s: %s)" % (type(e).__name__, e))
            return 2
        print("\n".join(offer_lines(offer(items, list(homes), modset), items, o.by_mod)))
        return 0
    if o.cmd == "json":
        print(json.dumps(dict(v, tickets={i: h for i, h in homes.items() if h}), indent=1))
    elif o.cmd == "no-home":
        print("no home: %d of %d open list tickets" % (len(v["no_home"]), v["total"]))
        for i in v["no_home"]:
            print("    " + i)
    elif o.cmd == "counts":
        print("\n".join(lines(v, tickets=False)))
    else:
        info = {i: "  [%s%s] %s" % (h["flag"].lower(), ": " + h["reason"] if h["reason"] else "",
                                    " ".join(str(items[i].title or "").split())[:110]) for i, h in homes.items() if h}  # cut-ok: terminal display
        if o.home and o.home not in v["homes"]:
            print("no open ticket has the home %s (%d homes read)" % (o.home, len(v["homes"])))
            return 0
        print("\n".join(lines(v, only=o.home, info=info)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
