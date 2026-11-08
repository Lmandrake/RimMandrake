# Trial 1: test the callers, not the kernels

*2026-11-07, detached helper on `RIMMASTER_WEIGH_POCOCK_SKILLS_TRIAL_BEFORE_INSTALL`. Trial rank 1 of `03-merged.md`, run
because the owner answered Card 1 *"Not yet: trial first"*. Agents only, offline: no game, no deploy, no loop branch.*

## Verdict

**The thesis holds here, in all three mods.** By the brief's thresholds (callers escape at half or more, and kernels are
caught), measured on frozen plants:

| mod | caller mutants caught | kernel mutants caught | threshold |
|---|---|---|---|
| Graffiti (viewer thought path) | **0 of 11** (12 escaped with one added after the count) | 7 of 7 | holds |
| KeelHoist (rider, tether, cradle, holder, pit, dialog) | **0 of 10** | 7 of 7 | holds |
| HugeThings (settings gate tree, wake crush, sea test) | **0 of 10** | 7 of 7 | holds |

The escape is **structural, not sampled.** In all three mods the C# fuzz project compiles only kernel files (Graffiti adds two
plain enum files, HugeThings the shared `DrawnExtentKernel.cs`), so it cannot execute a caller, and no other offline
test compiles or runs C# at all (checked: the Python selftests read source and defs as text, or check the DLL stamp). The one offline check that reads a caller, KeelHoist's
"every gate reads its toggle", checks that a setting's *name* appears in a method body: it caught the one mutant of that
family (a setting replaced by a literal) and nothing that keeps the names. So any caller fault that compiles and keeps
its names gets past the offline suite. Which plants I chose barely matters.

**The replacement works and is cheap here:** literal scenarios at Graffiti's ThoughtWorker (the real file on a fake
`Verse`) caught **16 of 20** mutants from a batch made by a rule frozen before the test was written, where the old tests
caught **0 of 20**. The four it missed are arguments no scenario exercises yet.

## Method

**Hypothesis (Pocock):** logic extracted into pure one-line "kernel" gates gets truth-table tests, and the bugs hide in
the code that calls those gates. **Sides:** a *caller* mutant edits the game-facing file that calls a kernel gate (a wrong
literal, a swapped non-symmetric argument, a missing call, an inverted use of the result, a wrong argument); a *kernel*
mutant edits the gate itself (a dropped conjunct or negation, AND for OR, a priority swap).

**Where:** a scratch branch (`scratch/pocock-trial1-mutants`) in this item's own clone
(`/home/mandrake/rm/relentless/clones/RIMMASTER_WEIGH_POCOCK_SKILLS_TRIAL_BEFORE_INSTALL.det`). No mutant was committed.

**Per mutant**, by `D:\Luke\dev\RimMandrake\design\RimMandrake\2026-11-07-pocock-design\trial1_mutants.py`, serially within
a mod:

1. Write the mutant into the source file. The anchor text must occur exactly once, and the result must differ from the
   original; otherwise the mutant is reported `NOT_APPLIED` by name and not scored. None was.
2. Rebuild the mod with `winbuild.py <Mod>`, as a builder would before committing. A mutant that does not compile is
   `INVALID`, not "caught". None was. The rebuild also re-stamps the DLL's `.srchash`, so the committed-DLL stamp check
   (`selftest_graffiti_v1_live.py`) reads the mutant's own stamp. Without the rebuild that check goes red on any edit,
   harmless ones too, and would credit itself with every plant.
3. Run every offline selftest of the mod (lists below), each keyed on its own exit code. The log of every run is kept.
4. Restore the source and `Assemblies/` (`git checkout`), and check the restore by hash.

