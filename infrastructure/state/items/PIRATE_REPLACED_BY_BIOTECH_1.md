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
