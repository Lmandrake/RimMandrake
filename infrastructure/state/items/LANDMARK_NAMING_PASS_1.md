
## Source
Review B2 (`design/Jawa/worldbuilding/review/WORLDMAP_FINAL_REVIEW_2026-09-08.md`
line ~154): 32 landmark names appear on 2+ landmarks (74 dupe rows total); "Dead
Sarlacc" x7 worst. Corrective: hand-name the ~15 that matter, let a namer-variety
pass cover the rest. Cost estimate: "an hour of naming, the fun kind."

## Rename tool — EXISTS, source-committed, NOT YET DEPLOYED
`jawa/world_landmark_rename` was built this session:
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchLandmarkNameTool.cs`
(commit d502e2e3, confirmed an ancestor of current HEAD). `Landmark.name` is a
plain public scribed string (`Source/RimWorld/Landmark.cs:9`) — the write is
durable in the save, no world_commit needed (labels redraw per frame).
Deploy status: the currently-deployed companion DLL was built from commit
5ed3e2a1 (2026-09-09 07:13), which PREDATES d502e2e3 (23:49) — so the live
game does not yet expose this tool. This rides the same already-planned
game-down deploy as `BRIDGETOOLS_DLL_GM_DRIFT_1` (rebuild with `--gm --apply`
picks up both). Not a separate deploy problem — just not yet actionable
because the game is up.

## The ~15/16/18 that matter — NAMED, not yet applied
`infrastructure/state/items/LANDMARK_NAMING_PASS_1.names.md` (commit 0fdb4990,
fork product) hand-names 18 landmarks (6 Dead Sarlacc dupes across 3 regional
voices + Sunmouth + Bad Investment + Old Drywell, plus cavern/karst/scar/ruins/
vent pairs) in faction/region voice, one holder of each duplicated name kept as
the "senior/central" instance. Tile reserved for The Gaping Doom
(`GAPING_DOOM_SITE_1`) is explicitly excluded here. Owed: owner skim of the
name list, then apply via the rename tool once deployed + world_commit + save
(batch this with GAPING_DOOM_SITE_1's placement and OASIS_LANDMARK_PLACEMENT_1
— all three are bridge-write items queued for the same session per
GAPING_DOOM_SITE_1's note).

## Namer variety for the remaining ~14 — NO MECHANISM EXISTS, checked
Investigated whether the repo (or vanilla/DLC) has a namer convention that
could auto-vary the rest without hand-authoring. Found vanilla Odyssey DOES
have a per-instance procedural namer for its own landmark types
(`RulePacks_Namers_Landmarks.xml` — `NamerLandmark_Oasis`, `_Lake`, `_Pond`,
etc., resolved via GrammarResolver at generation time). But the actual
offender, `sw_DeadSarlacc` (workshop mod 3497316713,
`Defs/ThingDefs_Buildings/SW_Buildings_Natural.xml:319`), carries a bare
static `<label>dead Sarlacc</label>` with no namer RulePack reference at all —
every instance is the literal ThingDef label, not a generated name. Same
appears true of the other reused defs in the review (Cavern, VEE_Cenotes,
TerraformingScar, Ruins, AncientHeatVent — all fixed-label modded LandmarkDefs).
**There is no automated "namer variety" route** — grepped the repo for any
namer/RulePack tooling under our own tools (`src/RimMandrake/Utils/`,
`bridgetools/`) and found none for landmarks specifically (settlement namers
exist, e.g. `DV_NamerSettlementOutlanderBuzzer`, but nothing wired to
landmarks). Giving the remaining ~14 duplicate groups variety means hand
names via the same rename tool — i.e. the "fun/cheap" half of B2 is not
actually cheaper than the "matters" half; it's the same mechanism, lower
stakes per name. Left undone this pass per the owner's standing rule against
inventing lore names ungrounded in an existing doc — this batch doesn't have
one. Next agent: either get the owner to skim/approve names for these too, or
treat "namer variety" as "good enough with the tool once it's live and nobody
minds duplicates outside the ~18 that got individual treatment."

## Owed
1. Deploy the companion DLL (rides `BRIDGETOOLS_DLL_GM_DRIFT_1`'s already-owed
   game-down window: `taskkill` → `build.py --gm --apply` → restart).
2. Owner skim of `LANDMARK_NAMING_PASS_1.names.md`'s 18 names.
3. Apply the 18 renames live via `jawa/world_landmark_rename`, batched with
   `GAPING_DOOM_SITE_1` (tile 2403 placement + name) and
   `OASIS_LANDMARK_PLACEMENT_1` in one bridge session.
4. Decide (owner) whether the remaining ~14 duplicate groups get hand names
   too, or stay as-is — no procedural fallback exists to fall back on.
