## spec
🔴 **The Free Droid Enclaves field plain humans, and the fix is a content choice DECIDE
has to make.** `DROID_ENCLAVES_FIELD_HUMANS_1` measured it live: `Jawa_Droid_Grunt`
spawned into its own faction comes out `Baseliner` **4 of 4**, and it is the only one of
the eight factions that fails.

**The mechanism, measured 2026-08-21 — this part is settled and needs no ruling:**
- All four `Jawa_Droid_*` kinds declare `<race>Human</race>` with
  `useFactionXenotypes: true`, so their species comes entirely from the faction's
  `xenotypeSet`.
- `Jawa_FreeDroidEnclaves`' set is `<xenotypeSet Inherit="False" />` — **empty**. It offers
  nothing, so every pawn falls back to `Baseliner`.
- ⛔ **Filling that set cannot fix it.** There is no shipping droid xenotype anywhere:
  139 `XenotypeDef`s in the stack, exactly one has "droid" in its name and it is
  `guy762_debugxenotype_droid`, a debug def. Our own races mod ships **71 xenotypes and
  every one is an organic species**.
- 🔑 **In this stack droids are RACES, not xenotypes**, and the working examples prove it:
  `OuterRim_ProtocolDroid` declares `race=OuterRim_ProtocolDroid`, `OuterRim_KXSecurityDroid`
  declares `race=OuterRim_KXSecurityDroid` — both `ThingDef`s. **This faction's own Trader
  group already fields exactly those two.**

⇒ The repair is to change `<race>` on the four kinds. **Which droid wears which role is
the ruling wanted here.** ~34 Humanlike droid races are loaded (`OuterRim_*` and
`guy762_DroidRace_*`). A plausible ladder, offered as a starting point and **not** as a
recommendation BUILD is entitled to make:

| kind | role | candidate races already loaded |
|---|---|---|
| `Jawa_Droid_Grunt` | line | `OuterRim_BattleDroid` · `guy762_DroidRace_ADMkI` |
| `Jawa_Droid_Heavy` | heavy | `OuterRim_SuperBattleDroid` · `OuterRim_MagnaGuardDroid` |
| `Jawa_Droid_Specialist` | specialist | `OuterRim_TacticalDroid` · `guy762_DroidRace_T3series` |
| `Jawa_Droid_Leader` | leader | `OuterRim_SuperTacticalDroid` · `OuterRim_HKDroid` |

⚠️ **Two things to weigh that are not obvious:**
1. `intelligence` is not uniform. `OuterRim_BattleDroid` and the ones above are
   `Humanlike`; many droid ThingDefs (`OuterRim_GNKDroid`, `OuterRim_MSEDroid`, the whole
   `JDSCIS_*` battle line) are **`ToolUser`** and cannot be colonists or hold a role.
   Choose only from the Humanlike set.
2. `useFactionXenotypes` should probably come OFF these four once they carry a droid race,
   or the faction's set will be asked for a xenotype the race cannot wear. Say so in the
   ruling either way, so BUILD does not have to guess.

## verify
After the ruling, BUILD edits the four `<race>` values in
`src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml`, and the named races all
resolve against the def dump as `Humanlike` `ThingDef`s.

## criteria
DECIDE names a race for each of the four kinds, and says whether `useFactionXenotypes`
stays. No artefact is owed by this item itself.

## notes
⚠️ For whoever writes the ruling: BUILD froze `Jawa_FreeDroidEnclaves`' `xenotypeSet`
earlier the same day, but that does NOT obstruct this — the freeze only stops
`apply_race_factions.py` refilling the set with `RimMandrakeUgnaught`, and the set is not
where the fix goes.
🔑 The live measurement that found this was itself a correction: CHECK's first sweep used
`faction: "hostile"`, which drops a pawn into whatever faction opposes the player and so
reads THAT faction's xenotypeSet — producing a false "49 of 55 kinds spawn Baseliners".
The species roster is in good shape; exactly one faction is wrong.
