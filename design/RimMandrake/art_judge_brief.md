# Art judge brief — the written constraints an art-judging agent applies

*Drafted 2026-10-22 under `design/RimMandrake/delegation_policy.md` (§4). You are the judge: a fresh agent, not
the one that made the art. Read this whole file. Then read the subject's canon entry, if the subject has one
(`design/RimStarWars/canon_references/<slug>/description.md`). Judge only against what this file and the canon entry
say. If you want to add a constraint, write it in your report as a proposal. Never put it into a verdict.*

The Artist (`src/RimMandrake/rimflow/roles/artist.md`) holds this brief. The owner has overridden the pipeline.
`design/RimMandrake/art_style_memory.md` records what his overrides show. That file is not a constraint, and it
decides no verdict.

Every constraint carries its source:

- **Owner** = his words or his card, dated.
- **Lesson** = an agent finding that he has not ruled on. A Lesson line can support a REDO only together with an
  Owner line or a measurement.
- "req N" is requirement N of `skills/rimworld-review-sheets/references/art_requirements.md`.

## What you are given

For each subject, you get:

- every candidate picture at full resolution;
- each facing (north, south, east; west if it is not a mirror);
- a true-scale panel beside a vanilla human;
- the 32 px/cell play-zoom copy;
- the subject's def facts (drawSize, footprint, kind);
- its **sibling keeps** (other live slots of the same species or thing);
- any donor or past art;
- his notes on the subject, verbatim.

If one of these is missing, answer `UNSURE: not given <what>`. Never guess the missing input.

## The constraints

### A. Canon is the target (Star Wars subjects)
- A1. Sourced canon plus the entry's visual brief IS the acceptance target; an empty `## ruling` means canon
  stands unopposed. — Owner 2026-09-15 (`standing_rulings.md`, What is where; `AGENT_BRIEF.md`)
- A2. Every `## Must show` line is a yes/no check against the picture. — Owner 2026-09-15 / 2026-10-04
- A3. Where the reference images disagree with the prose, the images win on appearance. — `AGENT_BRIEF.md`
- A4. Never REDO for a **rig limit** (neck length, leg form, overall proportion the pawn skeleton cannot show:
  Ithorian, Kaminoan, Muun, Lasat) or an **engine limit** the entry lists. Judge the best achievable silhouette.
  A missing gene is a def fix, not an art REDO. — Owner, three defect classes: missing gene, engine limit, rig limit
  (`standing_rulings.md`; the table in `AGENT_BRIEF.md`)
- A5. The canon grader's score is evidence, never the verdict. — Owner card 2026-10-15 (`art_requirements.md` req 6)

### B. Style
- B1. The painterly vanilla-RimWorld style: real anatomy, legs allowed, high resolution where the player sees it.
  Not toy-figurine flat cel. — Owner 2026-09-14 (`infrastructure/state/items/closed/ART_PAINTERLY_RESTORATION_1.md`)
- B1a. **No outlines.** Value and colour contrast against the ground carry the silhouette. The silhouette never
  rests on a drawn black outline or keyline. A sprite without an outline is correct. A heavy drawn keyline is STYLE_OFF. — Owner card
  2026-10-04 (`ART_VERSION_WRANGLING_1`; the house register `HOUSE_ART_REGISTER` in
  `src/RimMandrake/Utils/artpipe/common.py`). This card retired the outline clause that B1 carried from 2026-09-14.
  Exception: the Pyrelands ullai carries a MEDIUM black outline (option B) by the owner's pick of 2026-11-23, this creature only.
- B2. Legibility at play zoom: at 32 px/cell the subject reads as a few bold shapes, with a body value clearly
  apart from the ground. Grey mud is a REDO reason. Grey mud is either of two faults, and one alone is a REDO. Fault
  one: the body blends into the ground. Fault two: the body is dull, with no clear shapes. A plain body with clear
  shapes, clearly apart from the ground, is not grey mud. Judge both faults by eye. This is an advisory measure
  only: never refuse on a number. — Lesson 2026-09-12, softened by Owner 2026-09-14; the two faults: Owner card
  2026-11-23 (`RIMMANDRAKE_ANSWER_SEVEN_TERMS_NO_SOURCE_DEFINES_GREY_MUD`)
- B3. Matches its **sibling keeps**: the other sex, lifestages and variants that he already approved set the style,
  palette and scale. A candidate that reads as a different artist or size class is REDO. — Owner 2026-10-21
  (Varactyl; `ART_SHEET_FIX_SIBLING_KEEPS_UNSEEN`, `art_sheet.py sibling_keeps`)
- B4. A built thing's colour reads as its material, not a coat of paint. — Lesson (`colour-with-material-not-paint`)
- B5. Palettes are options, never bans: never REDO because a colour appears that another build passed over. —
  Owner correction 2026-08-27 (`Palettes/`, memory `material-palettes`)
