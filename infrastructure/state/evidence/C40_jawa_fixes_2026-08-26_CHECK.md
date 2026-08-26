# C40 — three Jawa fixes, run live 2026-08-26, seat CHECK

**Config:** full list, **582 active mods** read from `ModsConfig.xml` (not a doc).
`guy762.kotorweapons` ACTIVE; `btd.xenotyperemix.starwars` ABSENT — which is (b)'s premise.
Game `game_loaded`, one map, `ticksGame 1174` (paused debug map, animals only, no colony).
Driven through `jawa/spawn_pawn` → `jawa/pawn_get`, i.e. spawn then read the pawn back.

## (a) `MandrakeJawa` + `canGenerateAsCombatant` — PASS

20 `Jawa_Tribal_Scavenger` requested in `Jawa_IndigenousTribes` across three calls;
**16 landed as the kind and every one of them is `MandrakeJawa`.**

```
Jawa_Tribal_Scavenger on map: 16
  MandrakeJawa      : 16/16
  ARMED             : 14/16
  guy762_Robes_jawa : 16/16
  guy762_JawaHood   :  0/16
```

Weapons actually carried: `GS_Gaffi`, `MeleeWeapon_BreachAxe`, `SkalderTusk`,
`MA_GnautHorn`, `MA_CapryakHorn`, `BMT_CrystalMantisClaw`, `BMT_FungalMantisClaw`,
`BMT_PustuleHornetStinger`. ⇒ They generate as combatants and they arm themselves.

⚠️ 2 of 16 spawned unarmed. `jawa/pawnkind_audit --filter jawa` reports **71 tool-using
Jawa kinds, every kind that intends to arm can** — so this is a per-pawn roll, not a
tag or budget defect. Not counted against the criterion, which asks for six.

## (b) Geonosian Foundry Hive xenotype — PASS

The kind names in C40's own text do not exist. The real roster, from
`jawa/pawnkind_audit --filter geonos`: `Jawa_Geonosian_Grunt` · `_Heavy` ·
`_Specialist` · `_Leader` (all healthy, cheapest weapon `guy762_sonpistol` @220).

```
Jawa_Geonosian_Grunt  xeno=RimMandrakeGeonosianVariants
                      weapon=['guy762_sonrifle']  apparel=['guy762_JediCloak_light']
```

⇒ **Not a baseliner.** The re-gated xenotype node is being read.

## (c) starting gear — PASS on the graded half

`guy762_Robes_jawa` on **16 of 16**. This is the clause that matters: the def lives in a
mod we kept, so its presence in a dump proves nothing — the pawn wearing it is the evidence,
and 16 pawns are wearing it.

⛔ The voice clause is **not graded** (owner, 2026-08-16).

## Two things this run found that C40 did not ask about

1. **`guy762_JawaHood` appears on 0 of 16.** They wear `Apparel_WarVeil` instead. The robe
   half of (c) passes on its own, so C40 is not failed on it — filed separately.
2. **Stray `Colonist`/`Baseliner` pawns appeared in `Jawa Trade Moot` (4) and
   `Geonosian Foundry Hive` (1) during the spawn runs.** ⚠️ NOT a `spawn_pawn` defect:
   the tool calls `PawnGenerator.GeneratePawn(kind, fac)` verbatim with no fallback
   (`JawaBenchTerrainTools.cs:1806`), and its own per-pawn rows came back `ok:true` with
   ids that read back as `Jawa_Tribal_Scavenger`/`MandrakeJawa` **8 for 8** on the third
   call. Observed, not explained. Filed separately.
