# Narrative Dictionary Pilot (Batch 1) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build one vertical slice that proves — or disproves — that featurizing placeable objects by narrative role lets a generator dress a room whose story a naive viewer can read.

**Architecture:** A claim-primary index over defNames. Hand-authored vignettes are *predicates over featurization axes*, resolved at authoring time to concrete defNames; the dressing plan is composited to a PNG offline with PIL and read by a blind reviewer that never sees the brief or any filename. No intermediate role layer, no tile placement (that is `rimplace`'s job), no room scoring (that is `DUNGEON_RUBRIC.md`'s job).

**Tech Stack:** Python 3.12, stdlib + PIL 12.3 + PyYAML (both verified present on this machine). No .NET, no game, no bridge.

**Spec:** `design/RimMandrake/narrative_dictionary_design.md`

## Global Constraints

- **Offline machine.** No `dotnet`, no RimSage MCP, no def dump, no game, no bridge. Any claim about a def outside this repo's own XML is `UNMEASURED`.
- **defNames are the output.** No role vocabulary file. Generalisation lives in query predicates over the axes (spec §2a).
- **Claim-primary; mood filters and ranks.** Never a second vocabulary (spec §2, ruling 1).
- **Every ingredient carries a traceability grade.** An observable must encode its own cause. A claim may not rest solely on `LOW` traceability ingredients (spec §5a).
- **≥2 signals in different registers per claim.** Never two of the same register (spec §5b).
- **Premise-then-subtract**, never accumulate (spec §6).
- **Per-field provenance** on every sheet field: `VISION` | `DEF_TEXT` | `MEASURED` | `OWNER`.
- **Stewardship ⊥ abundance. Poverty never implies neglect** (spec §4c).
- **Connotation is ad hoc by finding**, not a principled axis; mood match is fuzzy, never equality (spec §4a).
- **Selftest convention:** file named `selftest*.py` under `src/`, must run as bare `python3 <path>`, and must include negative controls — "a check that cannot fail is worthless."
- **Git:** explicit paths, and the **pathspec goes on the `git commit`**, not only the `git add` (hook-enforced, shared index). Never `git add -A`.
- **Vanilla `techLevel` and vanilla defNames are mechanical** and out of scope for the archotech ruling.

## Decisions taken so this plan has no placeholders

The spec's §12 left four open. The owner said "yes for implementation," so they are decided here and flagged for override:

| Question | Decided | Why |
|---|---|---|
| Which room does batch 1 dress? | **Salvage bay, 13×9, `ROOM_KIND=service`** | Terrain is our strength (101 TerrainDefs) and event traces are absent, so floors and wrecks must carry the claim. |
| Who is the naive reviewer? | **Subagent on `haiku`**, image only | Genuine model separation: authoring is opus, judging is a different tier that never sees the brief. |
| Mapgen-time or authoring-time? | **Authoring-time only** | defNames bake into a flat plan; `rimplace verify` guards staleness (spec §3). |
| The unread retry sources? | **Task 1 reads them first** | They could still change the axes; cheaper to fold in before code than after. |

## File Structure

| Path | Responsibility |
|---|---|
| `src/RimMandrake/Utils/narrative/bar.py` | The pre-registered bar, as data. Written and committed before any dressing exists. |
| `src/RimMandrake/Utils/narrative/metrics.py` | Measure a sprite PNG: footprint, alpha coverage, contrast, silhouette distinctness → legibility grade. |
| `src/RimMandrake/Utils/narrative/sheets.py` | Object sheet schema, def-XML skeleton extraction, provenance, merge + validate. |
| `src/RimMandrake/Utils/narrative/contact.py` | Labelled contact sheets for the vision featurization pass. |
| `src/RimMandrake/Utils/narrative/vignettes.py` | Vignette schema, loader, and the two hard validators (traceability, registers). |
| `src/RimMandrake/Utils/narrative/query.py` | claim + mood + room_kind → dressing plan. Premise-then-subtract. Seeded. |
| `src/RimMandrake/Utils/narrative/compose.py` | Dressing plan → PNG at play zoom. Also the control dresser. |
| `src/RimMandrake/Utils/narrative/evaluate.py` | Build the four images, shuffle, dispatch reviewers, score against the bar. |
| `src/RimMandrake/Utils/narrative/selftest.py` | Every test in this plan. Bare-runnable. Negative controls throughout. |
| `infrastructure/state/narrative/objects.jsonl` | The sheets. Machine-written, regenerable. |
| `infrastructure/state/narrative/sprite_metrics.json` | Measured legibility. Machine-written. |
| `infrastructure/state/narrative/vignettes/*.yml` | Hand-authored compositions. |
| `infrastructure/state/narrative/PREREGISTERED_BAR.md` | The bar, in prose, committed before dressings exist. |
| `infrastructure/state/narrative/GAPS.md` | The deliverable that scopes `EVENT_TRACE_PROPS_LIBRARY_1`. |

---

### Task 1: Pre-register the bar, and fold in the unread literature

Pre-registration is only real if git timestamps it before any result exists. This task must land first.

**Files:**
- Create: `infrastructure/state/narrative/PREREGISTERED_BAR.md`
- Create: `src/RimMandrake/Utils/narrative/bar.py`
- Create: `src/RimMandrake/Utils/narrative/selftest.py`
- Modify: `design/RimMandrake/narrative_dictionary_design.md` (§12 item 4)

**Interfaces:**
- Produces: `bar.BAR` — a dict with keys `claim_recovery_ratio: float`, `false_claim_rule: str`, `min_intended_claims: int`; and `bar.verdict(dict_scores) -> str` returning one of `PASS` | `FAIL` | `PROXY_UNTRUSTWORTHY`.

- [ ] **Step 1: Read the 12 retry sources and record what changes**

Read every file in `/Users/mandrake/dev/GameDesignContent/sources/object_semantics_retry/` (or wherever the `2026-09-15_dungeon_spatial_story_retry` delivery was copied). Highest value: Don Carson's environmental-storytelling article, Valve's `Leading the player`, the Three Clue Rule, Liz England's "The Door Problem".

Then replace spec §12 item 4 with what they actually said, and if any of them contradicts or extends an axis in §4, amend §4 in the same edit. If nothing changes, write one line saying they were read and changed nothing — that is a legitimate outcome and must be recorded rather than left ambiguous.

- [ ] **Step 2: Write the bar as data**

```python
# src/RimMandrake/Utils/narrative/bar.py
"""The pre-registered bar for the narrative-dictionary pilot.

🔑 This file is committed BEFORE any dressing exists. That is the whole point:
a bar written after seeing results is not a bar. Do not edit it to accommodate
an outcome — if it turns out to be the wrong bar, say so in the verdict and
leave the number standing.
"""
from __future__ import annotations

BAR = {
    # The dictionary must recover at least this multiple of the control's
    # intended-claim count.
    "claim_recovery_ratio": 2.0,
    # ...while inventing no more false claims than the control did.
    "false_claim_rule": "dictionary_false <= control_false",
    # Below this, the sample is too thin to read either way.
    "min_intended_claims": 4,
}


def verdict(scores: dict) -> str:
    """Return PASS | FAIL | PROXY_UNTRUSTWORTHY from a scores dict.

    scores keys: dict_recovered, control_recovered, dict_false, control_false,
                 intended_total, proxy_agrees (bool or None)
    """
    if scores["intended_total"] < BAR["min_intended_claims"]:
        return "PROXY_UNTRUSTWORTHY"
    if scores.get("proxy_agrees") is False:
        return "PROXY_UNTRUSTWORTHY"
    if scores["dict_false"] > scores["control_false"]:
        return "FAIL"
    if scores["control_recovered"] == 0:
        return "PASS" if scores["dict_recovered"] > 0 else "FAIL"
    ratio = scores["dict_recovered"] / scores["control_recovered"]
    return "PASS" if ratio >= BAR["claim_recovery_ratio"] else "FAIL"
```

- [ ] **Step 3: Write the failing selftest, including negative controls**