- B6. A Modern tier looks like a building you would see today. A Modern tier is never bright red or paint-coloured as
  a tier marker. — Owner 2026-11-06 ("you KNOW that you're not supposed to just use bright red for modern. Make it look like a "modern" building, I.e. one that I would see right now.")

### C. Facings and perspective
- C1. North is the creature's rear (no face, no eyes); south looks at the camera; never a top-down view rotated.
  — Owner 2026-09-15 (`rimworld-sprite-facings`)
- C2. Facings agree on size, proportions and palette. If one facing looks huge or small, that is REDO. West mirrors
  east unless a west file exists. — `rimworld-sprite-facings`; Owner 2026-11-19 ("Allow the Judge to bounce
  incorrectly sized creatures")
- C3. A building's south facing is drawn from the measured building camera (orthographic, ~35°; a round top is an
  ellipse 0.56 tall for its width). — `design/RimMandrake/building_camera_perspective_2026-10-14.md`
- C4. Registration on the rigid body: line the pictures up on the part that does not move, never on the picture's
  outer extremes. For a flyer, that part is the body. For a head, that part is the skull. Heads are centred and sized
  on the skull mass (crown to chin), never ear tips, horns or crests. A flyer's body stays static across frames while
  wings move. — Owner 2026-10-20 (`FLIER_FRAMES_AUDIT_BODY_NOT_WING_EXTREMES`)
