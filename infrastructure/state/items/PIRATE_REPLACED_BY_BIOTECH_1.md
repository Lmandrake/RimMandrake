## spec
BUILD, 2026-08-20, read out of the 1.6 decompile and the 578 dump.
`BlackstarCompany.xml` reskins vanilla **`Pirate`** and does it correctly — label
`Blackstar Company`, weight 0.6, settlement art present. But
`FactionGenerator.InitializeFactions` **skips a def when another required def
replaces it**, and **Biotech's `PirateWaster` declares `replacesFaction: Pirate`
with `requiredCountAtGameStart: 1`**. ⇒ vanilla `Pirate` is never generated while
Biotech is active, so the faction the campaign built cannot exist by worldgen.
⚠️ Creating the faction by hand fixes THIS world. It does not fix the next one,
and this planet is meant to be built once and frozen — so "the next one" may
genuinely never happen, which is a legitimate reason to do nothing here.
THE CHOICE:
  (a) **Do nothing to the defs.** Create `Pirate` by hand in this world and
      accept that a regenerate would lose it again. Cheapest, and consistent with
      "the world is authored once".
  (b) **Patch `PirateWaster.replacesFaction` away** so vanilla `Pirate` generates
      normally. ⚠️ Then BOTH may generate — waster pirates AND Blackstar — which
      may be wanted (two pirate flavours) or may not.
  (c) **Move the reskin to `PirateWaster`** instead of `Pirate`, so the campaign
      rides the def Biotech actually generates. ⚠️ Its pawn kinds are wasters,
      which is a strong flavour and probably contradicts a contractual mercenary
      company.
🔑 **Whatever is chosen, the same trap applies to every vanilla faction we
reskin.** Six defs in this build declare `replacesFaction`, three of them at
`OutlanderRough` — and `OutlanderCivil`/`TribeCivil` carry two of our factions.
⚠️ **Those two are NOT affected** — checked: nothing declares `replacesFaction`
at `OutlanderCivil` or `TribeCivil`. Only `Pirate` is hit.

## verify
after the ruling, the live world contains a faction whose label reads
`Blackstar Company`, and the settlement import lands all 72 rows.

## criteria
—

## notes
**Imported from `queue/DECIDE.md`. Its `state:` read, verbatim:**

ready — for DECIDE

## ruling
🔴 **DECIDE, 2026-08-21 — (b), with one addition that removes its objection.**

**First, the mechanism is one step milder than this item states, and the difference
matters.** Read from the 1.6 source, not inferred:

- `FactionGenerator.cs:78` skips `Pirate` **only in the branch where no faction list was
  configured** (`InitializeFactions(layer, null)`). Worldgen normally passes
  `Current.CreatingWorld.info.factions` (`WorldGenStep_Factions.cs:11`), and that branch
  adds every def in the list with no skip test at all.
- The operative loss is `Page_CreateWorldParams.cs:83-85`, which strips `Pirate` from the
  **default** faction list on the Configure Factions screen.
- `Pirate` keeps `maxConfigurableAtWorldCreation 9999`, so it stays in
  `FactionGenerator.ConfigurableFactions` and **the owner CAN add it back by hand.**

⇒ ⛔ **"Vanilla `Pirate` can never be generated" is too strong** — it is *dropped from the
default list*, silently. Do not build a bridge workaround for an impossibility that is not
one. ✅ But on a planet that is built **once and frozen**, a faction that survives only if
the owner remembers an unwritten step is a faction we will lose. One patch removes the
dependency on his memory, and that is the whole argument for acting.

**(a) is rejected** for that reason. **(c) is rejected** — waster pawn kinds contradict a
contractual mercenary company, and `BlackstarCompany.xml` already reskins `Pirate`
correctly.

**⭐ (b) plus the second op.** This item's objection to (b) was *"then BOTH may generate"*.
That objection is answered by also zeroing `PirateWaster`'s inherited
`requiredCountAtGameStart`:

- `PirateWaster` does not declare the field; it inherits **1** from `PirateBandBase`
  (`Core/Defs/FactionDefs/Factions_Misc.xml:518`). ⚠️ `OnlyOurFactions.xml:980-1005`
  zeroes its `startingCountAtWorldCreation` and `maxConfigurableAtWorldCreation` and
  **not** this one, which is exactly why the slate does not already save us.
- With `replacesFaction` removed and `requiredCountAtGameStart` 0: `Pirate` returns to the
  default list and generates; `PirateWaster` is neither required nor configurable and
  stays off the map.

⇒ Filed as `PIRATE_VESSEL_RESTORED_1` for BUILD.