```python
# src/RimMandrake/Utils/narrative/selftest.py
"""Selftest for the narrative dictionary. Runs bare: python3 selftest.py

🔑 Every negative control here exists because a check that cannot fail is
worthless.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bar  # noqa: E402

FAILS: list[str] = []


def check(name: str, cond: bool) -> None:
    if not cond:
        FAILS.append(name)


def test_bar_verdicts() -> None:
    base = dict(intended_total=6, proxy_agrees=True,
                dict_false=1, control_false=1)
    # passes: 2x recovery exactly at the bar
    check("bar_pass_at_ratio",
          bar.verdict({**base, "dict_recovered": 4,
                       "control_recovered": 2}) == "PASS")
    # NEGATIVE CONTROL: just under the bar must FAIL, or the bar is decorative
    check("bar_fails_under_ratio",
          bar.verdict({**base, "dict_recovered": 3,
                       "control_recovered": 2}) == "FAIL")
    # NEGATIVE CONTROL: more false claims must FAIL even at huge recovery
    check("bar_fails_on_false_claims",
          bar.verdict({**base, "dict_recovered": 99, "control_recovered": 1,
                       "dict_false": 5}) == "FAIL")
    # NEGATIVE CONTROL: a thin sample must not be reported as a pass
    check("bar_thin_sample_untrustworthy",
          bar.verdict({**base, "intended_total": 2, "dict_recovered": 9,
                       "control_recovered": 1}) == "PROXY_UNTRUSTWORTHY")
    # NEGATIVE CONTROL: owner disagreeing with the proxy overrides a pass
    check("bar_proxy_disagreement_wins",
          bar.verdict({**base, "proxy_agrees": False, "dict_recovered": 9,
                       "control_recovered": 1}) == "PROXY_UNTRUSTWORTHY")


def main() -> int:
    test_bar_verdicts()
    if FAILS:
        for f in FAILS:
            print("FAIL", f)
        print("%d FAILED" % len(FAILS))
        return 1
    print("narrative selftest: all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run it and confirm it passes**

Run: `python3 src/RimMandrake/Utils/narrative/selftest.py`
Expected: `narrative selftest: all checks passed`

Then prove the selftest itself can fail — temporarily change `claim_recovery_ratio` to `0.1`, re-run, and confirm `bar_fails_under_ratio` FAILS. Revert. A selftest you have never seen fail is not evidence.

- [ ] **Step 5: Confirm the runner discovers it**

Run: `python3 src/RimMandrake/Utils/run_selftests.py`
Expected: the summary count increases by one and the new file is **not** listed as SKIPPED. If it is skipped, the bare-run import is wrong — fix it rather than adding it to `NOT_STANDALONE`.

- [ ] **Step 6: Write the bar in prose**

Create `infrastructure/state/narrative/PREREGISTERED_BAR.md` stating, in plain language: the two claim sets, that the same room plan and object budget are used for all four dressings, that the control is random-within-job-category, that the reviewer sees only a PNG with no filenames, the exact numeric bar from `bar.py`, and the sentence: **"A failure means the dictionary is decoration. That is a real permitted outcome and the number does not move afterward."**

- [ ] **Step 7: Commit**

```bash
git add infrastructure/state/narrative/PREREGISTERED_BAR.md src/RimMandrake/Utils/narrative/bar.py src/RimMandrake/Utils/narrative/selftest.py
git commit infrastructure/state/narrative/PREREGISTERED_BAR.md src/RimMandrake/Utils/narrative/bar.py src/RimMandrake/Utils/narrative/selftest.py design/RimMandrake/narrative_dictionary_design.md -m "narrative dictionary: pre-register the bar before any dressing exists

Bar as data plus prose, with negative controls proving each clause can fail.
Retry literature read and folded into the spec."
```

---

### Task 2: Measure sprite legibility

Legibility is the one axis that is genuinely measurable offline, and it gates every claim-bearing placement.

**Files:**
- Create: `src/RimMandrake/Utils/narrative/metrics.py`
- Modify: `src/RimMandrake/Utils/narrative/selftest.py`
- Create: `infrastructure/state/narrative/sprite_metrics.json`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `metrics.measure(png_path: Path) -> dict` with keys `w, h, alpha_frac, rms_contrast, edge_density, legibility` where `legibility` ∈ `{"HIGH","MED","LOW"}`; and `metrics.measure_all(paths: list[Path]) -> dict[str, dict]` keyed by path string.

- [ ] **Step 1: Write the failing test**

```python
# add to selftest.py
import metrics  # noqa: E402
from PIL import Image  # noqa: E402
import tempfile  # noqa: E402


def _png(tmp: Path, name: str, size, fill) -> Path:
    p = tmp / name
    Image.new("RGBA", size, fill).save(p)
    return p


def test_metrics() -> None:
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        # a big opaque high-contrast block reads at a glance
        big = _png(tmp, "big.png", (128, 128), (250, 250, 250, 255))
        # NEGATIVE CONTROL: a fully transparent sprite must never be HIGH
        empty = _png(tmp, "empty.png", (128, 128), (0, 0, 0, 0))
        # NEGATIVE CONTROL: a tiny sprite must never be HIGH
        tiny = _png(tmp, "tiny.png", (4, 4), (250, 250, 250, 255))

        mb = metrics.measure(big)
        check("metrics_alpha_full", abs(mb["alpha_frac"] - 1.0) < 1e-6)
        check("metrics_big_not_low", mb["legibility"] in ("HIGH", "MED"))

        me = metrics.measure(empty)
        check("metrics_empty_alpha_zero", me["alpha_frac"] == 0.0)
        check("metrics_empty_is_low", me["legibility"] == "LOW")

        mt = metrics.measure(tiny)
        check("metrics_tiny_is_low", mt["legibility"] == "LOW")
