## spec
Ruling: `items/FACTION_SLATE_ZEROES_KEEPS_1.md` `## ruling`.

`src/Jawa/JawaFactionSlate/Patches/OnlyOurFactions.xml` zeroes **two** fields on 48
FactionDefs. **It must zero only one.**

| field | today | should be |
|---|---|---|
| `startingCountAtWorldCreation` | zeroed | ✅ **keep zeroing** — this is what removes a faction from the DEFAULT list, which is the slate's whole job |
| `maxConfigurableAtWorldCreation` | zeroed | 🔴 **STOP. Leave the def's own value alone.** |

**Why.** `FactionGenerator.ConfigurableFactions` is
`from f in DefDatabase<FactionDef>.AllDefs where f.maxConfigurableAtWorldCreation > 0`, and
`Page_CreateWorldParams.cs:70` builds the Configure Factions page from that enumeration.
⇒ **at 0 the row is not capped, it is deleted**, and the owner cannot restore the faction at
the screen. Four rows the ratified `WORLDGEN_FACTION_CHECKLIST.md` tells him to tick are
currently among them.

⛔ **The file's header states the opposite and must be corrected in the same change:**
*"maxConfigurableAtWorldCreation is only a cap and changes nothing on its own."* That
sentence is false at zero and is why the generator does this.

⚠️ **`requiredCountAtGameStart` is not a safety net and nobody should treat it as one.**
`FactionGenerator.InitializeFactions` reads it **only** in the branch where no faction list
was configured; worldgen through the screen passes `Current.CreatingWorld.info.factions` and
adds that list verbatim. All four affected KEEPs carry `requiredCountAtGameStart 1` and
would still be absent.

⚠️ **The generator is not in this repo.** The file says *"Generated 2026-08-17. Do not
hand-edit."* and no script under `src/` writes it. ⇒ **find the generator and fix it there.**
If it cannot be found, say so and convert the file to hand-maintained with the header
corrected — but do not silently hand-edit a file that claims to be generated.

## verify
- **zero** `maxConfigurableAtWorldCreation` ops remain in `OnlyOurFactions.xml`
- the `startingCountAtWorldCreation` ops are unchanged in number and target
- the header no longer claims `maxConfigurableAtWorldCreation` is only a cap
- `validate_patch.py` clean, and the op count drops by roughly half

## criteria
At the Configure Factions screen the owner can add back any faction the slate turned off.
