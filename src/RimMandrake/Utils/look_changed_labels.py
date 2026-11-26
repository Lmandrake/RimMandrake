#!/usr/bin/env python3
"""look_changed_labels.py: each cell of a review save whose inputs changed since his last look is labelled so.

Page: design/specs/2026-11-26-look-changed-labels/boundary.md. Rule: design/RimMandrake/validation_map_and_rules.md rule 2f
(his card of 2026-11-12: "Who closes his objections -> His look, as a labelled cell in the next save"). A fixed cell is a
"changed since your last look" cell in the next save he opens anyway; it is never a sitting of its own, and he does not
re-inspect what he passed.

A CELL is one station or matrix cell of the save: {"key", "name", "inputs": [repo paths, files or folders], "params": any
JSON (optional)}. Its inputs hash is sha256 over each input file's bytes and the params, so a change to the scene script,
the mod file it exercises or its staged numbers moves it.

A LOOK is a cells file `design/concepts/<Mod>/look_cells/<save>.json` that the save builder wrote (`record`). His last look
is the newest cells file staged before the newest move out of `his_walk` that is his (by OWNER, or with his words or his
card), read from `version/stage_record.json`, every kept `version/stage_record_<version>.json` and every
`version/previous/*/stage_record.json`.

The save builder (python.exe or WSL, the visit's walk-save script):

    import look_changed_labels as LC
    res = LC.label_cells("<Mod>", CELLS)            # res["labels"][key]: LABEL_CHANGED, LABEL_NEW or None
    name = LC.sign_name(name, res["labels"][key])   # the label leads the sign's name; an AFTER/START tag stays last
    notes = res["notes"]                            # removed cells, one line each: put them on the save's notes sign
    LC.record("<Mod>", "<save name>", CELLS)        # once the save is written: the cells he will look at

    python3 src/RimMandrake/Utils/look_changed_labels.py show --mod <Mod> [--save <name>]   the walk brief's lines
    python3 src/RimMandrake/Utils/look_changed_labels.py label --mod <Mod> --cells <cells.json>
    python3 src/RimMandrake/Utils/look_changed_labels.py --selftest

Exit 0 answered (labels or lines printed); 2 could not look (a record that cannot be read, a cell input that is not there,
no cells file to show), never read as "every cell new".
"""
import glob
import hashlib
import json
import os
import sys
from datetime import datetime

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
LABEL_CHANGED = "changed since your last look"
LABEL_NEW = "new since your last look"
LOOK_DIR = "look_cells"


class CouldNotLook(Exception):
    pass


def mod_dir(root, mod):
    return os.path.join(root, "design", "concepts", mod)


def _ts(s):
    """-> a sortable epoch from an ISO time with an offset (or Z)."""
    return datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()


def inputs_hash(root, cell):
    """-> sha256 hex of a cell's input files (path and bytes, in path order) and its params. A missing input raises."""
    h = hashlib.sha256()
    files = []
    for p in cell.get("inputs") or []:
        full = os.path.join(root, p)
        if os.path.isdir(full):
            for d, _, names in os.walk(full):
                files += [os.path.relpath(os.path.join(d, n), root).replace(os.sep, "/") for n in names]
        elif os.path.isfile(full):
            files.append(str(p).replace(os.sep, "/"))
        else:
            raise CouldNotLook("cell %s: input %s is not there (name the files the cell is made from)" % (cell.get("key"), p))
    for f in sorted(set(files)):
        with open(os.path.join(root, f), "rb") as fh:
            h.update(f.encode() + b"\0" + hashlib.sha256(fh.read()).digest())
    h.update(json.dumps(cell.get("params"), sort_keys=True).encode())
    return h.hexdigest()


def his_look_times(root, mod):
    """-> sorted epochs of every move out of his_walk that is his. Raises CouldNotLook on a record that cannot be read."""
    vdir = os.path.join(mod_dir(root, mod), "version")
    # a passed version's record is kept as version/stage_record_<version>.json (maturation.py, the version opener)
    paths = ([os.path.join(vdir, "stage_record.json")] + sorted(glob.glob(os.path.join(vdir, "stage_record_*.json")))
             + sorted(glob.glob(os.path.join(vdir, "previous", "*", "stage_record.json"))))
    out = []
    for p in paths:
        if not os.path.exists(p):
            continue
        try:
            with open(p, encoding="utf-8") as f:
                moves = json.load(f).get("moves") or []
            for m in moves:
                conf = m.get("confirmed") or {}
                if m.get("from") == "his_walk" and (m.get("by") == "OWNER" or conf.get("owner_said") or conf.get("by_card")):
                    out.append(_ts(m["at"]))
        except (OSError, ValueError, KeyError, AttributeError, TypeError) as e:
            raise CouldNotLook("%s cannot be read (%s: %s)" % (os.path.relpath(p, root), type(e).__name__, e))
    return sorted(out)


