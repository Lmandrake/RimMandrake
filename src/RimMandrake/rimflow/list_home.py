#!/usr/bin/env python3
"""list_home.py: the kept list of old tickets by home. No model, no tokens. It launches, closes and drops nothing.

Item RIMMANDRAKE_GROUP_OLD_TICKETS_BY_HOME_AND_KEEP_THE_LIST_FOR_GOOD; page
design/specs/2026-11-23-old-tickets-by-home/boundary.md; selftest selftest_list_home.py. Why: the owner, 2026-11-23, wants
the old tickets grouped by mod, pipeline repair and other kinds once, and the list kept on the ledger.

    python3 src/RimMandrake/rimflow/list_home.py counts             each home with its count, and the no-home count
    python3 src/RimMandrake/rimflow/list_home.py list [--home HOME] each home, its groups, its tickets (one home: --home)
    python3 src/RimMandrake/rimflow/list_home.py no-home            the open list tickets that have no home
    python3 src/RimMandrake/rimflow/list_home.py json               the whole view, for a program
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

KINDS = ("mod", "pipeline", "game", "machine")
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
        return None, ("the home %r is not mod:<folder>, pipeline:<part>, game:<need>, machine:<name> or unplaced "
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


def main(argv=None, read=read):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("counts")
    s = sub.add_parser("list")
    s.add_argument("--home", help="one home, for example mod:FlowWorks")
    sub.add_parser("no-home")
    sub.add_parser("json")
    o = ap.parse_args(argv)
    try:
        homes, items = read()
    except Exception as e:  # noqa: BLE001 - could not look is never an empty list
        print("UNMEASURED: the list could not be read (%s: %s)" % (type(e).__name__, e))
        return 2
    v = view(homes)
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
