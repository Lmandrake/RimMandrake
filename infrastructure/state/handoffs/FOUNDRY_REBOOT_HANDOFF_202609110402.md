# FOUNDRY_REBOOT_HANDOFF_202609110402 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609110245`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

A wildAnimals dictionary VALUE naming a Cherry-Picker-cut creature is a
confirmed, previously-hit crash class (`BIOME_CAST_REFS_BREAK_MAPGEN_1`) —
not theoretical. Retiring `WYYYSCHOKK_FERALISK_MERGE_1`'s `-lisk` clade
required a follow-up sweep that found and fixed **10 live dangling
references** across `RUT_TheForge.xml`, `RUT_ExtremeDesert.xml` and
`BiomeCast_Ashkarr.xml` that the ruling itself never mentioned — a Cherry
Picker cut of any animal is not complete until that sweep runs. The
distinguishing regex: a bare `<CreatureName>value</CreatureName>` element
(dangerous, needs cross-ref resolution) vs. an xpath STRING naming the same
defName inside a `[defName="..."]` predicate for a `race/wildBiomes`
eviction (harmless — a PatchOperationRemove on a now-missing ThingDef just
matches nothing).

## What the owner should see

- **`CHERRYPICKER_SHIP_BASELINE_STALE_1` still needs him**, unchanged from
  when he last saw it: the live Cherry Picker config's 141→10 backstory
  un-cut could be deliberate or a review-window leftover, and only he (or
  whoever touched the in-game Cherry Picker UI tonight) can say which.
  Confirmed still correctly blocked, not stale — `rimflow why` shows "mode
  is afk."
- **The Pyrelands burrower slot was left open on purpose**, not forced: the
  obvious homeless candidate (FrogDog) turned out not to carry the burrow
  special its own eviction note claimed (that note was wrong and has been
  corrected). If he wants a dedicated grazer-burrower distinct from Orray,
  it's a third commission — not started.
- **`RUT_FurnaceBeast`/`RUT_FireHawk` art and defs are real and committed
  but their sheet-named mechanics (twig-carrying fire spread, heat aura,
  bed-down ignition) are NOT implemented** — `PYRELANDS_MECHANICS_1` is
  still unfiled. Both creatures currently behave as ordinary wild animals.
