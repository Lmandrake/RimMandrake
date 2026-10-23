# Automated RimWorld art evaluation — design (2026-10-23)

Status: §1–§4 DESIGN; §6 pilot SCORED; **§8 BUILT** — the owner's pipeline as adopted 2026-10-23, skill
`skills/rimworld-art-evaluation/`, code `src/RimMandrake/Utils/art_eval/` (item `ART_EVAL_PIPELINE_BUILD_OPUS_GRADES_FIRST`).
Authors: BENCH design helper (Opus 5.5); §8 by the BENCH build helper.
Tags: **MEASURED** = counted this sitting (command named) · **ESTIMATED** = reasoned, not run · **UNMEASURED** = nobody knows yet.

## 0. The request and what this is

Owner, 2026-10-23, verbatim:

> *"Please remember: GPT can review art sheets very well too. Very well! Give it the intended description and the
> imagery, plus the facing requirements, etc. Most of the feedback I've given you could have been gotten in an
> automated fashion there. I bet Claud Opus 5.5 can do so as well. In fact... let's try it! … This would be a new
> skill: automated Rimworld art evaluation. Same thing for all of these perspective checks on machines, pits,
> pipes, etc. Do a deep design pass now on this concept for what the sheet should look like (should be
> regularized, fast to generate, clear in its ask, complete in its information, templated in terms of random
> pool/alternates to compare/facings/gender/juveniles etc.), what the prompt should be, how many different templates
> we need to cover game art, whether it can be generated from the textures themselves or requires in-game capture,
> and the quality estimate of GPT vs. Opus 5.5 review."*

**What already exists and is reused, not rebuilt:**

| piece | path | role here |
|---|---|---|
| the judge's constraints (A1–F1, sourced) | `design/RimMandrake/art_judge_brief.md` | the reason-code vocabulary IS its constraint IDs |
| judge protocol, delegation, digest | `design/RimMandrake/delegation_policy.md` §4–§6 | the verdict file, maker≠judge, one rebuttal |
| building camera (35°, ellipse 0.56, front band 30–39 %) | `design/RimMandrake/building_camera_perspective_2026-10-14.md` | the numeric half of every building/machine check |
| scale panel beside a vanilla human, sizes from the live dump | `src/RimMandrake/Utils/art/scale_panel.py` | the true-scale strip on every card |
| full / scale / facings PNGs per question | `src/RimMandrake/Utils/art/chat_review.py` | the nearest existing thing to a card; the card generalises it |
| sibling keeps, random-folder variants, canon entry | `art_sheet.py` `sibling_keeps`, `random_folder_variants`, `canon_entry` | card fields |
| pre-review record (OK/FIXED/FLAG per row) | `src/RimMandrake/Utils/art/prereview.py` | the evaluator writes it (§5) |
| GPT with images | `src/RimMandrake/Utils/gpt_consult.py -i <png>` (codex exec, gpt-6.1-sol high) | the GPT reviewer transport |
| numeric gates (alpha, canvas, footprint, cylinder rim, symmetry, cross-facing size) | `skills/generating-rimworld-sprites/scripts/validate_sprite.py`, `src/RimMandrake/Utils/art/facing_scale_lint.py`, `placeholder_detect.py` | run FIRST; their numbers go on the card as facts |

**The one-line idea.** Every subject becomes one regularized *evaluation card* (a PNG plus a JSON twin) built
from the textures by a compositor; numeric gates run first and print their numbers onto it; a vision reviewer
answers a closed list of questions in a fixed JSON schema whose reason codes are the art judge brief's
constraint IDs; disagreement or low confidence goes to the owner, flagged. The owner's past verdicts are the
scoring key that tells us whether the reviewer can be trusted, per template.

## 1. Evaluation sheet spec — the card

### 1.1 One card per subject, always the same shape

A **subject** is one picture slot the owner rules on: a def's body texPath (a species' adult, a plant, a
building's graphic), with every facing and variant of that slot. Each subject gets one card. A card is built
twice from the same data: `card.png` (what a vision model and a human see) and `card.json` (every text fact,
given to the model as text — never only as pixels, because models misread small rendered text).

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HEADER (text, also in card.json)                                                                 │
│ RM_Duneskimmer · creature/walker · tier RM_ · drawSize 1.6 (adult) · body size 0.9 · mod <pkg>   │
│ template T1 creature v3 · candidate set "B" (artpipe job 8f2c…) vs installed "A"                 │
│ INTENDED: "a low, broad-backed sand lizard with a frilled neck; tan with rust banding; eyes on    │
│           top of the skull" (from def description + canon/visual brief)                           │
│ MUST SHOW (canon): [1] frill  [2] dorsal bands  [3] six legs                  ENGINE LIMITS: none │
│ OWNER NOTES (verbatim, dated): 2026-10-05 "too grey, reads as mud at zoom"                        │
│ CONSTRAINTS IN FORCE: B1 B2 B3 C1 C2 D1 D3 D4 E1 E4        GATES: alpha OK · canvas 205 px/cell   │
│                                                            cross-facing height spread 6 % OK      │
├────────────────────────────── PANEL A: FACINGS (candidate, 512 px tiles, checker bg) ────────────┤
│  [ SOUTH ]        [ EAST ]         [ NORTH ]        [ WEST* ]        * = mirrored from east       │
│  front, face     right profile    rear, no face    left profile      (or "own file" if present)   │
│  bbox h 0.92     bbox h 0.90      bbox h 0.94      mirror of E ✓                                  │
├────────────────────────────── PANEL B: TRUE SCALE (128 px/cell, biome ground colour) ────────────┤
│  [vanilla human S] [candidate S] [candidate E] [installed S]   │ grid 1 cell │ footprint outline  │
├────────────── PANEL C: PLAY ZOOM 32 px/cell ───────────┬──── PANEL D: VARIANTS ──────────────────┤
│  [S][E][N] on ground, actual size                       │ female S | juvenile S | baby S          │
│                                                         │ random pool a b c d (all, labelled)      │
│                                                         │ states: dessicated · corpse (if own art) │
├───────────────────────────────────────── PANEL E: CONTEXT ───────────────────────────────────────┤
│  SIBLING KEEPS (owner-kept, same species/family): [male S][female S][juv S] — style target         │
│  CANON REFS (reference only): [ref1][ref2]        INSTALLED NOW: [S][E][N]   DONOR/PAST: [..]      │
├───────────────────────────────────────── THE ASK (text only, in the prompt) ─────────────────────┤
│ Q1 facings correct? (C1/C2)  Q2 must-show 1..3 yes/no (A2)  Q3 style + sibling match (B1/B3)      │
│ Q4 legible at 32 px? (B2)  Q5 scale/footprint (D1/D3)  Q6 alpha/halo/shadow (D4)  Q7 owner note   │
│ honoured? (E4)  Q8 variants consistent (C2/B3)  → VERDICT per facing + set: KEEP/REDO/UNSURE      │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 What is image and what is text

