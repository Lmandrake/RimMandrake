# TIBANNA_SOURCE_CUT_1 — cut the non-beldon tibanna sources

**Source of intent:** `design/Jawa/tibanna_embargo_plot_spec.md`, CARD T1 —
RULED 2026-09-12: (a), cut the violators. Enforces `the_forge.md` §6 hard
ban 5 (line 127, verbatim): *"No tibanna source but the beldons — no
mineral or synthetic route, ever. The herds are the monopoly's whole
basis."* The live mod stack was found violating this in two independent
ways (`MECHANICS_CARDS_SITTING_1.md`'s T1 note); this item cuts both.

## What was cut

**1. The three OuterRim extractor/siphon buildings** (all
`neronix17.outerrim.core`, defined in
`1.6/Defs/ThingDefs_Buildings/_Tibanna/`) — Cherry Picker cut, added to
`infrastructure/state/cherrypicker/CherryPicker.SHIP.xml`:

| defName | file | what it is |
|---|---|---|
| `OuterRim_TibannaSiphon` | `_PipeSystem_Tibanna.xml` | the pipe-network harvesting node |
| `OuterRim_TibannaExtractorLight` | `Building_TibannaInstallationLight.xml` | light extractor building |
| `OuterRim_TibannaExtractorHeavy` | `Building_TibannaInstallationHeavy.xml` | heavy extractor building |

Used `cut(deftype, name)` shape (`ThingDef/<defName>` entries in the `<keys>`
list), never `cut_name`, per this repo's Cherry Picker doctrine
(`rimworld-content-moderation` skill) — `cut_name` matches any defType named
X, which risks cutting an unrelated def sharing the string.

**2. The LK mineable-route mod extension on the item itself.** Reading
`leutiankane.mines2patchouterrim`'s own
`Common/Patches/Patch_Mines2.0OuterRim.xml` directly (not guessed) showed a
`PatchOperationAddModExtension` attaching
`MinesAutomatedExtension.MineableSettings` (researchPrerequisites
`OuterRim_HypertechFabrication`, workOffset 200, mineableYield 10) onto
`Defs/ThingDef[defName="OuterRim_Tibanna"]` — the raw gas item itself,
making it directly minable via the "Mines and Automated Mining" framework.
This is **not a standalone def** — it is one `<li>` appended to an
ALREADY-EXISTING `<modExtensions>` list on `OuterRim_Tibanna`'s own base def
(which also carries an unrelated `VEF.Things.ThingDefExtension` for
`deepColor`) — so Cherry Picker's whole-def cut cannot reach it without also
removing the item the ruling says must stay.

Removed instead with a new scoped patch,
`src/RimUtinni/UtinniPatches/Patches/TibannaEmbargo_CutMineableRoute.xml`
(`mandrake.rut.patches`): `PatchOperationConditional` (outer `MayRequire`
gates on both `neronix17.outerrim.core` and `leutiankane.mines2patchouterrim`
being active; inner conditional confirms the specific `<li>` is present)
wrapping a `PatchOperationRemove` targeting
`ThingDef[defName="OuterRim_Tibanna"]/modExtensions/li[@Class="MinesAutomatedExtension.MineableSettings"]`.
Load order confirmed against the live `ModsConfig.xml`: `mandrake.rut.patches`
sits well after the OuterRim/LK block in the full 592-mod list, so LK's
`AddModExtension` has already run by the time this patch's `Remove` executes.

**Not touched, per the ruling**: `OuterRim_Tibanna` (the item) itself stays;
the beldons-only hard ban (the herds remain the sole in-fiction source) is
unaffected — no beldon-related def exists yet (roster pass owed elsewhere per
`the_forge.md` §Owed).

## Offline validation

`validate_patch.py --live --defs` (592-mod set): 0 errors. The inner
Conditional's target (`modExtensions/li[Class=...]`) correctly reads as "0
matches" against the RAW on-disk XML — expected, since that node does not
exist until LK's own patch creates it at actual load; this is exactly why
the ruling itself warns LK's patches can no-op silently, and exactly why this
item's real verification is live, not static.

## Live verification (2026-09-12, FOUNDRY)

**One real bug found and fixed before this could verify at all.** The first
edit to `CherryPicker.SHIP.xml` put the explanatory comment INSIDE the
`<keys>` list, interleaved between `<li>` entries — no other entry in this
2000+-line file has an inline comment. On the full 592-mod cold load this
threw `System.NullReferenceException` inside
`Verse.ScribeExtractor.ValueFromNode` →
`Verse.Scribe_Collections.Look` → `CherryPicker.ModSettings_CherryPicker.ExposeData()`
(`SaveableFromNode exception` in `Player.log`) while deserializing the WHOLE
2286-entry cut `HashSet<string>` — a comment node apparently is not the
plain-text `<li>` `ValueFromNode` expects. Confirmed live: with the comment
still present, `OuterRim_TibannaSiphon`/`ExtractorLight`/`Heavy` all remained
spawnable and Cherry Picker's own "defs removed" log line never printed them.
Fixed by deleting the inline comment (plain `<li>` entries only, matching
every other line in the file) — also discovered `cherrypicker_swap.py --ship
--apply` compares by parsed KEY SET, not raw bytes, so it reported "already
this profile, nothing written" and silently left the broken live file in
place; had to `cp` the fixed repo file directly over the live config to
actually push the fix. Both of these (the interleaved-comment crash and the
key-set-only diff in the swap tool) are new findings worth carrying into the
`rimworld-content-moderation` / `rimbridge` skills.

**With the fixed config, a clean reload confirmed both cuts:**

1. **Cherry Picker cut** — `Player.log` line 2447: *"[Cherry Picker] The
   database was processed in 00.64011 seconds and the following defs were
   removed:"* followed by exactly `ThingDef/OuterRim_TibannaSiphon`,
   `ThingDef/OuterRim_TibannaExtractorLight`, `ThingDef/OuterRim_TibannaExtractorHeavy`
   — the authoritative channel per this repo's own doctrine
   (`rimworld-content-moderation` skill: "the def dump is captured BEFORE
   Cherry Picker removes anything... the instrument that CAN answer 'did this
   cut take effect' is Player.log"). **New finding, doctrine-worthy**: the
   LIVE bridge's `rimworld/spawn_thing` and `jawa/get_defs` are ALSO blind to
   Cherry Picker's removal, not just the offline def dump — a differential
   control test spawned `GoldenCube` (a long-established, first-line CP cut)
   on this exact load and it spawned cleanly with a real label, proving the
   blindness is a pre-existing property of these tools' def-lookup path, not
   a defect in this cut. `spawn_thing` on the three Tibanna defNames also
   "succeeded" for the same reason — this is NOT evidence the cut failed.
2. **LK mineable-route removal** — `jawa/get_defs` on
   `ThingDef/OuterRim_Tibanna` (field `modExtensions`, unaffected by the
   Cherry Picker blind spot above since this is an ordinary PatchOperation,
   not a Cherry Picker removal — confirmed working correctly on this same
   session for `WRECKAGE_VERMIN_SPAWN_1`'s `tickerType` fix) now reads
   `["ThingDefExtension"]` only — `MinesAutomatedExtension.MineableSettings`
   is gone. Zero `Could not resolve cross-reference` errors mentioning
   Tibanna anywhere in `Player.log`.

Both mechanisms of the violation are closed; `OuterRim_Tibanna` (the item)
itself still resolves and is fully intact per the ruling.

## Closed

Verify met on both fronts (Cherry Picker's own removal log; a clean
patch-resolved `modExtensions` read with no cross-reference damage). Beldons
remain the sole in-fiction source. Mod list left on the campaign's
`FULL.LATEST` (592 active) after this session's testing.