def looks(root, mod):
    """-> [(staged epoch, path, data)] of every cells file of the mod, oldest first. Raises CouldNotLook on a bad file."""
    out = []
    for p in sorted(glob.glob(os.path.join(mod_dir(root, mod), LOOK_DIR, "*.json"))):
        try:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
            out.append((_ts(d["staged_at"]), p, d))
        except (OSError, ValueError, KeyError, TypeError) as e:
            raise CouldNotLook("%s cannot be read (%s: %s)" % (os.path.relpath(p, root), type(e).__name__, e))
    return sorted(out, key=lambda t: t[0])


def last_look(root, mod, before=None):
    """-> (path, data) of the cells file he last looked at, or (None, None) when he never looked. `before`: an epoch;
    only looks ended before it count (show uses the staging time of the save it reads)."""
    times = [t for t in his_look_times(root, mod) if before is None or t < before]
    if not times:
        return None, None
    seen = [(p, d) for t, p, d in looks(root, mod) if t <= times[-1]]
    return seen[-1] if seen else (None, None)


def compare(now, prior):
    """now: {key: {name, hash}}; prior: the same or None. -> (labels {key: label|None}, notes [str])."""
    if prior is None:
        return {k: LABEL_NEW for k in now}, []
    labels = {k: (LABEL_NEW if k not in prior else LABEL_CHANGED if prior[k].get("hash") != v["hash"] else None)
              for k, v in now.items()}
    notes = ["removed since your last look: %s %s" % (k, prior[k].get("name", "")) for k in sorted(prior) if k not in now]
    return labels, notes


def hashed(root, cells):
    out = {}
    for c in cells:
        k = str(c["key"])
        if k in out:
            raise CouldNotLook("cell key %s is used twice (one key per cell)" % k)
        out[k] = {"name": c.get("name", ""), "hash": inputs_hash(root, c)}
    return out


def label_cells(mod, cells, root=REPO):
    """-> {labels, notes, last_look, why}. why non-empty = could not look: labels and notes are then empty, never 'all new'."""
    try:
        now = hashed(root, cells)
        p, d = last_look(root, mod)
    except CouldNotLook as e:
        return {"labels": {}, "notes": [], "last_look": None, "why": [str(e)]}
    labels, notes = compare(now, d["cells"] if d else None)
    return {"labels": labels, "notes": notes, "last_look": os.path.relpath(p, root).replace(os.sep, "/") if p else None,
            "why": []}


def sign_name(name, label):
    """-> the sign name with the label in front ('[CHANGED SINCE YOUR LAST LOOK] burn front AFTER'); the tag stays last."""
    return "[%s] %s" % (label.upper(), name) if label else name


def record(mod, save, cells, root=REPO, now=None):
    """Write look_cells/<save>.json: the cells of the save he will look at. -> its path."""
    d = {"save": save, "staged_at": now or datetime.now().astimezone().isoformat(timespec="seconds"),
         "cells": hashed(root, cells)}
    p = os.path.join(mod_dir(root, mod), LOOK_DIR, "%s.json" % save)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, indent=1, sort_keys=True)
        f.write("\n")
    return p


def show(mod, save=None, root=REPO):
    """-> lines for the walk brief's 'What changed since his last look': the save's changed, new and removed cells."""
    all_ = looks(root, mod)
    pick = [x for x in all_ if save is None or x[2].get("save") == save]
    if not pick:
        raise CouldNotLook("no cells file for %s%s under design/concepts/%s/%s/ (the save builder writes it with record())"
                           % (mod, " save %s" % save if save else "", mod, LOOK_DIR))
    t, p, d = pick[-1]
    lp, ld = last_look(root, mod, before=t)
    labels, notes = compare(d["cells"], ld["cells"] if ld else None)
    head = "save %s against %s" % (d.get("save"), "his last look, save %s" % ld.get("save") if ld else "no earlier look (every cell new)")
    rows = ["%s %s: %s" % (k, d["cells"][k].get("name", ""), labels[k]) for k in sorted(labels) if labels[k]]
    return [head] + (rows or ["no cell changed since his last look"]) + notes


def selftest():
    """The item's acceptance test: the five promises of the page, in selftest_look_changed_labels.py. -> its exit code."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import selftest_look_changed_labels
    return selftest_look_changed_labels.main()


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("show")
    s.add_argument("--mod", required=True)
    s.add_argument("--save")
    lab = sub.add_parser("label")
    lab.add_argument("--mod", required=True)
    lab.add_argument("--cells", required=True, help="a JSON file: a list of {key, name, inputs[], params}")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "show":
            print("\n".join(show(a.mod, a.save)))
            return 0
        with open(a.cells, encoding="utf-8") as f:
            cells = json.load(f)
    except (CouldNotLook, OSError, ValueError) as e:
        print("COULD NOT LOOK: %s" % e, file=sys.stderr)
        return 2
    res = label_cells(a.mod, cells)
    print(json.dumps(res, indent=1, sort_keys=True))
    return 2 if res["why"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