| content | image | text (card.json → prompt) | why |
|---|---|---|---|
| defName, class, tier, sizes, px/cell, mod | label only (for humans) | **yes, authoritative** | models misread small rendered digits; the label on the PNG is for the owner |
| intended description, Must show, Engine limits | no | **yes** | text the model must quote back; pixels would invite OCR errors |
| owner notes (verbatim, dated) | no | **yes** | E4 needs the exact words |
| numeric gate results (alpha, canvas, cylinder b/a, symmetry, cross-facing spread) | small badge | **yes, with the number** | a measured number outranks the model's eye on what it measures (§3.5) |
| facings, scale strip, play-zoom strip, variants, sibling keeps, canon refs, installed/past art | **yes** | captions only | this is what the reviewer is for |
| the questions | no | **yes** | the ask is a closed list with answer slots (§3.3) |

Every panel tile is also sent as its **own image** beside the composite (§1.5): the composite gives the
comparison, the tiles keep detail above the model's resize limit.

### 1.3 Panel rules (the regularity the owner asked for)

| panel | always / when | rule |
|---|---|---|
| A facings | always for Graphic_Multi; one tile for Graphic_Single | fixed order **S E N W**; tile 512 px, subject fit to the visible-alpha bbox of the LARGEST facing so all four share one scale (a facing that looks big IS big); checkerboard background so a halo shows; W tile labelled `mirror` or `own file`; per-tile visible-alpha height printed (`rimworld-sprite-facings`: never `alpha>0`) |
| B true scale | always when the def has a world size | `scale_panel.py` unchanged: vanilla human composed as the engine does, 128 px/cell (256 for ≤1-cell subjects), biome ground colour, footprint outlined, candidate beside installed; FALLBACK sizes badged |
| C play zoom | always | 32 px/cell, on ground, actual pixels (not upscaled), so B2 is judged at what the player sees |
| D variants | whenever they exist | every member of the random pool / Graphic_Random folder (not a sample); female (`femaleGraphicData`), each lifestage with its own art (juvenile, baby), dessicated, damaged/stored/deployed/on/off states, stack-count stages; each tile labelled with the def field that selects it |
| E context | always | sibling keeps (owner-kept, B3) first; canon refs (reference, never judged); installed now; donor/past last (rank order from `art_requirements.md` req 4) |
| header + ask | always | text; constraint list = the brief IDs this template's checks cover, so the reviewer knows which it may cite |

### 1.4 One page per subject vs contact sheets

| mode | use | why |
|---|---|---|
| **one card per subject, one call per card** | every KEEP/REDO verdict | one subject per call stops cross-subject anchoring (a good neighbour lifting a weak one) and lets a verdict be re-run alone; it is also what the owner-verdict key is scored on |
| **contact sheet, 12–20 subjects, one call** | the cheap "obviously broken?" pre-pass (renders blank, wrong subject, garbage, background not cut) before cards are built | 10–20× cheaper per subject; good at gross failures, ESTIMATED poor at facing and style detail; its only output is DROP/PASS-TO-CARD, never KEEP |
| batch of cards in one call | ⛔ not used | worst of both: long context dilutes attention on late cards, and one bad output loses the batch |

### 1.5 Image size limits and cost per subject

| reviewer | image limit | card budget | per-subject images | cost / subject | latency / subject |
|---|---|---|---|---|---|
| Opus 5.5 (subagent or `claude -p`) | **2576 px long edge, ~3.75 MP, up to ~4784 image tokens per image** (Opus 5 tier; Opus 5.5 has "the same feature set" — `claude-api` skill, cached 2026-10-06; ESTIMATED that 5.5 keeps it) | composite **≤ 2560 × 1440**; tiles 512–1024 px | 1 composite + 4–8 tiles | ~25–40 k image tokens + ~6 k text in, ~2–4 k out → **≈ $0.15–0.25 at API list $4/$20 per MTok** (ESTIMATED); on the subscription it is quota, not dollars | **30–90 s** (ESTIMATED) |
| GPT (`gpt_consult.py -i`, codex exec, gpt-6.1-sol, high effort) | UNMEASURED for gpt-6.1-sol. Earlier GPT vision fitted an image into 2048² then shrank the short side to 768 px (a 2560×1440 card would be seen at ~1365×768); assume that until measured | same composite; **tiles carry the detail** — send every facing tile separately | 1 composite + 4–8 tiles (codex `-i` is variadic, already handled) | codex subscription: quota, not dollars; API-equivalent ESTIMATED similar order to Opus | **60–180 s** incl. ~10–20 s codex start-up (ESTIMATED; pilot measures) |
| contact-sheet pre-pass (either) | same | 1 image, 12–20 subjects at 256 px | 1 | ≈ 1/15 of a card each | 60–120 s per sheet |

Build cost (compositor, offline): ESTIMATED **< 2 s per card** with PIL from textures already resolved by
`scale_panel.py`/`gametex.py`; a 60-subject biome is ~2 minutes to build and, at 3 parallel reviewer calls,
~30–60 minutes to judge — against the owner's sitting it replaces.

## 2. Template taxonomy

### 2.1 How the art divides — MEASURED by path

11 047 PNGs under `src/**/Textures/` (`find … -name '*.png'`, classified by a path regex this sitting — a
**file** count, so a 3-facing creature counts 3; `other` = paths the regex could not place):

