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

## 🔴 RULED — TWO creatures, not one. Owner, 2026-09-23, by question card

A four-option card was offered. ⭐ **He took two of them**, and typed the second one's design into
the notes box. **Owner, verbatim (typed):**

> *"I select Vurrak and Illisk... Illisk should be a shoal of toothy fish (pirahnna essentially)
> that are crazy fast and nearly unkillable except with explosives."*

⇒ 🔴 **The Greentide gains TWO new creatures.** One vacated row becomes two — ⛔ do not treat this
as "pick one and the other is a fallback", and ⛔ do not preserve the old `0.15` as a fixed budget
to be split. Rosters are not fixed-sum.

### 1. ILLISK — a shoal of toothy fish (fully specified by him)

| property | ruled | note |
|---|---|---|
| form | **a shoal of toothy fish** — *"pirahnna essentially"* | 🔑 see the ban-2 note below |
| speed | **crazy fast** | direction ruled, number unset |
| durability | 🔴 **nearly unkillable EXCEPT with explosives** | the defining mechanic |

🔑 **This is the "changes the map, not a fight" option working as intended.** You cannot shoot a
shoal off a crossing — so a reach of water stops being a risk you accept and becomes terrain you
route around, until you spend explosives on it.

✅ **BAN 2 IS SATISFIED, and this needs saying because it looks like a violation.** §6 ban 2 reads
*"No vanilla-Earth fauna or flora … **terrestrial-analog shapes allowed, names are not**."* ⇒ A
piranha **shape** is explicitly permitted; only an Earth **name** is banned. "Illisk" is invented,
so the ban holds. ⛔ Do not "fix" this creature on a ban-2 reading, and ⛔ never let the word
*piranha* reach a def, label or description — it is his shorthand for the silhouette, not a name.

⚠️ **"Nearly unkillable except with explosives" is a direction, not an implementation.** The obvious
route is damage-type armour (high `ArmorRating_Sharp`/`ArmorRating_Blunt`, low or absent bomb
resistance), but whether that reads as *nearly unkillable* in play — and whether a shoal is **many
small pawns or one pawn** — is unset. 🔑 The two choices interact: explosives are the counter
precisely *because* they hit an area, which only matters if the shoal is genuinely many bodies.

### 2. VURRAK — the false bank (selected, not yet elaborated)

Selected as offered: **a silted ambusher that is indistinguishable from bank until weight lands on
it**, so the map's shoreline cannot be trusted. ⭐ It extends §6 ban 6 (*no safe standing water*)
onto the **shore**, which no other roster member does.

⚠️ **He added no detail beyond the selection**, so its silhouette, size and the disguise mechanism
are still open — and the card's own recorded risk stands: it must read as a **creature**, not as a
trap. ⛔ Do not build it as a terrain-trap ThingDef and call the creature delivered.

🔑 **The two chosen options compose rather than overlap**, which is why taking both works: the
Vurrak makes the **edge** of the water lethal, the Illisk makes the **body** of it impassable.
Together they close the water off from both directions without either being a boss silhouette that
competes with the Fever Wood's horror.

## open

- **Commonality for each of the two rows**, and whether both sit in the `lunger` band or the Illisk
  wants its own (a shoal is not a lunger in the §4 sense — it does not ambush, it denies).
- 🔴 **Is a shoal many pawns or one?** See above — the explosives counter depends on the answer.
- **How "nearly unkillable" is expressed** without making it feel unfair or bugged.
- **The Vurrak's silhouette and disguise mechanism**, and how it reads as animal rather than trap.
- ⚠️ **Impassable-water interaction with Odyssey**, flagged as a risk on the card and unresolved —
  Odyssey ships water content, and an effectively-walled river may fight it.
- **Tier**, per the Core-only tension above.

## verify

- [ ] The replacement's concept is owner-ruled, not agent-invented.
- [ ] `RUT_Greentide.xml` and `WildAnimals_Greentide.xml` agree on row count and sum after the add.
- [ ] The new row passes ban 2 (not Earth-nameable) and §4b (not fire-themed).
- [ ] A post-load def dump on the Desktop shows the new creature present and the dianoga absent.
