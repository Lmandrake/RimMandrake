#!/usr/bin/env python3
"""make_research_delta.py - build the DELTA review sheet for RESEARCH_TREE_NORMALIZATION_1.

Owner ruling 2026-09-04 by card ("Delta sheet only"): the frozen deck round 3
covered tree placement; the remaining owner pass covers only what the deck never
showed him:
  1. every row whose current manifest fate differs from the 09-03 prefill sheet
  2. the faction-held rows and their holders
  3. the new RUT_Rites / RUT_Antiq rows

Reads:  infrastructure/output/research_manifest_draft.csv        (schema v2)
        design/Jawa/research_review/research_review_decisions.json  (09-03 prefill)
Writes: design/Jawa/research_review/research_delta_decisions.json   (PREFILL ONLY)
        design/Jawa/research_review/research_delta_review.html      (from the template)

GUARD: refuses to overwrite a decisions file the sheet has touched (savedBy /
writeCount are stamped only by the sheet's own plumbing, never by this script).
Override: --i-know-this-overwrites-the-owners-decisions
"""
import csv
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MANIFEST = ROOT / "infrastructure/output/research_manifest_draft.csv"
OLD_DECISIONS = HERE / "research_review_decisions.json"
OUT_DECISIONS = HERE / "research_delta_decisions.json"
OUT_SHEET = HERE / "research_delta_review.html"
TEMPLATE = Path.home() / ".claude/skills/review-sheets/assets/sheet_template.html"
import sys as _sys

_sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils"))
from game_paths import DEF_DUMP  # noqa: E402

DUMP = Path(DEF_DUMP) / "defs/ResearchProjectDef.json"
# the KotOR mod family: rows named after game characters are undecidable
# without knowing the gear they gate (owner, 2026-09-04: "I have no idea
# what this stuff is") - mine the recipes/things that name each row.
KOTOR_FOLDERS = ["2938932438", "3047371944", "3254370945"]
WORKSHOP = Path("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100")


def dump_labels():
    try:
        d = json.loads(DUMP.read_text())
        defs = d["defs"] if isinstance(d, dict) and "defs" in d else d
        return {x["defName"]: x.get("label", "") for x in defs}
    except OSError:
        return {}


def kotor_gates():
    """defName -> sorted list of item labels whose recipe/thing names the row.
    Direct references only: a row reached solely via an abstract ParentName
    (the Lightsaber_Crafting trap) will read low, so treat counts as a floor."""
    import re as _re

    gates = {}
    for folder in KOTOR_FOLDERS:
        base = WORKSHOP / folder
        if not base.exists():
            print("warning: KotOR folder %s missing - gear-gate annotations will "
                  "be incomplete for its rows" % base)
            continue
        for p in base.rglob("Defs/**/*.xml"):
            try:
                txt = p.read_text(errors="ignore")
            except OSError:
                continue
            for m in _re.finditer(r"<(ThingDef|RecipeDef)[^>]*>.*?</\1>", txt, _re.S):
                block = m.group(0)
                rows = set(_re.findall(r"guy762_ResearchKotOR_\w+", block))
                if not rows:
                    continue
                lab = _re.search(r"<label>([^<]+)</label>", block)
                name = _re.search(r"<defName>([^<]+)</defName>", block)
                what = lab.group(1) if lab else (name.group(1) if name else "?")
                for rr in rows:
                    gates.setdefault(rr, set()).add(what)
    return {k: sorted(v) for k, v in gates.items()}


def cut_group(note: str) -> str:
    n = note.lower()
    if "mechanoid" in n:
        return "Cut - all mechanoid research (your frozen deck, 2026-09-04)"
    if "anomaly row" in n or "anomaly" in n:
        return "Cut - Anomaly rows (rule 5: content stays, research goes)"
    if "saber" in n or "force" in n or "jedi" in n or "sith" in n:
        return "Cut - lightsaber / Force tech (nobody teaches it)"
    if "droid" in n or "unbolting" in n:
        return "Cut - droid construction (Free Droid Enclave-owned)"
    if "no specific sitting ruling found" in n:
        return "Cut by the MODEL - no ruling of yours covers these; overrule freely"
    return "Cut - other (v4 model / deck)"


