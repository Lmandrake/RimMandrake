⚠️ **CORRECTED 2026-08-26 by `XENOTYPE_NONFACTION_SPAWN_ROUTES_1` — read this before the "66 of
67 cannot reach a player" number below.** That measurement is right about the FACTION side and is
not the whole answer. `PawnGenerator.XenotypesAvailableFor` (`Verse/PawnGenerator.cs:1747`) adds
**`kind.xenotypeSet` unconditionally, regardless of faction**, and **106 of our own PawnKindDefs
carry one**. Proven live, 12 spawns each into `Jawa_IndigenousTribes`, read off the instance:
`Jawa_Spawn_Hutt` → RimMandrakeHutt 7 / MandrakeJawa 5; `Jawa_Gamorrean_Guard`
(`useFactionXenotypes: false`) → Jawa_Xeno_Gamorrean **12 of 12**. The six vanilla `Ancient*`
kinds our `AncientsAreRakata.xml` patches deliver `RimMandrakeRakata` every time.
⇒ Non-canon species **can** reach a player without any faction fielding them. The ruling stands;
the measurement behind "they already cannot spawn" does not.
Evidence: `infrastructure/state/evidence/xenotype_nonfaction_routes_2026-08-26_CHECK.md`.

---

## spec
🔴 **OWNER'S RULING, filed 2026-08-23, `kind: ruling`:** *"The xenotype roster is PURE Star
Wars; non-canon species are cut, not reflavored."*

⛔ **This is not a decision to be made — it is his, already made.** DECIDE's job is to
propagate it and say what it costs. What follows is measurement, not deliberation.

## 🔑 MEASURED — the ruling is ALREADY ENFORCED, by a mechanism nobody wrote it down as

**139 XenotypeDefs installed. 72 are ours** (70 `RimMandrake - Star Wars Races`, 1 KotOR,
1 `Jawa Patches`). The other **67 are non-canon.** Cross-referencing every `FactionDef`'s
`xenotypeSet` against the twelve factions actually placed in
`world/ASHKARR_WORLDMAP_settlements.csv`:

| | count | |
|---|---:|---|
| 🔴 **reachable on our map** | **1** | `Baseliner` only — in 9 of our 12 factions |
| ⚠️ in a faction that is NOT placed | 47 | Big and Small ×13, Alpha Genes ×12, Biotech ×9, Det's ×6, and others |
| ✅ in no faction at all | 19 | |

⭐ **And the non-placed factions do not generate either.** Measured on the same capture:
every faction carrying an exotic xenotype has **`startingCountAtWorldCreation: 0`**, so
`Page_CreateWorldParams.ResetFactionCounts()` never adds it to the world.
`src/Jawa/JawaFactionSlate/Patches/OnlyOurFactions.xml` is what does this, across 48 FactionDefs.

⇒ **66 of the 67 non-canon xenotypes cannot reach a player today.** The roster is already pure
Star Wars in play. The ruling is satisfied by mechanism; it was simply never written down as
the thing that satisfies it.

## 🔴 DECIDE'S RULING ON HOW TO CARRY IT OUT — do NOT cut the defs

**Cutting them would cost real breakage for zero player-visible gain.**

- A `XenotypeDef` is referenced by `GeneDef` sets, `FactionDef.xenotypeSet`, quests and
  `PawnKindDef` xenotype fields. Cherry-picking one that anything still names produces
  `Could not resolve cross-reference` — the exact class of error that cost this project 26
  BiomeDefs and 101 CharacterDefs earlier on the same day.
- The gain is **nothing**: they already cannot spawn.
- ⚠️ **`xenotypeChances` is dictionary-keyed and an `<li>` there discards the WHOLE FactionDef
  silently** (`skills/rimworld-xenotypes`). Editing 47 factions' xenotype blocks to "clean" a
  roster that is already unreachable is a large silent-failure surface bought for no benefit.

✅ **`Baseliner` STAYS, and is not an exception to his ruling.** It is the default human and
9 of our 12 factions use it. A baseline, unmodified human is *canon Star Wars* — it is what
most of the galaxy is. Cutting it would leave nine factions unable to generate a pawn.

⇒ **The enforcement mechanism IS `startingCountAtWorldCreation: 0`, and that is what this
ruling should be recorded against.** Anything that re-enables one of those factions re-admits
its species, which makes `OnlyOurFactions.xml` a canon-bearing file and not merely a tidiness one.

## ⚠️ THE RESIDUAL RISK, and it is the only real work left
`xenotypeSet` on a placed faction is **not the only route a xenotype reaches a player.**
Wanderer-join events, quest-reward pawns, refugee chains, sanguophage encounters and
gene-extraction can each introduce a xenotype no faction on the map fields. **Nobody has checked
those routes**, and that — not def-cutting — is where a non-canon species would actually appear.
Filed as `XENOTYPE_NONFACTION_SPAWN_ROUTES_1`.

⚠️ **`maxConfigurableAtWorldCreation` is 9999 on those factions on purpose**, so the owner can
always add one back at the Configure Factions page. That is a deliberate escape hatch, not a
hole — but it means the ruling is enforced by a default, not by a wall.

## verify
    python3 -c "…"   # every FactionDef whose xenotypeSet names a non-SW xenotype has
                     # startingCountAtWorldCreation == 0
**PASS =** exactly one non-Star-Wars xenotype is reachable through a placed faction, and it is
`Baseliner`.

## criteria
- [x] Every non-canon xenotype is accounted for as reachable or not.
- [x] A ruling on whether to cut the defs, with the cost of cutting stated.
- [ ] ⏳ The non-faction spawn routes checked — `XENOTYPE_NONFACTION_SPAWN_ROUTES_1`.
