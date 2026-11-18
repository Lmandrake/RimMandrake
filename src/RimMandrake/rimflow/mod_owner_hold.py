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
  mod_owner_hold.py allow-design <Mod> --said "<his words>"   the hold stays on builds; his words on the row allow a
      design-only pass (designer_cleanse.py run refuses a held mod without them; item
      RIMMANDRAKE_UPGRADE_DESIGNER_CLEANSE_SIXTY_FOUR_BARS_LOCKED). Nothing else reads the field: no build, chain or
      Dispatch launch changes.
Selftest: selftest_mod_owner_hold.py.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
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
        d = h.get("design_allowed")
        if d is not None and not (isinstance(d, dict) and isinstance(d.get("said"), str) and d["said"].strip()
                                  and isinstance(d.get("date"), str) and d["date"].strip()):
            raise Unreadable("%s: design_allowed needs said (his words) and date: %r" % (p, h))
        if key(h["mod"]) in out:
            raise Unreadable("%s: %s is held twice (rows %r and %r)" % (p, key(h["mod"]), out[key(h["mod"])], h))
        out[key(h["mod"])] = h
    if path is None:
        # `pipe off <Mod>` (pipeline_control.py): a mod switched off in the one control store reads as held to every
        # reader of this list, the moment it is written (no publish); his own hold row wins where both stand
        import pipeline_control as PC
        try:
            for m, row in PC.off_mods().items():
                out.setdefault(key(m), row)
        except PC.Unreadable as e:
            raise Unreadable("the pipeline control store: %s" % e)
    return out


def _rewrite(p, change):
    """Read, change and write the hold file as one step: under an exclusive lock, validated by load() first, written to
    a temp file and moved over it, so a crash or a second writer never leaves a half or stale list. The lock lives in
    the temp dir (keyed by the file's real path), not beside the file: a lock file in the tree would dirty every clone."""
    import fcntl
    import hashlib
    import tempfile
    lock = os.path.join(tempfile.gettempdir(), "mod_owner_hold.%s.lock"
                        % hashlib.sha1(os.path.realpath(p).encode()).hexdigest()[:16])
    with open(lock, "a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        load(p)
        with open(p, encoding="utf-8") as f:
            doc = json.load(f)
        out = change(doc)
        fd, tmp = tempfile.mkstemp(prefix=".mod_owner_hold.", dir=os.path.dirname(os.path.abspath(p)))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(doc, f, indent=2, ensure_ascii=False)
                f.write("\n")
                f.flush()
                os.fsync(f.fileno())
            load(tmp)       # the new bytes must read as a hold list before they replace the old
            os.replace(tmp, p)
            dfd = os.open(os.path.dirname(os.path.abspath(p)), os.O_RDONLY)
            try:
                os.fsync(dfd)   # the rename itself survives a crash
            finally:
                os.close(dfd)
        except BaseException:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise
        return out


def held(name, holds=None):
    """-> the hold on `name` (any path spelling), or None. holds: load()'s mapping (read here when None)."""
    return (load() if holds is None else holds).get(key(name))


def status(h):
    """The one line every status prints for a held mod."""
    if h.get("control"):
        return "OFF by pipe (act %s at %s): %s (on: pipe on %s --why \"...\")" % (
            h.get("act"), h.get("at_pacific"), h.get("said"), h["mod"])
    return "HELD BY OWNER %s: \"%s\" (lift: %s)" % (h["date"], h["said"], LIFT % h["mod"])


def lift(mod, said, path=None):
    """Remove `mod` from the list. -> the hold removed. Raises KeyError when it is not held."""
    p = path or os.environ.get("RM_OWNER_HOLD_FILE") or PATH

    def change(doc):
        keep = [h for h in doc["holds"] if key(h.get("mod")) != key(mod)]
        if len(keep) == len(doc["holds"]):
            raise KeyError("%s is not held" % mod)
        gone = [h for h in doc["holds"] if key(h.get("mod")) == key(mod)][0]
        doc["holds"] = keep
        doc.setdefault("lifted", []).append(dict(gone, lifted_said=said))
        return gone
    return _rewrite(p, change)


def design_allowed(h):
    """-> his words allowing a design-only pass on the held mod `h` (a load() row), or None."""
    d = (h or {}).get("design_allowed")
    return d if isinstance(d, dict) and isinstance(d.get("said"), str) and d["said"].strip() else None


def allow_design(mod, said, path=None, date=None):
    """Write his words allowing a design-only pass on the held `mod` onto its hold row. -> the row. Raises KeyError when
    it is not held, ValueError on empty words. The hold itself stays: every build reader is unchanged."""
    import datetime
    if not (isinstance(said, str) and said.strip()):
        raise ValueError("allow-design needs his words")
    if date is not None and not (isinstance(date, str) and date.strip()):
        raise ValueError("allow-design's date must be a non-blank date string")
    p = path or os.environ.get("RM_OWNER_HOLD_FILE") or PATH

    def change(doc):
        rows = [h for h in doc["holds"] if key(h.get("mod")) == key(mod)]
        if not rows:
            raise KeyError("%s is not held" % mod)
        rows[0]["design_allowed"] = {"said": said.strip(), "date": date or datetime.date.today().isoformat()}
        return rows[0]
    return _rewrite(p, change)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show")
    lp = sub.add_parser("lift")
    lp.add_argument("mod")
    lp.add_argument("--said", required=True, help="his words lifting it")
    ap_ = sub.add_parser("allow-design")
    ap_.add_argument("mod")
    ap_.add_argument("--said", required=True, help="his words allowing a design-only pass")
    ap_.add_argument("--date", default=None, help="the day he said it (default today)")
    o = ap.parse_args(argv)
    if o.cmd == "show":
        hs = load()
        if not hs:
            print("no mod is held by the owner")
        for m, h in sorted(hs.items()):
            d = design_allowed(h)
            print("%-18s %s%s" % (m, status(h), "; design pass allowed %s: \"%s\"" % (d["date"], d["said"]) if d else ""))
        return 0
    if o.cmd == "allow-design":
        try:
            allow_design(o.mod, o.said, date=o.date)
        except (KeyError, ValueError) as e:
            print(str(e), file=sys.stderr)
            return 1
        print("design pass allowed on held %s; publish it: ./publish -m \"owner hold: allow design %s\" "
              "src/RimMandrake/rimflow/mod_owner_hold.json" % (key(o.mod), key(o.mod)))
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
