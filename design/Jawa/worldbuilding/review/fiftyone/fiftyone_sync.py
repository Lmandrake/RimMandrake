#!/usr/bin/env python
"""Move decisions between FiftyOne tags and the review sheet's decisions file.

  export   read the dataset's tags -> creature_register.fiftyone_export.json
           (the same {decision, prio, note} row shape the sheets use)
  diff     export shape vs the owner's creature_register.decisions.json
  import   push the owner's decisions file INTO the dataset as tags

This prototype NEVER writes creature_register.decisions.json. The export lands
beside it as creature_register.fiftyone_export.json; promoting it is a separate,
deliberate act (copy the "decisions" block over, or point the sheet at it).

Run in its own memory scope:
  systemd-run --user --scope -p MemoryMax=6G -p MemorySwapMax=1G \
      -p OOMPolicy=continue -- \
      /home/mandrake/.venvs/fiftyone/bin/python fiftyone_sync.py export
"""
import datetime
import json
import os
import sys

REVIEW = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECISIONS = os.path.join(REVIEW, "creature_register.decisions.json")
EXPORT = os.path.join(REVIEW, "creature_register.fiftyone_export.json")
DATASET = os.environ.get("FO_DATASET", "creature_art")

# One of these tags per sample IS the decision; anything else is a free label.
DECISION_TAGS = ("cut", "regen", "rescale", "keep")
PRIO_PREFIX = "prio:"


def load_dataset():
    import fiftyone as fo

    return fo.load_dataset(DATASET)


def row_from_tags(tags, note):
    decision = ""
    for t in DECISION_TAGS:          # first match wins, in severity order
        if t in tags:
            decision = t
            break
    prio = ""
    for t in tags:
        if t.startswith(PRIO_PREFIX):
            prio = t[len(PRIO_PREFIX):]
            break
    return {"decision": decision, "prio": prio, "note": note or ""}


def do_export():
    ds = load_dataset()
    out = {}
    for s in ds.select_fields(["defName", "note", "tags"]):
        out[s["defName"]] = row_from_tags(set(s.tags), s["note"])
    base = json.load(open(DECISIONS))
    doc = {
        "sheetId": base.get("sheetId"),
        "posture": base.get("posture"),
        "postureMeaning": base.get("postureMeaning"),
        "generatedBy": "fiftyone_sync.py export (dataset %s)" % DATASET,
        "generatedUtc": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "decisions": out,
    }
    with open(EXPORT, "w") as f:
        json.dump(doc, f, indent=1)
    print("wrote %s rows=%d -> %s" % (DATASET, len(out), EXPORT))


def do_diff():
    live = json.load(open(DECISIONS))["decisions"]
    exp = json.load(open(EXPORT))["decisions"]
    changed = []
    for k, v in exp.items():
        o = live.get(k)
        if o is None:
            changed.append((k, None, v))
            continue
        if (o.get("decision", ""), o.get("prio", ""), o.get("note", "")) != (
            v["decision"], v["prio"], v["note"]):
            changed.append((k, o, v))
    missing = [k for k in live if k not in exp]
    print("changed=%d missing_from_export=%d %s" % (len(changed), len(missing), missing[:6]))
    for k, o, v in changed[:40]:
        print("  %-32s %s -> %s" % (
            k,
            "ABSENT" if o is None else "%s/%s/%r" % (o.get("decision"), o.get("prio"), o.get("note")),
            "%s/%s/%r" % (v["decision"], v["prio"], v["note"])))
    return len(changed)


def do_import():
    ds = load_dataset()
    live = json.load(open(DECISIONS))["decisions"]
    n = 0
    for s in ds.select_fields(["defName", "tags"]):
        d = live.get(s["defName"])
        if not d:
            continue
        tags = [t for t in (d.get("decision"),
                            (PRIO_PREFIX + d["prio"]) if d.get("prio") else None) if t]
        if set(tags) != set(s.tags):
            s.tags = tags
            s.save()
            n += 1
    print("retagged %d samples from %s" % (n, os.path.basename(DECISIONS)))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "export"
    if cmd == "export":
        do_export()
    elif cmd == "diff":
        do_diff()
    elif cmd == "import":
        do_import()
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