- C6. A pipe, hose or nozzle is drawn in its true perspective plane. Its open bore shows only where the pipe
  really turns toward the camera. A pipe lying along the ground that shows its inside reads as "bent up" — REDO.
  — Owner card 2026-10-23 ("Reel_Deployed_north.png shows the inside of the pipe, which implies the pipe is
  "bent up" towards the viewer … Keep the pipe in the proper perspective plane please.")
- C5. Flyers: a whole-body directional flip-book, never a wing render-tree (separate wing layers that the game moves
  on the body; `skills/rimworld-modding/references/flight.md`). Judge frames from stills only. Never ask for a live
  flight capture. — Owner 2026-09-19 (CLAUDE.md, flight)
- C5a. Look at flyer frames one at a time, at full size. The head holds still and the eyes stay level. No wing lies
  baked along the body while another wing flaps. No wing breaks into specks where it turns edge-on. No body pixels
  leave with a lifted wing. Every part of a facing has its art. Frames with these faults passed a still-image check
  once, so say what you could not see. — Owner 2026-11-07 (`rimworld-sprite-facings`, "Cut-out flip-books")

### D. Size and resolution
- D1. Judge at true scale beside a vanilla human at 128–256 px/cell, and at 32 px/cell. — Owner 2026-10-04 (req 2)
- D2. The canvas errs generous (drawSize × 128 px per cell). Never down-resolve. — Owner 2026-08-23, 2026-09-14,
  2026-10-04
- D3. The silhouette sits inside the def's footprint. A picture that overflows the footprint, or floats inside it, is
  REDO. — `generating-rimworld-sprites`
- D4. Real alpha: no backdrop, halo, ground shadow or scenery. Some ground matter is the subject, not scenery: matter
  that the subject's own description says it makes where it stands (the fermatalis's mounds of mash). Any other prop
  on the ground is scenery. — `generating-rimworld-sprites`; the house art prompt (`HOUSE_ART_REGISTER`, the
  prompt text that B1's item made canonical); Owner 2026-10-24 picked `RM_DecayDrake` r2 with its mash mounds
  (criteria_ledger CL-035, on the review sheet `owner_escalations_cauldron_sheet_2026-10-24`)
  - D4 exception: `RM_LadderPortable` west/east facings may carry a small soft floor shadow attached to the foot. — Owner card 2026-10-22 ("How should we resolve the side walls? → Keep side walls, add a shadow")

### E. Provenance
- E1. Donor art (other mods, and vanilla Core/DLC) is never a final KEEP. A copied donor stand-in is temporary, and
  the slot still owes our own art. — Owner 2026-10-05, card 2026-10-05, 2026-10-18 (memory `no-donor-art-kept`)
- E2. Script-drawn stand-ins and borrowed vanilla textures are no art (`placeholder_detect.py`). — Owner
  2026-10-05 (req 3)
- E3. A delegated call (a call that an agent makes in the owner's place) never displaces a picture that he KEPT.
  The one exception is the art-eval pipeline's regen verdict: the picture is redrawn, and he sees it after on the
  shadow sheet as *replaced your kept art*, with a one-click revert. If a kept picture looks wrong, say so in the
  report. So on a picture that he kept, your verdict is KEEP, whatever other line it breaks. Write the concern in
  `notes`, with no refusal record. Only the art-eval pipeline's own judge, which does not use this brief, may write a
  regen verdict on it. — Owner 2026-10-19; owner card 2026-10-23 06:42 (*"Kept art judged really bad: may the pipeline redraw it on its own? → Yes, but show me after"*);
  `delegation_policy.md` §2.2
- E4. His note on a subject is a requirement, quoted verbatim. A candidate that ignores his note is REDO. — Owner
  (req 9)

### F. Cosmetic changes to pawns
- F1. A head, face-part, gene, skin or hair change must not break animated faces. KEEP such a change only with a
  screenshot of a spawned pawn of that xenotype that shows the face drawn whole (no missing eyes, no floating parts).
  — the reason behind the retired 2026-09-15 permission rule (`standing_rulings.md`)

## Checklist (per subject)

1. Inputs complete (else UNSURE).
2. Owner-kept? Apply E3. Flag concerns in the report. Any replacement follows its authorized art-eval regen route,
   shadow-sheet notice and one-click revert.
3. Canon: each Must show line yes/no; limits excluded (A).
4. Style and sibling match (B).
5. Every facing (C).
6. Scale, canvas, alpha (D).
7. Provenance and his notes (E).
8. Pawn faces (F).

## When the look is enough, and when to stop

- Enough: every picture and facing that you were given has one verdict (KEEP, REDO or UNSURE) with its evidence.
  Then stop. Do not look for more.
- Make one full inspection, then one check of the repairs. A re-judge after a regen looks only at the REDO lines. It
  raises something new only where the regen itself changed the picture. Never look a third time
  (`standing_rulings.md` §The judge refuses flaws, not polish). The danger that this count guards: a judge asked again
  never stops. Pyrelands stage 5 took nine recorded looks (2026-11-17).
- A REDO quotes a violated constraint. A wish that no constraint states is a `proposals` line. It files no ticket and
  blocks nothing.

## Output — one JSON file, committed by the window

The window that launched you commits one JSON file:
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

### Refusal record: every REDO is one (owner, 2026-11-12)

*"ANY refusals must be as detailed as the evidence they are rejecting and include the fixes and paths towards passing
that are attainable and reasonable. It also MUST include assessment of the acceptance criteria themselves."*

So the file also carries a `contract` block in the form of the refusal contract
(`design/specs/2026-11-12-refusal-contract-for-judges-and-gates.md` section 1). The block holds:

- one record for each refused constraint;
- every other constraint that you applied, in `passed`;
- a verdict on the constraint itself.

- `clause` is the constraint id. `evidence` names the picture that you looked at.
- `criterion_hash` is a short code made from the words of the constraint line. It shows which wording you judged. The
  launching window fills it in, so leave it empty.
- `new_since` says why a refusal is raised now. On the first look it is `first`. Later it is one of four:
  - `unfixed:<constraint id>`: an earlier refusal was not fixed;
  - `changed:<file>`: the named input changed;
  - `regression:<constraint id>`: a constraint that passed before now fails;
  - `late`: you could have raised it on an earlier look.

```json
{"contract": {"item": "<ledger item>", "family": "art_judge_brief", "sha": "<picture sha>",
  "passed": [{"clause": "D1", "evidence": ["north.png"]}],
  "refusals": [{"clause": "C1", "criterion_hash": "<refusal_contract.criterion_hash of C1's line>",
    "evidence": ["north.png"], "observed": "two eyes and a snout drawn on the north facing",
    "would_pass": "the north facing shows the back of the head and tail with no eyes, snout or mouth visible",
    "smallest_fix": {"what": "Redraw north.png as a rear view of the same subject, preserving its proportions, palette and scale.",
                     "attainable": "yes", "cost": "rerun"},
    "criterion_verdict": "sound",
    "criterion_why": "North is the rear by the game's convention, and a back view is drawable for this body.",
    "new_since": "first"}]}}
```

Before the launching window acts on any REDO, it does two things:

- The window writes `given`: the pictures and the constraint lines that the window gave you.
- The window runs `python3 src/RimMandrake/rimflow/refusal_contract.py submit <file> --given <given.json>`.

A malformed record is itself refused. You are then asked once more, with its errors. If your second answer is also
malformed, this brief is marked FAILED, and `REFUSAL_NOTHING_COULD_EVER_PASS` is raised. If you judge a
constraint `flawed` or `unattainable`, that constraint goes to a neutral criteria fixer. The
constraint never goes back to the artist.

## What reaches the owner

- Judge-KEEP pictures reach him, with these verdict lines beside them.
- Rows flagged *split*, *stuck* or *kept-but-flagged* also reach him (`delegation_policy.md` §6). Nothing else
  reaches him.
- Pages shown to him use the warm dark-brown palette that he chose (memory `owner-likes-70s-brown-palette`,
  2026-09-08). This palette is a page convention, never a constraint on game art.
- Every sheet is truly new (Owner 2026-10-21) and is gated by `art_sheet.py`.
- Every sheet is read before he sees it. The seat or a naive judge looks at every row. Broken rows are fixed or
  dropped. The look is recorded in `<stem>.prereview.json` (Owner 2026-10-05 and 2026-10-22, `standing_rulings.md`
  §Nothing reaches the owner unread). Your verdict file can be that look.
- When he overturns a KEEP, his reason becomes a new line here, sourced to his words.
