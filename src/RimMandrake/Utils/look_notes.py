#!/usr/bin/env python3
"""look_notes.py: the notes of his next look list every pinned line whose value a fix moved, old beside new.

Rule 2e of design/RimMandrake/validation_map_and_rules.md (his card, 2026-11-12: "A fix that changes something he
passed -> Allow it, list what moved"). A pass he gives in a look becomes a PINNED LINE: his words, the cell of the save
it was seen in, the value it had, and a reader that finds the value now. A fix may move a pin; it is never refused. The
next look's notes list each pin whose value moved (old -> new), each pin whose line is gone, and each pin that cannot be
compared (UNMEASURED, with its cause). A pin that did not move is not listed.

The pins of a mod: design/concepts/<Mod>/version/pins.json, {"pins": [{"id", "said", "cell", "value", "read":
{"path": "<repo path>", "regex": "<one group: the value>"}}]}. No pins file means no pass of his is pinned yet.

Callers: the walk brief writer pastes `look_notes.py <Mod>` under "What changed since his last look"
(src/RimMandrake/rimflow/roles/walk_brief.md), and maturation.py's walk_brief clause refuses a brief that does not name
each listed pin (walk_brief_pins_why). Item RIMMANDRAKE_LIST_MOVED_PINS_IN_LOOK_NOTES.

  look_notes.py <Mod> [--save S] [--root R] [--json]
                                              the notes, and each listed cell missing from the save he opens (its
                                              look_cells file); exit 0 (listed or nothing to list), 2 the pins file
                                              cannot be read
  look_notes.py pin <Mod> --id ID --said "his words" --cell CELL --path P --regex R [--value V]
                                              pin (or re-pin) a pass at the value its reader finds now (or V)
  look_notes.py --selftest                    prints PASS n/n
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import look_changed_labels as LC  # noqa: E402  the cells of the save he opens (look_cells/<save>.json)

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
PINS_REL = "version/pins.json"


def pins_path(root, mod):
    return os.path.join(root, "design", "concepts", mod, PINS_REL)


def read_pins(root, mod):
    """-> (pins, why): the mod's pin list. ([], None) when no pins file exists (none pinned); (None, cause) when it
    cannot be read or parsed, which is never read as an empty set."""
    p = pins_path(root, mod)
    try:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return [], None
    except (OSError, ValueError) as e:
        return None, "%s cannot be read (%s)" % (os.path.relpath(p, root), e)
    pins = data.get("pins") if isinstance(data, dict) else None
    if not isinstance(pins, list):
        return None, "%s has no \"pins\" list" % os.path.relpath(p, root)
    return pins, None


def read_now(root, read):
    """-> (state, value_or_cause): ("value", v) | ("gone", cause) | ("unmeasured", cause)."""
    if not isinstance(read, dict) or not read.get("path") or not read.get("regex"):
        return "unmeasured", "the pin has no reader (read.path and read.regex)"
    p = os.path.join(root, read["path"])
    try:
        rx = re.compile(read["regex"], re.M)
    except re.error as e:
        return "unmeasured", "its regex does not compile (%s)" % e
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except FileNotFoundError:
        return "gone", "%s is gone" % read["path"]
    except OSError as e:
        return "unmeasured", "%s cannot be read (%s)" % (read["path"], e)
    m = rx.search(text)
    if not m:
        return "gone", "its line is gone from %s" % read["path"]
    return "value", (m.group(1) if rx.groups else m.group(0)).strip()


def same(a, b):
    a, b = str(a).strip(), str(b).strip()
    try:
        return float(a) == float(b)
    except ValueError:
        return a == b


def notes(root, mod):
    """-> {"pins": n, "listed": [{id, said, cell, state, old, new, why}], "why": cause or None}. state: moved | gone |
    unmeasured. An unchanged pin is not listed; a pin that cannot be compared is listed, never dropped."""
    pins, why = read_pins(root, mod)
    if pins is None:
        return {"pins": None, "listed": [], "why": why}
    out = []
    for i, p in enumerate(pins):
        p = p if isinstance(p, dict) else {}
        row = {"id": p.get("id") or "pin #%d (no id)" % (i + 1), "said": p.get("said"), "cell": p.get("cell"),
               "old": p.get("value"), "new": None, "why": None}
        if row["old"] is None or str(row["old"]).strip() == "":
            row.update(state="unmeasured", why="no stored value: what he passed was never measured")
        else:
            st, v = read_now(root, p.get("read"))
            if st == "value":
                if same(row["old"], v):
                    continue
                row.update(state="moved", new=v)
            else:
                row.update(state=st, why=v)
        out.append(row)
    return {"pins": len(pins), "listed": out, "why": None}


def cells_of_save(root, mod, save=None):
    """-> (save name, {cell keys}) of the named save's cells file, else the newest one the save builder recorded
    (look_changed_labels.record). Raises LC.CouldNotLook when none can be read, never read as an empty save."""
    pick = [x for x in LC.looks(root, mod) if save is None or x[2].get("save") == save]
    if not pick:
        raise LC.CouldNotLook("no cells file for %s%s under design/concepts/%s/%s/ (the save builder writes it with "
                              "look_changed_labels.record)" % (mod, " save %s" % save if save else "", mod, LC.LOOK_DIR))
    d = pick[-1][2]
    return d.get("save"), set(str(k) for k in (d.get("cells") or {}))


def save_why(root, mod, listed, save=None):
    """-> [why] a listed pin's cell is not in the save he opens (rule 2e: "that cell is in the save he opens"). [] when
    nothing is listed; a cells file that cannot be read is named, never read as every cell present."""
    if not listed:
        return []
    try:
        name, keys = cells_of_save(root, mod, save)
    except LC.CouldNotLook as e:
        return ["the save's cells cannot be read, so no listed pin is shown to be in it: %s" % e]
    return ["pinned line %s names %s, which is not in save %s: stage that cell in the save he opens" % (
        r["id"], "cell %s" % r["cell"] if r["cell"] else "no cell", name) for r in listed if str(r["cell"]) not in keys
        or not r["cell"]]


def render(mod, n):
    if n["why"]:
        return "Look notes for %s: COULD NOT LOOK: %s" % (mod, n["why"])
    if not n["pins"]:
        return "Look notes for %s: no pass of his is pinned (%s holds none): nothing to list." % (mod, PINS_REL)
    if not n["listed"]:
        return "Look notes for %s: %d pinned lines, none moved: nothing to list." % (mod, n["pins"])
    lines = ["Look notes for %s: %d of %d pinned lines moved or cannot be compared; open each cell:" % (
        mod, len(n["listed"]), n["pins"])]
    for r in n["listed"]:
        head = "- %s (cell %s; he passed: \"%s\")" % (r["id"], r["cell"] or "NOT NAMED", r["said"] or "?")
        if r["state"] == "moved":
            lines.append("%s: %s -> %s" % (head, r["old"], r["new"]))
        elif r["state"] == "gone":
            lines.append("%s: %s -> gone (%s)" % (head, r["old"], r["why"]))
        else:
            lines.append("%s: UNMEASURED (%s)" % (head, r["why"]))
    return "\n".join(lines)


def pin(root, mod, pid, said, cell, path, regex, value=None):
    """Add or replace pin pid at the value its reader finds now (or value). -> (ok, message)."""
    read = {"path": path, "regex": regex}
    if value is None:
        st, v = read_now(root, read)
        if st != "value":
            return False, "cannot pin %s: %s; repair --path/--regex so it finds the value he passed" % (pid, v)
        value = v
    pins, why = read_pins(root, mod)
    if pins is None:
        return False, why
    pins = [p for p in pins if not (isinstance(p, dict) and p.get("id") == pid)]
    pins.append({"id": pid, "said": said, "cell": cell, "value": str(value), "read": read})
    p = pins_path(root, mod)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"pins": pins}, f, indent=2)
        f.write("\n")
    os.replace(tmp, p)
    return True, "pinned %s = %s (cell %s)" % (pid, value, cell)


# ---- the selftest: five cases, each a function of a scratch root (selftest_look_notes.py names them) -----------------
SHALLOW = {"id": "PIN_SHALLOW", "said": "it's very transparent at first", "cell": "pit_d05", "value": "0.49",
           "read": {"path": "src/water.cs", "regex": r"ShallowOpacity\s*=\s*([0-9.]+)f"}}


def _setup(root, code, pins):
    src = os.path.join(root, "src", "water.cs")
    os.makedirs(os.path.dirname(src), exist_ok=True)
    with open(src, "w") as f:
        f.write(code)
    p = pins_path(root, "M")
    if pins is None:
        if os.path.exists(p):
            os.remove(p)
        return
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        json.dump({"pins": pins}, f)


def case_unchanged_not_listed(root):
    _setup(root, "const float ShallowOpacity = 0.49f;\n", [SHALLOW])
    n = notes(root, "M")
    return n["pins"] == 1 and n["listed"] == [] and "none moved" in render("M", n)


def case_moved_listed_old_new(root):
    _setup(root, "const float ShallowOpacity = 0.25f;\n", [SHALLOW])
    n = notes(root, "M")
    t = render("M", n)
    return (len(n["listed"]) == 1 and n["listed"][0]["state"] == "moved" and "PIN_SHALLOW" in t and
            "0.49 -> 0.25" in t and "pit_d05" in t)


def case_deleted_listed_gone(root):
    _setup(root, "// the shallow end was rewritten\n", [SHALLOW])
    n = notes(root, "M")
    t = render("M", n)
    return len(n["listed"]) == 1 and n["listed"][0]["state"] == "gone" and "PIN_SHALLOW" in t and "-> gone" in t


def case_empty_says_so(root):
    _setup(root, "const float ShallowOpacity = 0.49f;\n", [])
    n1 = notes(root, "M")
    _setup(root, "const float ShallowOpacity = 0.49f;\n", None)
    n2 = notes(root, "M")
    return (n1["listed"] == [] and n2["listed"] == [] and n1["why"] is None and n2["why"] is None and
            "nothing to list" in render("M", n1) and "nothing to list" in render("M", n2))


def case_no_value_unmeasured(root):
    _setup(root, "const float ShallowOpacity = 0.25f;\n", [dict(SHALLOW, value=None)])
    n = notes(root, "M")
    t = render("M", n)
    return (len(n["listed"]) == 1 and n["listed"][0]["state"] == "unmeasured" and "PIN_SHALLOW" in t and
            "UNMEASURED (no stored value" in t)


CASES = (("an unchanged pin is not listed", case_unchanged_not_listed),
         ("a moved numeric pin is listed old -> new", case_moved_listed_old_new),
         ("a pin whose line was deleted is listed as gone", case_deleted_listed_gone),
         ("an empty pin set lists nothing and says so", case_empty_says_so),
         ("a pin with no stored value is listed UNMEASURED, never dropped", case_no_value_unmeasured))


def run_case(fn):
    root = tempfile.mkdtemp(prefix="look_notes_st_")
    try:
        return bool(fn(root))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def selftest():
    results = [(what, run_case(fn)) for what, fn in CASES]
    passed = sum(1 for _, ok in results if ok)
    for what, ok in results:
        print("%s  %s" % ("ok  " if ok else "FAIL", what))
    print("%s %d/%d" % ("PASS" if passed == len(results) else "FAIL", passed, len(results)))
    return 0 if passed == len(results) else 1


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["--selftest"]:
        return selftest()
    if argv[:1] == ["pin"]:
        ap = argparse.ArgumentParser(prog="look_notes.py pin")
        ap.add_argument("mod")
        ap.add_argument("--id", required=True)
        ap.add_argument("--said", required=True, help="his words of the pass")
        ap.add_argument("--cell", required=True, help="the cell of the save the pass was seen in")
        ap.add_argument("--path", required=True, help="repo path that holds the value")
        ap.add_argument("--regex", required=True, help="a regex whose one group is the value")
        ap.add_argument("--value", help="the value he passed, when it is not the value now")
        ap.add_argument("--root", default=REPO)
        a = ap.parse_args(argv[1:])
        ok, msg = pin(a.root, a.mod, a.id, a.said, a.cell, a.path, a.regex, a.value)
        print(msg)
        return 0 if ok else 2
    ap = argparse.ArgumentParser(prog="look_notes.py", description=__doc__.split("\n")[0])
    ap.add_argument("mod")
    ap.add_argument("--root", default=REPO)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--save", help="the save he opens (its look_cells file); default the newest one recorded")
    a = ap.parse_args(argv)
    n = notes(a.root, a.mod)
    n["save_why"] = [] if n["why"] else save_why(a.root, a.mod, n["listed"], a.save)
    print(json.dumps(n, indent=2) if a.json else "\n".join([render(a.mod, n)] + ["  NOT IN THE SAVE: %s" % w
                                                                               for w in n["save_why"]]))
    return 2 if n["why"] else 0


if __name__ == "__main__":
    sys.exit(main())
