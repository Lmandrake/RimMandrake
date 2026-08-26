# XENOTYPE_NONFACTION_SPAWN_ROUTES_1 — done 2026-08-26, seat CHECK

| route | verdict |
|---|---|
| ⭐ `PawnKindDef`'s own `xenotypeSet` | **CHECKED — REAL, and it is ours.** 106 of our own kinds carry one. Proven live |
| wanderer joins | **CHECKED** — `faction: null`, so `kind.xenotypeSet` is the only pool; `Villager` has none *today* |
| refugee chains | **CHECKED** — `Ghoul` carries its own set, generated against `Faction.OfEntities` |
| sanguophage | **CHECKED** — own set, `useFactionXenotypes: false`, hidden runtime faction |
| quest-reward pawns | **CHECKED (mechanism)** — `QuestNode_GeneratePawn` never sets `ForcedXenotype`. ⚠️ the ~300-QuestScriptDef roster is UNMEASURED |
| ideoligion memes (found, not in the original list) | **CHECKED** — route exists; **0 of 136** MemeDefs use it |
| gene extraction / xenogermination | 🔴 **UNMEASURED** — see the evidence for what would measure it and why it needs a scope ruling first |

## The answer in one line

`PawnGenerator.XenotypesAvailableFor` adds `kind.xenotypeSet` **unconditionally**, so a
PawnKindDef with its own set does not care what any FactionDef says. **`XENOTYPE_ROSTER_PURE_SW_1`'s
"66 of 67 cannot reach a player" measured the faction side only and is therefore not the whole
answer** — this line is the correction, and it is written into that item too.

## 🔑 Roll vs gate — the distinction that decides how bad it is

Twelve spawns each into `Jawa_IndigenousTribes`, xenotype read off the instance:

```
Jawa_Spawn_Hutt        RimMandrakeHutt 7  / MandrakeJawa 5
Jawa_Spawn_Lasat       RimMandrakeLasat 4 / MandrakeJawa 8
Jawa_Gamorrean_Guard   Jawa_Xeno_Gamorrean 12 / -          <- useFactionXenotypes: false
```

A weight-999 kind is a **coin flip** against the faction's own set. A kind with
`useFactionXenotypes: false` is a **certainty**. ⇒ The six vanilla `Ancient*` kinds our
`AncientsAreRakata.xml` patches to `RimMandrakeRakata` with `useFactionXenotypes: false` deliver
Rakata **every time**, through vanilla's own Ancients faction.

**Delivered defNames:** `RimMandrakeHutt`, `RimMandrakeLasat`, `Jawa_Xeno_Gamorrean`,
`RimMandrakeRakata`.

⛔ **No fix proposed here and no XenotypeDef cut** — `XENOTYPE_ROSTER_PURE_SW_1` ruled against
cutting, and whether these arrivals are wanted at all is a scope call. Filed for DECIDE as
`NONCANON_ARRIVES_BY_PAWNKIND_1`.

Evidence: `infrastructure/state/evidence/xenotype_nonfaction_routes_2026-08-26_CHECK.md`
