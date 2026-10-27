#!/usr/bin/env python3
"""audits.py - the Auditor's audits.jsonl and its schema, in one place (item AUDITOR_BUILD_AUDITS_FILE).

The schema is audits.schema.json beside this file; this module is its only reader and enforcer. Everything that
reads or writes D:\\ClaudeWork\\rimmandrake\\auditor\\audits.jsonl goes through here: audit_prescreen.py and
arbiter_tiers.py (past_audit_failed), the Auditor's appends (roles/auditor.md "Two records per result") and the
waiting index ("Carried picks").

  ensure   create the file when it is absent (an empty file = no audits yet), never truncate one that exists, then
           validate it. The Auditor's pre_launch (dispatcher_schedule.json) and the wave-2 setup step
           (design/RimMandrake/rimflow_v3_golive_wave1.md section 9) run it.
  check    validate every line; exit 2 on a missing file or a line that breaks the schema.
  waiting  print the waiting index: UNRESOLVED lines with waiting_for and no later SOUND/DEFECT for that item+sha.
  append   one JSON line from stdin, validated, refused when its idempotency key (item, sha, run) is already there.

    python3 src/RimMandrake/rimflow/audits.py ensure|check|waiting [--path P]
    python3 src/RimMandrake/rimflow/audits.py append [--path P] < line.json

Exit: 0 ok, 1 append refused as a duplicate, 2 UNMEASURED (missing/unreadable file, a schema-breaking line).
A missing file or a torn line is never "no audits": the readers raise and their callers report UNMEASURED.
"""
import argparse, fcntl, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(HERE, "audits.schema.json")
DEFAULT_PATH = "/mnt/d/ClaudeWork/rimmandrake/auditor/audits.jsonl"
SETTLING = ("SOUND", "DEFECT")
_SCHEMA = None


def schema():
    global _SCHEMA
    if _SCHEMA is None:
        with open(SCHEMA_PATH, encoding="utf-8") as fh:
            _SCHEMA = json.load(fh)
    return _SCHEMA


def key_fields():
    return tuple(schema()["x-idempotency-key"])


def _contracts():
    """-> (contracts.jsonl, contracts.models), imported on first use (pydantic costs ~50 ms; an empty file pays none)."""
    root = os.path.dirname(HERE)
    if root not in sys.path:
        sys.path.append(root)
    from contracts import jsonl, models
    return jsonl, models


def problems(d):
    """Pure. -> the ways one decoded line breaks audits.schema.json ([] = valid). The rule is contracts.models.AuditRecord
    (the schema's type/required/enum/minLength/pattern/items keywords and its two x-conditionals);
    selftest_contracts proves the model and this schema file say the same thing."""
    return _contracts()[1].audits_problems(d)


def key(d):
    return tuple(d.get(k) for k in key_fields())


def parse(text, where="audits.jsonl"):
    """Pure. File text -> rows, in file order. Blank lines are skipped; a line that is not JSON or breaks the schema
    raises ValueError naming it: it could be the DEFECT that matters."""
    rows = []
    lines = text.splitlines()
    if not any(ln.strip() for ln in lines):
        return rows
    cj = _contracts()[0]
    for i, line in enumerate(lines):
        r = cj.decode(line, i + 1, need_object=False)
        if not r.ok and r.code == cj.BLANK:
            continue
        if not r.ok:                            # not JSON (or nested past the decoder's depth)
            raise ValueError("%s line %d is not JSON" % (where, i + 1))
        d = r.value
        bad = problems(d)
        if bad:
            raise ValueError("%s line %d breaks audits.schema.json: %s" % (where, i + 1, "; ".join(bad)))
        rows.append(d)
    return rows


def read(path=DEFAULT_PATH):
    """-> every row. A missing or unreadable file raises OSError; a bad line raises ValueError."""
    with open(path, encoding="utf-8") as fh:
        return parse(fh.read(), path)


def past_failed(rows):
    """Items with a DEFECT audit (audit_prescreen's past_audit_failed)."""
    return {r["item"] for r in rows if r["verdict"] == "DEFECT"}


def waiting(rows):
    """The waiting index (schema x-waiting-index): every UNRESOLVED line with a non-empty waiting_for that no LATER
    line for the same item and sha settles (SOUND/DEFECT). A later UNRESOLVED does not settle it. File order."""
    out = []
    for i, r in enumerate(rows):
        if r["verdict"] == "UNRESOLVED" and r.get("waiting_for"):
            if not any(s["item"] == r["item"] and s["sha"] == r["sha"] and s["verdict"] in SETTLING
                       for s in rows[i + 1:]):
                out.append(r)
    return out


def ensure(path=DEFAULT_PATH):
    """Create the file if absent (O_EXCL: never truncates, safe beside a writer), then validate it.
    -> "created" | "exists". Raises like read() when what is there breaks the schema."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    try:
        os.close(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644))
        state = "created"
    except FileExistsError:
        state = "exists"
    read(path)
    return state


def append(d, path=DEFAULT_PATH):
    """Append one validated line unless a line with its idempotency key is already there. -> True if written.
    The file must exist (ensure); a bad line in it raises before anything is written."""
    bad = problems(d)
    if bad:
        raise ValueError("refused: %s" % "; ".join(bad))
    with open(path, "r+", encoding="utf-8") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        text = fh.read()
        if any(key(r) == key(d) for r in parse(text, path)):
            return False
        if text and not text.endswith("\n"):
            fh.write("\n")
        fh.write(json.dumps(d, sort_keys=True) + "\n")
    return True


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("cmd", choices=("ensure", "check", "waiting", "append"))
    a.add_argument("--path", default=DEFAULT_PATH)
    a = a.parse_args(argv)
    try:
        if a.cmd == "ensure":
            print("%s %s (%d line(s))" % (a.path, ensure(a.path), len(read(a.path))))
        elif a.cmd == "check":
            print("%s: %d valid line(s)" % (a.path, len(read(a.path))))
        elif a.cmd == "waiting":
            for r in waiting(read(a.path)):
                print(json.dumps({k: r.get(k) for k in ("item", "sha", "run", "ts", "waiting_for")}))
        else:
            if not append(json.loads(sys.stdin.read()), a.path):
                print("duplicate: a line for %r is already there" % (key_fields(),), file=sys.stderr)
                return 1
    except (OSError, ValueError) as ex:
        print("UNMEASURED: %s" % ex, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