| class (path regex) | PNGs | share |
|---|---|---|
| creature (animal, bestiary, droid, mech, insect) | 4 048 | 36.6 % |
| pawn / apparel (apparel, hair, heads, bodies, genes) | 2 613 | 23.7 % |
| plant | 1 006 | 9.1 % |
| item (items, weapons, resources, junk) | 821 | 7.4 % |
| machine with ports (FlowWorks, Gimme Some Slack, pipe/hose/coupler/reel/cable) | 636 | 5.8 % |
| building (other) | 460 | 4.2 % |
| flyer (frames) | 334 | 3.0 % |
| UI icon | 230 | 2.1 % |
| effect (filth, mote, fleck, weather) | 130 | 1.2 % |
| terrain / floor | 103 | 0.9 % |
| other (unclassified) | 666 | 6.0 % |

### 2.2 The templates

**Offline** = the compositor can build every panel from textures + def data (no game). **Capture** = a panel
needs the running game, and why. "Hybrid" = per-texture panels offline, one assembled panel captured.

| # | template | covers | required panels (beyond header/ask) | class-specific checks (brief IDs) | build |
|---|---|---|---|---|---|
| T1 | **Creature** | walkers, insectoids, mechs, droids, swimmers (module flags) | A S/E/N/W · B · C · D sex, every lifestage with own art, dessicated · E siblings + canon | north = rear, no face (C1); facings same size/palette (C2); Must show (A2, A4 limits excluded); painterly, keyline (B1); legible at 32 (B2); sibling match (B3); registration on body mass (C4); alpha (D4); mech/droid: no lifestage/sex panel, weapon overlay tile; swimmer: on its sea floor colour | **Offline.** Animal body graphics are plain Graphic_Multi at drawSize; the engine adds nothing an evaluator judges |
| T2 | **Flyer** | flying creatures | T1 panels + **flip-book strip** (every frame per facing, body registered) + grounded-wings-folded tile | body pixel-stable across frames, only wings move (C4, C5); grounded wings folded, symmetric; flip-book not wing render-tree | **Offline, always.** ⛔ Never a live flight capture (owner: *"Don't try to capture images of flight. It doesn't work."*) |
| T3 | **Humanlike pawn / xenotype / head** | heads, hair, beards, bodies, face parts, xenotype genes, tattoos | body-type grid (Male/Female/Thin/Fat/Hulk/Child) × S/E/N; head at its headOffset; hair over head; **spawned-pawn screenshot** | face drawn whole, no floating/missing eyes (F1); head sized on skull mass (C4); hair/head sit together on every facing; canon species Must show (A2) with rig limits excluded (A4) | **Capture** for anything touching faces (F1 *requires* a screenshot of a spawned pawn: animated face parts, gene-driven colour and the render tree are runtime). Hair/body tiles offline as a pre-pass |
| T4 | **Apparel (worn)** | clothing, armour, headgear, packs, belts | the item worn on every body type × S/E/N over a vanilla body+head (offline compose by the body type's offsets); the ground/stuff icon; stuff-tint swatches if `useStuffColor` | no clipping of head/hands per body type; north shows the back; colour reads as material (B4); tinted variants legible | **Offline** (worn apparel uses the body's mesh and the BodyTypeDef head offset — deterministic). Capture only when F1 applies (face-covering headgear) |
| T5 | **Plant** | ground cover, bush, tree, crop, special (giant leaf, greatbole) | A single + every Graphic_Random member · B at mature visualSize with mesh count · C · D growth stages (immature graphic, leafless, harvested/stump, sown), cluster as the engine scatters it | silhouette reads as its kind at 32 (B2); variants one family (B3); a tree's crown vs trunk scale against a human (D1); random pool has no outlier; no painted ground shadow (D4) | **Offline.** `scale_panel.py` already reproduces drawSize × visualSize × mesh count. Wind sway is a shader and is not judged |
| T6 | **Item** | items, weapons, resources, junk, drugs, food, chunks | single or stack-count stages (all) · on the ground at 1 cell beside a human · in-hand weapon tile (equippedAngleOffset) · icon at 64 px | reads as what it is at 32 (B2); stack stages grow monotonically; in-hand orientation; material colour (B4) | **Offline** |
| T7 | **Building, single-graphic** | furniture, props, 1×1 and multi-cell, rotatable (Graphic_Multi) and Graphic_Random buildings | A each rotation · B footprint outlined, drawSize overhang shown · C · D states with own art (on/off, damaged, stored/deployed, open/closed) · E siblings in its family/style looks | **camera**: orthographic, ~35°, round top b/a 0.56 ± 0.04 (C3, `validate_sprite.py --upright-cylinder`), boxy: lit top + front band ~⅓ depth; extra height goes north, base on south edge; material not paint (B4); fits footprint (D3); no painted cast shadow | **Offline** |
| T8 | **Linked / atlas** | walls, fences, conduits, rigid pipes drawn as `Graphic_Linked`/`Appearance` atlases, sandbags | a **standard link test layout** (straight runs both axes, L, T, cross, isolated, 3-wide block) composed by a linker emulator from the atlas; one cell per variant at 128 px | seams invisible; front band 30–39 % of depth (C3 walls); corners and T's continuous; the run's perspective plane (C6) | **Offline with a linker emulator** (to build; LinkFlags and atlas indexing are deterministic). One capture the first time a family is evaluated, to prove the emulator matches |
| T9 | **Machine with ports & connectors** | FlowWorks/GSS machines: pumps, tanks, reels, couplers, hoses, cords, masts, under-couplers | T7 panels per part **+ an assembled panel**: the machine with every attached part (coupler, hose, cord) in place, each rotation, connected to a neighbour | pipe bore shows only where it turns toward camera (C6); coupler/hose/cord meet the port at the right cell, height and plane; parts share the machine's camera (C3) and material set (the four GSS looks); layering: what is in front draws in front | **Hybrid.** Part textures offline; the **assembled panel needs capture**: hose geometry is procedural (drawn by C#), coupler/port offsets and altitude layer order come from comps and `Altitudes`, and the pumping-station coupler fix is still "live look owed" (commit `30eac3ee40`) |
| T10 | **Pit / depth layer** | SUPERDEEP cells, deep canals, ladders into depth, seabed layer edges, depth overlays | the cell in a 5×5 neighbourhood of normal ground, each edge/corner case; ladder in place; the same at 32 px | edge reads as a drop, not a painted ring; depth darkening consistent; ladder perspective (D4 exception for `RM_LadderPortable` shadow) | **Capture.** Map-layer drawers (SectionLayer), altitude ordering and edge shaders compose these at runtime |
| T11 | **Terrain / floor** | natural terrain, floors, water, mud | 4×4 tiled block (seam check) · edge against two common neighbours · 32 px | seamless tiling; scale of detail vs a human (pebbles not boulders); edge type | **Hybrid.** Tiling offline; edge blending (`edgeType` Fade/FadeRough, water shaders) **capture** |
| T12 | **Effect / overlay** | filth, motes, flecks, weather overlays, glows, fire-like | filth: offline on ground, all variants; others: a short capture sequence (3 frames) | reads at 32; transparency right; not confused with a creature/item | **Filth offline; the rest capture** (shaders, animation, additive blending) |
| T13 | **UI icon** | gizmo/designator icons, research, gene and xenotype icons, uiIconPath | at 75 px gizmo size on the UI's dark background · at 32 px · beside 6 sibling icons of its set | recognisable at size; style matches siblings; not the thing's in-world sprite when an icon was asked (`reading-rimworld-graphics`: an icon is not the appearance) | **Offline** |
| T14 | **World map object** | world objects, settlement/site icons, hill/peak decals | world-view crop at play zoom | reads on the planet; scale vs neighbours | **Capture or `worldview.py`** (the planet is painted once at the end; low priority) |

