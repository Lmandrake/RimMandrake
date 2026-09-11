# CHERRYPICKER_SHIP_BASELINE_STALE_1 — diagnosis (2026-09-10)

Method: `cherrypicker.py` for all set math (never a fresh regex). Full key
lists: `Transient/cherrypicker_drift_keys_2026-09-10.md`.

## Where the 141 BackstoryDef cuts came from

Not mysterious — commit `7a315536` (2026-08-29, Fable pass): a deliberate,
documented PAWN_FLAVOR curation cutting "141 backstories + 2 traits" from
**4 wrong-fiction mods**: tug.Minotaur (35 RBM_ + 1 trait), shavius.medieval.flavour
(26: REBC_/SH_MED_/VA_MED_), vanillaquestsexpanded.ancients (26 VQE_ + 1 trait),
vanillaracesexpanded.archon (54 VREA_). Owner ratified ALL 1,509 SHIP keys in
writing on 2026-09-02 (commit `b00303b4`): *"Cuts are lore, blanket, all 1509 -
his words."* The 30 ThingDef/5 PawnKindDef/2 TraitDef turret+Anomaly reversals
are equally deliberate: `TURRET_ROSTER_CURATION_1` (owner-ruled whitelist,
commit `291fcc8f`, 28 keys landed) plus the earlier Anomaly-content cuts.

## Existence check (does the def still exist in the CURRENT game?)

- **tug.Minotaur**: present on disk (Steam Workshop id 3548423129, packageId
  `tug.Minotaur`) but **NOT in the active ModsConfig.xml list**. Its 35 RBM_
  backstories + `RBM_Herculean_Trait` do not resolve in the current merged
  defset — **SELF-PRUNED** (mod present but inactive; matches the
  `.bak-nodef` no-def-pruning mechanism).
- **shavius.medieval.flavour, vanillaquestsexpanded.ancients,
  vanillaracesexpanded.archon**: all three **ACTIVE and present on disk**
  (workshop ids 2767940226 / 3618306875 / 3067715093). Spot-checked defNames
  (`SH_MED_LandlessKnight`, `VA_MED_Archer`, `REBC118`, `VQE_ArchiteVolunteer1`,
  `VQE_IdealPatient`, `VREA_ArchonCadet`, `VREA_VoidHarmonizer2`) all found in
  live 1.6 Defs XML. **These 106 BackstoryDef keys are NOT self-pruned — the
  defs exist and will load.**
- **Metalhorror, Trispike**: vanilla Anomaly DLC (`Data/Anomaly/Defs/...`),
  definitively exist. Cannot be self-pruned. Same for `Ghoul`/`ShamblerSoldier`/
  `ShamblerSwarmer` (vanilla). `DeadColumnMod` was a *named* deliberate cut
  (commit `f0e5e321`, "owner: no deadlife references") — its un-cut is a
  reversal of a specific, attributed decision, not drift.

## Timeline

- 2026-09-01 08:15 PRECHANGE backup: 141/141 backstory cuts intact (1,513 keys).
- 2026-09-02: SHIP captured + owner-ratified "blanket, all 1509."
- No `.bak-*`/`.PRECHANGE.*` snapshot exists between Sep 2 and Sep 10 — the
  reversal happened via Cherry Picker's in-game UI with no backup ritual run
  around it (the tool only snapshots when someone remembers to ask it to).
- The item file already reported the drift as present at 2026-09-09 22:26
  (LIVE was 1,948 keys then; it is 1,972 now — growth is 100% ThingDef, still
  the ongoing `sarg.alphamechs` addition work). So the backstory/turret
  reversal landed **before** 2026-09-09 22:26, bounded only to (Sep 2, Sep 9
  22:26]. Transient/Player_log filenames from 2026-09-08 (droid/mech
  consolidation, kotordroids retirement) are the best-correlated candidate
  window — same UI session class that also added the `AM_*` cuts — but no
  artifact pins an exact hour.

## Verdict per group

| Group | Count | Verdict |
|---|---|---|
| tug.Minotaur backstories + trait | 36 | **SELF-PRUNED** (mod inactive; harmless either way — its defs won't load) |
| shavius/VQE-ancients/VREA-archon backstories | 105 | **GENUINE REVERSAL** (defs exist, mods active, contradicts the owner's written "blanket, all 1509" ruling) |
| Turret ThingDefs/PawnKindDefs/TraitDef (incl. Metalhorror, Trispike, DeadColumnMod) | 37 | **GENUINE REVERSAL** (Metalhorror/Trispike/Ghoul/Shamblers are vanilla and definitely exist; DeadColumnMod was a named deliberate cut; the group rides `TURRET_ROSTER_CURATION_1`, an owner-ruled whitelist) |

Net: **139 of 178 reversed keys (78%) are genuine reversals of owner-ratified,
documented decisions — not self-pruning.** Only the 36 tug.Minotaur-sourced
keys plausibly self-pruned, and even those are consistent with someone
clicking "reset"/"select all" in Cherry Picker's UI rather than the game
engine silently dropping them (self-pruning would explain tug.Minotaur alone;
it cannot explain the other 142).

## Recommended action

**Do not `--capture-ship` yet.** Fix the live Cherry Picker list back to
SHIP's 141+30+5+2 = 178 keys via the mod's own in-game UI first (the
Alpha Mechs `+617` additions look like clean, separable curation and can be
folded in after), THEN run
`python3 src/RimMandrake/Utils/cherrypicker_swap.py --capture-ship --apply`.
The backstory/turret reversal reads as an accidental UI action (e.g. a
"reset"/"select all" click while doing the Sep 8 droid/mech work), not a
considered decision — it silently un-rules 105 backstories and 37 things/
pawnkinds the owner explicitly ratified 8 days earlier.
