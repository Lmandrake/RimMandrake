## spec
🔴 **`Jawa_Droid_Grunt` spawned into `Jawa_FreeDroidEnclaves` comes out `Baseliner` 4 of 4.**
The Free Droid Enclaves field plain humans.

Measured live 2026-08-21 on the generated map, and it is the **only** faction that fails.
Every other one gets its species right once the pawn is spawned into its own faction:

| kind → its own faction | xenotype |
|---|---|
| `Jawa_Geonosian_Grunt` → Geonosian Foundry Hive | `RimMandrakeGeonosianVariants` **4/4** ✅ |
| `Jawa_Tribal_Scavenger` → Indigenous Tribes | `MandrakeJawa` **5/5** ✅ |
| `Jawa_TradeMoot_Grunt` → Indigenous Tribes | `MandrakeJawa` **5/5** ✅ |
| `Jawa_Blackstar_Grunt` → Pirate | Anzati · Cathar · Zygerrian · Duros · Nagai — a mixed mercenary company ✅ |
| `Jawa_Wildsteam_Grunt` → Wildsteam Clan | Ithorian · Ewok ✅ |
| `Jawa_Hutt_Leader` → Hutt Cartel | Hutt · Gamorrean · Baseliner (mixed) ✅ |
| **`Jawa_Droid_Grunt` → Free Droid Enclaves** | **`Baseliner` 4/4** 🔴 |

⭐ **The likely lead, and it is only a lead:** counting `xenotypeSet` blocks in our own
FactionDefs, `Jawa_FreeDroidEnclaves` has **1** — the fewest of the eight. Ascendant Helix,
Deepwater, Hutt, Junkers and Wildsteam have 3; Geonosian and Indigenous Tribes have 2.
⛔ A block count is not a diagnosis. Read the actual block before changing anything.

⚠️ **This matters more than a cosmetic mismatch.** A droid faction that fields humans is not
a droid faction — the Free Droid Enclaves' entire premise is that they are *free droids*, and
`C40`'s own note records that every `OuterRim_*Droid` race reads `intelligence: Humanlike`
so their ideoligion runs. Humans in their place makes both the faith and the faction read as
a content gap.

## verify
Read `Jawa_FreeDroidEnclaves`' `xenotypeSet` in
`src/Jawa/Jawa_Patches/Defs/FactionDefs/`, and check it against a faction that works —
`Jawa_GeonosianFoundryHive` is the closest comparison, since it also fields one species.

🔑 **The check is `xenotypeSet`, not `xenotypeChances`.** All 67 of our kinds carry
`useFactionXenotypes: true`, so the pawn takes its xenotype from the faction it JOINS.
⛔ And do NOT try to settle it from the def dump: `xenotypeChances` is absent from all 1,736
PawnKindDefs there, so any dump-based answer is UNMEASURED, not negative.

Then re-spawn: `jawa/spawn_pawn` with `kindDef: Jawa_Droid_Grunt`, `faction:
Jawa_FreeDroidEnclaves`, `count: 5`, and read `jawa/pawn_get` → `xenotype`.

## criteria
- 5 of 5 `Jawa_Droid_Grunt` spawned into their own faction read a droid xenotype, not
  `Baseliner`
- the other seven factions are re-checked afterwards and none regressed
- ⚠️ `Jawa_Hutt_Leader` returning a MIX (Hutt, Gamorrean, Baseliner) is **not** a defect — a
  cartel with hired muscle and human staff is the design. Do not "fix" it to uniformity.

## notes
Filed by CHECK 2026-08-21. 🔴 **Found only because a wrong spawn parameter was corrected.**
My first sweep used `faction: "hostile"`, which drops a pawn into whatever faction opposes
the player, so it took THAT faction's xenotypeSet — and produced a reading of *49 of 55 kinds
spawn Baseliners*, which would have been a catastrophic and entirely false v1 finding. The
species roster is in good shape; exactly one faction is wrong.