**Count: 14 templates.** T1–T7 and T13 are fully offline; T8 offline once its emulator is proved; T9 and T11
hybrid; T3 (faces), T10, T12 (non-filth), T14 need capture.

### 2.3 The minimal set — 7 templates cover ≥ 90 %

| minimal template | absorbs | share of PNGs (§2.1) |
|---|---|---|
| T1 Creature (+ T2 flyer as a module) | creature + flyer | 39.6 % |
| T4 Apparel (+ T3 pawn as a capture module) | pawn / apparel | 23.7 % |
| T5 Plant | plant | 9.1 % |
| T6 Item | item | 7.4 % |
| T7 Building (+ T8 linked as a module) | building | 4.2 % |
| T9 Machine with ports | machine | 5.8 % |
| T13 UI icon | UI | 2.1 % |
| **total** | | **91.9 %** of all PNGs, **97.8 %** of the classified ones (MEASURED by path regex; the 6 % `other` is unplaced, not uncovered) |

Build order: T1 → T5 (the pilot's biome flora+fauna) → T7/T9 (the owner's perspective complaints) → T4 → T6 → T13.
T10–T12, T14 wait until a review actually needs them.

### 2.4 Offline vs capture — the split

| | templates | share of PNGs |
|---|---|---|
| **fully offline** | T1, T2, T4, T5, T6, T7, T13 (+ T8 after one proof capture) | ≈ 86 % (MEASURED classes; ESTIMATED that apparel needs no capture outside F1) |
| **hybrid** (parts offline, one assembled panel captured) | T9, T11 | ≈ 7 % |
| **capture required** | T3 faces/xenotypes, T10 pits, T12 effects, T14 world | ≈ 2–5 % (pawn heads/genes are inside the 23.7 % apparel line; not separated by the regex) |

Captures run through `rimworld-live-review` on the minimal mod list (22 s load, `rimworld-load-round`), batched
per review, held under the bridge lease, and saved as a keeper savegame so a re-evaluation never needs a new
capture. The capture panels are slotted into the same card; the reviewer never knows which panels were captured.

## 3. Prompt design

### 3.1 Structure — four layers, assembled by code, never hand-written per call

```
[1] SHARED PREAMBLE      (versioned file; identical for every subject and both reviewers)
[2] CLASS MODULE         (one per template: T1.md, T5.md, T9.md …; the checks of §2.2 as questions)
[3] CALIBRATION SET      (3–6 few-shot examples for THIS template, from the owner's past rulings, images + his verdict)
[4] SUBJECT CARD         (card.json as text + card.png + tiles; the questions with empty answer slots)
```

**[1] Shared preamble** (gist; the file is `prompts/preamble.md`):
- You are an art reviewer for a RimWorld mod. You did not make this art. Your verdicts decide whether a human
  ever sees it; a wrong KEEP costs his time, a wrong REDO costs a regeneration. Both are errors.
- RimWorld's view: south = the thing faces the camera; north = its back, no face; east/west = profiles; a
  top-down view rotated is never a facing. Buildings: orthographic, ~35° from horizontal, a round top is an
  ellipse 0.56 as tall as wide, extra height drawn north. (Facts, quoted from `rimworld-sprite-facings` and the
  building camera doc.)
- Judge ONLY against the constraints listed on the card, by ID. A constraint you wish existed goes in
  `proposals`, never in a verdict.
- **Describe before you judge.** First write what you see in each tile, in your own words, without reading the
  intended description. Then compare. (Anti-echo, §3.4.)
- Numbers on the card were measured by code. Do not re-estimate what a number measures; you may disagree with
  a number only by pointing at the pixels.
- If a panel is missing or unreadable, answer UNSURE for the questions that need it and say what is missing.

**[2] Class module** turns §2.2's checks into the template's question list, each bound to brief IDs. T1 example:

| Q | question | answer slot | cites |
|---|---|---|---|
| Q1 | For each facing, which surface of the animal is visible (front/rear/left/right/top)? Does north show a face or eyes? | per facing: `surface`, `face_visible` yes/no | C1 |
| Q2 | Do the four facings show the same animal at the same size and palette? Name any that differ. | yes/no + which | C2 |
| Q3 | For each Must show line: present yes/no, where | per line | A2 (A4 limits excluded) |
| Q4 | Painterly with a thin dark keyline, or flat cel / heavy black outline / photo? | one of 4 | B1 |
| Q5 | At 32 px (panel C), does the body read apart from the ground in a few bold shapes? | yes/no | B2 (advisory) |
| Q6 | Beside the sibling keeps (panel E): same artist, palette and size class? | yes/no + what differs | B3 |
| Q7 | Any backdrop, halo, painted ground shadow or scenery? | yes/no + where | D4 |
| Q8 | Each owner note: honoured yes/no | per note | E4 |
| Q9 | Variants (panel D): each a plausible member of the same set; any outlier? | per variant | B3, C2 |

T9 adds: *"Where does each pipe/hose show its open bore? Does the pipe turn toward the camera there?"* (C6);
*"Does each coupler/hose meet its port at the same height and plane?"*; *"Top rim of each round part: an
ellipse about half as tall as wide, or a circle facing the camera?"* (C3, with the measured b/a beside it).

