## spec
Finding and mechanism: `items/IMPERIAL_CAST_BINDING_1.md` `## ruling`.

**One question, answered once, for all 269 named characters:** when a named character's
authored race is not in their faction's `xenotypeSet`, which wins?

⭐ **51 of 269 are in that position** — every faction has some; the Junkers and Blackstar
have ten each.

🔴 **The engine does not leave this open, so a non-decision is a decision.** All our
`Jawa_*` pawn kinds carry `useFactionXenotypes: true`, and `PawnGenerator.cs`:
- `:1751` draws the xenotype **from the faction's set** at generation
- `:518` **rejects** any candidate pawn whose xenotype is not in that set

⇒ bind a named character to such a kind and their authored race is discarded or they simply
fail to generate. **Silently, both ways.**

### The answer the design already implies

`INHABITED_DESIGN.md` §4.2 has named people **drift between factions** — enslaved, escaped,
absorbed after a lost battle, sold by the player — and §4 redistributes them through the
displaced pool. ⇒ **a Muun in Imperial service is the setting working, not a defect**, and a
named character is an individual rather than a sample from a distribution.

**⇒ Proposed rule, for DECIDE to ratify or the owner to overturn:**
1. A named character's **authored race wins**. `CharacterApplier` forces the xenotype.
2. Named characters are **not** generated through a kind with `useFactionXenotypes: true`
   — either give `Inhabited` its own unconstrained kinds, or set that flag false on the
   kinds it uses. ⛔ Do not simply widen every faction's `xenotypeSet` to cover its cast:
   that would change what the faction's **anonymous** pawns look like, which is the owner's
   race/faction matrix and is not ours to edit.
3. `useFactionXenotypes` keeps governing anonymous fill, unchanged.

### ⏸️ Two things this item must NOT settle on its own

- ⚠️ **Two race strings are not species:** `savant caste` (an Imperial rank) and
  `labour-line` (a Helix vat caste). They need an authoring decision each, not a lookup.
- ⚠️ **`Inquisitor Vaunt` is "Sith"**, and four Sith xenotypes exist —
  `RimMandrakeSithZ` · `RimMandrakeSithKissaiPureblood` · `RimMandrakeSithMassassi` ·
  `OuterRim_Sith`. Which one is characterisation, not mapping.

## verify
- a written rule covering all 269, not one faction
- the 51 are enumerated by name with their mapped xenotype defName, each checked against the
  **2026-08-21 578-mod dump** ⚠️ *not* the 2026-08-15 one, which contains none of our races
  and will report every mapping as missing
- no faction's `xenotypeSet` was widened to make a named character fit

## criteria
A named character generates as the person who was written, in whatever faction currently
holds them.
