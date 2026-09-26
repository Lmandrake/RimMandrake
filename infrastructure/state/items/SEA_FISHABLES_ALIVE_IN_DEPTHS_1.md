# SEA_FISHABLES_ALIVE_IN_DEPTHS_1 — a catch item with nothing swimming is an unfinished species

## the ruling

Owner, at the bench 2026-09-26, typed:

> *"All the fishables should also be alive and moving around in the depths (this is true
> for ALL seas)."*

⇒ **Every entry in every sea's `fishTypes` owes a LIVING counterpart** on that sea's floor
pocket map. A catch item on its own is half a species.

🔑 This widens the standing "a sea species owes two defs" line from a per-species nicety
into a completeness bar on all four seas at once.

## the gap, MEASURED 2026-09-26

| sea | catch entries | floor animals | shortfall |
|---|---|---|---|
| `RM_TheScald` | 9 | 3 inline + 3 canon patch-added | some |
| `RM_GreySea` | 9 | 5 | 4+ |
| `RM_TwilightSea` | 12 | 6 | 6 |
| `RM_PropaneLake` | 9 | 6 | 3 — **and none of them can spawn**, see below |

The Grey Sea already shows the intended pattern: `RM_Essarn` (floor) ↔ `RM_EssarnCatch`
(catch), `RM_Sorruth` ↔ `RM_SorruthCatch`. Most entries have no such pair — e.g. the Grey's
`RUT_Sallik`, `RUT_Karrud`, `RUT_Hessal`, `RUT_Oomal`, `RUT_Maalu`, `RUT_Immu`, `RUT_Haarn`
exist only as items.

⚠️ Those seven are already written with real bodies and behaviour in their item
descriptions — a shell-less crab wearing its own excreted salt, a flat fish that gave up
swimming and grows a mineral plate, a bivalve whose shells are grown from the sea's crystal.
**The creature design is largely done inside the item text.** Read it before inventing.

## 🔴 blocked for the Propane Lake until a sibling item lands
`PROPANELAKE_ANIMALDENSITY_ZERO_1`: both Propane Lake defs leave `animalDensity` unset, so it
is `0f`, `AnimalEcosystemFull` is true from tick zero and **nothing spawns there at all**.
Authoring six more creatures for that sea before the field is fixed produces six more
creatures nobody will ever see.

## spec
Per sea, per catch entry without a living counterpart:
1. Decide **living counterpart** or **recorded catch-only reason**. Catch-only is a legitimate
   answer for something that is a harvested object rather than an animal — record WHY.
2. Author the `ThingDef` + `PawnKindDef` from the existing item description, not from scratch.
3. Wire into that sea's `<wildAnimals>` — ⚠️ shorthand form `<DefName>commonality</DefName>`,
   **no `<li>` wrapper**; `BiomeAnimalRecord`'s custom loader reads the node NAME as the animal
   and the node TEXT as the commonality, and an `<li>` silently discards the whole value.
4. Keep the `*Catch` pairing convention.
5. ⛔ Star Wars canon names route through the Utinni patch layer, never a `RM_` def.

## criteria
- [ ] Every catch entry in all four seas has a living counterpart or a written catch-only reason.
- [ ] Nothing authored for the Propane Lake until `PROPANELAKE_ANIMALDENSITY_ZERO_1` closes.
- [ ] Each new creature respects its sea's bans — the Grey is solitary-everything and nothing
      schools there; anything that schools belongs to the Twilight Deep.
- [ ] Rosters and the sea sheets updated to match.

## not in scope
- How a player reaches the floor. That is the ship, ruled 2026-09-26, and already built.
- Art. New creatures queue through artpipe separately.
