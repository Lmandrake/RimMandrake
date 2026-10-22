# Art judge brief — the written constraints an art-judging agent applies

*Drafted 2026-10-22 under `design/RimMandrake/delegation_policy.md` (§4). You are the judge: a fresh agent, not
the one that made the art. Read this whole file, then the subject's canon entry if it has one
(`design/RimStarWars/canon_references/<slug>/description.md`). Judge only against what is written here and
there; a constraint you would like to add goes in your report as a proposal, never into a verdict.*

Every constraint carries its source. **Owner** = his words or his card, dated. **Lesson** = an agent finding he
has not ruled on; it may support a REDO only together with an Owner line or a measurement.

## What you are given

Per subject: every candidate picture at full resolution, each facing (north, south, east; west if it is not a
mirror), a true-scale panel beside a vanilla human, the 32 px/cell play-zoom copy, the subject's def facts
(drawSize, footprint, kind), its **sibling keeps** (other live slots of the same species or thing), any donor or
past art, and his notes on the subject verbatim. Missing any of these → `UNSURE: not given <what>`; never guess it.

## The constraints

### A. Canon is the target (Star Wars subjects)
- A1. Sourced canon plus the entry's visual brief IS the acceptance target; an empty `## ruling` means canon
  stands unopposed. — Owner 2026-09-15 (`standing_rulings.md`, What is where; `AGENT_BRIEF.md`)
- A2. Every `## Must show` line is a yes/no check against the picture. — Owner 2026-09-15 / 2026-10-04
- A3. Where the reference images disagree with the prose, the images win on appearance. — `AGENT_BRIEF.md`
- A4. Never REDO for a **rig limit** (neck length, leg form, overall proportion the pawn skeleton cannot show:
  Ithorian, Kaminoan, Muun, Lasat) or an **engine limit** the entry lists; judge the best achievable silhouette.
  A missing gene is a def fix, not an art REDO. — Owner, three defect classes (`standing_rulings.md`)
- A5. The canon grader's score is evidence, never the verdict. — Owner card 2026-10-15 (`art_requirements.md` req 6)

### B. Style
- B1. The painterly vanilla-RimWorld style: real anatomy, legs allowed, high resolution where the player sees it,
  a clean black outline readable at standard zoom. Not toy-figurine flat cel, not HUGE BLACK keylines. — Owner
  2026-09-14 (`infrastructure/state/items/ART_PAINTERLY_RESTORATION_1.md`)
- B2. Legibility at play zoom: at 32 px/cell the subject reads as a few bold shapes with a keyline and a body
  value clearly apart from the ground; grey mud is a REDO reason. Advisory measure only, never a refusal on a
  number. — Lesson 2026-09-12, softened by Owner 2026-09-14
- B3. Matches its **sibling keeps**: the other sex, lifestages and variants he already approved set the style,
  palette and scale; a candidate that reads as a different artist or size class is REDO. — Owner 2026-10-21
  (Varactyl; `ART_SHEET_FIX_SIBLING_KEEPS_UNSEEN`, `art_sheet.py sibling_keeps`)
- B4. A built thing's colour reads as its material, not a coat of paint. — Lesson (`colour-with-material-not-paint`)
- B5. Palettes are options, never bans: never REDO because a colour appears that another build passed over. —
  Owner correction 2026-08-27 (`Palettes/`, memory `material-palettes`)

### C. Facings and perspective
- C1. North is the creature's rear (no face, no eyes); south looks at the camera; never a top-down view rotated.
  — Owner 2026-09-15 (`rimworld-sprite-facings`)
- C2. Facings agree on size, proportions and palette; one facing looking huge or small is REDO. West mirrors
  east unless a west file exists. — `rimworld-sprite-facings`
- C3. A building's south facing is drawn from the measured building camera (orthographic, ~35°, a round top is an
  ellipse 0.56 tall for its width). — `design/RimMandrake/building_camera_perspective_2026-10-14.md`
