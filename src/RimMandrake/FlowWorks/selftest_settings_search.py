#!/usr/bin/env python3
"""BLEED_WELL_STRINGS_RENAME_TAP_RETIRED -- the Flow Works settings search shows its hits, not blank rows (offline, no game).

Live 2026-10-22 (fw_gss_sitting): searching "bleed" in Mod Settings drew ~15 blank separator rows and never surfaced the
"Drilling and bleed wells" section in two scrolled frames. Cause, read in RimMandrakeFlowWorksMod.DoWindowContents:
  * every section's list.GapLine() was drawn OUTSIDE its Section(...) gate, so a hidden section left its separator behind;
  * sixteen blocks other classes draw (X.DoSettingsSection(list)) ignored the search and drew whole, so the hit sat below
    screens of unrelated settings;
  * the scroll position survived a new query, so the shrunken list could open mid-way down.
This checks, from source:
  1. no top-level list.GapLine() directly before an `if (Section(` -- the separator is drawn by Section when it shows;
  2. no bare X.DoSettingsSection(list) in DoWindowContents: each goes through Block(list, "<header>", X.DoSettingsSection),
     and <header> is a prefix of that block's own first list.Label (so a search for a word in the header finds it);
  3. the search box resets the scroll position when the query changes;
  4. the section "Drilling and bleed wells" exists and SettingsKitCore.Matches' rule (case-insensitive substring) hits it
     for "bleed" and "Bleed"; and each check above fails on a planted regression (can-fail).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
MOD = os.path.join(SRC, "RimMandrakeFlowWorksMod.cs")

FAILS = []


def check(name, ok, detail=""):
    print("  %-5s %s %s" % ("ok" if ok else "FAIL", name, detail if not ok else ""))
    if not ok:
        FAILS.append(name)


def body_of(src, sig):
    i = src.index(sig)
    j = src.index("{", i)
    d = 0
    for k in range(j, len(src)):
        d += {"{": 1, "}": -1}.get(src[k], 0)
        if d == 0:
            return src[j:k + 1]
    raise ValueError(sig)


def stray_gaplines(body):
    return re.findall(r"\n[ \t]*list\.GapLine\(\);\s*\n[ \t]*if \(Section\(list,", body)


def bare_blocks(body):
    return re.findall(r"^[ \t]*([\w.]+)\.DoSettingsSection\(list\);", body, re.M)


def first_label(cls):
    name = cls.split(".")[-1]
    for root, _, files in os.walk(SRC):
        for f in files:
            if not f.endswith(".cs"):
                continue
            t = open(os.path.join(root, f), encoding="utf-8").read()
            if not re.search(r"\bclass %s\b" % re.escape(name), t):
                continue
            k = t.find("static void DoSettingsSection", t.index("class %s" % name))
            if k < 0:
                continue
            m = re.search(r'\.Label\("((?:[^"\\]|\\.)*)"', t[k:])
            return m.group(1) if m else None
    return None


def matches(label, query):           # SettingsKitCore.Matches
    return not query.strip() or (label is not None and query.strip().lower() in label.lower())


def main():
    src = open(MOD, encoding="utf-8").read()
    body = body_of(src, "public void DoWindowContents(Rect inRect)")
    print("settings search (FlowWorks):")
    check("1 no separator outside a Section gate", not stray_gaplines(body), stray_gaplines(body)[:2])
    check("1 can-fail: a planted stray GapLine is caught",
          bool(stray_gaplines(body.replace('if (Section(list, "Swales"', 'list.GapLine();\n            if (Section(list, "Swales"', 1))))
    check("2 no block drawn past the search", not bare_blocks(body), bare_blocks(body))
    check("2 can-fail: a planted bare block is caught", bool(bare_blocks(body + "\n            Thirst.RM_ThirstSettings.DoSettingsSection(list);\n")))
    blocks = re.findall(r'Block\(list, "((?:[^"\\]|\\.)*)", ([\w.]+)\.DoSettingsSection\)', body)
    check("2 sanity: the gated blocks are seen (>= 10)", len(blocks) >= 10, len(blocks))
    drift = [(h, c, first_label(c)) for h, c in blocks if not (first_label(c) or "").startswith(h)]
    check("2 each Block header is its block's first Label", not drift, drift)
    check("2 can-fail: a drifted header is caught", not (first_label("Thirst.RM_ThirstSettings") or "").startswith("Drinking"))
    check("3 a new query resets the scroll", bool(re.search(r"if \(query != searchQuery\) scrollPosition = Vector2\.zero", body)))
    sec = re.search(r'Section\(list, "(Drilling and bleed wells)"', body)
    check("4 the drilling section is drawn by Section", bool(sec))
    title = sec.group(1) if sec else None
    check("4 'bleed' / 'Bleed' hit it", matches(title, "bleed") and matches(title, " Bleed "))
    check("4 can-fail: 'tap' (the retired word) does not", not matches(title, "tap"))
    gate = body_of(src, "private static bool Section(")
    check("1 Section draws its own separator after the search gate",
          gate.find("if (sectionsDrawn++ > 0) list.GapLine();") > gate.find("SectionHits(title, names, searchQuery)) return false;") > 0)
    print("settings search: %s" % ("PASS" if not FAILS else "FAIL (%d failing)" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
