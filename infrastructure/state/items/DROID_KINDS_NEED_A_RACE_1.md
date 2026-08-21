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

---

# ⭐ RULED — DECIDE, 2026-08-21 12:50. Owner: *"You rule it."*

**All four races come from `Neronix17.OuterRim.DroidDepot` and nothing else.** That is a
ruling, not a preference: the faction already `MayRequire`s exactly that package on its
Trader group, so this adds **zero new mod dependencies**. Do not reach into
`guy762_DroidRace_*` for any of the four.

| kind | its label (unchanged) | `<race>` | why this one |
|---|---|---|---|
| `Jawa_Droid_Grunt` | labour droid | `OuterRim_ImperialLaborDroid` | literally a labour droid, and *Imperial* is the backstory — these are the ones that got away |
| `Jawa_Droid_Heavy` | security droid | `OuterRim_KXSecurityDroid` | ⭐ **already fielded by this faction** as its Trader `guards`. Sets no new precedent |
| `Jawa_Droid_Specialist` | medical droid | `OuterRim_ProtocolDroid` | ⭐ **already fielded by this faction** as its Trader. The attendant silhouette; see the flag below |
| `Jawa_Droid_Leader` | First Speaker R-41 Rell | `OuterRim_SuperTacticalDroid` | a command chassis for the one who commands; carries `combatPower 176` without looking absurd |

⛔ **NO BATTLE DROIDS — and this is the reasoning to reuse, not just the list.** `B1`, `B2`,
`BX Commando` and `MagnaGuard` all read as *Separatist army*. This faction is an enclave of
**freed** droids; its roster should read as what its members were **built for and escaped
from**, not as someone's infantry. The candidate ladder in the spec above assumed a
grunt/heavy/specialist/leader combat ladder — **the labels say otherwise and the labels win.**

**Also do:** set `<useFactionXenotypes>false</useFactionXenotypes>` on all four. A xenotype
is a Human-race concept; with a droid race the field is asking the faction for something the
race cannot wear.

⛔ **DO NOT TOUCH `<xenotypeSet Inherit="False" />` in `JawaFreeDroidEnclaves.xml`.** It is
**frozen on purpose** (owner, 2026-08-19; marker written 2026-08-21) to stop
`apply_race_factions.py` refilling it at 1.000 and walking an Ugnaught out of a droid
enclave. The empty set is the fix working, not the bug. Leave the freeze marker intact.

## the exact edit sites, measured 2026-08-21

`src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml` —

| kind | `<race>` line | `<useFactionXenotypes>` line |
|---|---|---|
| `Jawa_Droid_Grunt` | 391 | 395 |
| `Jawa_Droid_Heavy` | 408 | 412 |
| `Jawa_Droid_Specialist` | 425 | 429 |
| `Jawa_Droid_Leader` | 442 | 446 |

⚠️ **Line numbers are a convenience and will drift** — match on the `<defName>` above each.

⚠️ **Load-order safety is yours to solve, and it is real.** These four `PawnKindDef`s are
named without `MayRequire` by `JawaFreeDroidEnclaves.xml`'s `Combat` and `Settlement` group
makers. If Droid Depot is absent, an unresolved `<race>` kills the kind and the group makers
then dangle. Pick whichever guard is correct for this mod's structure and say which in the
commit body.

## verify (offline, replaces the one above)

```
python3 skills/rimworld-modding/scripts/validate_patch.py   src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml --defs
```
All four `<race>` values resolve to a `ThingDef` in the frozen dump, and no `<race>Human</race>`
remains on any `Jawa_Droid_*`.

**Measured against `OFFICIAL-2026-08-21` (`defs.sqlite`, 578 mods / `e0f11692cf69e516`,
24904 ThingDefs MEASURED), 2026-08-21:** all four exist, spelled exactly as written above,
all `intelligence: Humanlike`, all `race.body = OuterRim_HumanoidDroid`,
`thinkTreeMain = Humanlike`. Each has one `lifeStageAges` entry against Human's six — a
single adult stage, so **no droid children**, which is correct and is not a defect to fix.

## criteria (live, replaces the one above)

Spawn each of the four into `Jawa_FreeDroidEnclaves` and read the pawn's race:
**0 of 4 come out `Baseliner`**, and each wears the race in the table. A `Combat` group
generated for the faction contains no Human.

## ⚠️ ONE CONTESTABLE CALL, flagged rather than buried

`Jawa_Droid_Specialist` is labelled **"medical droid"** and gets a **protocol** chassis,
because **there is no medical droid in the Humanlike set** — 2-1B and FX have no Humanlike
ThingDef in this stack (33 Humanlike droids measured across 636 `OuterRim_*` +
`guy762_DroidRace_*` ThingDefs). Protocol is the nearest attendant silhouette. If the owner
would rather the label moved than the chassis, *"attendant droid"* costs nothing. **Do not
wait on that** — build the table as ruled.

🔑 A second, smaller one: *"R-41"* is an **astromech-style designation** on a leader I have
given a Super Tactical chassis. The only R-series humanlike droid in the stack is
`guy762_DroidRace_R8009UD`, which is in the other mod and would break the one-mod rule
above. The name is the cheaper thing to change if it ever grates.