def cut_reason(note: str) -> str:
    # lead with the consequence; the note column carries provenance prose
    first = note.split("|")[0].strip()
    if first.startswith("owner frozen deck"):
        return "deck ruling: " + first.split(":", 1)[1].strip()
    return first


def main() -> int:
    force = "--i-know-this-overwrites-the-owners-decisions" in sys.argv
    touched = False
    if OUT_DECISIONS.exists():
        doc = json.loads(OUT_DECISIONS.read_text())
        touched = bool(doc.get("savedBy") or doc.get("writeCount"))
    if touched and force:
        touched = False
    # A touched decisions file holds the OWNER'S choices: the sheet is still
    # regenerated (the renderer is always safe to refresh mid-review), but the
    # decisions file is only MERGED - new row keys added, dropped rows removed,
    # every existing decision and provenance key preserved.

    header = MANIFEST.open().readline().strip()  # "# fingerprint=... capturedUtc=..."
    with MANIFEST.open() as f:
        next(f)
        rows = list(csv.DictReader(f))
    old = json.loads(OLD_DECISIONS.read_text())["decisions"]
    labels = dump_labels()
    gates = kotor_gates()

    items, seen = [], set()

    def add(row, group, effect, prefill="accept", **flags):
        # First category wins; a row also qualifying later (e.g. a NEW row that
        # is also faction-held) keeps its first group but the later pass's info
        # is appended to the effect line rather than silently dropped.
        if row["defName"] in seen:
            for it in items:
                if it["id"] == row["defName"]:
                    it["effect"] += " · also: " + group
                    break
            return True
        seen.add(row["defName"])
        dn = row["defName"]
        g = gates.get(dn)
        if g:
            effect += " · gates: " + ", ".join(g[:4]) + (
                " +%d more" % (len(g) - 4) if len(g) > 4 else ""
            )
        it = {
            "id": dn,
            "label": labels.get(dn) or dn,
            "group": group,
            "effect": effect,
            "prefill": prefill,
            "meta": {"mod": row["source_mod"]} if row["source_mod"] else {},
        }
        if "no specific sitting ruling found" in row["note"]:
            it["contested"] = True
        it.update(flags)
        items.append(it)
        return False

    # counts below are of rows actually RENDERED in each group (post-dedup),
    # so the briefHtml's numbers always match the page.
    # 1. new rows (Rites / Antiquities) - show these first
    n_new = 0
    for r in rows:
        if r["defName"] in old:
            continue
        if not add(
            r,
            "NEW rows - The Rites & Antiquities (authored 2026-09-04)",
            "NEW %s %s, cost %s - %s" % (r["tab"], r["tier"], r["cost"], cut_reason(r["note"])),
        ):
            n_new += 1

    # 2. faction-held rows, grouped by holder
    n_fh, n_defaulted = 0, 0
    for r in rows:
        if r["access"] != "faction-held":
            continue
        inferred = "no specific sitting ruling found" in r["note"]
        if not add(
            r,
            "Faction-held by %s - earned via techprints, never bought" % (r["holder"] or "?"),
            "%s %s cost %s - locked behind %s techprints. accept = ships locked to this holder"
            % (r["tab"], r["tier"], r["cost"], r["holder"] or "?"),
            inferred=inferred,
        ):
            n_fh += 1
            n_defaulted += inferred

    # 3. fate changed since the 09-03 prefill (all untouched -> cut today)
    n_cut = 0
    for r in rows:
        o = old.get(r["defName"])
        if not o or o["prefill"] == r["fate"]:
            continue
        if not add(
            r,
            cut_group(r["note"]),
            "was '%s' on 09-03, now '%s'. %s" % (o["prefill"], r["fate"], cut_reason(r["note"])),
        ):
            n_cut += 1

    prefill_decisions = {
        it["id"]: {"decision": it["prefill"], "prefill": it["prefill"], "note": ""}
        for it in items
    }
    if not touched:
        OUT_DECISIONS.write_text(
            json.dumps(
                {
                    "posture": "confirm-delta",
                    "criterion": (
                        "Delta vs what the frozen deck already showed - grouped by why "
                        "each row is here, not by quality. Prefill is ACCEPT everywhere: "
                        "this sheet exists to collect your overrides."
                    ),
                    "generatedBy": "make_research_delta.py",
                    "manifestFingerprint": header.lstrip("# ").strip(),
                    "decisions": prefill_decisions,
                },
                indent=2,
            )
            + "\n"
        )
    else:
        # merge: new row keys in, dropped rows out, his decisions untouched
        # Back up before any destructive merge: a row transiently absent from
        # the manifest would otherwise take the owner's recorded decision with
        # it, permanently and silently.
        backup = OUT_DECISIONS.with_suffix(".json.premerge-bak")
        backup.write_text(OUT_DECISIONS.read_text())
        doc = json.loads(OUT_DECISIONS.read_text())
        dec = doc.get("decisions", {})
        live = {it["id"] for it in items}
        dropped = [k for k in dec if k not in live]
        for k in dropped:
            del dec[k]
        for k, v in prefill_decisions.items():
            dec.setdefault(k, v)
        doc["decisions"] = dec
        OUT_DECISIONS.write_text(json.dumps(doc, indent=2) + "\n")
        print("MERGED decisions (sheet had been touched): his choices preserved; "
              "%d dropped row(s) %s; pre-merge backup at %s"
              % (len(dropped), dropped[:6], backup.name))

    config = {
        "sheetId": "research_delta_20260904",
        "title": "Research normalization - delta review",
        "subtitle": "the last owner pass on RESEARCH_TREE_NORMALIZATION_1",
        "briefHtml": (
            "<p><b>Everything the frozen deck (round 3, 2026-09-04) did NOT show you.</b> "
            "Three kinds of row: the %d NEW Rites/Antiquities rows, the %d faction-held rows "
            "and their holders, and the %d rows whose fate changed to <i>cut</i> since the "
            "09-03 sheet (your Anomaly / saber / droid / mechanoid rulings, applied). "
            "Prefill is <b>accept</b> on every row - click <b>wrong</b> and say what in the "
            "note. An unchanged row ships as shown.</p>"
        )
        % (n_new, n_fh, n_cut),
        "criterion": (
            "Grouped by WHY the row is on this sheet (new / holder / cut reason) - "
            "this orders explanation, not importance; it cannot rank what a row is worth to the campaign."
        ),
        "invented": [
            "%d of the %d faction-held rows carry 'no specific sitting ruling found' - "
            "their tab/tier was defaulted from the tier band by the manifest build, "
            "not ruled by you. They are marked 'inferred' and have their own filter."
            % (n_defaulted, n_fh),
        ],
        "posture": {
            "mode": "blacklist",
            "explain": (
                "Default is ACCEPT - every row ships exactly as written unless you "
                "mark it wrong. 'wrong' rows go back to BENCH with your note; nothing "
                "is stripped by leaving a row untouched."
            ),
        },
        "options": [
            {"key": "accept", "label": "Accept", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "wrong", "label": "Wrong", "hotkey": "2", "color": "#e06c6c", "counts": "out"},
        ],
        "groupLabel": "reason",
        "media": False,
        "decisionsFile": OUT_DECISIONS.name,
        "decisionsPath": str(OUT_DECISIONS),
        "sheetPath": str(OUT_SHEET),
    }

    html = TEMPLATE.read_text()
    import re

    for block, payload, indent in (("CONFIG", config, 2), ("ITEMS", items, 1)):
        pat = r'(<script id="%s" type="application/json">).*?(</script>)' % block
        html, n = re.subn(
            pat,
            lambda m, p=payload, i=indent: m.group(1) + "\n" + json.dumps(p, indent=i) + "\n" + m.group(2),
            html, count=1, flags=re.S,
        )
        if n != 1:
            sys.exit("REFUSING: template's %s block not found (matched %d) - the "
                     "sheet template markup changed; a silent no-op here ships a "
                     "data-less sheet." % (block, n))
    OUT_SHEET.write_text(html)
    print(
        "rows: %d (%d new, %d faction-held [%d inferred], %d cut-delta) -> %s"
        % (len(items), n_new, n_fh, n_defaulted, n_cut, OUT_SHEET)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