```

- [ ] **Step 2: Run and confirm it fails**

Run: `python3 src/RimMandrake/Utils/narrative/selftest.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'metrics'`

- [ ] **Step 3: Implement**

```python
# src/RimMandrake/Utils/narrative/metrics.py
"""Measure how strongly a sprite reads at play zoom.

An object's narrative power is capped by whether it can be SEEN. A tell nobody
notices is wasted budget, and one that reads as something else is worse than
wasted (spec §4d, Gaver's hidden and false affordances).

⚠️ These are PROXY measures of a PNG on disk, not of the game's renderer. They
carry no lighting, no terrain blending, no fog. Treat a legibility grade as a
prior to be checked against a real screenshot, never as a settled fact.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageFilter

# A sprite smaller than this in either dimension cannot carry a claim at play
# zoom. 24px is one RimWorld tile at default zoom; below that a shape is a smudge.
_MIN_DIM = 24


def measure(png_path: Path) -> dict:
    im = Image.open(png_path).convert("RGBA")
    w, h = im.size
    alpha = im.getchannel("A")
    px = w * h
    opaque = sum(v * c for v, c in enumerate(alpha.histogram())) / (255.0 * px)

    grey = im.convert("L")
    hist = grey.histogram()
    total = sum(hist) or 1
    mean = sum(i * c for i, c in enumerate(hist)) / total
    var = sum((i - mean) ** 2 * c for i, c in enumerate(hist)) / total
    rms = (var ** 0.5) / 255.0

    edges = grey.filter(ImageFilter.FIND_EDGES)
    ehist = edges.histogram()
    edge_density = sum(ehist[32:]) / float(total)

    out = {
        "w": w, "h": h,
        "alpha_frac": round(opaque, 6),
        "rms_contrast": round(rms, 6),
        "edge_density": round(edge_density, 6),
    }
    out["legibility"] = _grade(out)
    return out


def _grade(m: dict) -> str:
    if m["alpha_frac"] <= 0.0:
        return "LOW"
    if m["w"] < _MIN_DIM or m["h"] < _MIN_DIM:
        return "LOW"
    if m["alpha_frac"] >= 0.25 and m["rms_contrast"] >= 0.12:
        return "HIGH"
    if m["alpha_frac"] >= 0.08:
        return "MED"
    return "LOW"


def measure_all(paths: list[Path]) -> dict:
    return {str(p): measure(p) for p in paths}


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pngs", nargs="+", type=Path)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    res = measure_all(a.pngs)
    text = json.dumps(res, indent=2, sort_keys=True)
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(text, encoding="utf-8")
        print("wrote %d measurements to %s" % (len(res), a.out))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run and confirm it passes**

Run: `python3 src/RimMandrake/Utils/narrative/selftest.py`
Expected: `all checks passed`

- [ ] **Step 5: Commit**

```bash
git add src/RimMandrake/Utils/narrative/metrics.py
git commit src/RimMandrake/Utils/narrative/metrics.py src/RimMandrake/Utils/narrative/selftest.py -m "narrative dictionary: measure sprite legibility offline

Footprint, alpha coverage, RMS contrast, edge density -> HIGH/MED/LOW. Negative
controls: transparent and tiny sprites can never grade HIGH. Documented as a
proxy for the real renderer, not a settled fact."
```

---

### Task 3: Object sheets — skeleton from def XML, with provenance

**Files:**
- Create: `src/RimMandrake/Utils/narrative/sheets.py`
- Modify: `src/RimMandrake/Utils/narrative/selftest.py`
- Create: `infrastructure/state/narrative/objects.jsonl`

**Interfaces:**
- Consumes: `metrics.measure_all`.
- Produces: `sheets.Sheet` (dataclass), `sheets.skeleton_from_defs(def_paths, only=None) -> list[Sheet]`, `sheets.load(path) -> list[Sheet]`, `sheets.save(sheets, path) -> None`, `sheets.validate(sheets) -> list[str]` (returns problem strings; empty means clean). Every axis field is a `dict` of `{"value": ..., "from": "VISION"|"DEF_TEXT"|"MEASURED"|"OWNER"}`.

- [ ] **Step 1: Write the failing test**

```python
# add to selftest.py
import sheets  # noqa: E402


def test_sheets() -> None:
    xml = """<Defs>
      <ThingDef>
        <defName>RUT_TestCrate</defName>
        <label>battered crate</label>
        <description>A crate. It has seen use.</description>
        <techLevel>Industrial</techLevel>
        <graphicData><texPath>Things/Item/Crate</texPath></graphicData>
      </ThingDef>
      <TerrainDef>
        <defName>RM_TestFloor</defName>
        <label>scuffed plate</label>
      </TerrainDef>
    </Defs>"""
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "Defs_x.xml"
        p.write_text(xml, encoding="utf-8")
        got = sheets.skeleton_from_defs([p])
        by = {s.defName: s for s in got}
        check("sheets_found_both", set(by) == {"RUT_TestCrate", "RM_TestFloor"})
        check("sheets_label_from_deftext",
              by["RUT_TestCrate"].label["from"] == "DEF_TEXT")
        check("sheets_deftype",
              by["RM_TestFloor"].defType == "TerrainDef")
        # unfilled vision axes must be explicitly absent, never guessed
        check("sheets_connotation_unfilled",
              by["RUT_TestCrate"].connotation["value"] == [])
        check("sheets_connotation_provenance_none",
              by["RUT_TestCrate"].connotation["from"] is None)

        # round-trip
        out = Path(d) / "objects.jsonl"
        sheets.save(got, out)
        check("sheets_roundtrip", len(sheets.load(out)) == 2)

        # NEGATIVE CONTROL: a filled value with no provenance must be REJECTED
        bad = sheets.load(out)
        bad[0].connotation = {"value": ["homey"], "from": None}
        check("sheets_validate_catches_missing_provenance",
              any("provenance" in m for m in sheets.validate(bad)))

        # NEGATIVE CONTROL: an invented provenance word must be REJECTED
        bad2 = sheets.load(out)
        bad2[0].connotation = {"value": ["homey"], "from": "VIBES"}
        check("sheets_validate_catches_bad_provenance",
              any("VIBES" in m for m in sheets.validate(bad2)))
```

- [ ] **Step 2: Run and confirm it fails**

Run: `python3 src/RimMandrake/Utils/narrative/selftest.py`
Expected: FAIL — no module named `sheets`

- [ ] **Step 3: Implement**

```python
# src/RimMandrake/Utils/narrative/sheets.py
"""Object sheets: one row per placeable defName, with per-field provenance.

🔑 A field records WHERE its value came from. VISION means an agent looked at
the sprite; DEF_TEXT means it was read off the def; MEASURED means a script
computed it; OWNER means he said so. A value with no provenance is a guess
wearing a fact's clothes, and validate() refuses it.

⚠️ objects.jsonl is a FUNCTION OF THE LIVE MOD SET, not an archive. Regenerate
it when the set changes rather than trusting it (spec §2a).
"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict, fields
from pathlib import Path

PROVENANCE = ("VISION", "DEF_TEXT", "MEASURED", "OWNER")

# Axes filled by looking (spec §4). Empty until a vision pass fills them.
_VISION_AXES = ("connotation", "spatial_function", "communicative_act",
                "message_depth", "state_space", "stewardship", "abundance",
                "emergent_use")


def _unfilled() -> dict:
    return {"value": [], "from": None}


@dataclass
class Sheet:
    defName: str
    defType: str
    label: dict = field(default_factory=_unfilled)
    description: dict = field(default_factory=_unfilled)
    techLevel: dict = field(default_factory=_unfilled)
    texPath: dict = field(default_factory=_unfilled)
    legibility: dict = field(default_factory=_unfilled)
    connotation: dict = field(default_factory=_unfilled)
    spatial_function: dict = field(default_factory=_unfilled)
    communicative_act: dict = field(default_factory=_unfilled)
    message_depth: dict = field(default_factory=_unfilled)
    state_space: dict = field(default_factory=_unfilled)
    stewardship: dict = field(default_factory=_unfilled)
    abundance: dict = field(default_factory=_unfilled)
    emergent_use: dict = field(default_factory=_unfilled)


_PLACEABLE = {"ThingDef", "TerrainDef"}


def skeleton_from_defs(def_paths, only=None) -> list[Sheet]:
    """Extract skeleton sheets. Fills only DEF_TEXT fields; never invents."""
    out: list[Sheet] = []
    for p in def_paths:
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        if root.tag != "Defs":
            continue
        for node in root:
            if not isinstance(node.tag, str) or node.tag not in _PLACEABLE:
                continue
            name = node.findtext("defName")
            if not name or (only and name not in only):
                continue
            s = Sheet(defName=name, defType=node.tag)
            for f, tag in (("label", "label"), ("description", "description"),
                           ("techLevel", "techLevel")):
                v = node.findtext(tag)
                if v:
                    setattr(s, f, {"value": v.strip(), "from": "DEF_TEXT"})
            tex = node.find("./graphicData/texPath")
            if tex is not None and tex.text:
                s.texPath = {"value": tex.text.strip(), "from": "DEF_TEXT"}
            out.append(s)
    return out