**[4] Subject card**: card.json (§1.2) inlined as text, then the images in a fixed order (composite, then tiles
S, E, N, W, scale, play zoom, variants, siblings), each preceded by a one-line caption naming the panel.

### 3.2 The verdict schema (JSON, validated by code; an invalid reply is re-asked once, then UNSURE)

```json
{"schema": "rm-art-eval/v1",
 "subject": "RM_Duneskimmer", "template": "T1@v3", "prompt_version": "preamble@v2+T1@v3+cal@2026-10-23",
 "reviewer": "<model id>", "card_sha": "<sha256 of card.json+images>",
 "observed": {"south": "front of a low lizard, frill open, eyes visible", "north": "back, banded, tail", "...": "..."},
 "answers": {"Q1": {"south": {"surface": "front", "face_visible": true}, "north": {"surface": "rear", "face_visible": false}},
             "Q3": [{"line": 1, "present": true, "where": "neck"}, {"line": 3, "present": false, "where": "4 legs visible"}]},
 "verdicts": [
   {"facing": "south", "verdict": "KEEP", "codes": [], "confidence": 0.8},
   {"facing": "set", "verdict": "REDO", "codes": ["A2"], "seen": "four legs on every facing; canon has six",
    "quote": "Every ## Must show line is a yes/no check against the picture.", "redo_brief": "six legs, three per side", "confidence": 0.7}],
 "needs_human": false, "needs_human_why": null,
 "proposals": []}
```