- **Twinkle flora spike has no live tick-cost number** — the game was up
  the whole session (can't deploy a DLL to a live Mods copy while it runs),
  so the report gives a measurement protocol for the next game-down/up
  window instead of a fabricated benchmark. Code compiles clean and is
  committed, unwired from anything live.

## What is half-done, and where it stops

Nothing of mine left `doing`. All four items this window (`MIASMA_NURSERY_KINDS_1`,
`ART_BACKGROUND_TEMPLATE_1`, `WYYYSCHOKK_FERALISK_MERGE_1`,
`PYRELANDS_FIRE_WEB_COMMISSION_1`) plus `TWINKLE_FLORA_SPIKE_1` closed clean,
each validated against the live 575-mod set before closing. The 67 other
`doing` items in the ledger belong to other seats/windows from before this
session — not touched, not audited.

## Traps learned

- **The illegal-XML-comment-dash mistake ("--" inside `<!-- -->`) happened
  FOUR separate times this session** across four different files, always in
  my own newly-added header prose (never in pre-existing content). Every
  one only surfaced via `validate_patch.py`'s parse check, never by eye. If
  a def/patch file I just wrote fails to parse right after I touch its
  header comment, check for "--" before anything else.
- `validate_patch.py --defs` needs the **Mods** folder passed alongside
  Data and Workshop — custom/first-party mods (`mandrake.*`) live there, not
  in the Workshop content tree, so omitting it makes every `ParentName`
  cross-mod inheritance check to a first-party def report a false failure.
- A concrete, useful RimWorld mechanism fact worth keeping: `ParentName`
  inheritance requires the PARENT to carry a `Name="..."` XML attribute —
  `<defName>` alone does not make a def inheritable. `SeaBeasts_*.xml`'s
  7 base creatures never had one; added `Name=` to all 7 (ThingDef +
  PawnKindDef) to let `MIASMA_NURSERY_KINDS_1`'s juvenile variants inherit
  from them. Vanilla does this too (`Races_Animal_CowGroup.xml`'s
  `Name="BoomalopeThingBase"` on a live, concrete def) — not an invented
  pattern.
- `PawnKindDef.maxGenerationAge`/`minGenerationAge` are `int` (years) —
  cannot express a sub-1-year AnimalAdult threshold, and forcing one
  (`maxGenerationAge=0`) makes `PawnGenerator`'s age-roll loop fail its
  300 tries and spam `Log.Error` on every spawn. The actual working
  mechanism for a permanently-juvenile creature: drop the `AnimalAdult`
  entry from `race.lifeStageAges` entirely — `LifeStageUtility.GetLifeStageAgeForYears`
  then caps at the last remaining entry forever, no matter the rolled age.
- Rimflow ledger writes (`claim`/`start`/`close`) are LOCAL only — none of
  my four per-item commits included the ledger delta; caught and synced in
  one batch (`5a3c7451`) at wrap rather than each time. Next FOUNDRY window:
  either commit the ledger delta with each close, or sync it explicitly
  before handoff — don't let five windows of it pile up uncommitted.

## Closed since the last handoff (5)

- `MIASMA_NURSERY_KINDS_1` — 4b1f5b713709d592f7ab9bbe0f0a9373ccab2340
- `ART_BACKGROUND_TEMPLATE_1` — 62ea4f3c7093005e4fe41ab62fbe0708686f0158
- `WYYYSCHOKK_FERALISK_MERGE_1` — 7bad94185e11a3b3025d07ed837da50186789357
- `PYRELANDS_FIRE_WEB_COMMISSION_1` — 9406d5e0838bfcf04e076b6dbaf22ce21ee699c2
- `TWINKLE_FLORA_SPIKE_1` — cc967cd5f59678905fef8ea5d1c56feea96c8f23

## Filed and still open (0) — the next seat's queue

Nothing filed in this window.

## Commits

```
cc967cd5 Twinkle flora spike: glow-pulse feasible if quantized + rare-tick
beaf2687 SLIME_TRANSFORMATION_SYSTEM_1: design brief for the slimification ladder
8e03cbce Wave-2 ruled commissions: seven creature briefs (nightside trio, Cathedral pair, Pyrelands igniters) + two recasts
9406d5e0 Commission fire-hawk + furnace-beast, recast Razorjack/Barbslinger
3d95bbda Hssiss ruling note on its move row
f28f12b4 Card rulings: Hssiss stays Sump, wreck-fields is a region not a biome, slime transformation ruled, FrostboundBehemoth cut
55bb5d61 Findings: forge header reflects Cinderlisk/Maguana cuts (9->7)
06320d41 HYDROCARBON_ECOLOGY_COMMISSION_1 §14: harvest-item economy (owner's items-now ruling, §13.4)
c802cacf Fungal husk size ruled: 2 cells (medium)
25ffee09 Hydrocarbon ecology: four owner card rulings recorded (crystal lineage yes, hearthwheel+teal rim, rimshell, ITEMS COMMISSIONED)
7bad9418 Retire Alpha Animals' -lisk clade: Wyyyschokk stays the canon Feralisk
8f491fc3 HYDROCARBON_ECOLOGY_COMMISSION_1: hydrocarbon ecology brief — 9 owner seeds + waxblood through-line, 10 refs
88876d20 Lesson: parallel subagents must commit with explicit pathspecs on the shared index
c3d0dcc8 PALETTE_ANCHOR_DRAFT_1: poison_forest recalibrated to owner's rainbow-springs reference
2adf46d0 CHERRYPICKER_SHIP_BASELINE_STALE_1 ruled: restore all 139 genuine reversals at next game-down, then re-baseline SHIP
e1b1d9ba CHERRYPICKER_SHIP_BASELINE_STALE_1: investigate the 178-key SHIP reversal
62ea4f3c Art pipeline: proven black-background template for new-creature jobs
0bc14cd0 Klorslug ruled horror-injectable (nightside injection pool); sitting notes for bat cull + size calibration
8e49f8d5 Bat cull: BMT_GlowBat (the 'violescent bat') + BMT_BrownBat cut; Batbird/Megabat/Woollybat already out
4b1f5b71 Miasma nursery: juvenile-locked sea beasts, wildAnimals patch
7c8ad16d Deck: MERGE-RESERVED tag keeps AA_Feralisk off the webwork slide (caught by independent probe after 21/22 suite)
20ffc804 Round2 deck: drawSize instrument fix, visitor/fishing-result markers
6506e61d GOO_BOOM_COMMISSION_1: all 9 open calls ruled by owner cards - v1 vanilla worker, stats ratified, Boomalope body, painted glow; UNBLOCKED for FOUNDRY
19c56fe6 PALETTE_ANCHOR_DRAFT_1: draft biome palette anchors + owner color board
e3b6e2d2 Lesson: verify decision-row keys before batch edits
6e4497c7 Apply the card rulings to the real rows (Blarth homeless key; prior commit carried only the item file)
5e00b4a1 Card rulings: Blarth dual-listed, Megascarab faction-reserved (cut reversed), Beelzebufo rename+redefine, nine-species nursery roster
d8f9e276 Flora template §8 fully ruled: palette color-board, twinkle spike, contrast law ratified, set default 3
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-11T02:31:45Z

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M infrastructure/artpipe/throughput.jsonl
 M infrastructure/state/codebase_health_last.json
 M infrastructure/state/ledger/events.jsonl
 M infrastructure/state/queue/BENCH.md
 M infrastructure/state/queue/FOUNDRY.md
?? defs.sqlite
?? design/Jawa/worldbuilding/review/serve_fauna.log
?? design/Jawa/worldbuilding/review/serve_flora.log
?? infrastructure/artpipe/done/pyrelands_firehawk_v1.json
?? infrastructure/artpipe/done/pyrelands_firehawk_v1.manifest.json
?? infrastructure/artpipe/done/pyrelands_furnacebeast_v1.json
?? infrastructure/artpipe/done/pyrelands_furnacebeast_v1.manifest.json
?? src/RimStarWars/Armoury/Textures/Things/Item/Resource/Crystal/
```