def save(rows: list[Sheet], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for r in sorted(rows, key=lambda s: s.defName):
            fh.write(json.dumps(asdict(r), sort_keys=True) + "\n")


def load(path: Path) -> list[Sheet]:
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(Sheet(**json.loads(line)))
    return rows


def validate(rows: list[Sheet]) -> list[str]:
    """Return human-readable problems. Empty list means clean."""
    problems: list[str] = []
    seen = set()
    for r in rows:
        if r.defName in seen:
            problems.append("duplicate defName: %s" % r.defName)
        seen.add(r.defName)
        for f in fields(r):
            if f.name in ("defName", "defType"):
                continue
            cell = getattr(r, f.name)
            if not isinstance(cell, dict) or "value" not in cell:
                problems.append("%s.%s is not a provenanced cell"
                                % (r.defName, f.name))
                continue
            filled = cell["value"] not in ([], "", None)
            src = cell.get("from")
            if filled and src is None:
                problems.append("%s.%s has a value but no provenance"
                                % (r.defName, f.name))
            if src is not None and src not in PROVENANCE:
                problems.append("%s.%s has unknown provenance %r"
                                % (r.defName, f.name, src))
    return problems
```

- [ ] **Step 4: Run and confirm it passes**

Run: `python3 src/RimMandrake/Utils/narrative/selftest.py`
Expected: `all checks passed`

- [ ] **Step 5: Generate the real skeleton for the pilot subset**

Choose the ~30 pilot defNames from the salvage-bay palette: every `TerrainDef` that can floor a salvage bay, the four rubble/wreck ThingDefs, the eleven filths, the four `RM_Graffiti_*` marks, and enough furniture (shelves, crates, a light, a workbench) to fill a 13×9 room. Write the list into the commit message so the choice is auditable.

Run:
```bash
python3 - <<'PY'
from pathlib import Path
import sys; sys.path.insert(0, "src/RimMandrake/Utils/narrative")
import sheets, metrics, json
defs = list(Path("src").rglob("Defs/**/*.xml"))
only = set(Path("infrastructure/state/narrative/pilot_defnames.txt").read_text().split())
rows = sheets.skeleton_from_defs(defs, only=only)
print("skeleton rows:", len(rows), "of", len(only), "requested")
missing = only - {r.defName for r in rows}
if missing: print("NOT FOUND (say so, do not substitute):", sorted(missing))
sheets.save(rows, Path("infrastructure/state/narrative/objects.jsonl"))
print("validate:", sheets.validate(rows) or "clean")
PY
```

If a requested defName is not found, report it as missing — **do not substitute a similar one.** Missing is data.

- [ ] **Step 6: Commit**

```bash
git add src/RimMandrake/Utils/narrative/sheets.py infrastructure/state/narrative/objects.jsonl infrastructure/state/narrative/pilot_defnames.txt
git commit src/RimMandrake/Utils/narrative/sheets.py src/RimMandrake/Utils/narrative/selftest.py infrastructure/state/narrative/objects.jsonl infrastructure/state/narrative/pilot_defnames.txt -m "narrative dictionary: object sheets with per-field provenance

Skeleton extraction fills DEF_TEXT fields only; vision axes stay explicitly
empty. validate() refuses a value with missing or invented provenance."
```

---

### Task 4: Labelled contact sheets for the vision pass

**Files:**
- Create: `src/RimMandrake/Utils/narrative/contact.py`
- Modify: `src/RimMandrake/Utils/narrative/selftest.py`

**Interfaces:**
- Consumes: `sheets.load`.
- Produces: `contact.build(rows, tex_roots, out_dir, per_sheet=48) -> list[Path]` and `contact.resolve_tex(texPath, tex_roots) -> list[Path]` (folder-aware: a `texPath` may name a file stem OR a directory of `Graphic_Random` variants).

- [ ] **Step 1: Write the failing test**

The folder-aware resolution is the part that already bit once — a naive resolver reported 68 unwired texPaths where the true number was 20, because `Graphic_Random` names a *folder*. Test that specifically.

```python
# add to selftest.py
import contact  # noqa: E402


def test_contact_resolution() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d) / "Textures"
        # a plain stem
        (root / "Things/Item").mkdir(parents=True)
        Image.new("RGBA", (64, 64), (200, 0, 0, 255)).save(
            root / "Things/Item/Crate.png")
        # a Graphic_Random FOLDER of variants
        (root / "Things/Filth/Art/RM_Mark").mkdir(parents=True)
        for i in range(3):
            Image.new("RGBA", (64, 64), (0, 200, 0, 255)).save(
                root / ("Things/Filth/Art/RM_Mark/mark_%d.png" % i))
        # a directional set
        (root / "Things/Building").mkdir(parents=True)
        for f in ("Bench_north.png", "Bench_south.png"):
            Image.new("RGBA", (64, 64), (0, 0, 200, 255)).save(
                root / "Things/Building" / f)

        check("contact_stem",
              len(contact.resolve_tex("Things/Item/Crate", [root])) == 1)
        check("contact_random_folder",
              len(contact.resolve_tex("Things/Filth/Art/RM_Mark", [root])) == 3)
        check("contact_directional",
              len(contact.resolve_tex("Things/Building/Bench", [root])) == 2)
        # NEGATIVE CONTROL: a genuinely absent path resolves to nothing,
        # and must NOT fall back to a near-match
        check("contact_absent_is_empty",
              contact.resolve_tex("Things/Item/Nope", [root]) == [])
