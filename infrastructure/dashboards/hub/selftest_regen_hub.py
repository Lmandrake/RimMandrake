#!/usr/bin/env python3
"""selftest_regen_hub.py — regen_hub.py's validation core, offline.

    python3 infrastructure/dashboards/hub/selftest_regen_hub.py

⛔ LAUNCHES NOTHING. No subprocess, no real generator, no write inside the
repo — every fixture lives under a throwaway tempfile.mkdtemp() dir. Exercises
only the pure validation functions regen_hub.py's `--check` path (and every
other path, before it declares READY) relies on:

  1. A healthy JSON data file with `generatedAt` validates OK and reports age.
  2. A 0-byte file is EMPTY, not a silent pass — "a footnote" per CLAUDE.md.
  3. A JSON file that parses to `{}` is EMPTY too — parsing successfully is
     not the same as carrying real content.
  4. Invalid JSON syntax is caught and named.
  5. A JSON data file with no `generatedAt` field fails rather than reporting
     a fabricated age.
  6. A `generatedAt` with no timezone (a naive stamp that slipped through the
     contract) fails rather than silently comparing against an aware `now`.
  7. U+FFFD inside an HTML file is caught with the right line/col — this is
     the exact defect that blocked a real publish on 2026-09-13.
  8. A clean HTML file with no U+FFFD passes without being JSON-parsed (an
     .html file is not required to carry generatedAt).
  9. A missing source file is MISSING, not skipped.
 10. validate() aggregates correctly: any one failing file makes the whole
     set NOT ok, and total_bytes sums every file including failures.
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import regen_hub as rh  # noqa: E402

FAILS = []
TMP = tempfile.mkdtemp(prefix="regen_hub_selftest_")


def eq(got, want, what):
    if got != want:
        FAILS.append("%s: got %r, want %r" % (what, got, want))


def ok_(cond, what):
    if not cond:
        FAILS.append("%s: expected truthy" % what)


def write(name: str, content: str) -> str:
    p = os.path.join(TMP, name)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(content)
    return p


def write_bytes(name: str, content: bytes) -> str:
    p = os.path.join(TMP, name)
    with open(p, "wb") as fh:
        fh.write(content)
    return p


from pathlib import Path  # noqa: E402

# ---- 1. healthy JSON, generatedAt present -> ok, age reported -------------
good = write("good.json", json.dumps({"generatedAt": "2026-09-13T00:00:00Z", "n": 1}))
e = rh.validate_file("data/good.json", Path(good))
ok_(e.get("ok"), "healthy json validates ok")
ok_("ageHours" in e, "healthy json reports ageHours")
ok_(e.get("ageHours", -1) >= 0, "ageHours is non-negative for a past timestamp")

# ---- 2. 0-byte file is EMPTY, not a silent pass ----------------------------
empty_file = write("empty.json", "")
e = rh.validate_file("data/empty.json", Path(empty_file))
ok_(not e.get("ok"), "0-byte file must not validate ok")
ok_("EMPTY" in (e.get("error") or ""), "0-byte file error names EMPTY")

# ---- 3. JSON parses to {} -> EMPTY -----------------------------------------
empty_obj = write("emptyobj.json", "{}")
e = rh.validate_file("data/emptyobj.json", Path(empty_obj))
ok_(not e.get("ok"), "{} must not validate ok")
ok_("EMPTY" in (e.get("error") or ""), "{} error names EMPTY")

# ---- 4. invalid JSON syntax -------------------------------------------------
bad_json = write("bad.json", "{not json")
e = rh.validate_file("data/bad.json", Path(bad_json))
ok_(not e.get("ok"), "invalid JSON must not validate ok")
ok_("INVALID JSON" in (e.get("error") or ""), "invalid JSON error names INVALID JSON")

# ---- 5. missing generatedAt -------------------------------------------------
no_gen = write("nogen.json", json.dumps({"n": 1}))
e = rh.validate_file("data/nogen.json", Path(no_gen))
ok_(not e.get("ok"), "missing generatedAt must not validate ok")
ok_("generatedAt" in (e.get("error") or ""), "missing generatedAt error names the field")

# ---- 6. naive (no-timezone) generatedAt -------------------------------------
naive = write("naive.json", json.dumps({"generatedAt": "2026-09-13 00:00:00"}))
e = rh.validate_file("data/naive.json", Path(naive))
ok_(not e.get("ok"), "naive generatedAt must not validate ok")

# ---- 7. U+FFFD inside an HTML file, right line/col --------------------------
fffd_html = write_bytes("bad.html", "<html>\n<body>ok\nbroken�here</body>\n</html>".encode("utf-8"))
e = rh.validate_file("tabs/bad.html", Path(fffd_html))
ok_(not e.get("ok"), "U+FFFD in html must not validate ok")
ok_("U+FFFD" in (e.get("error") or ""), "U+FFFD error names it")
ok_("line 3" in (e.get("error") or ""), "U+FFFD error names the right line")

# ---- 8. clean HTML, no generatedAt required ---------------------------------
clean_html = write("clean.html", "<html><body>fine</body></html>")
e = rh.validate_file("tabs/clean.html", Path(clean_html))
ok_(e.get("ok"), "clean html with no generatedAt still validates ok")

# ---- 9. missing source file --------------------------------------------------
e = rh.validate_file("data/ghost.json", Path(os.path.join(TMP, "does_not_exist.json")))
ok_(not e.get("ok"), "a missing source file must not validate ok")
ok_("MISSING" in (e.get("error") or ""), "missing source error names MISSING")

# ---- 10. validate() aggregation: one bad file fails the whole set ----------
pub = {"data/good.json": Path(good), "data/empty.json": Path(empty_file),
       "tabs/clean.html": Path(clean_html)}
set_ok, entries, total_bytes = rh.validate(pub)
eq(set_ok, False, "one failing file must fail the whole set")
eq(len(entries), 3, "validate() returns one entry per published file")
expect_total = sum(os.path.getsize(p) for p in (good, empty_file, clean_html))
eq(total_bytes, expect_total, "total_bytes sums every file, including the failing one")

pub_all_good = {"data/good.json": Path(good), "tabs/clean.html": Path(clean_html)}
set_ok2, _, _ = rh.validate(pub_all_good)
eq(set_ok2, True, "an all-clean set validates ok")

if FAILS:
    print("FAIL selftest_regen_hub.py")
    for f in FAILS:
        print("  " + f)
    sys.exit(1)
print("ok  selftest_regen_hub.py — JSON contract, U+FFFD detection, missing "
      "files, and validate() aggregation, all offline against temp fixtures")
