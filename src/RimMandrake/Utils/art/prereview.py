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
     "criteria": [<every line of CRITERIA: what the looker checked each row against; init writes them>],
     "rows": {"<row id>": {"fp": "<row fingerprint>", "verdict": "OK" | "FIXED" | "FLAG", "note": "<what was seen>"}},
     "dropped": [{"row": "<row id>", "why": "<what was broken>"}]}

  OK    = looked at, nothing obviously broken.    FIXED = was broken, fixed, looked at again (note says what).
  FLAG  = cannot be judged by an agent, or a doubt he must see (note says what) — the row still reaches him.
  A broken row that is not fixed is DROPPED: removed from the sheet and listed under "dropped".

CRITERIA — what every row is checked against (owner, 2026-10-26: "It was making me choose between different objects for
bottles and barrels." / "The choice between wrecked and repaired is also coupled."): it renders and is recognisable;
EVERY CANDIDATE IN A QUESTION DEPICTS THE SAME OBJECT (no tint previews, no grid of style x liquid, no second object in
one choice); COUPLED STATES ARE OFFERED AS SETS (a building's Wrecked/Kludged/Repaired is one question whose options are
whole sets, never three separate picks that can mix machines). Two of these are also checked by code, shape_problems():
  MIXED    a pickable lane whose render ids vary on two or more name parts at once (style x liquid), or a column whose
           prompt says it is a preview that is never installed;
  COUPLED  two or more rows that are states of one thing (<stem>_Wrecked / _Kludged / _Repaired / ...) not tagged with
           one `stateSet` (art_sheet.py tags them; sheet_to_artifact.py then shows each set as ONE question).

REFUSED when: no record; the record does not list every CRITERIA line (`init` adds them, keeping verdicts: re-look
against them); a MIXED or COUPLED row (fix the sheet: drop the previews, rebuild so states are one set); looked_by not `seat:`/`judge:`; caught missing; a sheet row with no entry, verdict TODO or
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
CRITERIA = (
    "renders, and is recognisable as the named thing",
    "every candidate in a question depicts the same object",
    "coupled states are offered as sets",
    "does not repeat a ruling he already made",
)
STATE_WORDS = ("Wrecked", "Ruined", "Broken", "Damaged", "Derelict", "Kludged", "Patched", "Jury", "Repaired", "Restored",
               "Pristine", "Working")
STATE_RE = re.compile(r"^(?P<stem>.+?)_(?P<state>" + "|".join(STATE_WORDS) + r")$")
PREVIEW_RE = re.compile(r"preview only|never install", re.I)
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


def _render_id(col: dict) -> str | None:
    lab = str(col.get("short") or col.get("label") or "")
    m = re.match(r"\s*render\s+(\S+)", lab)
    return m.group(1) if m else None


def state_of(row_id: str) -> tuple[str, str] | None:
    """(stem, state) for a row that is one state of a stateful thing (RM_DesalPlant_Wrecked), else None."""
    m = STATE_RE.match(str(row_id))
    return (m.group("stem"), m.group("state")) if m else None


def shape_problems(items: list) -> list[str]:
    """The two owner criteria a program can check. A list of problems, each naming its row; [] when well formed."""
    out = []
    for it in items:
        if not isinstance(it, dict):
            continue
        rid = str(it.get("id"))
        for g in it.get("graphics") or []:
            if (g.get("lane") or "slot") != "slot":
                continue
            cols = [c for c in g.get("cols") or [] if isinstance(c, dict)]
            prev = [c.get("letter") or "?" for c in cols if PREVIEW_RE.search(str(c.get("prompt") or "") + " " +
                                                                                str(c.get("detail") or ""))]
            if prev:
                out.append(f"{rid}: MIXED - set(s) {', '.join(prev)} are previews that are never installed, not candidates")
            ids = [re.sub(r"_v\d+$", "", r).lower().split("_") for r in map(_render_id, cols) if r]
            by_len = {}
            for parts in ids:
                by_len.setdefault(len(parts), []).append(parts)
            for parts in by_len.values():
                if len(parts) < 3:
                    continue
                varying = [i for i in range(len(parts[0])) if len({p[i] for p in parts}) > 1]
                if len(varying) >= 2:
                    axes = " x ".join("/".join(sorted({p[i] for p in parts})) for i in varying)
                    out.append(f"{rid}: MIXED - one choice offers {len(parts)} different objects ({axes})")
                    break
    groups = {}
    for it in items:
        st = state_of(it.get("id")) if isinstance(it, dict) else None
        if st:
            groups.setdefault(st[0], []).append(it)
    for stem, members in sorted(groups.items()):
        if len(members) < 2:
            continue
        loose = [str(m.get("id")) for m in members if m.get("stateSet") != stem]
        if loose:
            out.append(f"{stem}: COUPLED - states {', '.join(loose)} are separate rows, not one set (stateSet {stem!r})")
    return out


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
    html = sheet.read_text(errors="replace")
    rows = _rows(html)
    if not rows:
        return False, f"{sheet.name} has no readable ITEMS rows, so nothing can be shown as pre-reviewed"
    bad = []
    have = rec.get("criteria") if isinstance(rec.get("criteria"), list) else []
    missing = [c for c in CRITERIA if c not in have]
    if missing:
        bad.append("not checked against: " + "; ".join(repr(c) for c in missing) + " (`init` adds them and keeps "
                   "verdicts; look at every row again against them)")
    bad += shape_problems(items_of(html) or [])
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
           "caught": old.get("caught", ""), "criteria": list(CRITERIA), "rows": out, "dropped": old.get("dropped") or []}
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
        # the owner's two shape criteria (2026-10-26): every record lists them, and the code checks what it can
        rec = json.loads(rp.read_text())
        rec.pop("criteria", None)
        rp.write_text(json.dumps(rec))
        sp.write_text(sheet_with(items2[:1]))
        ok, msg = verify(sp)
        check(not ok and "same object" in msg and "offered as sets" in msg, "record without the criteria -> refused")
        init(sp, "seat:BENCH")
        check(verify(sp)[0], "init adds the criteria and keeps the verdicts")
        grid = [{"letter": "A", "label": "IN GAME — FlowWorks"}] + [
            {"letter": chr(66 + i), "label": f"render liqcont_barrel_{st}_{lq}"}
            for i, (st, lq) in enumerate((s_, l_) for s_ in ("modern", "scrapper") for l_ in ("tar", "toxic"))]
        bad = shape_problems([{"id": "RM_Barrel", "graphics": [{"lane": "slot", "cols": grid}]}])
        check(len(bad) == 1 and "MIXED" in bad[0] and "modern/scrapper x tar/toxic" in bad[0],
              f"style x liquid grid in one choice -> MIXED ({bad})")
        same = [{"letter": "A", "label": "IN GAME"}, {"letter": "B", "label": "render RM_FerryPost_v1"},
                {"letter": "C", "label": "render RM_FerryPost_v2"}, {"letter": "D", "label": "render RM_FerryPost_v3"}]
        check(shape_problems([{"id": "RM_FerryPost", "graphics": [{"cols": same}]}]) == [],
              "several renders of one object -> well formed")
        prev = [{"letter": "A", "label": "IN GAME"}, {"letter": "B", "label": "render x", "prompt": "TINT PREVIEW ONLY (never install)"}]
        bad = shape_problems([{"id": "RM_Bottle", "graphics": [{"cols": prev}]}])
        check(len(bad) == 1 and "set(s) B are previews" in bad[0], f"a never-installed preview offered -> MIXED ({bad})")
        states = [{"id": f"RM_Pump_{s_}", "graphics": []} for s_ in ("Wrecked", "Kludged", "Repaired")] + [{"id": "RM_Pump"}]
        bad = shape_problems(states)
        check(len(bad) == 1 and "COUPLED" in bad[0] and "RM_Pump_Kludged" in bad[0], f"state rows not one set -> COUPLED ({bad})")
        for m in states[:3]:
            m["stateSet"] = "RM_Pump"
        check(shape_problems(states) == [], "state rows tagged as one stateSet -> well formed")
        check(shape_problems([{"id": "RM_Lone_Wrecked"}]) == [], "a single state row alone is not coupled")
        rp.write_text(json.dumps(json.loads(rp.read_text())))
        sp.write_text(sheet_with(items2[:1] + states[:1]))
        init(sp, "seat:BENCH")
        rec = json.loads(rp.read_text())
        rec["rows"]["RM_Pump_Wrecked"]["verdict"] = "OK"
        rp.write_text(json.dumps(rec))
        check(verify(sp)[0], "a stateSet-tagged row passes verify")
        states[0].pop("stateSet")
        states[1]["stateSet"] = None
        sp.write_text(sheet_with(items2[:1] + states[:2]))
        init(sp, "seat:BENCH")
        rec = json.loads(rp.read_text())
        for e in rec["rows"].values():
            e["verdict"] = "OK"
        rp.write_text(json.dumps(rec))
        ok, msg = verify(sp)
        check(not ok and "COUPLED" in msg, "verify refuses a sheet with coupled state rows")
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