```

- [ ] **Step 2: Run and confirm it fails**

Run: `python3 src/RimMandrake/Utils/narrative/selftest.py`
Expected: FAIL — no module named `contact`

- [ ] **Step 3: Implement**

```python
# src/RimMandrake/Utils/narrative/contact.py
"""Labelled contact sheets, so a vision pass can read many sprites at once.

🔑 texPath is folder-aware. For Graphic_Random it names a DIRECTORY of variants,
not a file stem — a resolver that assumes a stem reported 68 unwired texPaths
in this repo when the true count was 20. Directional sets append _north/_south/
_east/_west. Resolve all three shapes, and never fall back to a near-match:
absent is data.

These sheets ARE labelled with defNames, deliberately — the featurization pass
needs the mapping. The EVALUATION sheets in compose.py must not be.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

_SUFFIXES = ("_north", "_south", "_east", "_west",
             "_a", "_b", "_c", "_d", "_m", "_n")


def resolve_tex(tex_path: str, tex_roots) -> list[Path]:
    tex_path = (tex_path or "").strip().lstrip("/")
    if not tex_path:
        return []
    hits: list[Path] = []
    for root in tex_roots:
        root = Path(root)
        exact = root / (tex_path + ".png")
        if exact.is_file():
            hits.append(exact)
        folder = root / tex_path
        if folder.is_dir():
            hits.extend(sorted(folder.glob("*.png")))
        parent = (root / tex_path).parent
        stem = Path(tex_path).name
        if parent.is_dir():
            for suf in _SUFFIXES:
                cand = parent / (stem + suf + ".png")
                if cand.is_file():
                    hits.append(cand)
    seen, out = set(), []
    for h in hits:
        if h not in seen:
            seen.add(h)
            out.append(h)
    return out


def build(rows, tex_roots, out_dir: Path, per_sheet: int = 48) -> list[Path]:
    """One labelled tile per sprite. Returns the sheet paths written."""
    cell, pad, cols = 96, 26, 8
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    tiles: list[tuple[str, Path]] = []
    for r in rows:
        tex = r.texPath.get("value") if isinstance(r.texPath, dict) else None
        for p in resolve_tex(tex, tex_roots)[:1]:
            tiles.append((r.defName, p))
    written = []
    for n in range(0, len(tiles), per_sheet):
        chunk = tiles[n:n + per_sheet]
        rowsn = (len(chunk) + cols - 1) // cols
        img = Image.new("RGBA",
                        (cols * (cell + pad), rowsn * (cell + pad)),
                        (24, 24, 28, 255))
        d = ImageDraw.Draw(img)
        for i, (name, path) in enumerate(chunk):
            cx = (i % cols) * (cell + pad)
            cy = (i // cols) * (cell + pad)
            sp = Image.open(path).convert("RGBA")
            sp.thumbnail((cell, cell))
            img.alpha_composite(sp, (cx + (cell - sp.width) // 2, cy))
            d.text((cx + 2, cy + cell + 2), name[:22], fill=(230, 230, 230, 255))
        out = out_dir / ("contact_%02d.png" % (n // per_sheet))
        img.save(out)
        written.append(out)
    return written
```

- [ ] **Step 4: Run and confirm it passes**

Run: `python3 src/RimMandrake/Utils/narrative/selftest.py`
Expected: `all checks passed`

- [ ] **Step 5: Build the real sheets and measure legibility**

Build contact sheets for the pilot rows, and run `metrics.measure_all` over the resolved sprites, writing `infrastructure/state/narrative/sprite_metrics.json`. Then merge each sprite's `legibility` into its sheet with provenance `MEASURED`.

- [ ] **Step 6: Commit**

```bash
git add src/RimMandrake/Utils/narrative/contact.py infrastructure/state/narrative/sprite_metrics.json
git commit src/RimMandrake/Utils/narrative/contact.py src/RimMandrake/Utils/narrative/selftest.py infrastructure/state/narrative/sprite_metrics.json infrastructure/state/narrative/objects.jsonl -m "narrative dictionary: folder-aware contact sheets and measured legibility

resolve_tex handles all three texPath shapes (stem, Graphic_Random folder,
directional suffixes) and never falls back to a near-match."
```

---

### Task 5: Fill the vision axes by looking

This task is agent work, not code. Its deliverable is a filled `objects.jsonl` that passes `sheets.validate`.

**Files:**
- Modify: `infrastructure/state/narrative/objects.jsonl`
- Create: `infrastructure/state/narrative/VOCABULARY.md`

**Interfaces:**
- Consumes: the contact sheets from Task 4, `sheets.load/save/validate`.
- Produces: an `objects.jsonl` with every vision axis filled and provenanced, plus the controlled connotation vocabulary as a committed file.

- [ ] **Step 1: Write the controlled vocabulary down first**

Create `VOCABULARY.md` fixing the closed vocabularies verbatim from spec §4, so the featurization cannot drift into invented words:

- `spatial_function` ∈ {`path`, `edge`, `district`, `node`, `landmark`}
- `communicative_act` ∈ {`prohibition`, `mandatory`, `warning`, `safe_condition`, `fire_safety`, `none`}
- `message_depth` ∈ {`rudimentary`, `cautionary`, `basic`, `complex`}
- `state_space` ⊆ {`in_situ`, `disturbance`, `killed_object`, `midden`, `assemblage`, `fill`, `patina_acquired`, `patina_applied`}
- `stewardship` ∈ {`tended`, `neglected`, `abandoned`}
- `abundance` ∈ {`poor`, `modest`, `resourced`}
- `emergent_use` ∈ {`designed`, `worn_in`, `none`}
- `connotation`: **open tag list, ad hoc by finding** (spec §4a). Seed it from wabi-sabi's register (asymmetry, roughness, simplicity, economy, austerity, modesty, intimacy) and grow it. Every new tag gets appended to this file when first used, so the vocabulary is always readable.

- [ ] **Step 2: Dispatch the featurization pass**

For each contact sheet, dispatch a subagent with **the sheet image and the def text for those rows**, and this instruction shape:

> For each labelled sprite, fill only these axes, using only words from `VOCABULARY.md` except for `connotation` which is an open list. Say `UNSURE` for any axis you cannot judge from the image — an `UNSURE` is useful and a guess is not. For each axis, state whether you judged it from the IMAGE or from the DEF TEXT; those become the provenance. Where image and def text disagree, say so explicitly and do not reconcile them yourself.

Record `VISION` for image-judged fields, `DEF_TEXT` for text-judged. Leave `UNSURE` axes empty rather than filling them.

- [ ] **Step 3: Validate and record conflicts**

Run:
```bash
python3 - <<'PY'
import sys; sys.path.insert(0, "src/RimMandrake/Utils/narrative")
import sheets; from pathlib import Path
rows = sheets.load(Path("infrastructure/state/narrative/objects.jsonl"))
probs = sheets.validate(rows)
print("rows:", len(rows), "problems:", len(probs))
for p in probs[:20]: print(" ", p)
filled = sum(1 for r in rows if r.connotation["value"])
print("connotation filled: %d/%d" % (filled, len(rows)))
PY
```

Expected: `problems: 0`. Report the filled fraction honestly — a low fraction is a finding about the sprites, not a failure to be papered over.

- [ ] **Step 4: Commit**

```bash
git add infrastructure/state/narrative/VOCABULARY.md
git commit infrastructure/state/narrative/VOCABULARY.md infrastructure/state/narrative/objects.jsonl -m "narrative dictionary: featurize the pilot subset by looking

Closed vocabularies fixed before the pass so it cannot drift into invented
words. UNSURE axes left empty; image-vs-def-text conflicts recorded, not
reconciled."
```

---

### Task 6: Vignettes, and the two hard validators

**Files:**
- Create: `src/RimMandrake/Utils/narrative/vignettes.py`
- Create: `infrastructure/state/narrative/vignettes/*.yml` (8 files)
- Modify: `src/RimMandrake/Utils/narrative/selftest.py`

**Interfaces:**
- Consumes: `sheets.Sheet`.
- Produces: `vignettes.Vignette` (dataclass with `name, claim, fits, ingredients, registers`), `vignettes.load_dir(path) -> list[Vignette]`, `vignettes.validate(v) -> list[str]`, `vignettes.matches(ingredient, sheet) -> bool`.

- [ ] **Step 1: Write the failing test — the two rules must be able to reject**

```python
# add to selftest.py
import vignettes  # noqa: E402


def _ing(**kw):
    base = dict(predicate={"defType": "ThingDef"}, state="in_situ",
                placement="wall_hug", traceability="HIGH", register="state")
    base.update(kw)
    return base


def test_vignette_rules() -> None:
    ok = vignettes.Vignette(
        name="ok", claim="someone left in a hurry", fits=["service"],
        ingredients=[_ing(register="state"), _ing(register="placement")])
    check("vignette_ok", vignettes.validate(ok) == [])

    # NEGATIVE CONTROL: two signals in the SAME register is not redundancy
    same = vignettes.Vignette(
        name="same", claim="c", fits=["service"],
        ingredients=[_ing(register="state"), _ing(register="state")])
    check("vignette_rejects_same_register",
          any("register" in m for m in vignettes.validate(same)))

    # NEGATIVE CONTROL: a claim resting only on LOW traceability is refused
    low = vignettes.Vignette(
        name="low", claim="c", fits=["service"],
        ingredients=[_ing(register="state", traceability="LOW"),
                     _ing(register="placement", traceability="LOW")])
    check("vignette_rejects_all_low_traceability",
          any("traceability" in m for m in vignettes.validate(low)))

    # NEGATIVE CONTROL: a single ingredient can never satisfy two registers
    single = vignettes.Vignette(name="one", claim="c", fits=["service"],
                                ingredients=[_ing()])
    check("vignette_rejects_single_ingredient",
          vignettes.validate(single) != [])

    # NEGATIVE CONTROL: an unknown ROOM_KIND is a typo, not a new room type
    bad_fit = vignettes.Vignette(
        name="badfit", claim="c", fits=["throne_room"],
        ingredients=[_ing(register="state"), _ing(register="placement")])
    check("vignette_rejects_unknown_room_kind",
          any("throne_room" in m for m in vignettes.validate(bad_fit)))


def test_vignette_matching() -> None:
    s = sheets.Sheet(defName="X", defType="ThingDef")
    s.legibility = {"value": "HIGH", "from": "MEASURED"}
    s.stewardship = {"value": ["neglected"], "from": "VISION"}
    check("match_on_deftype",
          vignettes.matches({"defType": "ThingDef"}, s) is True)
    check("match_on_list_axis",
          vignettes.matches({"stewardship": "neglected"}, s) is True)
    # NEGATIVE CONTROL: a predicate naming an axis the sheet has not filled
    # must NOT match — an empty axis is unknown, not a wildcard
    check("match_unfilled_axis_is_not_a_match",
          vignettes.matches({"connotation": "homey"}, s) is False)
```

- [ ] **Step 2: Run and confirm it fails**

Run: `python3 src/RimMandrake/Utils/narrative/selftest.py`
Expected: FAIL — no module named `vignettes`

- [ ] **Step 3: Implement**

```python
# src/RimMandrake/Utils/narrative/vignettes.py
"""Vignettes: the unit of narrative meaning.

Meaning is not a property of an object — a potted plant in a barracks and in a
throne room make different claims. The unit is a small composition: object +
state + placement + neighbours (spec §5).

