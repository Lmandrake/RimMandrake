#!/usr/bin/env python3
r"""selftest_arena_prompt_rewrites.py — bank-repair prompt rewrites (ARENA_BANK_REPAIR_THIN_PROMPTS_RESCUABLE).
Offline and fast; never runs a census, vet or reader.

  schema     load_prompt_rewrites: absent file -> {}; wrong schema, a blank field, a short sha, an item twice raise
  apply      apply_prompt_rewrite replaces prompt + criteria, sets prompt_source bank_repair and prompt_base_sha256;
             a changed base prompt or fix sha leaves the task untouched and returns why (stale)
  committed  the committed prompt_rewrites.json loads; no row names a fix-introduced test path or sha
  bank       against the live bank (<arena>/tasks + judge/hidden) when it exists: each row's base_prompt_sha256 and
             fix_sha match the task it rewrites, and the rewritten task trips no hidden check (Matcher over every
             hidden file, the census's own leak scan). A probe proves the scan can see. No bank -> UNMEASURED.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_tasks as A  # noqa: E402

FAILS = []


def check(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def _raises(fn):
    try:
        fn()
    except A.ArenaError:
        return True
    return False


def _row(**kw):
    r = {"item": "X_FIX_Y", "fix_sha": "a" * 40, "base_prompt_sha256": hashlib.sha256(b"old").hexdigest(),
         "prompt": "new prompt", "criteria": "new criteria", "reason": "thin", "judge": "PASS"}
    r.update(kw)
    return r


def t_schema(tmp: Path):
    check(A.load_prompt_rewrites(tmp / "absent.json") == {}, "absent file loads as no rewrites")

    def doc(rows, schema=A.PROMPT_REWRITES_SCHEMA):
        p = tmp / "rw.json"
        p.write_text(json.dumps({"schema": schema, "rewrite": rows}))
        return p
    check(set(A.load_prompt_rewrites(doc([_row()]))) == {"X_FIX_Y"}, "a valid row loads")
    check(_raises(lambda: A.load_prompt_rewrites(doc([_row()], schema="x/1"))), "wrong schema raises")
    check(_raises(lambda: A.load_prompt_rewrites(doc([_row(prompt="  ")]))), "blank prompt raises")
    check(_raises(lambda: A.load_prompt_rewrites(doc([_row(judge=None)]))), "missing judge raises")
    check(_raises(lambda: A.load_prompt_rewrites(doc([_row(fix_sha="abc1234")]))), "short fix sha raises")
    check(_raises(lambda: A.load_prompt_rewrites(doc([_row(base_prompt_sha256="0" * 63)]))), "short sha256 raises")
    check(_raises(lambda: A.load_prompt_rewrites(doc([_row(), _row()]))), "an item twice raises")
    check(_raises(lambda: A.load_prompt_rewrites(doc(["X"]))), "a non-object row raises")


def t_apply():
    base = {"prompt": "old", "criteria": "old", "prompt_source": "base_parent", "criteria_source": "title"}
    t = dict(base)
    check(A.apply_prompt_rewrite(t, _row(), "a" * 40) is None, "matching row applies")
    check(t["prompt"] == "new prompt" and t["criteria"] == "new criteria", "prompt and criteria replaced")
    check(t["prompt_source"] == "bank_repair" and t["prompt_base_sha256"] == _row()["base_prompt_sha256"]
          and "prompt_rewrites.json" in t["criteria_source"], "provenance recorded")
    t = dict(base, prompt="old, then edited")
    snap = dict(t)
    why = A.apply_prompt_rewrite(t, _row(), "a" * 40)
    check(bool(why) and t == snap, "changed base prompt: stale, task untouched (%s)" % why)
    t = dict(base)
    why = A.apply_prompt_rewrite(t, _row(), "b" * 40)
    check(bool(why) and t == base, "changed fix sha: stale, task untouched (%s)" % why)


def t_committed():
    rows = A.load_prompt_rewrites()
    check(len(rows) >= 1, "committed prompt_rewrites.json loads (%d rows)" % len(rows))
    for item, r in sorted(rows.items()):
        text = (r["prompt"] + "\n" + r["criteria"]).lower()
        check(r["fix_sha"][:7] not in text, "%s: text does not name its fix sha" % item)
    return rows


def t_bank(rows):
    root = A.arena_root()
    tasks, hdir = root / "tasks", root / "judge" / "hidden"
    if not (tasks.is_dir() and hdir.is_dir() and any(hdir.glob("RP_*.json"))):
        print("UNMEASURED bank: %s or %s not readable" % (tasks, hdir))
        return
    hidden = []
    for p in sorted(hdir.glob("RP_*.json")):
        h = json.loads(p.read_text())
        h.setdefault("task", p.stem)
        hidden.append(h)
    m = A.Matcher(hidden)
    probe_done, measured = False, 0
    for item, r in sorted(rows.items()):
        tp, hp = tasks / ("RP_%s.json" % item), hdir / ("RP_%s.json" % item)
        if not (tp.exists() and hp.exists()):
            print("UNMEASURED %s: not in the bank" % item)
            continue
        t, h = json.loads(tp.read_text()), json.loads(hp.read_text())
        src = t.get("prompt_source")
        if src == "bank_repair":          # the bank already holds the rewrite (census rerun after landing)
            check(t["prompt"] == r["prompt"] and t["criteria"] == r["criteria"]
                  and t.get("prompt_base_sha256") == r["base_prompt_sha256"] and h.get("fix_sha") == r["fix_sha"],
                  "%s: bank holds this rewrite (prompt, criteria, base sha256, fix sha)" % item)
            t2 = dict(t, prompt=r["prompt"], criteria=r["criteria"])    # scan the ROW's text, not the stored copy
        else:
            t2 = dict(t)
            why = A.apply_prompt_rewrite(t2, r, h.get("fix_sha") or "")
            check(why is None, "%s: row matches the bank's base prompt and fix sha (%s)" % (item, why or "fresh"))
        hits = m.hits(A._public_bytes(t2))
        check(not hits, "%s: rewritten task trips no hidden check %s" % (item, hits[:1]))
        leak = [c.get("path") for c in h.get("checks") or () if c.get("added")]
        if leak and not probe_done:
            probe = dict(t2, prompt=t2["prompt"] + " " + leak[0])
            check(bool(m.hits(A._public_bytes(probe))), "probe: the scan sees an added test path (%s)" % leak[0])
            probe_done = True
        probe = dict(t2, prompt=t2["prompt"] + " " + r["fix_sha"][:10])     # always available: the fix sha
        check(bool(m.hits(A._public_bytes(probe))), "%s probe: the scan sees its fix sha" % item)
        measured += 1
    check(measured == len(rows), "every row was measured against the bank (%d of %d)" % (measured, len(rows)))


def main():
    tmp = Path(tempfile.mkdtemp(prefix="rw_selftest_"))
    try:
        t_schema(tmp)
        t_apply()
        t_bank(t_committed())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
