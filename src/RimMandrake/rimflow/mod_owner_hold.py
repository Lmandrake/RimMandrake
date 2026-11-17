#!/usr/bin/env python3
"""The owner's hold on mods in the Maturation Pipeline (item RIMMANDRAKE_HOLD_SIX_BIOME_MODS_ONLY_PYRELANDS_STAYS).

The owner, 2026-11-16 ~5:20 PM PST: "And stop the new biome mods work. Only Pyrelands as a biome mod right now. They are
poorly defined builds right now and the system choked at their lack of precision I think."

One list, in mod_owner_hold.json beside this file. A mod on it:
  - the Dispatch tick (maturation_dispatch._tick) launches nothing on it: no builder, judge, live driver, steward, fixer
    or holder; its row reads decision owner_hold, klass held, status HELD BY OWNER with his words, date and the lift
    command, and it counts toward no idle, paused or stalled list;
  - the Designer and DesignerCodex chain (role_launch.chain_sweep, chain_ask) asks no run for it, and a run-now already
    pending on it is refused at launch (said once, no alarm);
  - ops_watch's queues.designer stall reader skips it.
A run already live on a held mod is allowed to finish: nothing here stops, kills or reaps anything, and its spend and
ledger rows are still recorded by the tick. Names match by the last path part, so design/concepts/Cauldron,
RimMandrake/Cauldron and Cauldron are one mod. An unreadable or malformed file raises Unreadable: a reader launches
nothing it cannot prove unheld (never a calm "no holds").

  mod_owner_hold.py show            the list, each with his words, date and lift command
  mod_owner_hold.py lift <Mod> --said "<his words>"   remove one (then publish mod_owner_hold.json)
Selftest: selftest_mod_owner_hold.py.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "mod_owner_hold.json")
LIFT = 'python3 src/RimMandrake/rimflow/mod_owner_hold.py lift %s --said "<his words>"'


class Unreadable(Exception):
    pass


def key(name):
    """design/concepts/Cauldron, /abs/.../Cauldron/, RimMandrake/Cauldron, Cauldron -> Cauldron."""
    return os.path.basename(os.path.normpath(str(name or "")))


def load(path=None):
    """-> {mod: {"mod", "date", "said"}}. Raises Unreadable on a missing, unparsable or wrong-shaped file."""
    p = path or os.environ.get("RM_OWNER_HOLD_FILE") or PATH
    try:
        with open(p, encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, ValueError) as e:
        raise Unreadable("%s: %s" % (p, e))
    holds = doc.get("holds") if isinstance(doc, dict) else None
    if not isinstance(holds, list):
        raise Unreadable("%s: no \"holds\" list" % p)
    out = {}
    for h in holds:
        if not (isinstance(h, dict) and isinstance(h.get("mod"), str) and h["mod"].strip()
                and isinstance(h.get("said"), str) and h["said"].strip() and isinstance(h.get("date"), str)):
            raise Unreadable("%s: a hold needs mod, said (his words) and date: %r" % (p, h))
        out[key(h["mod"])] = h
    return out


def held(name, holds=None):
    """-> the hold on `name` (any path spelling), or None. holds: load()'s mapping (read here when None)."""
    return (load() if holds is None else holds).get(key(name))


def status(h):
    """The one line every status prints for a held mod."""
    return "HELD BY OWNER %s: \"%s\" (lift: %s)" % (h["date"], h["said"], LIFT % h["mod"])


def lift(mod, said, path=None):
    """Remove `mod` from the list. -> the hold removed. Raises KeyError when it is not held."""
    p = path or os.environ.get("RM_OWNER_HOLD_FILE") or PATH
    load(p)
    with open(p, encoding="utf-8") as f:
        doc = json.load(f)
    keep = [h for h in doc["holds"] if key(h.get("mod")) != key(mod)]
    if len(keep) == len(doc["holds"]):
        raise KeyError("%s is not held" % mod)
    gone = [h for h in doc["holds"] if key(h.get("mod")) == key(mod)][0]
    doc["holds"] = keep
    doc.setdefault("lifted", []).append(dict(gone, lifted_said=said))
    with open(p, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return gone


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show")
    lp = sub.add_parser("lift")
    lp.add_argument("mod")
    lp.add_argument("--said", required=True, help="his words lifting it")
    o = ap.parse_args(argv)
    if o.cmd == "show":
        hs = load()
        if not hs:
            print("no mod is held by the owner")
        for m, h in sorted(hs.items()):
            print("%-18s %s" % (m, status(h)))
        return 0
    try:
        lift(o.mod, o.said)
    except KeyError as e:
        print(str(e), file=sys.stderr)
        return 1
    print("lifted %s; publish it: ./publish -m \"owner hold: lift %s\" src/RimMandrake/rimflow/mod_owner_hold.json"
          % (key(o.mod), key(o.mod)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