**Harness checks, before any mutant counted:** the unmutated control is green on every instrument; two harmless edits
per mod (the gate inlined at its caller, and the gate rewritten with the same truth table) stay green, so no instrument
reads "changed" as "broken"; every kernel mutant goes red, so the harness can see. Logs:
`D:\ClaudeWork\rimmandrake\pocock_trial1\<Mod>\`.

**Predictions, frozen before the control ran:** `D:\ClaudeWork\rimmandrake\pocock_trial1\PREDICTIONS.md`. Read before
predicting: Graffiti's fuzz project (`Source\SelfTest\RimMandrakeGraffiti.SelfTest.csproj`) compiles only the kernel
and two enum files, and no offline Python test reads ThoughtWorker logic. The prediction was that every caller mutant
would escape every behaviour check. One prediction was overtaken by the method: I predicted the committed-DLL stamp check
would go red on every edit, then added the rebuild step (step 2), which re-stamps the DLL, so that check stayed green
throughout.

**Equivalent mutants excluded** (no behaviour changes, so no test could catch them):

| candidate | why it is no mutant |
|---|---|
| swap any two arguments of `ThoughtActive` | a symmetric four-way AND |
| swap `SameRoomOrUnknown`'s first two arguments | symmetric in them |
| drop `p.Spawned` (or `p.Map != null`) from `ThoughtActive` | vanilla `Verse/Thing.cs` (RimSage): `Map` is non-null exactly when `mapIndexOrState >= 0`, which is `Spawned` (outside an invalid-map-index error state). One of the two arguments is redundant at the gate's only call |
| swap the two halves of any `ReactionSlot` pair (`hasX`, `conditionX`) | each pair is a symmetric AND |
| swap `HugeGates.Smash`'s arguments | a symmetric four-way AND |

One exclusion made while planning was **wrong** and is withdrawn: swapping `SameRoomOrUnknown`'s first and third
arguments (`room != null` with `room == cellRoom`) is a real mutant (two known rooms that differ: the original blocks the
mark, the mutant lets it through). It was run afterwards as `X_ROOM_ARGS_SWAP` and is reported apart from the frozen count.

**Instruments per mod** (every offline selftest that reads the mod's source or defs):

- **Graffiti:** `selftest_graffiti_fuzz.py` (C# kernel fuzz, 17,099 cases), `selftest_graffiti_lint.py`, and the five
  `Graffiti\selftest_*.py` (`v1_live`, `full_list_mode`, `fresh_quicktest`, `play_zoom`, `spree_surprise`).
  `selftest_settings_screens.py` reads only `RM_GraffitiMod.cs` and the csproj, which no mutant touches. `ship_check.py`
  is **red on clean main** (three of five clauses: `settings` "viewerReaction labelled=False", `review` "not CLEAN:
  validation.py", `deploy` drift on one texture), so it cannot score anything; its two green clauses are texture paths
  and the DLL stamp, which the rebuild re-stamps.
- **KeelHoist:** `selftest_keelhoist_fuzz.py`, `KeelHoist\selftest_keelhoist.py` (the source-text "every gate reads its
  toggle" bars of `validation.py`, run on the real tree), `selftest_peaceful_landing.py`. `selftest_settings_screens.py`
  reads only `KeelHoistMod.cs` and the csproj, which no mutant touches; it was left out so KeelHoist could run beside
  HugeThings.
- **HugeThings:** `selftest_hugethings_fuzz.py`, `_lint`, `_titanic_lint`, `_test_races`, `_trunk_probe`,
  `HugeThings\selftest_hugethings_footprint.py`, `selftest_titan_passage_dark_side.py`, `selftest_settings_screens.py`.
- **Live proofs are out of scope** (no game). Graffiti's `graffiti_v1_live_proof.py A5` is the only behavioural proof of the
  thought path ("an enemy's tag 3 cells from a colonist: mood True"). Read, not run, so its catch is UNMEASURED: it stages one
  case, so it can catch only a mutant that silences that case, and never a lost room or clan-only check, the setting
  swap or a crossed ideo slot. `validation.py` proves the `viewerReactionEnabled` setting by write and read-back only.

## Results

### Graffiti: the viewer thought path (`ThoughtWorker_ViewedGraffitiMark.cs` and `RM_GraffitiKernel.cs`)

| mutant | side | what it breaks | fuzz | lint | v1_live | full_list | fresh_qt | play_zoom | spree | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| `GREEN_CLEAN` | green | unmutated control | green | green | green | green | green | green | green | stays green |
| `GREEN_CALLER_INLINED` | green | harmless: the one-line gate inlined (the deletion-test repair itself) | green | green | green | green | green | green | green | stays green |
| `GREEN_KERNEL_EARLY_RETURN` | green | harmless: the kernel gate rewritten with an early return | green | green | green | green | green | green | green | stays green |
| `C_LITERAL_FALSE` | caller | wrong literal: the viewer thought never fires | green | green | green | green | green | green | green | **escaped** |
| `C_SETTING_WRONG` | caller | wrong argument: the 'viewer reaction' toggle no longer turns the thought off (painting's does) | green | green | green | green | green | green | green | **escaped** |
| `C_INVERT_ACTIVE` | caller | inverted result: thought fires only with the setting OFF | green | green | green | green | green | green | green | **escaped** |
| `C_SWAP_CLAN_ARGS` | caller | swapped non-symmetric args: colonists lose public-mark reactions, outsiders read clan-only marks | green | green | green | green | green | green | green | **escaped** |
| `C_INVERT_CLAN` | caller | inverted result: only clan-only marks seen by outsiders react | green | green | green | green | green | green | green | **escaped** |
| `C_MISSING_CLAN` | caller | missing call: outsiders get the reaction from clan-only (Cant) marks, owner ruling #4 broken | green | green | green | green | green | green | green | **escaped** |
| `C_ROOM_ARG_INVERT` | caller | wrong argument: marks in the viewer's own room are ignored, marks in other rooms count | green | green | green | green | green | green | green | **escaped** |
| `C_INVERT_ROOM` | caller | inverted result: only marks in other rooms count | green | green | green | green | green | green | green | **escaped** |
| `C_MISSING_ROOM` | caller | missing call: a mark through a wall (another room, within 8 cells) gives the thought | green | green | green | green | green | green | green | **escaped** |
| `C_IDEO_ARG_NEGATED` | caller | wrong argument: the same-ideo reaction goes to viewers of a DIFFERENT ideo | green | green | green | green | green | green | green | **escaped** |
| `C_SWITCH_CROSSED` | caller | wrong use of result: a same-ideo viewer gets the other-ideo thought | green | green | green | green | green | green | green | **escaped** |
| `K_THOUGHT_DROP_SPAWNED` | kernel | dropped conjunct | **RED** | green | green | green | green | green | green | caught |
| `K_THOUGHT_PRECEDENCE` | kernel | precedence slip: setting on alone activates | **RED** | green | green | green | green | green | green | caught |
| `K_ROOM_DROP_NOT` | kernel | dropped negation | **RED** | green | green | green | green | green | green | caught |
| `K_CLAN_DROP_NOT` | kernel | dropped negation | **RED** | green | green | green | green | green | green | caught |
| `K_SLOT_PRIORITY_SWAP` | kernel | priority order swapped | **RED** | green | green | green | green | green | green | caught |
| `K_SLOT_HOSTILE_OR` | kernel | AND became OR | **RED** | green | green | green | green | green | green | caught |
| `K_SLOT_PROVENANCE_INVERT` | kernel | inverted guard | **RED** | green | green | green | green | green | green | caught |

Added after the frozen count (the exclusion withdrawn above), reported apart:

| mutant | side | what it breaks | fuzz | lint | v1_live | full_list | fresh_qt | play_zoom | spree | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| `X_ROOM_ARGS_SWAP` | caller | swapped non-symmetric args: a mark in the next room counts when both rooms are known | green | green | green | green | green | green | green | **escaped** |

**Graffiti: callers 0 of 11 caught (12 of 12 escaped with the added one); kernels 7 of 7 caught**, every one by the fuzz
alone. No other instrument went red on any mutant: the lint and the five Python selftests check defs and their wiring
(the thought's `workerClass`), harness shapes and the DLL stamp, never the thought's behaviour. The fuzz cannot see a caller at all: its project does not compile the
ThoughtWorker.

### KeelHoist: rider, tether, cradle, holder, pit and dialog gates (`RM_KeelHoist.cs`, `KeelHoistPatches.cs`, `RM_HoistFrame.cs`, `RM_HoistKernel.cs`)

| mutant | side | what it breaks | fuzz | keelhoist | peaceful | verdict |
|---|---|---|---|---|---|---|
| `GREEN_CLEAN` | green | unmutated control | green | green | green | stays green |
| `GREEN_CALLER_INLINED` | green | harmless: the rider gate inlined | green | green | green | stays green |
| `GREEN_KERNEL_REWRITE` | green | harmless: GateOpen folded into one test | green | green | green | stays green |
| `C_TETHER_LITERAL_FALSE` | caller | wrong literal: the tether lock never refuses a launch | green | green | green | **escaped** |
| `C_TETHER_INVERT` | caller | inverted result: the tether lock is checked only when it should not be | green | green | green | **escaped** |
| `C_RIDER_INVERT` | caller | inverted result: riders who should ride are dropped, awake colonists with riding off are carried | green | green | green | **escaped** |
| `C_RIDER_ARGS_SWAP` | caller | swapped non-symmetric args: with riding off, a downed stranger is dropped and an awake colonist carried | green | green | green | **escaped** |
| `C_CRADLE_SETTINGS_SWAP` | caller | swapped settings: the riding toggle decides captures and the capture toggle decides riding | green | green | green | **escaped** |
| `C_CRADLE_OURS_NARROW` | caller | wrong argument: the colony's own awake prisoners and slaves are left behind | green | green | green | **escaped** |
| `C_HOLDER_ARGS_SWAP` | caller | swapped non-symmetric args: an awake colonist goes into the sealed holder, a downed stranger is dropped | green | green | green | **escaped** |
| `C_KEEPERS_ARGS_SWAP` | caller | swapped non-symmetric args: a friendly pit's keepers never buy (no faction satisfies the swapped test) | green | green | green | **escaped** |
| `C_GATE_MISSING` | caller | missing call: a held pit is never sealed | green | green | green | **escaped** |
| `C_DIALOG_INVERT` | caller | inverted result: the dialog hides every pawn it should show | green | green | green | **escaped** |
| `K_RIDER_DOWNED` | kernel | dropped negation | **RED** | green | green | caught |
| `K_TETHER_DROP_MAP` | kernel | dropped conjunct | **RED** | green | green | caught |
| `K_HOLDER_OR` | kernel | AND became OR | **RED** | green | green | caught |
| `K_CRADLE_CAPTURE_ANY` | kernel | dropped conjunct | **RED** | green | green | caught |
| `K_GATE_INVERT` | kernel | dropped negation | **RED** | green | green | caught |
| `K_KEEPERS_HOSTILE` | kernel | dropped negation | **RED** | green | green | caught |
| `K_DIALOG_SLAVE` | kernel | dropped conjunct | **RED** | green | green | caught |

Added after the frozen count, to show what the source-text gate bars do reach (they are the only offline check here
that reads a caller), reported apart:

| mutant | side | what it breaks | fuzz | keelhoist | peaceful | verdict |
|---|---|---|---|---|---|---|
| `X_RIDER_SETTING_LITERAL` | caller | wrong literal for a setting: the riding toggle does nothing on entry | green | **RED** | green | caught |

**KeelHoist: callers 0 of 10 caught; kernels 7 of 7 caught**, all by the fuzz. `selftest_keelhoist.py` runs
`validation.py`'s static bars on the real tree; they check that each setting's *name* appears in the right method body
(`KeelHoistSettings.colonistsMayRide` inside `OnEntered`, and so on). A setting replaced by a literal is caught; a call
that keeps every name but inverts, swaps or narrows them is not.

### HugeThings: the settings gate tree, the wake's crush gate and the sea test (`RM_HugeThingsSettings.cs`, `TitanicWakeProcessor.cs`, `TitanPassage.cs`, `RM_HugeTitanKernel.cs`, `RM_TitanicKernel.cs`)

| mutant | side | what it breaks | fuzz | lint | titanic_lint | test_races | trunk_probe | footprint | dark_side | settings | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `GREEN_CLEAN` | green | unmutated control | green | green | green | green | green | green | green | green | stays green |
| `GREEN_CALLER_INLINED` | green | harmless: one settings gate inlined | green | green | green | green | green | green | green | green | stays green |
| `GREEN_KERNEL_COMMUTED` | green | harmless: AND operands commuted | green | green | green | green | green | green | green | green | stays green |
| `C_TRUNK_WRONG_FEATURE` | caller | wrong argument (copy-paste): the trunk toggle does nothing, trunks follow the selection toggle | green | green | green | green | green | green | green | green | **escaped** |
| `C_HITBOX_WRONG_MASTER` | caller | wrong argument: Giant animals off leaves the pawn hitbox on (all-off contract broken) | green | green | green | green | green | green | green | green | **escaped** |
| `C_ROOFHOLING_WRONG_GATE` | caller | wrong gate: roof holing runs with the wake off | green | green | green | green | green | green | green | green | **escaped** |
| `C_SMASH_WRONG_GATE` | caller | wrong gate: titans smash giant plants with Giant plants off (the seam ruling) | green | green | green | green | green | green | green | green | **escaped** |
| `C_CLEARING_WRONG_FEATURE` | caller | wrong argument (copy-paste): titan clearing follows the roof-holing toggle | green | green | green | green | green | green | green | green | **escaped** |
| `C_SCAVENGERS_DROPPED` | caller | missing conjunct at the call: the scavengers toggle does nothing | green | green | green | green | green | green | green | green | **escaped** |
| `C_CRUSH_INVERT` | caller | inverted result: the wake crushes giant plants and spares ordinary ones | green | green | green | green | green | green | green | green | **escaped** |
| `C_CRUSH_WRONG_MASTER` | caller | wrong argument: with Giant plants off, a giant is still spared from the crush table | green | green | green | green | green | green | green | green | **escaped** |
| `C_SEA_ARGS_SWAP` | caller | swapped non-symmetric args: land titans pass through sea maps and sea titans through land | green | green | green | green | green | green | green | green | **escaped** |
| `C_EVENTS_WRONG_FEATURE` | caller | wrong argument (copy-paste): the Titan events toggle does nothing | green | green | green | green | green | green | green | green | **escaped** |
| `K_PLANT_OR` | kernel | AND became OR | **RED** | green | green | green | green | green | green | green | caught |
| `K_ANIMAL_NO_MASTER` | kernel | dropped conjunct | **RED** | green | green | green | green | green | green | green | caught |
| `K_WAKE_NO_WAKE` | kernel | dropped conjunct | **RED** | green | green | green | green | green | green | green | caught |
| `K_SMASH_NO_PLANTS` | kernel | dropped conjunct | **RED** | green | green | green | green | green | green | green | caught |
| `K_GIANT_NO_MASTER` | kernel | dropped conjunct | **RED** | green | green | green | green | green | green | green | caught |
| `K_CRUSH_INVERT` | kernel | dropped negation | **RED** | green | green | green | green | green | green | green | caught |
| `K_SEA_NO_LAND` | kernel | dropped conjunct | **RED** | green | green | green | green | green | green | green | caught |

**HugeThings: callers 0 of 10 caught; kernels 7 of 7 caught**, all by the fuzz. The two lints check defs against the C#
(crush rules, tier floors, DefOf names, translation keys) and settings defaults against the XML and their Scribe keys,
per their own plants; none reads which toggle a `*Active` property passes: a copy-paste of the wrong toggle
into a property (`C_TRUNK_WRONG_FEATURE`, `C_CLEARING_WRONG_FEATURE`, `C_EVENTS_WRONG_FEATURE`) and the seam ruling's
gate lost (`C_SMASH_WRONG_GATE`: titans smash giant plants with Giant plants off) all pass.

### The replacement test: literal scenarios at the ThoughtWorker

`D:\Luke\dev\RimMandrake\design\RimMandrake\2026-11-07-pocock-design\trial1_scenario\` compiles the real
`ThoughtWorker_ViewedGraffitiMark.cs` and the real kernel against `Stubs.cs` (a fake `Verse`/`RimWorld`: a 30x30 map of
cells with rooms, fog and thing lists, pawns, factions, ideos) and runs 15 scenarios in play terms. It built on the first
attempt and was green on the clean tree: 15 of 15.

**Fresh batch (the fair score).** Its author knew the hand-planted mutants, so its kills there are fitted. The fresh
batch is a rule frozen before any scenario file existed (`PREDICTIONS.md`, 16:44:47; the first file, the csproj, 16:44:58),
though after the scenarios were planned:
negate each argument of each kernel call on the thought path, one at a time, 20 mutants, every instrument plus the
scenario test.

| mutant | side | what it breaks | fuzz | lint | v1_live | full_list | fresh_qt | play_zoom | spree | scenario | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `GREEN_CLEAN` | green | unmutated control | green | green | green | green | green | green | green | green | stays green |
| `F01_THOUGHTACTIVE_ARG_NEGATED` | caller | rule: ThoughtActive argument `RM_GraffitiSettings.viewerReactionEnabled` negated | green | green | green | green | green | green | green | **RED** | caught |
| `F02_THOUGHTACTIVE_ARG_NEGATED` | caller | rule: ThoughtActive argument `p.Map != null` negated | green | green | green | green | green | green | green | **RED** | caught |
| `F03_THOUGHTACTIVE_ARG_NEGATED` | caller | rule: ThoughtActive argument `p.Spawned` negated | green | green | green | green | green | green | green | **RED** | caught |
| `F04_THOUGHTACTIVE_ARG_NEGATED` | caller | rule: ThoughtActive argument `true` negated | green | green | green | green | green | green | green | **RED** | caught |
| `F05_SAMEROOMORUNKNOWN_ARG_NEGATED` | caller | rule: SameRoomOrUnknown argument `room != null` negated | green | green | green | green | green | green | green | **RED** | caught |
| `F06_SAMEROOMORUNKNOWN_ARG_NEGATED` | caller | rule: SameRoomOrUnknown argument `cellRoom != null` negated | green | green | green | green | green | green | green | **RED** | caught |
| `F07_SAMEROOMORUNKNOWN_ARG_NEGATED` | caller | rule: SameRoomOrUnknown argument `room == cellRoom` negated | green | green | green | green | green | green | green | **RED** | caught |
| `F08_CLANONLYBLOCKS_ARG_NEGATED` | caller | rule: ClanOnlyBlocks argument `ext.visibility == GraffitiVisibility.ClanOnly` negated | green | green | green | green | green | green | green | **RED** | caught |
| `F09_CLANONLYBLOCKS_ARG_NEGATED` | caller | rule: ClanOnlyBlocks argument `p.Faction == Faction.OfPlayer` negated | green | green | green | green | green | green | green | **RED** | caught |
| `F10_REACTIONSLOT_ARG_NEGATED` | caller | rule: ReactionSlot argument `prov` negated | green | green | green | green | green | green | green | **RED** | caught |
| `F11_REACTIONSLOT_ARG_NEGATED` | caller | rule: ReactionSlot argument `ext.onViewSubject != null` negated | green | green | green | green | green | green | green | green | **escaped** |
| `F12_REACTIONSLOT_ARG_NEGATED` | caller | rule: ReactionSlot argument `prov && mark.subject == viewer` negated | green | green | green | green | green | green | green | green | **escaped** |
| `F13_REACTIONSLOT_ARG_NEGATED` | caller | rule: ReactionSlot argument `ext.onViewOwnFaction != null` negated | green | green | green | green | green | green | green | green | **escaped** |
| `F14_REACTIONSLOT_ARG_NEGATED` | caller | rule: ReactionSlot argument `prov && mark.makerFaction != null && mark.makerFaction == viewer.Faction` negated | green | green | green | green | green | green | green | green | **escaped** |
| `F15_REACTIONSLOT_ARG_NEGATED` | caller | rule: ReactionSlot argument `ext.onViewSameIdeo != null` negated | green | green | green | green | green | green | green | **RED** | caught |
| `F16_REACTIONSLOT_ARG_NEGATED` | caller | rule: ReactionSlot argument `prov && mark.makerIdeo != null && mark.makerIdeo == viewer.Ideo` negated | green | green | green | green | green | green | green | **RED** | caught |
| `F17_REACTIONSLOT_ARG_NEGATED` | caller | rule: ReactionSlot argument `ext.onViewHostileMaker != null` negated | green | green | green | green | green | green | green | **RED** | caught |
| `F18_REACTIONSLOT_ARG_NEGATED` | caller | rule: ReactionSlot argument `prov && mark.makerFaction != null && viewer.Faction != null && mark.makerFaction.HostileTo(viewer.Faction)` negated | green | green | green | green | green | green | green | **RED** | caught |
| `F19_REACTIONSLOT_ARG_NEGATED` | caller | rule: ReactionSlot argument `ext.onViewOtherIdeo != null` negated | green | green | green | green | green | green | green | **RED** | caught |
| `F20_REACTIONSLOT_ARG_NEGATED` | caller | rule: ReactionSlot argument `prov && mark.makerIdeo != null && mark.makerIdeo != viewer.Ideo` negated | green | green | green | green | green | green | green | **RED** | caught |

**Old tests 0 of 20; the scenario test 16 of 20.** The four escapes (`F11` to `F14`) are the Subject and OwnFaction
arguments of `ReactionSlot`: no scenario sets a subject thought or an own-faction thought. The frozen
prediction named exactly these. They show where this scenario set is thin: the next two scenarios to write.

**Hand-planted set (fitted, reported apart):**

| mutant | side | what it breaks | scenario | verdict |
|---|---|---|---|---|
| `GREEN_CLEAN` | green | unmutated control | green | stays green |
| `GREEN_CALLER_INLINED` | green | harmless: the one-line gate inlined (the deletion-test repair itself) | green | stays green |
| `GREEN_KERNEL_EARLY_RETURN` | green | harmless: the kernel gate rewritten with an early return | green | stays green |
| `C_LITERAL_FALSE` | caller | wrong literal: the viewer thought never fires | **RED** | caught |
| `C_SETTING_WRONG` | caller | wrong argument: the 'viewer reaction' toggle no longer turns the thought off (painting's does) | **RED** | caught |
| `C_INVERT_ACTIVE` | caller | inverted result: thought fires only with the setting OFF | **RED** | caught |
| `C_SWAP_CLAN_ARGS` | caller | swapped non-symmetric args: colonists lose public-mark reactions, outsiders read clan-only marks | **RED** | caught |
| `C_INVERT_CLAN` | caller | inverted result: only clan-only marks seen by outsiders react | **RED** | caught |
| `C_MISSING_CLAN` | caller | missing call: outsiders get the reaction from clan-only (Cant) marks, owner ruling #4 broken | **RED** | caught |
| `C_ROOM_ARG_INVERT` | caller | wrong argument: marks in the viewer's own room are ignored, marks in other rooms count | **RED** | caught |
| `C_INVERT_ROOM` | caller | inverted result: only marks in other rooms count | **RED** | caught |
| `C_MISSING_ROOM` | caller | missing call: a mark through a wall (another room, within 8 cells) gives the thought | **RED** | caught |
| `C_IDEO_ARG_NEGATED` | caller | wrong argument: the same-ideo reaction goes to viewers of a DIFFERENT ideo | **RED** | caught |
| `C_SWITCH_CROSSED` | caller | wrong use of result: a same-ideo viewer gets the other-ideo thought | **RED** | caught |
| `X_ROOM_ARGS_SWAP` | caller | swapped non-symmetric args: a mark in the next room counts when both rooms are known | **RED** | caught |
| `K_THOUGHT_DROP_SPAWNED` | kernel | dropped conjunct | green | **escaped** |
| `K_THOUGHT_PRECEDENCE` | kernel | precedence slip: setting on alone activates | **RED** | caught |
| `K_ROOM_DROP_NOT` | kernel | dropped negation | **RED** | caught |
| `K_CLAN_DROP_NOT` | kernel | dropped negation | **RED** | caught |
| `K_SLOT_PRIORITY_SWAP` | kernel | priority order swapped | green | **escaped** |
| `K_SLOT_HOSTILE_OR` | kernel | AND became OR | green | **escaped** |
| `K_SLOT_PROVENANCE_INVERT` | kernel | inverted guard | **RED** | caught |

Callers 12 of 12 caught. Kernels 4 of 7: the scenario set misses two priority boundaries of `ReactionSlot`
(`K_SLOT_PRIORITY_SWAP`: own faction against same ideo; `K_SLOT_HOSTILE_OR`: a hostile-maker thought on a mark whose maker
is not hostile), so the 4,096-case fuzz table of `ReactionSlot` must not be retired until scenarios cover each adjacent
pair of the five-rule priority order. `K_THOUGHT_DROP_SPAWNED` escapes because it changes nothing a player can see: the
only caller passes both `p.Map != null` and `p.Spawned`, which vanilla makes equivalent. The fuzz goes red on it. That
red is about the function, not the game.

## The repair, as a proposal

A proposal for the Conductor, not a change made: no mod file was edited by this trial. It is a technical call under
delegation policy §1 (`--why "delegated: technical"`), unless the Conductor routes it elsewhere.

**1. Test the behaviour at the caller, one literal scenario at a time.** For a mod whose gates are called from game-facing
code (a ThoughtWorker, a Harmony patch, a building), compile the *real* caller file against a small fake of the game
types it touches and drive it with scenarios written in play terms ("an enemy's tag through the wall: no thought"), never
by restating the gate's boolean expression. Graffiti's version is
`D:\Luke\dev\RimMandrake\design\RimMandrake\2026-11-07-pocock-design\trial1_scenario\`: `Stubs.cs` (the fake `Verse` and
`RimWorld`, about 150 lines), `Scenarios.cs` (15 scenarios), `run_scenarios.py` (built through `winbuild.stage_build`, as
the fuzz is). Write them vertically: one scenario, watch it go red on the fault it names, then the next.

**2. Retire the truth-table rows the scenarios replace.** A fuzz row such as
`Check(ThoughtActive(a, b, c, d) == (a && b && c && d))` restates the gate: it catches a slip inside the one-line function and
nothing at its call. Keep the fuzz where it checks a real invariant against an independent oracle (Graffiti's weighted
pick, candidate gathering and breach-lure choice), and drop the rows that only restate an expression
once a scenario covers that behaviour.

**3. Inline the gates that fail the deletion test.** Pocock's test: delete the function; if no complexity reappears at its
callers, it was not earning its place. Every Graffiti and KeelHoist gate on the tested paths has **exactly one call
site** (counted outside `Kernel/` and `SelfTest/`), so deleting any of them moves its one line back to the one place
that already holds every input:

| gate | call sites | deletion test |
|---|---|---|
| `RM_GraffitiKernel.ThoughtActive` | 1 | **fails**: its fourth argument is the literal `true` at the only call, and `spawned` duplicates `onMap` (vanilla `Thing.cs`); inlined it is `if (!RM_GraffitiSettings.viewerReactionEnabled \|\| !p.Spawned) return false;` |
| `RM_GraffitiKernel.SameRoomOrUnknown` | 1 | **fails**: `if (room != null && cellRoom != null && room != cellRoom) continue;` reads plainer than the call |
| `RM_GraffitiKernel.ClanOnlyBlocks` | 1 | **fails**: `if (ext.visibility == GraffitiVisibility.ClanOnly && p.Faction != Faction.OfPlayer) continue;` |
| `RM_GraffitiKernel.ReactionSlot` | 1 | **fails**: 11 positional booleans, an enum and a switch express five ordered `if ... return` lines; positional booleans are where the swap mutants live |
| KeelHoist `HoldsRiderInTransit`, `TetherBlocksLaunch`, `GoesIntoHolder`, `CradleTakesPawn`, `DialogHidesPawn`, `GateOpen`, `KeepersBuying` | 1 each | **fail**, the same way; `TetherBlocksLaunch` also takes a literal `true` at its only call |
| HugeThings `HugeGates.Plant` / `Animal` / `Wake` | 4 / 10 / 2 | **shallow but named**: deleting them moves `a && b` into 16 property bodies with no complexity added, but the all-off contract ("a feature is live only when its master is on") loses its one name. Keep, and test at the properties (point 4) |

Inlining loses no test signal today: the harmless-edit control `GREEN_CALLER_INLINED` (the Graffiti gate inlined at its
caller) stayed green on every instrument, because no instrument could see the call in the first place.

**4. Cost to adopt, estimated, not measured:** Graffiti's scenario test was written in about a minute of this run (file
times 16:44:58 to 16:45:52, after planning) and was green on its first build. Each further mod needs its own fakes: KeelHoist's callers touch `Pawn`, `Faction`,
`MapPortal`, `Building_GravEngine` and `AcceptanceReport`, so its fake is larger (an estimate: 2 to 3 hours an agent).
HugeThings' gate tree needs the least: a test at the `*Active` properties ("with Giant animals off, every animal feature reads
off"; "each feature toggle turned off alone turns off only its own property") would, by reading, catch 7 of its 10
caller mutants (all but the crush inversion, the crush master and the sea swap, which live in game code). That is
UNMEASURED, and whether the properties can be reached without the game (through the built assembly, or a copy of the
property block) is unverified. The fakes' risk is drift: a stand-in type (`ModExtension_Graffiti`,
`Filth_Mark` here) that renames a field breaks the build loudly, but a stand-in cannot see def loading or the real
radial-scan order.

## Limits

- **The hand-planted mutants are mine**, a floor and not a sample of real bugs. The escape result does not lean on them
  (it is structural, above). The scenario test's fair score comes from the rule-made fresh batch, which I also froze, so
  sealing guards against fitting but not against a narrow rule.
- **How often real bugs land in these callers is not measured.** That would come from the fix history of the caller files.
  This trial shows that the offline suite would not catch them, not that they occur.
- **Offline only.** The live proofs (`graffiti_v1_live_proof.py`, each mod's `validation.py`) would catch some caller
  mutants. Read, not run: Graffiti's A5 covers one hostile-tag case.
- **The scenario test is not wired into the suite.** It lives in the design folder and is not named `selftest*.py`, so
  `run_selftests.py` never runs it. Adopting it means moving it under `Graffiti\Source\SelfTest\` with a `selftest_` runner.
- **Its fakes are stand-ins**: `ModExtension_Graffiti`, `Filth_Mark` and `RM_GraffitiSettings` carry only the fields the
  worker reads. A renamed field breaks the build, which is loud; a changed default or def-loading behaviour is not seen.

## Cost

- **His minutes: 0.** No card, no game, no deploy, no bridge.
- **Wall time:** about an hour, 16:34 to 17:36 PST, one detached helper, no subagents.
- **Spend:** about $10 of the run's $40 bound, by the session's own meter at the time of writing (this run's token count
  appears in the detached-run end line of `D:\ClaudeWork\rimmandrake\conductor\log.md`).
- **Machine time:** 106 mutant or control runs, 68 minutes of build plus selftest time summed (HugeThings 42 of them;
  `selftest_hugethings_footprint.py` and the Graffiti lint, about 60 s and 28 s a run, were most of it). Three mods ran
  side by side where their files did not overlap. Each mod's runs were serial.
- **Files:** `trial1_mutants.py` (the runner and every mutant, rerunnable: `python3
  design/RimMandrake/2026-11-07-pocock-design/trial1_mutants.py <Mod>`, `--table` to print a run's table) and
  `trial1_scenario\` (the replacement test), both beside this report. Raw logs and `results.json` per mod:
  `D:\ClaudeWork\rimmandrake\pocock_trial1\` (regenerable; not committed).