Two rules are HARD, and both exist because their absence produced real
failures elsewhere:
  1. TRACEABILITY - an observable must encode its own cause. Deconstructed
     stone blocks do not encode a violently broken door. A claim may not rest
     entirely on LOW-traceability ingredients (spec §5a).
  2. REGISTERS - a claim needs >= 2 signals in DIFFERENT registers, never two
     of the same. Redundancy across channel TYPE is what worked in the warning
     literature; repetition is not redundancy (spec §5b).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

# picker's own vocabulary (GameDesignContent/tools/picker/plan.py). A fit
# outside this set is a typo, not a new room type.
ROOM_KINDS = ("entry", "hall", "service", "territory", "chokepoint", "cache",
              "vault", "deadend_payoff", "hub", "flooded", "control")
REGISTERS = ("state", "placement", "absence", "marking", "wear")
TRACEABILITY = ("HIGH", "MED", "LOW")


@dataclass
class Vignette:
    name: str
    claim: str
    fits: list = field(default_factory=list)
    ingredients: list = field(default_factory=list)
    mood: list = field(default_factory=list)


def load_dir(path: Path) -> list:
    out = []
    for p in sorted(Path(path).glob("*.yml")):
        d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        out.append(Vignette(**d))
    return out


def validate(v: Vignette) -> list:
    problems = []
    for fit in v.fits:
        if fit not in ROOM_KINDS:
            problems.append("%s: unknown ROOM_KIND %r" % (v.name, fit))
    if len(v.ingredients) < 2:
        problems.append("%s: needs >= 2 ingredients to carry two registers"
                        % v.name)
    regs, traces = set(), []
    for i, ing in enumerate(v.ingredients):
        r = ing.get("register")
        if r not in REGISTERS:
            problems.append("%s[%d]: unknown register %r" % (v.name, i, r))
        else:
            regs.add(r)
        t = ing.get("traceability")
        if t not in TRACEABILITY:
            problems.append("%s[%d]: unknown traceability %r" % (v.name, i, t))
        else:
            traces.append(t)
        if not ing.get("predicate"):
            problems.append("%s[%d]: no predicate" % (v.name, i))
    if len(regs) < 2:
        problems.append("%s: all signals share a register (%s) - repetition is "
                        "not redundancy" % (v.name, sorted(regs) or "none"))
    if traces and all(t == "LOW" for t in traces):
        problems.append("%s: every ingredient is LOW traceability - the claim "
                        "would not be readable back to its cause" % v.name)
    return problems


def matches(predicate: dict, sheet) -> bool:
    """True if the sheet satisfies every key in the predicate.

    🔑 An UNFILLED axis is UNKNOWN, never a wildcard. A predicate naming an
    axis the sheet has not filled does not match - otherwise unfeaturized
    objects would silently satisfy everything.
    """
    for key, want in predicate.items():
        if key == "defType":
            if sheet.defType != want:
                return False
            continue
        cell = getattr(sheet, key, None)
        if not isinstance(cell, dict):
            return False
        have = cell.get("value")
        if have in ([], "", None):
            return False
        if isinstance(have, list):
            if want not in have:
                return False
        elif have != want:
            return False
    return True
```

- [ ] **Step 4: Run and confirm it passes**

Run: `python3 src/RimMandrake/Utils/narrative/selftest.py`
Expected: `all checks passed`

- [ ] **Step 5: Author the eight vignettes**

Write eight `.yml` files under `infrastructure/state/narrative/vignettes/`, every one passing `validate`. Four must serve the *poor-but-tended* claim set and four the *rich-but-abandoned* set, so the discriminative test of Task 9 has material on both sides. Each must name a claim in the S01 register — a sentence about what happened, not an adjective. Verify all eight:

```bash
python3 - <<'PY'
import sys; sys.path.insert(0, "src/RimMandrake/Utils/narrative")
import vignettes; from pathlib import Path
vs = vignettes.load_dir(Path("infrastructure/state/narrative/vignettes"))
bad = {v.name: vignettes.validate(v) for v in vs}
bad = {k: p for k, p in bad.items() if p}
print("loaded %d vignettes; %d invalid" % (len(vs), len(bad)))
for k, p in bad.items(): print(" ", k, p)
PY
```
Expected: `8 vignettes; 0 invalid`

- [ ] **Step 6: Commit**

```bash
git add src/RimMandrake/Utils/narrative/vignettes.py infrastructure/state/narrative/vignettes
git commit src/RimMandrake/Utils/narrative/vignettes.py src/RimMandrake/Utils/narrative/selftest.py infrastructure/state/narrative/vignettes -m "narrative dictionary: vignettes with traceability and register rules enforced

Both rules have negative controls proving they can reject: two same-register
signals, and a claim resting only on LOW traceability. An unfilled axis is
unknown, never a wildcard."
```

---

### Task 7: The query engine — premise, then subtract

**Files:**
- Create: `src/RimMandrake/Utils/narrative/query.py`
- Modify: `src/RimMandrake/Utils/narrative/selftest.py`

**Interfaces:**
- Consumes: `sheets.Sheet`, `vignettes.Vignette`, `vignettes.matches`.
- Produces: `query.dress(claim_set, room, rows, vigs, seed) -> DressingPlan` where `DressingPlan` has `.placements: list[dict]` (each `{defName, state, placement, register, traceability, vignette, claim}`), `.premise: str`, `.subtracted: list[dict]` (what was removed and why), `.unmet: list[str]` (claims with no candidate — the gap ledger's raw input).

- [ ] **Step 1: Write the failing test**

```python
# add to selftest.py
import query  # noqa: E402


def _rows_for_test():
    a = sheets.Sheet(defName="TendedShelf", defType="ThingDef")
    a.legibility = {"value": "HIGH", "from": "MEASURED"}
    a.stewardship = {"value": ["tended"], "from": "VISION"}
    b = sheets.Sheet(defName="RustHeap", defType="ThingDef")
    b.legibility = {"value": "HIGH", "from": "MEASURED"}
    b.stewardship = {"value": ["neglected"], "from": "VISION"}
    return [a, b]


def _vig(name, claim, stew):
    return vignettes.Vignette(
        name=name, claim=claim, fits=["service"],
        ingredients=[
            {"predicate": {"stewardship": stew}, "state": "in_situ",
             "placement": "wall_hug", "traceability": "HIGH",
             "register": "state"},
            {"predicate": {"stewardship": stew}, "state": "in_situ",
             "placement": "aisle", "traceability": "MED",
             "register": "placement"}])


def test_query_premise_then_subtract() -> None:
    rows = _rows_for_test()
    vigs = [_vig("tended", "someone keeps this", "tended"),
            _vig("neglected", "nobody has been here", "neglected")]
    room = {"kind": "service", "w": 13, "h": 9}

    plan = query.dress({"premise": "poor but tended",
                        "mood": ["tended"],
                        "claims": ["someone keeps this"]},
                       room, rows, vigs, seed=7)
    names = {p["defName"] for p in plan.placements}
    check("query_keeps_on_premise", "TendedShelf" in names)
    # premise-then-subtract: the contradicting object must be REMOVED, and the
    # removal must be RECORDED, not silently dropped
    check("query_subtracts_contradiction", "RustHeap" not in names)
    check("query_records_subtraction",
          any(s["defName"] == "RustHeap" for s in plan.subtracted))

    # determinism: same seed, same plan
    p2 = query.dress({"premise": "poor but tended", "mood": ["tended"],
                      "claims": ["someone keeps this"]},
                     room, rows, vigs, seed=7)
    check("query_deterministic",
          [p["defName"] for p in plan.placements]
          == [p["defName"] for p in p2.placements])

    # NEGATIVE CONTROL: an unservable claim must be reported UNMET, never
    # satisfied by the nearest available object
    plan3 = query.dress({"premise": "poor but tended", "mood": ["tended"],
                         "claims": ["a corpse was dragged out through here"]},
                        room, rows, vigs, seed=7)
    check("query_reports_unmet",
          "a corpse was dragged out through here" in plan3.unmet)