- `verdict` ∈ {KEEP, REDO, UNSURE}; one per facing plus one for `set` (cross-facing and variant issues).
- `codes` — **closed vocabulary = the art judge brief's constraint IDs** (A1–A5, B1–B5, C1–C6, D1–D4, E1–E4,
  F1) plus four mechanical codes: `X-BLANK` (nothing rendered), `X-WRONG` (not the named subject), `X-CROP`
  (cut off by the canvas), `X-INPUT` (card incomplete). A REDO without a code, a `seen` and a `quote` is invalid
  (the brief's own rule).
- `confidence` 0–1 per verdict; `needs_human` true when any verdict is UNSURE, any confidence < 0.6, a canon
  ruling would be needed (A4 limit unclear).

### 3.3 Calibration examples (few-shot from his rulings)

- Source: the owner's past verdicts — sheets' `*.decisions.json` (MEASURED rough: 181 files under `Transient/`,
  ~974 rows with a note; schemas vary, a parser per schema version is owed) and his card/notes quoted in the
  brief (C6 pipe bore, B3 Varactyl, D4 ladder shadow).
- Per template, **3–6 examples**: at least one KEEP, one REDO per most-frequent reason code, and one
  *near-miss* (a picture he kept that looks wrong to a naive eye — teaches restraint). Each example is its card
  (downsized to one composite) + his verdict + his words + the codes a labeller assigned.
- ⛔ **Calibration examples are never in the scoring set** (`evaluation-independence` rule 1–5): the key is
  split once, by subject, before any prompt is written; the split file is committed and a script refuses to use
  a scoring subject as an example.

### 3.4 Anti-sycophancy, anti-anchoring, anti-echo

| risk | measure |
|---|---|
| **echoing the description** ("it has a frill, as described") | two-pass prompt: pass 1 sees images only and writes `observed` per tile; pass 2 adds the card text and judges. Code checks `observed` was written before the description was sent (two turns; for codex, two calls). A Must-show YES whose `where` cannot be found in `observed` is downgraded to UNSURE |
| **anchoring on the installed art or on "candidate"** | candidate/installed columns labelled by letter only, positions balanced (candidate left half the time), and the reviewer is not told which is newer |
| **KEEP bias** (models praise) | the preamble states both error costs; calibration includes REDOs at ≥ 40 %; the scoring harness reports REDO recall first; a template whose REDO recall < 0.7 does not ship |
| **anchoring on gate numbers** | numbers are given only for what they measure; the model is told it may not re-estimate them, so it neither defers on other things nor argues with them |
| **leading wording** | questions name the surface, never the hoped-for answer ("which surface is visible?", not "is the north correctly a rear view?") — the same rule as `rimworld-sprite-facings` "say the surface, never the compass" |
| **position / order** | facings always S E N W; across a batch of runs, subject order randomised |
| **self-grading** | the maker never reviews (delegation policy §4.1); a GPT-made render (codex imagegen) is reviewed by Opus first, and vice versa, when only one reviewer runs |

### 3.5 What code checks and what the model checks

The model is never asked a question a number already answers well; the number goes on the card and the model
is asked the residue.

| property | instrument | model's role |
|---|---|---|
| real alpha, canvas size, px/cell, footprint overflow | `validate_sprite.py`, `scale_panel.py` | none (D2–D4 mechanical) |
| cross-facing height/size spread | `facing_scale_lint.py` (> 15 % flag) | judge whether a flagged spread is real or a pose |
| north = rear | mirror symmetry catches profile-as-north **only sometimes** (Gizka 0.845 is a profile) | **primary** — the model is the instrument (`rimworld-sprite-facings`: "the ruled LLM judge IS the instrument") |
| round-top ellipse b/a | `validate_sprite.py --upright-cylinder` | judge where the fit is unusable (lugs, hatches) |
| pipe bore plane, coupler fit, style match, Must show, painterly | none | **primary** |
| placeholder / borrowed vanilla | `placeholder_detect.py` | none |

## 4. Reviewer strategy and quality estimate

### 4.1 The three options

| option | how | strengths | failure modes to expect | cost / latency per subject |
|---|---|---|---|---|
| **GPT** (`gpt_consult.py -i`, gpt-6.1-sol high) | one codex exec per card (two for the anti-echo pass) | the owner says it reviews art sheets *"very well"* (his observation, unscored); strong at style and aesthetic description; independent of the Opus that runs our seats | image downscaling to ~768 px short side (UNMEASURED for 6.1) blurs small detail — eyes on a north facing, a pipe bore, a 2-px keyline; codex start-up overhead; occasional sandbox/file hangs (`gpt_consult.py` docstring) | quota; 60–180 s (ESTIMATED) |
| **Opus 5.5** (fresh subagent or `claude -p`, no maker context) | one call per card; may crop and zoom its own tiles if given a crop tool | 2576-px images (fewer resize losses); the `claude-api` skill notes the Opus 5 tier is "stronger on chart, document and diagram understanding" and that *giving it tools to crop and verify* is its best vision lever; lives in our harness (structured output, re-ask) | the same family as the maker seats → correlated blind spots with our own looks (an independence cost, not a capability one); facing confusion on symmetric blobs is shared by every model | quota; 30–90 s (ESTIMATED) |
| **Both, ensemble** | both run blind on the same card; agree → that verdict; disagree or either `needs_human` → the owner's set, flagged *split* | errors of two different model families are only partly correlated, so agreement is a much stronger signal than either alone | 2× cost; disagreement rate sets how much reaches the owner — if it is high the ensemble saves him little | 2× quota; wall time = the slower one |

### 4.2 Quality estimate (ESTIMATED until §6 fills; reasoning given so it can be refuted)

Per check, the expected agreement with the owner's verdict on the same card:

| check | GPT | Opus 5.5 | reasoning |
|---|---|---|---|
| gross failure (blank, wrong subject, background, crop) | ≥ 95 % | ≥ 95 % | easy for any vision model; already caught in 17.8 s by a visual judge (Gizka) |
| north shows a face / profile passed as north (C1) | 80–90 % | 85–90 % | needs the tile at ≥ 512 px; GPT's downscale is the risk; the "which surface?" wording helps both |
| facings disagree in size/palette (C2) | 70–80 % | 70–80 % | models judge relative size poorly — the lint number carries this; the model only confirms |
| Must show line present (A2) | 75–85 % | 75–85 % | small parts (six legs vs four, a frill) are the classic small-detail miss; the observed-first pass reduces echo |
| painterly vs flat / heavy keyline (B1) | 85–90 % | 80–85 % | aesthetic vocabulary; the owner rates GPT highly here |
| sibling style match (B3) | 75–85 % | 75–85 % | needs side-by-side; the card gives it |
| building camera / pipe-bore plane (C3, C6) | 60–75 % | 65–80 % | perspective geometry is where vision models are weakest; the numeric ellipse fit carries the round cases; the bore question is a narrow, answerable one |
| legibility at 32 px (B2) | 70–80 % | 70–80 % | the brief makes it advisory anyway |
| **overall KEEP/REDO per subject** | **κ ≈ 0.5–0.65** | **κ ≈ 0.5–0.65** | dominated by the weakest checks a subject triggers |
| **ensemble, agreeing subset** | — | — | **κ ≈ 0.7–0.8 on the ~60–75 % of subjects where they agree**; the rest go to him flagged |

**Headline (ESTIMATED):** neither model alone is a substitute for the owner on perspective and small-detail
checks, and both are good enough to remove most of what he has had to say about facings, style and gross
defects. The ensemble with disagreement → human is the design default, and the expected effect is that
**roughly two thirds of subjects reach him already agreed by two model families, and his review becomes the
split third plus a sample**. Which model is better is not knowable from here; the pilot decides it per template,
and the design lets the winner be chosen per template, not globally.

### 4.3 How quality is measured — the scoring harness

The owner's past verdicts are the key. The harness follows `blind-evaluation`, `grader-validation` and
`evaluation-independence`:

1. **Key.** Extract (subject, picture sha, his verdict KEEP/REDO, his note, date) from every `*.decisions.json`
   and the art ledger (`artledger.py`), one row per picture he ruled. A labeller (Sonnet, checked by a script
   that the code is one of the closed vocabulary) maps each REDO note to brief codes. ⚠️ Owner verdicts are
   **incomplete ground truth** (`incomplete-ground-truth`): he ruled with different panels, sometimes reversed
   himself (Bolotaur, Gualaar, `rimworld-live-review`), and a KEEP may mean "good enough today". Reversed
   rulings are dropped from the key, not resolved.
2. **Split once, by subject, stratified by template:** calibration (examples) 20 % · scoring 60 % · frozen
   regression 20 %. Committed; a script refuses a scoring subject as an example.
3. **Blind.** The reviewer sees the card as built today from the picture he ruled, never his verdict, never
   whether it is installed, candidates lettered, positions balanced. The key sits outside the bundle.
4. **Metrics per template and reviewer:**
   - **REDO recall** (of his REDOs, how many the model called REDO) — the number that saves him time; ship bar ≥ 0.7.
   - **REDO precision** (of the model's REDOs, how many he also REDO'd) — wasted regenerations; bar ≥ 0.6.
   - **Cohen's κ** on KEEP/REDO (UNSURE counted as disagreement, and separately reported as abstention rate).
   - **Reason agreement**: for true-positive REDOs, does a model code match a labelled code? (a right verdict for
     the wrong reason does not generalise).
   - **Ensemble**: agreement rate, κ on the agreed subset, and what fraction would still reach him.
   - Confidence calibration: REDO precision binned by `confidence`.
5. **Controls that could have won** (`blind-evaluation` rule 2): a baseline that says KEEP to everything, and the
   numeric gates alone. A reviewer that does not beat the gates-alone baseline on a template is not used there.
6. **Mutation check** (`grader-validation` rule 5): plant 10 known defects (mirror a south into the north,
   paint eyes on a north, shrink one facing 30 %, add a halo, swap a sibling's palette) into kept art and confirm
   each reviewer catches them; a check that never fires is not a check.
7. **Set the refutation bar before running:** if both reviewers' REDO recall < 0.5 on T1 in the pilot, the
   automated route is not trusted for creatures and the owner's sheet stays primary for them.

## 5. Pipeline and skill

### 5.1–5.2 Where it sits, file layout — moved

The ensemble-and-reconcile flow first proposed here was replaced by the owner's pipeline (2026-10-23). The built
flow and file layout are §8 and `skills/rimworld-art-evaluation/references/pipeline.md`.

### 5.3 The skill

- **Name:** `rimworld-art-evaluation`.
- **Triggers:** before any game art reaches the owner (sheet, phone set, walk); after any render or regen
  lands; whenever a pre-review record is owed for an art sheet; when asked "does this art look right / is this
  facing correct / is this in the right perspective" for a sprite, machine, pit or pipe; when comparing
  reviewer models; when the owner overturns an agent art verdict (→ feedback).
- **Neighbours:** `rimworld-review-sheets` (his page), `art_judge_brief.md` (the constraints), `generating-rimworld-sprites`
  and `rimworld-sprite-facings` (the facts quoted in the preamble), `rimworld-live-review` (captures).
- Authored with `skill-creator:skill-creator` in a curation session (CLAUDE.md: skills are edited only there).

### 5.4 How the prompts get better — the feedback ledger

1. **Every owner override is a row** in `feedback.jsonl`: subject, card sha, model verdicts, his verdict, his
   words (`--owner-said`), date.
2. Same day (delegation policy §4.6): his reason becomes a **brief line** if it is a new constraint (sourced to
   his words), or a **new question** in the template module if the brief already had the constraint but no
   question asked it, or a **calibration example** if both existed and the model still missed it.
3. **Prompt versions** are files (`preamble@v2.md`); a verdict records the exact versions. A new version must
   **re-run the frozen regression split and not lose** REDO recall or κ by more than one subject's worth on any
   template before it is used; the score file is committed beside it.
4. The new owner override itself joins the **regression split** (never the calibration one it was fixed with —
   otherwise the fix is graded on its own example).
5. Weekly: the scoring run on new owner verdicts (the scoring split grows as he rules); a template whose recall
   drops below its bar is pulled back to "sheet primary" until fixed.

### 5.5 Build order (each step useful alone)

| step | delivers | depends on |
|---|---|---|
| 1 | `key_extract.py` + split + `score.py` | nothing — and it is what the pilot is doing by hand |
| 2 | `build_card.py` for T1 and T5 (offline) | `scale_panel.py`, `chat_review.py` code |
| 3 | `evaluate.py` with both reviewers, schema, two-pass anti-echo | `gpt_consult.py`, a `claude -p` call |
| 4 | `reconcile.py` writing the delegated verdict + prereview record | `prereview.py` |
| 5 | T7/T9 cards (camera checks; T9's assembled panel from a capture) | `validate_sprite.py --upright-cylinder` |
| 6 | the skill; T4, T6, T13 | |

## 6. Pilot results

Scored 2026-10-23: `Transient/art_eval_pilot_20261023/SCORE.md` (pinned). RM_WeepingStones, 47 subjects, owner
18 REDO / 28 KEEP / 1 CUT; always-KEEP baseline 28/47. Small N: accuracy 95 % intervals are ~±0.13.

| measure (all 47; clean 39 in brackets) | GPT gpt-6.1-sol high | Opus 5.5 | both agree → auto | always KEEP |
|---|---|---|---|---|
| accuracy · Cohen's κ (MEASURED) | 33/47 · 0.39 (29/39 · 0.47) | 35/47 · 0.44 (28/39 · 0.40) | 27/32 auto correct | 28/47 · 0 |
| REDO recall · precision | 11/18 · 11/18 | 9/18 · 9/11 | 6 auto-REDO, 8 to him, **4 silently kept** | 0/18 |
| his defect named, 16 judgeable REDO notes (one rater) | 8 HIT, 8 MISS | 8 HIT, 7 PARTIAL, 1 MISS | either HIT 11 | — |
| abstention / needs_human | 0 / — | 0 / 8 | — | — |
| GPT↔Opus agreement · fraction to him | — | — | 32/47 (κ 0.27) · 15/47 | — |
| latency (MEASURED) · tokens (no resize: PNGs ≤ 2000 px) | 24 s/call, 1131 s summed · UNMEASURED | 629 s wall, ~13 s/subject · UNMEASURED | | |

Decisions: (a) **no reviewer alone**; GPT vs Opus is a tie on accuracy (McNemar 6 vs 8 discordant). GPT
perceives less (misses "too camel", catch/species mismatch) but rules hard; Opus sees the defect almost every
time but files it as polish. Run both; disagreement → him. (b) §4.2's estimates are not yet testable on this N;
the ensemble's 4 silent misses (swimmers/catches) mean an agreed KEEP is not yet safe to auto-ship. (c) Card
defects found: the living reference on catch rows is unlabelled, two-slot catch rows look like donor picks.
Top prompt fixes (SCORE.md §6): catch verdict depends on the living row's verdict; "reads as Earth X" is
blocking for invented creatures; every reason tagged blocking/polish, REDO iff blocking. Re-race on a
different biome before quoting any improved rate.

## 7. Risks and open questions for the owner

### 7.1 Risks (ours to manage)

| risk | mitigation |
|---|---|
| key is noisy: his verdicts were given on older, different panels and some were reversed | drop reversed rows; report scores with n; never tune to agreement (`evaluation-independence` §6) |
| calibration leakage makes the score look better than it is | frozen split, refused by script |
| reviewers share blind spots (perspective, tiny parts) → ensemble agrees and is wrong | mutation fixtures per template; his sampled audit of agreed KEEPs (Q3 below) |
| GPT downscaling hides detail | per-facing tiles as separate images; measure the applied resize in the pilot |
| capture templates (T9 assembled, T3 faces) bottleneck on the bridge | captured once into a keeper save, re-evaluated offline from it |
| the model echoes the description | observed-first two-pass, `where` must appear in `observed` |
| volume: hundreds of renders a night → quota | numeric gates first, contact-sheet pre-pass, ensemble only on survivors |

### 7.2 Open questions (each becomes a question card)

1. **ANSWERED 2026-10-23 (§8): Opus first, GPT only on weak.** ~~Ensemble or one reviewer?~~ Run GPT and Opus on every subject and send him only the splits (2× quota,
   fewest wrong KEEPs), or the pilot's winner per template alone (half the quota, more wrong KEEPs reach him)?
2. **ANSWERED 2026-10-23 (§8): auto-accept, then a shadow sheet after the run until a template earns trust.** ~~What may an agreed KEEP do?~~ Install without his look (delegation policy allows it), or always appear on
   his next sheet as "pre-approved, glance only"?
3. **ANSWERED 2026-10-23 (§8): every decision on the shadow sheet while shadow mode is on; the turn-off threshold is §8.4 Q2.** ~~Audit rate of agreed verdicts.~~ Should he see a random sample (say 10 %) of agreed KEEPs and REDOs every
   sitting so drift is caught — or only flagged rows?
4. **Is his past verdict history the right key?** Some rulings were "good enough for now". Use all of them, or
   only rulings he marks as standing (a short sitting to mark them)?
5. **Capture budget.** May machines-with-ports (T9) and xenotype faces (T3) wait for a batched capture
   session, or must every such render be captured before it reaches him?
6. **Bars to ship a template.** REDO recall ≥ 0.7 and precision ≥ 0.6 — right, or does he want a stricter
   recall (fewer bad pictures reaching him at the cost of more regenerations)?
7. **ANSWERED 2026-10-23 (§8): Opus always looks first; GPT is never the sole judge of a GPT-image render.** ~~Does GPT's own art get GPT's review?~~ Codex imagegen makes most renders; should a GPT-made render always
   be judged by Opus (independence), with GPT only as the second opinion?

## 8. The adopted pipeline (BUILT 2026-10-23)

### 8.1 His words

Owner, 2026-10-23, by card (his words), on reviewers: *"None of those. Opus scores first. If it says good, auto-accept.
If it says really bad, regen. If it says weak/need a call, send to GPT. If GPT says strong accept, accept, otherwise
regen. If Human live walk notices a problem, look back and improve evaluation criteria or process that generated the
issue. Please evaluate this proposal for issues and improve."* On the experiment: *"Use the system right now, but
while we're evaluating it, build human review sheets AFTER the process works for quick human feedback. Then we turn
the human review off when it looks good."* Scope: *"Creatures + plants + machines (Recommended)"*.

### 8.2 His pipeline, with the seat's guards (each: owner's rule + guard)

Full text, evidence and code pointers: `skills/rimworld-art-evaluation/references/pipeline.md`.

| # | owner's rule | guard added | why (evidence) |
|---|---|---|---|
| 1 | Opus good → accept | good = 0 policy-blocking findings + every checklist item answered ok + model did not doubt; severity from `severity_policy.md`, never the model | pilot: Opus saw 15/16 of his defects but called 7 minor (§6) |
| 2 | weak → GPT | a TARGETED second look: GPT answers each Opus concern confirmed/refuted/unclear | GPT perceives less than Opus (§6); it settles named questions |
| 3 | GPT strong accept → accept | strong = every concern refuted WITH evidence + no blocking finding of its own | a bare "looks fine" is not a refutation |
| 4 | otherwise regen | the unrefuted blocking findings become explicit prompt edits; ≤ 3 rounds, then ESCALATE (one line) | a reroll repeats the defect; delegation_policy §4.5 |
| 5 | — | owner-KEPT art may be redrawn on a regen verdict, only with a revert record; flagged *replaced your kept art* on the shadow sheet with a one-click revert | owner card 2026-10-23 06:42: *"Yes, but show me after"* (delegation_policy §2.3 exception) |
| 6 | — | Opus always first: the GPT-image generator is never the sole judge of its own output | independence |
| 7 | shadow sheets after, turned off when good | `shadow.py`: gated art_sheet sheet, decision + verdicts per row, KEEP/OVERRIDE; prereview.json from the run; per-template streak, threshold a setting (30) | his experiment answer |
| 8 | live walk → improve criteria | criteria ledger (`ledger.py`) → a named check/prompt/policy change + regression example; `runner.py regress` on every prompt version | his rule |
| 9 | — | catch items follow their living animal (REGEN_AFTER_SOURCE); invented subjects get description-derived required departures instead of a blunt Earth-animal rule | pilot §5–§6: catch REDOs = species redone; blunt rule flips Burrak/Vobbal |
| 10 | — | every decision logs prompt versions (tag + sha), model ids read back from the CLIs, card + source image sha256s | reproducibility; nothing names an account |

Machines (T9) are built as a template but every machine card without the in-game **assembled** capture is
`HOLD_INPUT` — never judged on part textures alone.

### 8.3 End-to-end run (MEASURED, test mode)

Run `infrastructure/state/art_eval/runs/e2e_weepingstones_20261023/` (+ `_r2`): 6 pilot subjects, one candidate each
(the render he ruled on 2026-10-10), Opus = `claude-opus-5-5`, GPT = `gpt-6.1-sol`, regen prompts =
`claude-sonnet-5-5` (all read back from the CLIs).

| subject | his verdict | pipeline | path |
|---|---|---|---|
| RM_Huldu C | REDO | REGEN | Opus REALLY_BAD (Earth otter, departures missing, facings) |
| RM_Ssurr B | REDO | REGEN | Opus REALLY_BAD (fan does not turn with the body — his defect) |
| RM_Vellak B | REDO | REGEN | Opus WEAK → GPT confirmed facing inconsistency (GPT refuted "camel") |
| RM_HulduCatch C | REDO | REGEN_AFTER_SOURCE | living Huldu REGEN — no model call |
| RM_Burrak B | KEEP | REGEN | Opus REALLY_BAD (Earth body + facing size) — a false regen; ledger CL-003 OPEN |
| RM_Shadefern B | KEEP | REGEN | Opus WEAK → GPT: Earth fern. Fixed (CL-001: plants get `earth_body_named`); re-run r2 still REGEN on ANCHOR (both models) — CL-002 OPEN |

All 4 of his REDOs were kept from shipping; 2 of his 2 KEEPs were sent to regeneration (wasted renders, not bad art
shipped). Timing: Opus 21–47 s per call, GPT 25–41 s, regen prompt 10–15 s; ~55–100 s per subject end to end.
Claude cost as reported by the CLI: ~$0.31–0.38 per Opus call, ~$0.12 per regen prompt (subscription quota, not
billed). **Caveats:** N = 6 is a function check, not a score; the severity tolerances were taken from this same
sitting's verdicts (pilot §6), so this run cannot validate them — the shadow sheets on NEW renders are the test.
The shadow sheet built for this run passes the 14-requirement gate and its prereview check, and correctly FLAGs 5
rows: the judged (historical) pictures are no longer what the sheet shows — production specs carry their
`artpipe_job` so the judged render is a column.

### 8.4 His answers (owner cards 2026-10-23 06:42)

1. **Kept art** — *"Yes, but show me after"*: the pipeline may redraw kept art on a regen verdict; every swap is on
   the next shadow sheet flagged *replaced your kept art*, revertible in one click through the art ledger.
2. **Shadow turn-off** — *"30 in a row (Recommended)"*: 30 consecutive subjects per template with no blocking override.
3. **Blocking override** — *"Keep that definition (Recommended)"*: an accept↔regen flip, "other" or a REVERT; polish notes don't count.

