# CANON_CREATURE_REGEN_1 — regenerate every SW-canon creature under library guidance

Filed by BENCH, 2026-09-13. Owner: *"THEN we regenerate canon creatures with
that guidance."* Gated on CANON_REFERENCE_LIBRARY_1 (the guidance) alone.

🔴 The toy-figurine pilot that once gated this item is DEAD — terminated by the
owner 2026-09-15, its art and lawset deleted. Painterly is the only style law.

## spec

Every SW-canon creature in the stack (the library's roster), re-rendered:
prompts authored from the library entry (owner ruling > images > text), under
the RESTORED PAINTERLY style law (ART_PAINTERLY_RESTORATION_1, owner
2026-09-14 — painterly is the only style law; the legibility gate is advisory,
never a rejector), vivid coloration and drawSize×128 sizing surviving, all
shipped facings, through the daemon. The Wyyyschokk is the acceptance exemplar: the regen must
show blue-grey body, yellow-orange abdomen cross, bristle tufts — not a brown
hairy spider. Renders reviewed on a sheet showing the library candidates
BESIDE each render (fidelity judged, not remembered). Pyrelands roster canon
creatures may land via PYRELANDS_CREATURE_RERENDER_1 first — do not
double-generate; check the registry.

## verify

Per creature: library entry cited in the job prompt note; gate band recorded;
fidelity sheet served; owner's fidelity grades collected. Zero canon creature
regenerated from memory or bare text.

## Watch out

- Two borderline gate cases from the pilot (wyyyschokk 1.30, dragonsnake
  1.10) show the fitted model strains on thin-legged and dark-serpent body
  plans — collect the owner's grades on exotic body plans and recalibrate
  (a size/body-plan-stratified regrade) rather than forcing the stroke.
- Codex budget: this is ~dozens of creatures × facings; batch by wave,
  report spend per wave.

## 2026-09-18 wave 1 (FOUNDRY, belt mode, subagent)

**Checked what was already done before generating anything** (per this item's
own gate and the CLAUDE.md lesson about re-verifying before acting): Pyrelands
roster canon creatures (Anooba, Iriaz, Nuna, Orray, Zeer, Dalgo) are out of
scope here per `PYRELANDS_CREATURE_RERENDER_1`; Anooba/Orray/Zeer/Gizka/Dalgo
were already regenerated this session (`dde341c12`, "Canon-5 lawset renders
installed"); Wyyyschokk/Dragonsnake/Pekopeko/Dactillion were the now-DEAD
toy-figurine pilot (`c5b3e3ad3`) and are not painterly yet, but were left for
a later wave rather than picked here since they're the pilot's own
recalibration subjects (see Watch out above). Several other creatures
(Boma, Dewback, Insectomorph, Shiro, Vornskyr, Whisperbird, Zakkeg) were hit
by pre-library art waves (toy-figurine or the old `star_wars_canon_names.md`
check) but not the canon-reference library — left for a future wave, not
double-counted as "done" here.

**Picked 5 clearly-uncovered creatures, all with an existing owner ruling
in their library entry** (from the 2026-09-14 reference-image review sheet,
`Transient/canon_review_sheet.html` / `canon_review_decisions.json`) so this
wave's prompts have the strongest possible provenance:

| creature | defName | library entry cited | ruling followed | canvas (drawSize×128, ceiling) |
|---|---|---|---|---|
| Acklay | `RSW_Acklay` | `design/RimStarWars/canon_references/acklay/description.md` | "regenerate to something more like #2 [green]... more surface texture" | drawSize 2.9 → 512 |
| Beldon | `RSW_Beldon` | `.../beldon/description.md` | donor's orange gas-bladder look confirmed correct | drawSize 1.0 → 256 |
| Borcatu | `RSW_Borcatu` | `.../borcatu/description.md` | "Mix #1 and #2 together... #3 is HORRIBLE, ignore" | drawSize 1.1 → 256 |
| Can-cell | `RSW_CanCell` | `.../cancell/description.md` | "Follow this render" (Teth CGI, Clone Wars film) | drawSize 1.25 → 256 |
| Wampa | `RSW_Wampa` | `.../wampa/description.md` | "giant ape-like predator, capable of standing upright" | drawSize 2.0 → 256 |

Each prompt was authored directly from that entry's Visual brief / Must-show /
ruling (not memory) — e.g. Acklay's prompt states "green (never blue-teal)…
textured and ridged… six legs, two raised as grappling arms" verbatim from
the entry's Must-show list. `drawSize` read from
`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_*.xml` (largest life
stage), canvas = drawSize×128 rounded up to next pow2, floor 256
(ART_PAINTERLY_RESTORATION_1) — all 5 landed exactly on the computed ceiling,
no oversize warning.

**Filed via `fill_queue.py`** (`infrastructure/artpipe/pending/`,
`rimflow_item_id=CANON_CREATURE_REGEN_1`), 3 facings each (east/north/south,
15 jobs total), style shape matching the `ronto_v1_east` painterly exemplar
verbatim ("RimWorld creature sprite, side view, painterly vanilla-RimWorld
animal art style: …"). The word "painterly" is used deliberately —
`ART_PAINTERLY_RESTORATION_1` restored it ("the word is back, it names the
style"); the `PYRELANDS_CREATURE_RERENDER_1` Watch-out line banning it
predates that restoration by one day and is stale.

**Result: 15/15 generated, 0 failed**, `infrastructure/artpipe/done/canon_*`.
**Gate band: `legibility=skipped`** on all 15 — the fitted-model gate is
disabled by default (advisory-only per `ART_PAINTERLY_RESTORATION_1`), so
"skipped" is the expected value, not a miss; no borderline scores to
recalibrate against this wave. Canvas confirmed exact on every manifest
(512×512 Acklay, 256×256 the other four). **Spend**: ~1,512 worker-seconds
of Codex generation across 15 calls (~100 s/call average), ~8–9 minutes wall
time on 3 daemon workers; no dollar cost (Codex subscription channel,
`cost_usd: null` throughout — this project's Codex spend is tracked as
context-window %, never $).

**Fidelity sheet**: `Transient/canon_regen_wave1_2026-09-18/sheet.html`
(served via `review-sheets`' `serve_sheet.py`, decisions at
`Transient/canon_regen_wave1_2026-09-18/decisions.json`) — one row per
creature, each showing a composite (`<slug>_fidelity.png`) with the
owner-ruled canon reference image beside the three new renders. **All 5 rows
are deliberately left un-prefilled** — `check_sheet.py` reports exactly one
FAIL for this (`rows are pre-filled`, 0/5) and it is intentional, stated in
the sheet's own "invented rules" panel: this wave's brief was explicit that
fidelity grading is the owner's call, not this agent's, so no
keep/close/redo grade was fabricated to make the gate green. **Not yet
graded — the owner has not looked.** No art was deployed to any ArtOverride
mod or the Mods folder this wave; that is owed only after his grade.

**Note, not actioned**: the Can-cell ruling also said "Rename to Can-cell" —
a display-name change, out of this art-only wave's scope; flagged on its
sheet row for whoever picks up naming.

**Wave 2 candidates** (ruled in the library, not yet regenerated, not
Pyrelands-scoped): Dianoga, Eopie, Fanback, Hawkbat, Jerba, Kinrath, Kreetle,
Vulptex.

Files: `infrastructure/artpipe/done/canon_{acklay,beldon,borcatu,cancell,wampa}_v1_{east,north,south}.json(+.manifest.json)`,
`Transient/canon_regen_wave1_2026-09-18/` (composites, sheet.html,
decisions.json).

Left `doing` — this is wave 1 of many, not a close.