```

- [ ] **Step 2: Run and confirm it fails**

Run: `python3 src/RimMandrake/Utils/narrative/selftest.py`
Expected: FAIL — no module named `query`

- [ ] **Step 3: Implement**

```python
# src/RimMandrake/Utils/narrative/query.py
"""claim + mood + room_kind -> a dressing plan.

The algorithm is PREMISE-THEN-SUBTRACT, taken from a study of a human world
builder (research/RimMandrake/samuel_streamer_study/02_TECHNIQUE_ANALYSIS.md
Part 2, "One-sentence premise, then subtract everything that contradicts it").
It is also the owner's "mood as a filter", reached independently.

🔑 A subtraction is RECORDED, never silent. And a claim with no candidate is
reported UNMET rather than satisfied by the nearest available object - that
substitution is exactly how a generator produces confident nonsense, and the
unmet list is the raw material for GAPS.md.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from vignettes import matches


@dataclass
class DressingPlan:
    premise: str = ""
    placements: list = field(default_factory=list)
    subtracted: list = field(default_factory=list)
    unmet: list = field(default_factory=list)


def _contradicts(sheet, mood: list) -> bool:
    """A sheet contradicts the premise if its stewardship or abundance is
    filled and shares no value with the mood."""
    if not mood:
        return False
    for axis in ("stewardship", "abundance"):
        cell = getattr(sheet, axis, None)
        have = cell.get("value") if isinstance(cell, dict) else None
        if have:
            if not (set(have) & set(mood)):
                return True
    return False


def dress(claim_set: dict, room: dict, rows, vigs, seed: int) -> DressingPlan:
    rng = random.Random(seed)
    plan = DressingPlan(premise=claim_set.get("premise", ""))
    mood = list(claim_set.get("mood") or [])
    kind = room.get("kind")

    # Step 1: subtract everything contradicting the premise, and say so.
    keep, dropped = [], []
    for r in rows:
        if _contradicts(r, mood):
            dropped.append({"defName": r.defName,
                            "why": "contradicts premise %r" % plan.premise})
        else:
            keep.append(r)
    plan.subtracted = dropped

    # Step 2: for each claim, find a vignette that fits this room kind and
    # whose every ingredient resolves against the surviving rows.
    for claim in claim_set.get("claims", []):
        served = False
        for v in vigs:
            if v.claim != claim or kind not in v.fits:
                continue
            resolved = []
            for ing in v.ingredients:
                cands = [r for r in keep if matches(ing["predicate"], r)]
                cands = [c for c in cands
                         if (c.legibility.get("value") or "LOW") != "LOW"]
                if not cands:
                    resolved = []
                    break
                pick = rng.choice(sorted(cands, key=lambda s: s.defName))
                resolved.append({"defName": pick.defName,
                                 "state": ing["state"],
                                 "placement": ing["placement"],
                                 "register": ing["register"],
                                 "traceability": ing["traceability"],
                                 "vignette": v.name, "claim": claim})
            if resolved:
                plan.placements.extend(resolved)
                served = True
                break
        if not served:
            plan.unmet.append(claim)
    return plan
```

- [ ] **Step 4: Run and confirm it passes**

Run: `python3 src/RimMandrake/Utils/narrative/selftest.py`
Expected: `all checks passed`

- [ ] **Step 5: Commit**

```bash
git add src/RimMandrake/Utils/narrative/query.py
git commit src/RimMandrake/Utils/narrative/query.py src/RimMandrake/Utils/narrative/selftest.py -m "narrative dictionary: premise-then-subtract query engine

Subtractions are recorded, not silent. An unservable claim is reported UNMET
rather than satisfied by the nearest object - that substitution is how a
generator produces confident nonsense."
```

---

### Task 8: Compose the images, and the control dresser

**Files:**
- Create: `src/RimMandrake/Utils/narrative/compose.py`
- Modify: `src/RimMandrake/Utils/narrative/selftest.py`

**Interfaces:**
- Consumes: `query.DressingPlan`, `contact.resolve_tex`, `sheets.Sheet`.
- Produces: `compose.render(plan, room, rows, tex_roots, out_png) -> Path` and `compose.control_dress(claim_set, room, rows, seed, budget) -> query.DressingPlan`.

- [ ] **Step 1: Write the failing test**

```python
# add to selftest.py
import compose  # noqa: E402


def test_compose_and_control() -> None:
    rows = _rows_for_test()
    room = {"kind": "service", "w": 13, "h": 9}
    # the control must use the SAME budget, or the comparison is rigged
    plan = compose.control_dress({"premise": "x", "mood": ["tended"],
                                  "claims": ["c"]},
                                 room, rows, seed=3, budget=6)
    check("control_respects_budget", len(plan.placements) == 6)
    # NEGATIVE CONTROL: the control must NOT filter on mood - that is the
    # dictionary's job, and a mood-aware control is not a control
    plan2 = compose.control_dress({"premise": "x", "mood": ["tended"],
                                   "claims": ["c"]},
                                  room, rows, seed=3, budget=40)
    names = {p["defName"] for p in plan2.placements}
    check("control_ignores_mood", "RustHeap" in names)

    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        root = tmp / "Textures/Things/Item"
        root.mkdir(parents=True)
        Image.new("RGBA", (64, 64), (180, 40, 40, 255)).save(root / "X.png")
        for r in rows:
            r.texPath = {"value": "Things/Item/X", "from": "DEF_TEXT"}
        out = compose.render(plan, room, rows, [tmp / "Textures"],
                             tmp / "out.png")
        check("compose_wrote_png", out.is_file())
        im = Image.open(out)
        # the image must be the room, at play zoom, not a thumbnail
        check("compose_room_sized", im.size == (13 * 24, 9 * 24))
```

- [ ] **Step 2: Run and confirm it fails**

Run: `python3 src/RimMandrake/Utils/narrative/selftest.py`
Expected: FAIL — no module named `compose`

- [ ] **Step 3: Implement**

Write `compose.py` with:
- `PLAY_ZOOM = 24` (px per tile), image size `(w*24, h*24)`.
- `control_dress(...)`: picks `budget` sheets uniformly at random from **all** rows with `legibility != "LOW"`, ignoring mood entirely, assigning `state="in_situ"` and a random placement. It must reuse `query.DressingPlan` so both conditions produce the same shape.
- `render(...)`: resolves each placement's `texPath` via `contact.resolve_tex`, lays placements out by their `placement` keyword (`wall_hug` → perimeter cells, `aisle` → interior lane, `strewn` → a jittered line, `corner` → a corner cell), pastes each sprite scaled to its tile footprint on a neutral floor, and **writes no text of any kind onto the image**.
- A docstring stating: *"🔴 This image carries NO defNames, labels, or filenames. The evaluation's blinding depends on it. If you add a debug label, add it to a separate `_debug` variant that never reaches a reviewer."*

- [ ] **Step 4: Run and confirm it passes**

Run: `python3 src/RimMandrake/Utils/narrative/selftest.py`
Expected: `all checks passed`

- [ ] **Step 5: Verify the blinding by looking**

Build one image and read it yourself. Confirm no text appears anywhere. Then check the file name it is written under does not leak the condition — use `dressing_a.png`, `dressing_b.png`, `dressing_c.png`, `dressing_d.png` with the mapping held in a separate file the reviewer never receives.

- [ ] **Step 6: Commit**

```bash
git add src/RimMandrake/Utils/narrative/compose.py
git commit src/RimMandrake/Utils/narrative/compose.py src/RimMandrake/Utils/narrative/selftest.py -m "narrative dictionary: PIL composer at play zoom, plus the control dresser

The control ignores mood deliberately - a mood-aware control is not a control -
and uses the same object budget. Images carry no text, because the blinding
depends on it."
```

---

### Task 9: Run the evaluation, and publish the verdict and the gap ledger

**Files:**
- Create: `src/RimMandrake/Utils/narrative/evaluate.py`
- Create: `infrastructure/state/narrative/GAPS.md`
- Create: `Transient/narrative_pilot_verdict_2026-09-15.md`
- Modify: `src/RimMandrake/Utils/narrative/selftest.py`

**Interfaces:**
- Consumes: `bar.verdict`, `query.dress`, `compose.render`, `compose.control_dress`.
- Produces: `evaluate.score(reviews, intended) -> dict` matching `bar.verdict`'s expected keys, and `evaluate.shuffle_conditions(seed) -> dict` mapping image filename → condition.

- [ ] **Step 1: Write the failing test**

```python
# add to selftest.py
import evaluate  # noqa: E402


def test_scoring() -> None:
    intended = ["someone keeps this", "they left in a hurry",
                "nobody has been here", "it was searched"]
    reviews = {
        "dict": "Someone keeps this place tidy. They left in a hurry.",
        "control": "There is stuff on the floor.",
    }
    sc = evaluate.score(reviews, intended)
    check("score_counts_recovered", sc["dict_recovered"] == 2)
    check("score_control_zero", sc["control_recovered"] == 0)
    check("score_total", sc["intended_total"] == 4)
    # NEGATIVE CONTROL: an empty review must score zero, not crash or default
    sc2 = evaluate.score({"dict": "", "control": ""}, intended)
    check("score_empty_is_zero", sc2["dict_recovered"] == 0)
    # NEGATIVE CONTROL: the shuffle must actually permute across seeds
    a = evaluate.shuffle_conditions(1)
    b = evaluate.shuffle_conditions(2)
    check("shuffle_varies", a != b)
```

- [ ] **Step 2: Run and confirm it fails**

Run: `python3 src/RimMandrake/Utils/narrative/selftest.py`
Expected: FAIL — no module named `evaluate`

- [ ] **Step 3: Implement**

`evaluate.py` provides:
- `shuffle_conditions(seed)`: deterministic permutation of the four conditions onto `dressing_{a,b,c,d}.png`, written to a mapping file the reviewer never sees.
- `score(reviews, intended)`: matches each intended claim against a review. Use a conservative matcher — a claim counts as recovered only if the review states the *substance*, and the matcher must be reviewed by a human on the first run because automated claim matching is itself a proxy. Count false claims as assertions about the room's history that are not in `intended`.
- A docstring recording: *"⚠️ score() is a proxy for whether a human would say the reviewer got it. On the first run, hand-check every match and record the disagreement rate. If the matcher disagrees with a human read more than once in ten, the scoring is the weak link and must be replaced by hand-scoring."*

- [ ] **Step 4: Build the four dressings and dispatch the reviewers**

Generate `dressing_{a,b,c,d}.png` from the two claim sets × {dictionary, control}, then dispatch **four separate subagents on `haiku`**, one per image, each receiving only the image and this prompt:

> Describe this room. Then answer: what does it appear happened here in the past to explain this room? Who was here, and are they still? Answer only from what you can see in the image.

Each reviewer must be a fresh context with no access to the brief, the claim sets, the vignettes, or any other reviewer's answer.

- [ ] **Step 5: Score, and write the verdict without moving the bar**

Compute `evaluate.score(...)` and pass it to `bar.verdict(...)`. Write `Transient/narrative_pilot_verdict_2026-09-15.md` containing: the pre-registered bar quoted verbatim from `bar.py`, the four reviews in full, the scores, the verdict, and the hand-check disagreement rate from Step 3.

🔴 If the verdict is `FAIL`, write it as `FAIL`. Do not adjust the bar, re-run with a different seed until it passes, or reinterpret the reviews. A failure is the pilot working correctly.

- [ ] **Step 6: Write GAPS.md**

From every `plan.unmet` claim and every vignette ingredient whose candidate set was empty or all-`LOW`-legibility, write `infrastructure/state/narrative/GAPS.md`: each gap as one line naming the claim, the register that could not be filled, and what kind of object would fill it. This file is the input that scopes `EVENT_TRACE_PROPS_LIBRARY_1` — expect blaster scars, scorch marks, scrapes and drag trails to dominate it, since §6a measured zero event traces in the repo.

- [ ] **Step 7: Run the full selftest sweep and commit**

```bash
python3 src/RimMandrake/Utils/run_selftests.py
git add src/RimMandrake/Utils/narrative/evaluate.py infrastructure/state/narrative/GAPS.md Transient/narrative_pilot_verdict_2026-09-15.md
git commit src/RimMandrake/Utils/narrative/evaluate.py src/RimMandrake/Utils/narrative/selftest.py infrastructure/state/narrative/GAPS.md Transient/narrative_pilot_verdict_2026-09-15.md -m "narrative dictionary pilot: verdict and gap ledger

Four dressings, blind haiku reviewers, scored against the bar committed in
Task 1. Verdict recorded as measured. GAPS.md scopes
EVENT_TRACE_PROPS_LIBRARY_1.

Closes: NARRATIVE_DICTIONARY_PILOT_1"
```

- [ ] **Step 8: Close the ledger item and hand the proxy question to the owner**

```bash
python3 src/RimMandrake/rimflow/cli.py close NARRATIVE_DICTIONARY_PILOT_1 --seat BENCH --sha "$(git rev-parse --short HEAD)"
```

Then tell the owner, in one line each: the verdict, the disagreement rate of the automated matcher, and that **the proxy still needs validating once against the real renderer on his machine** — one pair of dressings built in-game, screenshotted, read by him. Until that happens the offline verdict is provisional, however it came out.

---

## Self-Review

**Spec coverage.** §2 rulings 1-5 → Tasks 6/7 (claim-primary, mood filter), the whole plan's task shape (vertical slice), Task 5 (vision + def text with provenance), Tasks 1/9 (blind test, pre-registered bar), Tasks 3/7 (defNames, no roles). §3 pipeline position → Task 7 output shape is a dressing plan, not tiles. §4 axes → Task 5 `VOCABULARY.md` fixes every closed vocabulary; §4a's ad-hoc finding → connotation is the one open list. §4c stewardship ⊥ abundance → both are separate axes in `sheets.Sheet` and both are checked in `query._contradicts`. §4d → `metrics` docstring names hidden/false affordances. §5a traceability → `vignettes.validate`. §5b registers → `vignettes.validate`. §6 premise-then-subtract → `query.dress`. §6a inventory → Task 3 Step 5 subset choice and Task 9 Step 6's expectation. §7 pilot → Tasks 8/9. §7a proxy layers → Task 9 Step 8 hands the renderer validation to the owner. §7b regimes → **not implemented, correctly**: the optimisation loop is a later experiment, not batch 1. §8 guard rails → the density ceiling is **not yet implemented**; noted as a gap below. §10 non-goals → no task places tiles or scores rooms. §11 deliverables → all seven produced.

**One real gap found and left deliberately:** spec §8's *density ceiling per claim* has no task. Batch 1 places ~6 objects in a 13×9 room, so clutter cannot arise at this scale, and inventing a ceiling before seeing a crowded room would be a guess. **Add it in batch 2, from a measured over-crowded case.** Recorded here rather than silently dropped.

**Placeholder scan.** No TBDs. Every code step carries real code. Tasks 5, 8 Step 3, and 9 Step 3 describe agent work and file contents rather than pasting code — for Task 5 and 9 Step 4 that is inherent (they are prompts), and for 8 Step 3 and 9 Step 3 the interfaces block fixes the exact signatures so an implementer cannot drift.

**Type consistency.** `sheets.Sheet` field names are used identically in `vignettes.matches` predicates, `query._contradicts`, and Task 5's vocabulary. `query.DressingPlan` is produced by both `query.dress` and `compose.control_dress`, so `compose.render` and `evaluate` consume one shape. `bar.verdict`'s six score keys match `evaluate.score`'s output exactly: `dict_recovered`, `control_recovered`, `dict_false`, `control_false`, `intended_total`, `proxy_agrees`. `metrics.measure`'s `legibility` string feeds `query.dress`'s `LOW` filter and `compose.control_dress`'s eligibility filter with the same three values.
