# CANON_CREATURE_REGEN_1 — regenerate every SW-canon creature under library guidance

Filed by BENCH, 2026-09-13. Owner: *"THEN we regenerate canon creatures with
that guidance."* CANON_REFERENCE_LIBRARY_1 (the guidance) closed
`779938cbb2c43ab0390afd9e2d94d519367af707`; this item is unblocked and `doing`.

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

## 2026-09-18 wave 2 (FOUNDRY, belt mode, subagent)

**Re-verified the named candidate list before generating anything.** All 8
wave-2 candidates named in wave 1 (Dianoga, Eopie, Fanback, Hawkbat, Jerba,
Kinrath, Kreetle, Vulptex) do carry an owner ruling in their
`design/RimStarWars/canon_references/<slug>/description.md` entry and none
are Pyrelands-scoped, confirming wave 1's list. But per-creature history
checks (`git log --oneline --all -- '*<name>*'`, texture-folder searches)
found **3 of the 8 already carry art from a pre-library wave**:

- **Hawkbat** — `HawkbatArtOverride` mod (`Art-review platform: install
  every gate-passed render awaiting verdict (95 stems)`, cea007c3a)
- **Kinrath** — `KinrathArtOverride` mod, same commit
- **Kreetle** — `KreetleArtOverride` mod (`ART_REGEN_WAVE1_WIRE_IN_1`,
  1dfd4b36f, "reference gathered online per the redo-semantics ruling")

All three predate both the canon-reference library (2026-09-13/14) and
`ART_PAINTERLY_RESTORATION_1` (2026-09-14) — same bucket as wave 1's own
Boma/Dewback/Insectomorph/Shiro/Vornskyr/Whisperbird/Zakkeg exclusion.
**Left uncovered for a future wave** rather than picked here, both because
they need the same treatment wave 1 gave that bucket and because replacing
an already-wired `ArtOverride` mod's texture is a slightly different
operation (touches an existing mod, not just artpipe filing) that deserves
its own attention rather than being rushed into this wave.

**Picked the remaining 5 clearly-uncovered creatures** — matching wave 1's
pacing exactly (5 creatures × 3 facings = 15 jobs):

| creature | defName / donor | library entry cited | ruling followed | canvas (drawSize×128, ceiling) |
|---|---|---|---|---|
| Dianoga | `RSW_Dianoga` | `.../dianoga/description.md` | "Mixture of #2 [Battlefront infobox] dominant with some hints of #1" | drawSize 3.8 → 512 |
| Eopie | `RSW_Eopie` | `.../eopie/description.md` | "regenerated Eopie... pretty good, but [legs need fixing]... remove and regenerate to the new spec level" | drawSize 2.25 → 512 |
| Fanback | `Fanback` (donor `mlie.starwarsanimalcollection`, not vendored) | `.../fanback/description.md` | "supposed to be olive green, not just brown... Make it Olive colored" | drawSize 3.5 → 512 |
| Jerba | `RSW_Jerba` | `.../jerba/description.md` | "Definitely shaggy, huge mouth, long ears. Confirmed. NOT the Bantha picture" | drawSize 1.2 → 256 |
| Vulptex | `RSW_Vulptex` | `.../vulptex/description.md` | Wookieepedia infobox render (crystalline coat) | drawSize 1.45 → 256 |

`drawSize` read from each `RSW_*` ThingDef's largest life stage in
`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/`; canvas = drawSize×128
rounded to next pow2, floor 256 — all 5 landed exactly on the computed
ceiling. Each prompt was authored directly from that entry's Must-show list
and ruling (not memory) — e.g. Dianoga's prompt states "several long, thin,
tapering tentacles radiate and hang downward... NOT four legs and a tail"
verbatim from the Must-show list, since the donor sprite is a legged mammal
misdrawn as this cephalopod.

**Two provenance notes flagged rather than silently resolved** (both also on
the fidelity sheet):
- **Eopie's ruling text is genuinely ambiguous** read literally against its
  own Must-show list (which *requires* four thin legs) — "it has legs...
  remove and regenerate" most likely refers to the existing Aug-24 pre-library
  regen's stilt-like leg proportions (that commit's own words: "a camel body
  on stilt legs"), not an instruction to remove legs entirely, since the
  ruled reference image (`wookieepedia_infobox.png`) itself clearly shows
  legs. Prompted per the Must-show list (thin legs, low camel silhouette);
  flagged for the owner to correct if this reading is wrong.
