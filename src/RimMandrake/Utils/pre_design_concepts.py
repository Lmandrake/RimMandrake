#!/usr/bin/env python3
"""pre_design_concepts.py: read and keep the Pre-Design Concepts store, design/pre_design_concepts/. No model.

Promises: design/specs/2026-11-26-pre-design-concepts/boundary.md. Rules of the store: its README.md. Item
RIMMANDRAKE_BUILD_IDEAS_LIST_AT_INTAKE_TWO_IDEAS_SAT_UNPLACED.

    pre_design_concepts.py list                       one line per concept: name, kind, date added, date last offered
    pre_design_concepts.py check                      exit 0 when every concept file has every head field; else 1,
                                                      naming each file and field; 2 when the store cannot be read
    pre_design_concepts.py due                        the concepts for the next card (at most four): never offered
                                                      first, oldest added first; then offered longest ago
    pre_design_concepts.py offered <name> --answer "<his answer>"
                                                      write today's date and his answer into the concept's file
    pre_design_concepts.py sweep [--apply]            the weekly line: once per ISO week, append
                                                      "PRE-DESIGN CONCEPTS: card due" and the output of `due` to the
                                                      Conductor log; every run writes the reading (last_sweep.json)
        --store DIR    another store (tests); default design/pre_design_concepts of this repo

A concept file is every *.md in the store but README.md. Its head is bullet lines `- **<Field>:** <text>`, with the
fields of FIELDS. `Last offered` is `never` or a date YYYY-MM-DD. An optional `- **Went to:**` with text says where the
concept went when the owner picked it; such a concept no longer waits: it is not counted and never due.
A store that cannot be read is UNMEASURED with its cause, never 0. An empty store is a measured 0.
"""
import argparse
import datetime as DT
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
STORE = os.path.join(REPO, "design", "pre_design_concepts")
UNM = "UNMEASURED"
FIELDS = ("Name", "Kind", "Gets", "Added", "From ticket", "Code", "Last offered", "His answer")
CARD_LINE = "PRE-DESIGN CONCEPTS: card due"
DUE_MAX = 4     # the most options one question card holds besides "let them all sleep" (the question-card skill)
_HEAD = re.compile(r"^- \*\*([A-Za-z ]+):\*\*[ \t]*(.*)$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse(path):
    """-> {"file", "fields": {field: text}, "body", "faults": [str]}; raises OSError / UnicodeDecodeError."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    fields = {}
    for line in text.splitlines():
        if line.startswith("## "):
            break       # the head ends at the first section
        m = _HEAD.match(line.rstrip())
        if m and m.group(1) not in fields:
            fields[m.group(1)] = m.group(2).strip()
    name = os.path.basename(path)
    faults = ["%s: no %s" % (name, f) for f in FIELDS if not fields.get(f)]
    for f in ("Added",):
        if fields.get(f) and not _DATE.match(fields[f]):
            faults.append("%s: %s is not a date YYYY-MM-DD: %r" % (name, f, fields[f]))
    lo = fields.get("Last offered", "")
    if lo and lo != "never" and not _DATE.match(lo):
        faults.append("%s: Last offered is neither 'never' nor a date YYYY-MM-DD: %r" % (name, lo))
    return {"file": name, "path": path, "fields": fields, "body": text, "faults": faults,
            "name": fields.get("Name") or os.path.splitext(name)[0], "went": fields.get("Went to", "")}


def read_store(store=STORE):
    """-> {"count": int|UNM, "names": [str], "concepts": [dict], "faults": [str], "why": str, "gone": [str]}.
    count and names hold the concepts that wait (no `Went to`)."""
    out = {"count": UNM, "names": [], "concepts": [], "faults": [], "why": "", "gone": []}
    try:
        files = sorted(f for f in os.listdir(store) if f.endswith(".md") and f != "README.md")
    except FileNotFoundError:
        out["why"] = "the store is missing (%s)" % store
        return out
    except OSError as e:
        out["why"] = "the store could not be read: %s: %s" % (e.__class__.__name__, e)
        return out
    for fn in files:
        try:
            c = parse(os.path.join(store, fn))
        except (OSError, UnicodeDecodeError) as e:
            out["why"] = "the concept file %s could not be read: %s: %s" % (fn, e.__class__.__name__, e)
            out["concepts"], out["names"], out["gone"] = [], [], []
            return out
        out["concepts"].append(c)
        out["faults"] += c["faults"]
        (out["gone"] if c["went"] else out["names"]).append(c["name"])
    out["count"] = len(out["names"])
    return out


def due(concepts, n=DUE_MAX):
    """The concepts for the next card: never offered first (oldest added first), then offered longest ago."""
    wait = [c for c in concepts if not c["went"]]

    def key(c):
        lo = c["fields"].get("Last offered", "never")
        never = lo == "never" or not _DATE.match(lo)
        return (0 if never else 1, c["fields"].get("Added", "") if never else lo, c["name"].lower())
    return sorted(wait, key=key)[:n]


def line_of(c):
    f = c["fields"]
    return "%s · %s · added %s · last offered %s" % (c["name"], f.get("Kind", "?"), f.get("Added", "?"),
                                                                  f.get("Last offered", "?"))


def find(concepts, name):
    want = name.strip().lower().replace("_", " ")
    for c in concepts:
        if want in (c["name"].lower(), os.path.splitext(c["file"])[0].lower().replace("_", " ")):
            return c
    return None


def set_offered(path, answer, today):
    """Write today's date and his answer into the head; keep every earlier offer in `## Offers`."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    text = re.sub(r"(?m)^- \*\*Last offered:\*\*.*$", lambda m: "- **Last offered:** %s" % today, text, count=1)
    text = re.sub(r"(?m)^- \*\*His answer:\*\*.*$", lambda m: "- **His answer:** %s" % answer, text, count=1)
    entry = "- %s: %s\n" % (today, answer)
    if re.search(r"(?m)^## Offers\s*$", text):
        text = re.sub(r"(?m)^## Offers\s*\n(\n?)", lambda m: "## Offers\n\n" + entry, text, count=1)
    else:
        text = text.rstrip("\n") + "\n\n## Offers\n\n" + entry
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def conductor_dir():
    """<agent storage>/rimmandrake/conductor; RM_PDC_CONDUCTOR_DIR overrides it (tests)."""
    if os.environ.get("RM_PDC_CONDUCTOR_DIR"):
        return os.environ["RM_PDC_CONDUCTOR_DIR"]
    helper = os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")
    r = subprocess.run([sys.executable, helper, "rimmandrake"], capture_output=True, text=True, timeout=60)
    root = (r.stdout or "").strip()
    if r.returncode or not root:
        raise SystemExit("pre_design_concepts: agent_storage.py rimmandrake gave no root (rc %s): %s"
                         % (r.returncode, (r.stderr or "").strip()))
    return os.path.join(root, "conductor")


def sweep(store, conductor, apply, now=None):
    """Once per ISO week, append the card line and `due` to <conductor>/log.md. Writes the reading
    <conductor>/../pre_design_concepts/last_sweep.json on every applied run. -> (rc, reading)."""
    now = now or DT.datetime.now()
    y, w, _ = now.date().isocalendar()
    week = "%dW%02d" % (y, w)
    rdir = os.path.join(os.path.dirname(conductor.rstrip("/")), "pre_design_concepts")
    rpath = os.path.join(rdir, "last_sweep.json")
    try:
        with open(rpath, encoding="utf-8") as f:
            last = json.load(f)
    except (OSError, ValueError):
        last = {}
    r = read_store(store)
    rec = {"at": now.strftime("%Y-%m-%d %H:%M"), "week": week, "count": r["count"], "why": r["why"],
           "card_week": last.get("card_week"), "act": "none", "due": []}
    if r["count"] == UNM:
        rec["act"] = "could not look"
    elif last.get("card_week") == week:
        rec["act"] = "none: the card line of %s is written" % week
    else:
        d = due(r["concepts"])
        rec["due"] = [c["name"] for c in d]
        if not d:
            rec["act"] = "none: no concept waits"
        else:
            rec["act"] = "card line written" if apply else "card line due (a plan: nothing written)"
            rec["card_week"] = week
            if apply:
                lines = ["", "%s %s (%s; %d of %d waiting; `pre_design_concepts.py due`):"
                         % (now.strftime("%Y-%m-%d %H:%M"), CARD_LINE, week, len(d), r["count"])]
                lines += ["- " + line_of(c) for c in d]
                with open(os.path.join(conductor, "log.md"), "a", encoding="utf-8") as f:
                    f.write("\n".join(lines) + "\n")
    if apply:
        os.makedirs(rdir, exist_ok=True)
        with open(rpath + ".tmp", "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=1)
        os.replace(rpath + ".tmp", rpath)
    return (2 if r["count"] == UNM else 0), rec


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--store", default=STORE)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("list", "check", "due"):
        sp = sub.add_parser(c)
        sp.add_argument("--store", default=argparse.SUPPRESS)
    o = sub.add_parser("offered")
    o.add_argument("name")
    o.add_argument("--answer", required=True)
    o.add_argument("--store", default=argparse.SUPPRESS)
    s = sub.add_parser("sweep")
    s.add_argument("--apply", action="store_true")
    s.add_argument("--store", default=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    store = os.path.abspath(a.store)
    if a.cmd == "sweep":
        rc, rec = sweep(store, conductor_dir(), a.apply)
        print(json.dumps(rec))
        return rc
    r = read_store(store)
    if r["count"] == UNM:
        print("COULD NOT LOOK: %s" % r["why"])
        return 2
    if a.cmd == "list":
        for c in r["concepts"]:
            print(line_of(c) + ((" · went to: " + c["went"]) if c["went"] else ""))
        print("%d waiting, %d gone" % (r["count"], len(r["gone"])))
        return 0
    if a.cmd == "check":
        for f in r["faults"]:
            print("FAULT " + f)
        print("%s: %d concept files, %d faults" % ("FAILS" if r["faults"] else "HOLDS", len(r["concepts"]),
                                                    len(r["faults"])))
        return 1 if r["faults"] else 0
    if a.cmd == "due":
        for c in due(r["concepts"]):
            print(line_of(c))
        return 0
    c = find(r["concepts"], a.name)
    if c is None:
        print("no such concept: %r (names: %s)" % (a.name, ", ".join(x["name"] for x in r["concepts"])))
        return 1
    set_offered(c["path"], a.answer.strip(), DT.date.today().isoformat())
    print("offered %s on %s: %s" % (c["name"], DT.date.today().isoformat(), a.answer.strip()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
