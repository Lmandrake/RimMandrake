## spec
Ruling and the scope evidence: `items/FIFTEEN_TAGLESS_KINDS_RULING_1.md` `## ruling`.
**Three of the fifteen tagless kinds are in scope. This is those three.**

In `src/Jawa/Jawa_Patches/Patches/WeaponTags_Renormalise.xml`, add the vanilla tag `Gun` to
each — **appended, not replacing** the existing dead tag:

| defName | keeps | gains | why it matters |
|---|---|---|---|
| `AncientSoldierBoss` | `AMHP` | `Gun` | CP 225 |
| `AncientSoldierBossN` | `AMHP` | `Gun` | |
| `AncientMallGuards` | `PKM` | `Gun` | ⭐ **CP 425** |

🔑 **`Gun` is not a chosen weapon — it is the pool their own lighter sibling already uses.**
Core's `AncientSoldier` carries `weaponTags: [Gun]` and is **not** on the tagless list, so
`weapon_tag_audit.py` itself proves that tag is non-empty. All three carry
`weaponMoney 2100~7500` against the soldier's `300~900`, so **the budget makes them elite;
the tag pool does not have to.** Nobody picks a gun.

⛔ **Do NOT delete `AMHP` or `PKM`.** They are additive and harmless. If the donor mod is
ever installed its weapons rejoin the pool on their own; deleting the tag makes that
silently impossible.
⛔ **Do not touch the other twelve.** Five are upstream-deliberate; seven belong to factions
or routes that never reach this planet — `BS_*` to medieval-fantasy factions the checklist
unticks, `Tribal_Archer_Fire` to `TribeSavageImpid`, `OuterRim_ImperialTrader` to the
**struck** `OuterRim_GalacticEmpire`, and `VEE_Hunter`/`VEE_TribalHunter` have **no
references anywhere in any loaded Defs tree**.

⚠️ **These same three defs are relabelled by `FORSAKEN_LABELS_FINISHED_1`** (`AncientMallGuards`
⇒ `Forsaken sentinel`, the two Boss kinds ⇒ `Forsaken special unit`). **Do both in one pass.**

🔴 **They are not reached through factions.** They carry no `defaultFactionDef` and appear in
no `pawnGroupMakers` — Ancient urban ruins places them from map set pieces
(`AM_Supermarket_*`, `AM_Reserve*`, `AM_ReserveBunker`) via
`AncientMarket_Libraray.CustomMapDataDef`. ⇒ **a faction-based check will report them
unreachable and be wrong.**

## verify
- `python3 src/RimMandrake/Utils/weapon_tag_audit.py` reports **12** kinds with every tag
  empty, not 15, and the three above are gone from the list
- ⚠️ the tool **refuses to report unless the dump's mod set matches `ModsConfig.xml`** — if
  it refuses, regenerate the dump rather than reading a stale one
- the twelve that remain are exactly the ones named out of scope above, by name
- `validate_patch.py` clean; each new op reports 1 hit

## criteria
Nothing walks out of an ancient supermarket at combat power 425 with empty hands.