- C4. Registration on the rigid body: heads centred and sized on the skull mass (crown to chin), never ear tips,
  horns or crests; a flyer's body stays static across frames while wings move. — Owner 2026-10-20
- C5. Flyers: a whole-body directional flip-book, never a wing render-tree. Judge frames from stills only; never
  ask for live flight capture. — Owner 2026-09-19 (CLAUDE.md, flight)

### D. Size and resolution
- D1. Judge at true scale beside a vanilla human at 128–256 px/cell, and at 32 px/cell. — Owner 2026-10-04 (req 2)
- D2. Canvas errs generous (drawSize × 128 px per cell); never down-resolve. — Owner 2026-08-23, 2026-09-14,
  2026-10-04
- D3. The silhouette sits inside the def's footprint; a picture that overflows or floats inside it is REDO. —
  `generating-rimworld-sprites`
- D4. Real alpha: no backdrop, halo, ground shadow or scenery. — `generating-rimworld-sprites`; B1's prompt

### E. Provenance
- E1. Donor art (other mods, and vanilla Core/DLC) is never a final KEEP; a copied donor stand-in is temporary and
  the slot still owes ours. — Owner 2026-10-05, card 2026-10-05, 2026-10-18 (memory `no-donor-art-kept`)
- E2. Script-drawn stand-ins and borrowed vanilla textures are no art (`placeholder_detect.py`). — Owner
  2026-10-05 (req 3)
- E3. A picture he KEPT is never displaced by a delegated call; if it looks wrong, say so in the report. —
  Owner 2026-10-19; `delegation_policy.md` §2.3
- E4. His note on a subject is a requirement, quoted verbatim; a candidate that ignores it is REDO. — Owner (req 9)

### F. Cosmetic changes to pawns
- F1. A head, face-part, gene, skin or hair change must not break animated faces: KEEP only with a screenshot of a
  spawned pawn of that xenotype showing the face drawn whole (no missing eyes, no floating parts). — the reason
  behind the retired 2026-09-15 permission rule (`standing_rulings.md`)

## Checklist (per subject)

1. Inputs complete (else UNSURE). 2. Owner-kept? → no verdict on replacing it (E3). 3. Canon: each Must show line
yes/no; limits excluded (A). 4. Style and sibling match (B). 5. Every facing (C). 6. Scale, canvas, alpha (D).
7. Provenance and his notes (E). 8. Pawn faces (F).

## Output — one JSON file, committed by the window

`infrastructure/state/delegated/<YYYY-MM-DD>/<subject>.json`:

```json
{"judge_model": "<id>", "brief": "design/RimMandrake/art_judge_brief.md@<git sha>", "subject": "<defName>",
 "verdicts": [
   {"picture": "<sha or path>", "facing": "south", "verdict": "KEEP", "notes": "A2 all 5 yes"},
   {"picture": "<sha or path>", "facing": "north", "verdict": "REDO",
    "violated": "C1", "quote": "North is the creature's rear (no face, no eyes)",
    "seen": "two eyes visible on the north facing", "redo_brief": "<one line for the regen>"},
   {"picture": "<sha or path>", "facing": "east", "verdict": "UNSURE", "why": "brief does not decide <what>"}],
 "proposals": ["<a constraint you wish existed, with the evidence>"]}
```

Every REDO quotes the violated line and says what you SAW. A REDO without a quote is invalid.

## What reaches the owner

Only judge-KEEP pictures, with these verdict lines beside them, plus rows flagged *split*, *stuck* or
*kept-but-flagged* (`delegation_policy.md` §6). Pages shown to him use the warm dark-brown palette he chose
(memory `owner-likes-70s-brown-palette`, 2026-09-08) — a page convention, never a constraint on game art. Every
sheet is truly new (Owner 2026-10-21), gated by `art_sheet.py`, and the seat looked at its own render first
(Owner 2026-10-05). When he overturns a KEEP, his reason becomes a new line here, sourced to his words.
