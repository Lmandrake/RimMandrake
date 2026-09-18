#!/usr/bin/env python3
"""Generate the validation-walk decision sheet for the owner.

Joins `modcheck lint` (40 FAIL) and `modcheck doctor` (41 FAIL) per WALK, because the
walk — not the individual finding — is the unit he decides. Emits:

    Transient/walk_decisions_sheet.html     the sheet (chrome from the review-sheets template)
    Transient/walk_decisions.json           the PRE-FILL (my calls, for him to overrule)

🔴 Re-running this OVERWRITES the pre-fill. Once he has reviewed, the decisions file is his,
not mine: this script refuses to clobber a file the sheet's plumbing has touched unless
--i-know-this-overwrites-the-owners-decisions is passed. Regenerating the HTML is always safe.

Why a sheet and not a sweep: §10.5 of the determinism assessment records that an automated
repointing sweep is what CREATED the subject-collisions `doctor` now reports. Nothing here is
applied; the sheet only collects his calls.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
UTILS = HERE
TEMPLATE = os.path.expanduser("~/.claude/skills/review-sheets/assets/sheet_template.html")
# The SHEET is regenerable and he reads it once -> Transient/. His DECISIONS are not:
# a file holding his rulings must never sit in a tree with a ~14-day shelf life, so it
# lives beside the walks it rules on.
OUT_HTML = os.path.join(ROOT, "Transient", "walk_decisions_sheet.html")
OUT_JSON = os.path.join(ROOT, "design", "validation_walks", "WALK_DECISIONS.json")


def live_mods():
    """{packageId: {folder, name}} for every mod that really ships.

    Identity, not existence: a folder is a mod only if it declares About/About.xml.
    `src/RimMandrake/Pits` passes os.path.isdir while holding only __pycache__.
    """
    out = {}
    for ax in glob.glob(os.path.join(ROOT, "src", "**", "About", "About.xml"), recursive=True):
        try:
            root = ET.parse(ax).getroot()
        except ET.ParseError:
            continue
        pid = (root.findtext("packageId") or "").strip()
        if pid:
            folder = ax.split(os.sep + "About" + os.sep)[0]
            out[pid.lower()] = {"folder": os.path.relpath(folder, ROOT),
                                "name": (root.findtext("name") or "").strip()}
    return out


def checker(verb):
    r = subprocess.run([sys.executable, "-m", "modcheck.cli", verb],
                       cwd=UTILS, capture_output=True, text=True)
    return r.stdout


def lint_by_walk():
    rows = {}
    lines = checker("lint").splitlines()
    for i, l in enumerate(lines):
        m = re.match(r"🔴 (\w+)\s+(\S+):(\d+)\s+`([^`]+)`", l)
        if not m:
            continue
        kind, path, ln, ident = m.groups()
        walk = os.path.relpath(path, ROOT)
        rows.setdefault(walk, []).append(
            {"kind": kind, "line": int(ln), "ident": ident,
             "detail": lines[i + 1].strip() if i + 1 < len(lines) else ""})
    return rows


def doctor_by_walk():
    rows, cur = {}, None
    for l in checker("doctor").splitlines():
        m = re.match(r"[🔴🟠] (\w+)\s+(.+)$", l)
        if m:
            kind, what = m.group(1), m.group(2).strip()
            cur = (kind, what)
            if what.startswith("/"):
                rows.setdefault(os.path.relpath(what, ROOT), []).append({"kind": kind, "what": what})
            else:
                rows.setdefault("_bymod:" + what, []).append({"kind": kind, "what": what})
        elif cur and l.startswith("    ") and not l.strip().startswith("remedy:"):
            key = (os.path.relpath(cur[1], ROOT) if cur[1].startswith("/") else "_bymod:" + cur[1])
            if rows.get(key):
                rows[key][-1].setdefault("why", l.strip())
    return rows


def collisions():
    """{mod folder: [walk basenames]} from doctor's SUBJECT_COLLISION.

    Keyed by the FOLDER, not by a walk path, and its detail line lists walk NAMES — so a
    parser that only understands path-keyed findings drops all 10 silently. These are the
    findings an automated repointing sweep created (assessment §10.5), which makes them the
    last thing that may be dropped from a sheet asking him to authorise repointing.
    """
    out, cur = {}, None
    for l in checker("doctor").splitlines():
        m = re.match(r"🔴 SUBJECT_COLLISION\s+(\S+)", l)
        if m:
            cur = m.group(1)
            continue
        if cur and l.startswith("    ") and " walks all declare subject:" in l:
            names = l.rsplit("--", 1)[-1]
            out[cur] = [n.strip() for n in names.split(",") if n.strip()]
            cur = None
    return out


SUBJECT_RE = re.compile(r"^subject:\s*(\S+)")
PID_RE = re.compile(r"packageId\s*`([^`]+)`")


def read_walk(path):
    """subject path, subject packageId, and whether the walk DECLARES it is not built.

    The subject line is found by SEARCHING, never by index: a sweep that read line 2
    reported zero failures across 78 walks while missing the one still broken, because
    AtmosphericBase.md carries `subject:` on line 3.
    """
    text = open(os.path.join(ROOT, path), encoding="utf-8").read()
    sub = pid = None
    for line in text.splitlines():
        m = SUBJECT_RE.match(line)
        if m and sub is None:
            sub = m.group(1)
            p = PID_RE.search(line)
            pid = p.group(1).lower() if p else None
            break
    head = text[:4000].upper()
    not_built = ("NOT BUILT" in head) or ("NOT-BUILT" in head)
    return sub, pid, not_built, text


def absorbed_into(dead_name, mods):
    """Where a retired mod's content actually went, by EVIDENCE not name similarity:
    a live mod carrying a subdirectory named after the dead one holds its defs.
    `FlowWorks/Defs/Pits/` is what proves Pits was absorbed into FlowWorks."""
    hits = []
    for pid, v in mods.items():
        for d in glob.glob(os.path.join(ROOT, v["folder"], "**", dead_name), recursive=True):
            if os.path.isdir(d):
                hits.append((pid, os.path.relpath(d, ROOT)))
                break
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--i-know-this-overwrites-the-owners-decisions", action="store_true",
                    dest="force")
    ap.add_argument("--html-only", action="store_true",
                    help="regenerate the sheet from the existing decisions (always safe)")
    a = ap.parse_args()

    mods = live_mods()
    lint, doc = lint_by_walk(), doctor_by_walk()
    coll = collisions()
    in_collision = {name: folder for folder, names in coll.items() for name in names}
    walks = sorted(set(lint) | {k for k in doc if not k.startswith("_bymod:")})

    items, prefills = [], {}
    for walk in walks:
        sub, pid, not_built, _ = read_walk(walk)
        tier = walk.split(os.sep)[2] if len(walk.split(os.sep)) > 2 else "?"
        name = os.path.basename(walk)[:-3]
        findings = lint.get(walk, []) + doc.get(walk, [])
        kinds = sorted({f["kind"] for f in findings})
        vac = [f for f in findings if f.get("kind") == "VACUOUS"]
        subject_live = bool(pid and pid in mods)
        went = absorbed_into(name, mods) if not subject_live else []

        # ---- the consequence, and my call ----------------------------------------
        inferred = contested = False
        if not_built:
            effect = (f"Deliberately NOT BUILT — the walk says so itself, so its "
                      f"{len(findings)} finding(s) are by-design, not rot.")
            call, why = "markok", "walk declares NOT BUILT; annotate so the checker stops flagging it"
        elif went:
            target = went[0]
            effect = (f"Subject `{pid}` is gone; its content is in "
                      f"{os.path.basename(os.path.dirname(went[0][1]))or went[0][0]} "
                      f"(evidence: {went[0][1]}). {len(findings)} finding(s).")
            call, why = "repoint", f"absorbed into {target[0]} — proven by {target[1]} on disk"
            contested = True
        elif vac and subject_live:
            effect = (f"Subject ships, but {len(vac)} step(s) assert the ABSENCE of an id "
                      f"that exists nowhere — they can never fail.")
            call, why = "repoint", "live mod with a vacuous step: fix the identifier"
        elif not subject_live:
            effect = (f"Subject `{pid or '?'}` is declared by no About.xml and no live mod "
                      f"carries its content. {len(findings)} finding(s): {', '.join(kinds)}.")
            call, why = "delete", "no subject and no absorber found — nothing left to validate"
            inferred = True
            contested = True
        else:
            effect = f"{len(findings)} finding(s): {', '.join(kinds)}. Subject ships."
            call, why = "repoint", "subject is live; the finding is in the step text"

        # Pits is spoken for by a ruling — refuse to pre-fill it.
        if name == "Pits":
            effect = ("12 VALIDATED bars, and PIT_SUPERDEEP_COLLAPSE_1 rewrites them: several "
                      "are claims about a `Building` the ruling retires. Do NOT move as-is.")
            call, why = None, "blocked by PIT_SUPERDEEP_COLLAPSE_1 — left undecided on purpose"
            contested = True

        # A walk sharing its subject folder is UNREACHABLE by `modcheck run` unless it wins
        # the basename — decide-relevant, so it rides on the row rather than in a second sheet.
        if name in in_collision:
            peers = [p for p in coll[in_collision[name]] if p != name]
            effect += f" ⚠ Also collides on subject with {len(peers)} other walk(s): {', '.join(peers)}."

        items.append({"id": walk, "label": f"{name}", "group": tier, "effect": effect,
                      "inferred": inferred, "contested": contested,
                      **({"prefill": call} if call else {})})
        prefills[walk] = {"decision": call or "", "prefill": call or "", "note": why}

    # ---- one row per collision GROUP: a different question from any single walk ----------
    for folder, names in sorted(coll.items()):
        rid = "collision:" + folder
        winner = sorted(names)[0]
        items.append({
            "id": rid, "label": os.path.basename(folder), "group": "SUBJECT COLLISION",
            "effect": (f"{len(names)} walks all declare subject `{folder}` — "
                       f"{', '.join(names)}. Only one basename is reachable by `modcheck run`, "
                       f"so the rest validate nothing no matter what they say."),
            "contested": True, "inferred": False, "prefill": "featurekey"})
        prefills[rid] = {"decision": "featurekey", "prefill": "featurekey",
                         "note": (f"keep them as per-feature walks under a new `feature:` key rather "
                                  f"than losing {len(names) - 1} of them; merging into {winner} "
                                  f"would concatenate bars written for different features")}

    cfg = {
        "sheetId": "walk_decisions_20260918",
        "title": "Validation walks — repoint, delete, or mark OK",
        "subtitle": f"{len(items)} walks · modcheck lint 40 FAIL + doctor 41 FAIL",
        "briefHtml": (
            "<p><b>What this is.</b> Two new deterministic checkers (<code>modcheck lint</code> "
            "and <code>modcheck doctor</code>) found 81 failures across the validation walks. "
            "Almost all of it is one story: mods were absorbed into other mods, and their walks "
            "stayed behind. A walk left pointing at a mod that no longer exists still <i>looks</i> "
            "like coverage while asserting nothing.</p>"
            "<p><b>Why you are being asked instead of told.</b> §10.5 of the determinism "
            "assessment records that an <i>automated</i> repointing sweep is what CREATED the 10 "
            "subject-collisions <code>doctor</code> now reports. So nothing here is applied. "
            "Each row is one walk, pre-filled with my call; overrule it and the note is what I act on.</p>"
            "<p><b>The four calls.</b> <b>Repoint</b> — the mod moved, fix the walk to name where "
            "it went. <b>Merge</b> — fold these bars into the absorbing mod's own walk, then delete "
            "this one. <b>Delete</b> — nothing left to validate. <b>Mark OK</b> — the finding is "
            "correct but deliberate (a walk for a mod not built yet), so annotate it and let the "
            "checker go quiet. <b>feature: key</b> — for the SUBJECT COLLISION group only: several "
            "walks claim one mod folder, so keep them as per-feature walks under a new "
            "<code>feature:</code> key instead of losing all but one.</p>"
            "<p><b>Two kinds of row.</b> The tier groups (RimMandrake / RimStarWars / RimUtinni) "
            "are one row per walk. The <b>SUBJECT COLLISION</b> group is one row per contested mod "
            "folder — a different question, and a walk can legitimately appear in both, because "
            "\"where should this walk point\" and \"which of six walks owns this folder\" are not "
            "the same decision.</p>"
            "<p>⚠️ <b>A repoint is not free.</b> A walk's bars were written against a specific mod; "
            "moving them can quietly strengthen or weaken something already validated. That is why "
            "every repoint row is marked contested.</p>"),
        "criterion": ("Sorted by tier, then name. My call ranks what is MECHANICALLY recoverable — "
                      "whether an absorber can be proven on disk. It cannot rank whether a walk's "
                      "bars are still worth keeping, which is the actual question on a merge."),
        "invented": [
            "\"Absorbed into X\" is inferred from a live mod carrying a subdirectory named after "
            "the dead mod (e.g. FlowWorks/Defs/Pits/ ⇒ Pits went to FlowWorks). That is real "
            "evidence of where the DEFS went — it is NOT evidence that the walk's bars still hold "
            "there. I did not verify a single bar against the absorbing mod's behaviour.",
            "Rows marked ⚠ inferred had no absorber found at all. \"Delete\" there is my guess "
            "that nothing is left, not a finding.",
            "I pre-filled Pits as UNDECIDED on purpose: PIT_SUPERDEEP_COLLAPSE_1 rewrites its 12 "
            "bars, so any call now would be overtaken.",
        ],
        "posture": {"mode": "blacklist",
                    "explain": ("Default is DO NOTHING. A walk you leave undecided stays exactly as "
                                "it is — still failing the checker, still asserting nothing. Only "
                                "decided rows get acted on.")},
        "options": [
            {"key": "repoint", "label": "Repoint", "hotkey": "1", "color": "#6aa6e8", "counts": "out"},
            {"key": "merge",   "label": "Merge",   "hotkey": "2", "color": "#5ac37f", "counts": "out"},
            {"key": "delete",  "label": "Delete",  "hotkey": "3", "color": "#e06c6c", "counts": "out"},
            {"key": "markok",  "label": "Mark OK", "hotkey": "4", "color": "#e8b64c", "counts": "in"},
            {"key": "featurekey", "label": "feature: key", "hotkey": "5", "color": "#b08cf0",
             "counts": "out"},
        ],
        "groupLabel": "tier",
        "media": False,
        "decisionsFile": "WALK_DECISIONS.json",
        "decisionsPath": OUT_JSON,
        "sheetPath": OUT_HTML,
    }

    html = open(TEMPLATE, encoding="utf-8").read()
    html = re.sub(r'(<script id="CONFIG" type="application/json">\n).*?(\n</script>)',
                  lambda m: m.group(1) + json.dumps(cfg, indent=2, ensure_ascii=False) + m.group(2),
                  html, count=1, flags=re.S)
    html = re.sub(r'(<script id="ITEMS" type="application/json">\n).*?(\n</script>)',
                  lambda m: m.group(1) + json.dumps(items, indent=1, ensure_ascii=False) + m.group(2),
                  html, count=1, flags=re.S)
    open(OUT_HTML, "w", encoding="utf-8").write(html)
    print(f"wrote {os.path.relpath(OUT_HTML, ROOT)}  ({len(items)} rows)")

    if a.html_only:
        print("--html-only: pre-fill left untouched")
        return 0
    if os.path.exists(OUT_JSON) and not a.force:
        cur = json.load(open(OUT_JSON))
        if cur.get("touchedBySheet") or cur.get("savedBy") or cur.get("writeCount"):
            print("REFUSED: the decisions file has been touched by the sheet — those are HIS "
                  "calls, not my pre-fill. Re-run with "
                  "--i-know-this-overwrites-the-owners-decisions if you really mean it.")
            return 2
    json.dump({"posture": "blacklist", "sheetId": cfg["sheetId"], "decisions": prefills},
              open(OUT_JSON, "w"), indent=1)
    n = sum(1 for v in prefills.values() if v["decision"])
    print(f"wrote {os.path.relpath(OUT_JSON, ROOT)}  ({n}/{len(prefills)} pre-filled, "
          f"{len(prefills) - n} deliberately undecided)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
