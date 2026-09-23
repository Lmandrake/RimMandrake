# GREENTIDE_TERROR_REPLACEMENT_1 — something new and terrifying for the Greentide

## spec

**Owner, 2026-09-23, in conversation** (quoted from the chat turn; ⚠️ **not** recorded via
`--owner-said`, because the provenance guard refused the quote twice — so treat this as an
accurate transcript quote, not a ledger-stamped authorization):

> *"It's a mistake to have dianoga in the GreenTime. It belongs only in tank prisons and the
> Fever Wood. Create something new and terrifying for the Green Tide."*

⇒ The dianoga has been removed from the Greentide (executed 2026-09-23 — see *what was already
done* below), which leaves **one vacated slot at commonality 0.15 in the `lunger` band**. This
item fills it.

🔴 **Fill it with a NEW creature, never a neighbour's species.** CLAUDE.md fauna law, owner
2026-09-21: *"We have plenty of creatures left to fill rosters if there are holes."* ⛔ Do not
reach for an existing `RSW_`/`RM_` animal already homed in another biome to close the count.

## 🔴 the constraint that rules out most ideas

The Greentide is the **saturated-growth** biome, and its own roster records two standing
exclusions that a replacement must respect — both visible in `rosters/the_greentide.json`:

- ⛔ **No fire-themed fauna.** `AA_FireWasp` was evicted precisely for *"§4b fire is not the tool
  — fire-themed fauna contradicts the saturated-growth doctrine."*
- ⛔ **No Earth-nameable animal** (ban 2). `BMT_LandOctopus` was evicted as *"nameable on sight
  despite terrestrial form"*, and `BMT_SonarRabbit` for being a rabbit. 🔑 **This is the trap for a
  tentacled replacement** — an octopus-adjacent design fails ban 2 on sight, which is part of why
  the dianoga sat oddly here in the first place.
- ⚠️ **It must not be a second eldritch tentacled horror.** The Sekkulaath/dianoga is the Fever
  Wood's centrepiece; duplicating the silhouette here would spend that creature's distinctiveness.

## what the slot actually needs

| property | value | source |
|---|---|---|
| band | `lunger` | the vacated row's own band |
| commonality | 0.15 | the vacated row's weight; keeps the roster sum at 9.168 if matched |
| tier | ⚠️ **UNDECIDED** — see below | |

🔴 **Tier is a real decision, not a default.** The Greentide ships as a franchise-free `RM_` mod
whose own header commits it to a **Core-only** roster, with all franchise cast added by
`UtinniPatches/Patches/WildAnimals_Greentide.xml`. ⇒ An **invented** exotic name may live in the
`RM_` tier and be cast inline (CLAUDE.md Q11a: *"Star Wars style naming is NOT Star Wars IP"*), but
`RM_Greentide`'s Core-only promise means it would still be cast through the patch layer unless that
promise is revisited. Resolve before authoring defs.

## ✅ what was already done, 2026-09-23 — do not redo

The de-wire is **complete and verified**; only the replacement creature is owed.

- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Greentide.xml` — dianoga row removed. 🔑 **This
  is the roster the live world runs on**, so this removal is the one that changes the planet.
- `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Greentide.xml` — `RSW_Dianoga` row removed, and
  the header's stale numbers corrected in the same pass (27→26 rows, 9.318→9.168 sum, 22→21 donor
  bare-name rows, and the "confirm all 27 rows" verification note).
- ✅ **MEASURED after the edit:** both files carry **26 rows summing to 9.168**, and the dianoga is
  absent from both. Parsed, not grepped.
- `rosters/the_greentide.json` — the row's disposition moved from `move:AB_MiasmicMangrove` to
  `move:the_fever_wood`, with the supersession recorded.
- `rosters/the_miasma.json` — the dianoga `import` row **removed**. ⚠️ It had to be removed rather
  than relabelled, because `review/rosters_residency.py` counts residency from a row's *presence*,
  regardless of its `action` value.

⚠️ **UNVERIFIED AGAINST A LOAD.** Authored on the Mac laptop — no def dump, no game. Confirm on the
Desktop that the Greentide resolves 26 rows and that the dianoga is absent; that absence is this
ruling's live test.

## 🔴 flagged for the owner — a decision of his was retired

The Miasma placement was **his own** earlier review decision, recorded on the row as: *"would be
awesome if we could add tentacle pulling capabilities like the lasso power or future sarlacc mod,
put it in the maiasma."*

🔑 **That intent is now delivered where he wants the creature instead** —
`FEVERWOOD_TENTACLE_BESTIARY_1`'s **snare** limb *grabs and drags*, which is exactly the
tentacle-pulling he was reaching for. So the wish is satisfied by the Fever Wood rather than
abandoned. ⇒ Recorded openly for his veto; the removal was executed on the strength of *"it belongs
only in tank prisons and the Fever Wood"*, which covers the Miasma explicitly.

## open

- 🔴 **The creature itself** — concept, name, silhouette, and what makes it terrifying in a
  saturated-growth jungle without being fire-themed, Earth-nameable, or a second tentacled horror.
  ⛔ Not to be invented unilaterally; the owner refines options rather than receiving one.
- **Tier**, per the Core-only tension above.
- Whether it inherits the vacated `0.15` weight exactly, or the band wants rebalancing once the
  concept exists.

## verify

- [ ] The replacement's concept is owner-ruled, not agent-invented.
- [ ] `RUT_Greentide.xml` and `WildAnimals_Greentide.xml` agree on row count and sum after the add.
- [ ] The new row passes ban 2 (not Earth-nameable) and §4b (not fire-themed).
- [ ] A post-load def dump on the Desktop shows the new creature present and the dianoga absent.
