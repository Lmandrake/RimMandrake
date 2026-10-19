# BIOME_ARRIVAL_LETTERS_ALL_1 — arrival letters for every biome that has had its sitting

Source: `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` rows X-6 and FV-5 (owner card 2026-10-08:
queue all batches). Machinery: `RM_BiomeArrivalLetterExtension` (EnvironmentalHazards, BIOME_ARRIVAL_NARRATION_1),
fired once per save on the first gravship landing; setting `biomeArrivalLettersEnabled`.

## what
Built at `4b1b7c63c`, text only. One extension on each of 10 BiomeDefs, Fever Wood first: RM_FeverWood,
RM_RustCathedral, RM_Webwork, RM_TheForge, RM_FloodedCanyon (the Cracked Lands), RM_LongShade, RM_WeepingStones,
RM_Pyrelands, RM_Stillsand, RM_Greentide. Each gives the biome's survival reads, then a heat line that follows its
declared heat kind as built at `4b1b7c63c`. ⚠️ Those heat lines are now false: the owner ruled 2026-10-19 there
are no heat kinds and the shade gear is parasols and roofs (*"Keep only Parasols and Tents"*). Their rewrite (the
tile's sun, roof/parasol, long shadows at low sun; air heat for the Forge, Scald, Fever Wood, Greentide) is
spec 9 of `DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES`.

Selection: a declared heat kind (`RM_SunHeatExtension`) AND a bedazzle review on file. **The Scald is left out**:
only a floor sitting agenda exists. The Sump already had its letter.

Guard: `MayRequire="mandrake.rm.biomes"` on each `<li>` (EnvironmentalHazards now ships inside that mod; a
MayRequire naming the folded `mandrake.rm.environmentalhazards` would silently drop the letter).

**Every text is a PLACEHOLDER** drafted by an agent from the biome's own description, its definition sheet's
"always true" list and shipped mechanics. Review copy with per-letter sources:
`Transient/arrival_letters_draft_20261008.md` (~14-day shelf life; the shipped copy is each BiomeDef's
`<letterText>`). The owner's edits replace them; the Utinni voice layer may later replace any of them.

## criteria
- O1 L0: every touched BiomeDef parses; each carries one RM_BiomeArrivalLetterExtension with label and text
- A1 L1: the ten BiomeDefs load with the extension on the live list (no config errors)
- A2 L2: a gravship landing on a Fever Wood map raises the letter once; a second landing does not
- H1 L4: the owner reviews and edits the ten placeholder texts

## verify

Run each criterion at its stated level and record it with `rimflow verify BIOME_ARRIVAL_LETTERS_ALL_1 --criterion <ID> --result pass|fail|partial --config <list> --evidence <path>`:
- L0: offline build, selftest/fuzz/lint (already run at implementation).
- L1: one minimal-list load, read Player.log for config/cross-reference errors and the specific line, or one spawn-and-read bridge probe.
- L2: one quicktest map via the bridge or modcheck: set up the scenario in the criterion, step ticks, read the state named.
- L4: owner judgement in a sitting; not a FOUNDRY acceptance task.
Evidence is the Player.log line or bridge read the criterion names; a screenshot is not evidence of state.
