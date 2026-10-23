#!/usr/bin/env python3
"""prereview.py — nothing reaches the owner unread (owner, 2026-10-22; standing_rulings.md "Nothing reaches the owner
unread"). A review sheet is served (serve_gated.py, review_queue.py) or sent to the phone (sheet_to_artifact.py) only
with a PRE-REVIEW RECORD beside it saying who looked at every row and what they saw.

    python3 prereview.py init  <sheet.html> --by seat:BENCH      # write/refresh <stem>.prereview.json, every new row TODO
    python3 prereview.py check <sheet.html>                       # exit 0 OK, 4 REFUSED (the reason names the fix)
    python3 prereview.py --selftest

THE RECORD — <sheet stem>.prereview.json beside the sheet:
    {"sheet": "<file name>",
     "looked_by": "seat:BENCH" | "judge:<model id>",        # the seat that looked, or a naive judge that did not make it
     "when": "<ISO time>",
     "caught": "<one line for the owner: what was fixed or dropped before he saw it; 'nothing' is a valid answer>",
     "rows": {"<row id>": {"fp": "<row fingerprint>", "verdict": "OK" | "FIXED" | "FLAG", "note": "<what was seen>"}},
     "dropped": [{"row": "<row id>", "why": "<what was broken>"}]}

  OK    = looked at, nothing obviously broken.    FIXED = was broken, fixed, looked at again (note says what).
  FLAG  = cannot be judged by an agent, or a doubt he must see (note says what) — the row still reaches him.
  A broken row that is not fixed is DROPPED: removed from the sheet and listed under "dropped".

REFUSED when: no record; looked_by not `seat:`/`judge:`; caught missing; a sheet row with no entry, verdict TODO or
not one of the three; FIXED/FLAG without a note; a row whose fingerprint changed since it was looked at (its pictures
or label changed: look again, `init` resets only those rows to TODO); a dropped row still on the sheet; no readable
ITEMS block. The fingerprint is the row's pictures (graphics/fulls/thumbs) and label — or label+desc for a row with
no pictures — so a rebuild that changes nothing he would see keeps the record valid.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from pathlib import Path

ITEMS_RE = re.compile(r'<script id="ITEMS"[^>]*>(.*?)</script>', re.S)
VERDICTS = ("OK", "FIXED", "FLAG")
PICTURE_KEYS = ("graphics", "fulls", "thumbs")
HOW = ("Look at every row yourself (or have a naive judge do it: a fresh Opus that did not make it, or "
       "gpt_consult.py for a big sheet), fix or drop what is obviously broken, then record it: "
       "`python3 src/RimMandrake/Utils/art/prereview.py init <sheet> --by seat:<SEAT>|judge:<model>` and fill each "
       "row's verdict OK/FIXED/FLAG + note, `caught`, `dropped`. Rule: standing_rulings.md \"Nothing reaches the owner unread\".")


def record_path(sheet: Path) -> Path:
    sheet = Path(sheet)
    return sheet.with_name(sheet.stem + ".prereview.json")


def items_of(html: str) -> list | None:
    m = ITEMS_RE.search(html)
    if not m:
        return None
    try:
        v = json.loads(m.group(1).replace("<\\/", "</"))
    except ValueError:
        return None
    return v if isinstance(v, list) else None


def fingerprint(item: dict) -> str:
    keys = [k for k in PICTURE_KEYS if item.get(k)] or ["desc"]
    body = {k: item.get(k) for k in ["label"] + keys}
    return hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()[:16]


def _rows(html: str) -> dict | None:
    items = items_of(html)
    if items is None:
        return None
    return {str(it.get("id")): fingerprint(it) for it in items if isinstance(it, dict) and it.get("id") is not None}


def verify(sheet) -> tuple[bool, str]:
    """(ok, message). ok only when every row on the sheet was looked at, as it is now, and given a verdict."""
    sheet = Path(sheet)
    rp = record_path(sheet)
    if not rp.is_file():
        return False, f"{sheet.name} has no pre-review record ({rp.name}). {HOW}"
    try:
        rec = json.loads(rp.read_text())
    except (OSError, ValueError) as e:
        return False, f"{rp.name} is unreadable ({e}). {HOW}"
    if not isinstance(rec, dict):
        return False, f"{rp.name} is not a JSON object. {HOW}"
    rows = _rows(sheet.read_text(errors="replace"))
    if not rows:
        return False, f"{sheet.name} has no readable ITEMS rows, so nothing can be shown as pre-reviewed"
    bad = []
    by = str(rec.get("looked_by") or "")
    if not re.fullmatch(r"(seat|judge):\S.*", by):
        bad.append(f"looked_by {by!r} is not 'seat:<SEAT>' or 'judge:<model>'")
    if not str(rec.get("caught") or "").strip():
        bad.append("'caught' is empty (one line for him; 'nothing' is a valid answer)")
    got = rec.get("rows") if isinstance(rec.get("rows"), dict) else {}
    dropped = {str(d.get("row")) for d in rec.get("dropped") or [] if isinstance(d, dict)}
    for rid, fp in rows.items():
        e = got.get(rid)
        if rid in dropped:
            bad.append(f"{rid}: listed as dropped but still on the sheet")
        elif not isinstance(e, dict):
            bad.append(f"{rid}: never looked at")
        elif e.get("verdict") not in VERDICTS:
            bad.append(f"{rid}: verdict {e.get('verdict')!r}")
        elif e.get("fp") != fp:
            bad.append(f"{rid}: changed since it was looked at")
        elif e["verdict"] != "OK" and not str(e.get("note") or "").strip():
            bad.append(f"{rid}: {e['verdict']} without a note")
    if bad:
        more = f" (+{len(bad) - 8} more)" if len(bad) > 8 else ""
        return False, f"{rp.name}: {len(bad)} problem(s): " + "; ".join(bad[:8]) + more + f". {HOW}"
    n = {v: sum(1 for r in rows if got[r]["verdict"] == v) for v in VERDICTS}
    return True, (f"pre-reviewed by {by}: {len(rows)} rows ({n['OK']} OK, {n['FIXED']} fixed, {n['FLAG']} flagged), "
                  f"{len(dropped)} dropped; caught: {rec['caught']}")


def init(sheet, by: str) -> Path:
    """Write or refresh the record: rows unchanged since their verdict keep it; new or changed rows become TODO."""
    sheet = Path(sheet)
    rows = _rows(sheet.read_text(errors="replace"))
    if rows is None:
        raise SystemExit(f"REFUSED prereview init: {sheet.name} has no readable ITEMS block")
    rp = record_path(sheet)
    try:
        old = json.loads(rp.read_text())
    except (OSError, ValueError):
        old = {}
    prev = old.get("rows") if isinstance(old.get("rows"), dict) else {}
    out = {}
    for rid, fp in rows.items():
        e = prev.get(rid)
        out[rid] = e if isinstance(e, dict) and e.get("fp") == fp else {"fp": fp, "verdict": "TODO", "note": ""}
    rec = {"sheet": sheet.name, "looked_by": by, "when": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "caught": old.get("caught", ""), "rows": out, "dropped": old.get("dropped") or []}
    rp.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
    todo = sum(1 for e in out.values() if e["verdict"] == "TODO")
    print(f"{rp}  {len(out)} rows, {todo} TODO")
    return rp


def selftest() -> int:
    import tempfile
    fails = 0

    def check(cond, what):
        nonlocal fails
        print(("PASS " if cond else "FAIL ") + what)
        fails += 0 if cond else 1

    def sheet_with(items):
        return "<html><body><script id=\"ITEMS\" type=\"application/json\">" + json.dumps(items) + "</script></body></html>"

    items = [{"id": "A", "label": "pump", "graphics": [{"res": "x", "cols": [{"faces": {"south": "s1"}}]}]},
             {"id": "B", "label": "rule two", "desc": "text only"}]
    with tempfile.TemporaryDirectory() as td:
        sp = Path(td) / "t_sheet_2026-10-22.html"
        sp.write_text(sheet_with(items))
        ok, msg = verify(sp)
        check(not ok and "no pre-review record" in msg and "prereview.py init" in msg, "no record -> refused, names the fix")
        init(sp, "seat:BENCH")
        ok, msg = verify(sp)
        check(not ok and "verdict 'TODO'" in msg, "fresh init is all TODO -> refused")
        rp = record_path(sp)
        rec = json.loads(rp.read_text())
        rec["rows"]["A"]["verdict"] = "OK"
        rec["rows"]["B"]["verdict"] = "FLAG"
        rp.write_text(json.dumps(rec))
        ok, msg = verify(sp)
        check(not ok and "FLAG without a note" in msg and "'caught' is empty" in msg, "FLAG needs a note; caught required")
        rec["rows"]["B"]["note"] = "rule text contradicts rule 4"
        rec["caught"] = "nothing"
        rp.write_text(json.dumps(rec))
        ok, msg = verify(sp)
        check(ok and "2 rows" in msg, f"complete record -> OK ({msg[:60]})")
        rec["looked_by"] = "BENCH"
        rp.write_text(json.dumps(rec))
        check(not verify(sp)[0], "looked_by without seat:/judge: -> refused")
        rec["looked_by"] = "judge:claude-opus-5-5"
        rp.write_text(json.dumps(rec))
        check(verify(sp)[0], "judge:<model> accepted")
        # a rebuild that changes a picture invalidates that row only; unchanged-content rebuild keeps the record
        sp.write_text(sheet_with(items))
        check(verify(sp)[0], "identical rebuild keeps the record valid")
        items2 = json.loads(json.dumps(items))
        items2[0]["graphics"][0]["cols"][0]["faces"]["south"] = "s2"
        sp.write_text(sheet_with(items2))
        ok, msg = verify(sp)
        check(not ok and "A: changed since it was looked at" in msg, "changed picture -> that row refused")
        init(sp, "judge:claude-opus-5-5")
        rec = json.loads(rp.read_text())
        check(rec["rows"]["A"]["verdict"] == "TODO" and rec["rows"]["B"]["verdict"] == "FLAG",
              "re-init resets only the changed row")
        rec["rows"]["A"]["verdict"] = "FIXED"
        rec["rows"]["A"]["note"] = "hose now meets reel"
        rec["dropped"] = [{"row": "B", "why": "contradicts rule 4"}]
        rp.write_text(json.dumps(rec))
        ok, msg = verify(sp)
        check(not ok and "dropped but still on the sheet" in msg, "dropped row still on the sheet -> refused")
        sp.write_text(sheet_with(items2[:1]))
        ok, msg = verify(sp)
        check(ok and "1 dropped" in msg, "dropped row removed -> OK")
        sp.write_text("<html>no items</html>")
        check(not verify(sp)[0], "no ITEMS -> refused")
        rp.write_text("{not json")
        sp.write_text(sheet_with(items))
        check(not verify(sp)[0], "unreadable record -> refused")
    print(f"prereview selftest: {'GREEN' if not fails else f'{fails} FAIL'}")
    return 1 if fails else 0


def main(argv) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--selftest":
        return selftest()
    if argv[0] == "check" and len(argv) == 2:
        ok, msg = verify(Path(argv[1]))
        print(("OK " if ok else "REFUSED ") + msg, file=sys.stdout if ok else sys.stderr)
        return 0 if ok else 4
    if argv[0] == "init" and len(argv) == 4 and argv[2] == "--by":
        init(Path(argv[1]), argv[3])
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