- **Jerba ships today sharing `RSW_Bantha`'s texPath** (owner's earlier,
  separate instruction, predating this canon-library ruling) — this wave
  generated Jerba dedicated art per the 2026-09-14 ruling ("NOT the Bantha
  picture"), but wiring a *new* texPath into `RSW_Jerba`'s ThingDef is
  deploy-step work belonging to whoever wires this wave's art in, not done
  here.

**Filed via `fill_queue.py`** (same mechanism as wave 1:
`infrastructure/artpipe/pending/`, `rimflow_item_id=CANON_CREATURE_REGEN_1`),
3 facings each (east/north/south, 15 jobs total), same painterly style
shape as wave 1's prompts verbatim ("RimWorld creature sprite, side view,
painterly vanilla-RimWorld animal art style: …", heavy black outline
clause). The already-running `artpiped.py` daemon (no restart needed)
picked all 15 up automatically; facing-direction wording (rear-view/no-face
for north, face-on for south, strict side profile for east/west) is
injected by the daemon itself (`artpiped.py` `_SPRITE_ART_DIRECTION`/
`facing_direction` block) from the bare `facing` field, not authored by
hand in the prompt — confirmed by reading the daemon source before filing,
same as wave 1's prompts show no facing text either.

**Result: 15/15 generated, 0 failed, all on the first attempt** (0 retries),
`infrastructure/artpipe/done/canon_{dianoga,eopie,fanback,jerba,vulptex}_*`.
**Gate band: `legibility=skipped`** on all 15 (fitted-model gate disabled by
default per `ART_PAINTERLY_RESTORATION_1` — expected, not a miss). Canvas
confirmed exact on every manifest (512×512 Dianoga/Eopie/Fanback, 256×256
Jerba/Vulptex). **Spend**: ~1,503 worker-seconds of Codex generation across
15 calls (~100 s/call average, in line with wave 1's ~100 s/call), ~7.8
minutes wall time (466 s between first and last manifest write) on the same
3 daemon workers; no dollar cost (Codex subscription channel, this
project's Codex spend is tracked as context-window %, never $).

**Fidelity sheet**: `D:\\Luke\\dev\\Rimworld\\Transient\\canon_regen_wave2_2026-09-18\\sheet.html`
(served via `review-sheets`' `serve_sheet.py` at
`http://localhost:36611/?t=OPIs585iKHYTh1HrzpU9xQ` — port/token are
per-launch and will differ if re-served; decisions at
`D:\\Luke\\dev\\Rimworld\\Transient\\canon_regen_wave2_2026-09-18\\decisions.json`)
— one row per creature, each showing a composite (`<slug>_fidelity.png`,
owner-ruled reference beside the three new east/north/south renders).
`check_sheet.py` reports exactly one FAIL (`rows are pre-filled`, 0/5),
same intentional gap as wave 1: fidelity grading is the owner's call, not
this agent's, so no keep/close/redo grade was fabricated. **Not yet graded —
the owner has not looked.** `serve_sheet.py --status` confirms
`touchedBySheet: false`, `decided: 0` — this is still the untouched
pre-fill, nothing to mistake for a real review. No art was deployed to any
ArtOverride mod or the Mods folder this wave; owed only after his grade
(and, for Jerba specifically, after a texPath/ThingDef change too — see
above). Sheet served over `localhost`/WSL relay via `explorer.exe`, same
mechanism as wave 1; a real-browser click-test of the sheet's controls was
NOT performed this wave (chrome-devtools MCP failed to connect in this
session) — the script itself is unchanged from wave 1's already-proven run.

**Wave 3 candidates** (ruled in the library, not yet regenerated under
canon-library+painterly guidance, not Pyrelands-scoped): **Hawkbat, Kinrath,
Kreetle** — each needs its existing pre-library `ArtOverride` mod's texture
replaced in place (not a fresh `fill_queue.py` filing into empty space),
which is worth its own wave rather than folding in here. Beyond those three,
the other "pre-library art wave" creatures wave 1 named (Boma, Dewback,
Insectomorph, Shiro, Vornskyr, Whisperbird, Zakkeg) remain equally
uncovered by the canon-reference library and are candidates for whichever
wave picks up this same "replace an existing ArtOverride" pattern.

Files: `infrastructure/artpipe/done/canon_{dianoga,eopie,fanback,jerba,vulptex}_v1_{east,north,south}.json(+.manifest.json)`,
`Transient/canon_regen_wave2_2026-09-18/` (composites, sheet.html,
decisions.json, serve.log).

Left `doing` — wave 2 of many, not a close.

## 2026-09-23 wave 3 (FOUNDRY, belt mode, subagent)

**Checked the artpipe done-queue before generating anything, per this item's
own gate and the CLAUDE.md standing rule "Check for existing regenerated art
before queuing more".** All 9 renders for the three wave-2-named "wave 3
candidates" (Hawkbat, Kinrath, Kreetle — each already ships a pre-library
`ArtOverride` mod, per wave 2's note) were found **already generated and
sitting unused**: `infrastructure/artpipe/done/canon_{hawkbat,kinrath,kreetle}_v1_{east,north,south}.json`
+ `.manifest.json`, every one `status: ok`, `rimflow_item_id:
CANON_CREATURE_REGEN_1`, prompts authored directly from each creature's
library ruling (same painterly style shape as waves 1/2, e.g. Hawkbat's
prompt states "the Legends field-guide design, NOT the Star Wars Rebels
loth-bat and NOT a generic fanged dragon-bat... Wing membrane violet-purple
on the dorsal side fading to cream/pale-gold on the ventral side" verbatim
from that entry's ruling). PNGs live at
`infrastructure/artpipe/_artsrc/canon_{name}_v1_{facing}/canon_{name}_v1_{facing}.png`.
Job/manifest timestamps are **2026-09-18T08:25–08:30Z / worker rollouts
01:25–01:30 that same morning** — the same day as waves 1/2, evidently filed
and completed by a separate pass that ran despite wave 2's own note saying
these three were "left uncovered for a future wave" — but never surfaced on
a sheet or graded. **Nothing was regenerated this wave**; this pass only
found, verified and surfaced existing work, per the standing rule.

**Verified each render against its library ruling before building the
sheet** (`preview_alpha.py` on all 9 facings, read at display size): Hawkbat
matches the ruled `wookieepedia_legends_infobox.jpg` reference closely
(violet-to-cream wing gradient, forehead horn, hooked beak, long tail,
clawed wingtips); Kinrath matches the current-canon "netcaster" design line
the ruling points at (six-eye cluster, six-petal flower organ, golden-tan
banded spoon body, no blue anywhere); Kreetle matches the ruled
`wookieepedia_infobox.jpg` (domed ribbed maroon shell, mottled tan/spotted
head, dark mandibles, yellow eyes). All three read correctly per facing too
(east strict side profile, north rear-view with no face visible, south
face-on) — the daemon-authored facing wording was reconstructed by hand from
`src/RimMandrake/Utils/artpipe/artpiped.py`'s `facing_direction` dict since
this pass did not use the daemon (below), confirming the *existing* renders
already got it right when they were generated in-daemon on 2026-09-18.

**Canvas note, not resolved here**: Hawkbat and Kreetle rendered at 256x256
(drawsize 2.0 / 1.0 x 128, floor 256) and Kinrath at 512x512 (drawsize 2.5 x
128); the shipped `ArtOverride` textures for all three are 512x512. The
donor mod (`mlie.starwarsanimalcollection`) is not vendored, so no local
ThingDef exists to re-derive drawsize independently — flagged on the sheet
for whoever wires this in, not fixed here.

**Did not touch `infrastructure/artpipe/pending/`** — that queue is being
actively driven by a concurrent process this session (visible in this
session's own `git status`, dozens of `pending/*.json` deletions for
unrelated subjects mid-processing). No new job was filed.

**Fidelity sheet**: `Transient/canon_regen_wave3_2026-09-23/sheet.html`
(served via `review-sheets`' `serve_sheet.py`, decisions at
`Transient/canon_regen_wave3_2026-09-23/decisions.json`) — one row per
creature, each showing a composite (`<slug>_fidelity.png`, built fresh this
pass from the owner-ruled reference image beside the three already-existing
east/north/south renders). `check_sheet.py` reports exactly one FAIL (`rows
are pre-filled`, 0/3), same intentional gap as waves 1/2: fidelity grading
is the owner's call, not this agent's. **Not yet graded — the owner has not
looked.** `serve_sheet.py --status` confirms `reviewStatus.state: prefill`,
`decided: 0`. No art was deployed to any `ArtOverride` mod this wave; owed
only after his grade (and, for Hawkbat/Kreetle, after the canvas-mismatch
question above is resolved).

**Remaining candidates**, same bucket, still uncovered: Boma, Dewback,
Insectomorph, Shiro, Vornskyr, Whisperbird, Zakkeg (named in wave 1's own
note as hit by pre-library art waves, not the canon-reference library).
Checked the done-queue for these too before stopping — **none have a
`canon_*` job in `infrastructure/artpipe/done/` or `pending/`**, so unlike
Hawkbat/Kinrath/Kreetle these are genuinely ungenerated, not just
unsurfaced. Left for a future wave — this wave's scope was the three
explicitly-named wave-3 candidates plus the done-queue check the brief
required before generating anything, and finding all three already done
closed that scope without spending any Codex budget.

Files: `infrastructure/artpipe/_artsrc/canon_{hawkbat,kinrath,kreetle}_v1_{east,north,south}/*.png`
(pre-existing, dated 2026-09-18, first surfaced this wave),
`infrastructure/artpipe/done/canon_{hawkbat,kinrath,kreetle}_v1_*.json(+.manifest.json)`
(pre-existing),
`Transient/canon_regen_wave3_2026-09-23/` (composites, sheet.html,
decisions.json, serve.log, build_composites.py).

Left `doing` — wave 3 of many, not a close.
