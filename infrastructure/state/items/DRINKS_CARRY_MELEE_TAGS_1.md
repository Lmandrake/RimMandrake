## spec
🔴 **Measured live 2026-08-21: two of five `Jawa_Tribal_Scavenger` spawned holding a bottle
of ale as their PRIMARY weapon.**

    equipment: [{"def": "TarisianAle", "stuff": null, "isPrimary": true}]

**The mechanism, read off the 2026-08-21 dump:**

| def | mod | ingestible | weaponTags |
|---|---|---|---|
| `TarisianAle` | Star Wars Animal Collection (Continued) | **true** | `NeolithicMeleeBasic`, `NeolithicMeleeDecent` |
| `FungusBeer` | — | **true** | `NeolithicMeleeBasic`, `NeolithicMeleeDecent` |

`Jawa_Tribal_Scavenger` carries exactly one tag — `NeolithicMeleeDecent` — with
`weaponMoney` fixed at 150. So the drink is inside its pool, and a bottle wins the roll
about as often as a real weapon does.

⚠️ **This is a THIRD-PARTY tagging choice, not our bug**, and it is arguable on its own
terms: RimWorld will let a pawn club someone with a bottle, and both defs carry `tools`, so
they are genuinely swingable. What is not arguable is a scavenger being *generated* holding
one instead of a weapon.

🔑 **Scope is small and worth stating so nobody over-fixes it.** Only **4** PawnKindDefs in
the whole loaded game use `NeolithicMeleeDecent`, and exactly **one** is ours. Everything
else sharing that tag — the horns, tusks, claws and clubs — is a genuine melee weapon;
`ingestible` is what separates them, not `category` or a missing `verbs`.

⛔ **The obvious wrong fix:** I first filtered for `category: Item` with no `verbs` and got
41 defs including `MeleeWeapon_BreachAxe` and `BS_OgreClub`. Real melee weapons keep their
attacks under `tools`, not `verbs`. Do not strip a tag from that list.

## verify
Patch `TarisianAle` and `FungusBeer` to drop `NeolithicMeleeBasic` and `NeolithicMeleeDecent`
(a `PatchOperationRemove` on their `weaponTags`), OR give `Jawa_Tribal_Scavenger` a tag pool
that excludes them.

Then re-run the live check: spawn `Jawa_Tribal_Scavenger` ×10 and read
`jawa/pawn_get` → `equipment`. ⚠️ Ten, not five — at roughly two in five the bottle needs a
sample big enough that its absence means something.

## criteria
- no `Jawa_Tribal_Scavenger` in 10 spawns holds an `ingestible` as `isPrimary`
- the two drinks still exist and are still drinkable — this removes a tag, not an item
- ⛔ and no other kind loses a real weapon from its pool: re-run `jawa/pawnkind_audit` and
  confirm `emptyTagPool` and `cannotAfford` both stay at 0

## notes
Filed by CHECK 2026-08-21 from `C40`'s failing run. Related but distinct from
`WEAPON_MONEY_ROLL_NOT_CEILING_1`: that one is about a low money roll leaving hands empty,
this one is about the pool containing something that should not be in it. A kind can suffer
both, and `Jawa_Tribal_Scavenger` does — one of its five had no equipment at all.
