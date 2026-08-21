## spec
BUILD, 2026-08-20. Ten factions in the live world wear generated names; the
repair is filed as `FACTION_NAMES_ARE_GENERATED_1` in `queue/CHECK.md` and needs
no def change — clearing the stored name makes each fall through to its
`def.LabelCap`, which is already correct.
⇒ **The repair is settled. This item is only about RECURRENCE.**
`FACTION_SPEC.md:71` says `fixedName` is for *"only where the world must say a
specific name"* — a deliberate restraint, and BUILD is not overriding it
unilaterally. But the evidence is now in: **without `fixedName`, a newly
generated world names these factions at random**, and this one did.
THE QUESTION: does the restraint survive that? Two readings, both defensible:
  (a) **Add `fixedName` to all ten.** The campaign names these factions
      everywhere; a generated name is never wanted. Costs ten one-line patches.
  (b) **Leave the defs alone.** The world is generated ONCE and then frozen, so
      a repair-after-generation is sufficient and the restraint stands. Costs
      nothing now, and costs the same repair again if the world is ever rebuilt.
⚠️ `FACTION_SPEC.md:124` is relevant and easy to miss: *"Do NOT patch
`factionNameMaker` away — `fixedName` overrides it for the faction, and the namer
is still used for settlements."* So (a) is safe for settlement naming.
⚠️ One nuance either way: `def.LabelCap` capitalises, so `the Junkers` presents as
**"The Junkers"**. If the lower-case article is wanted, that faction needs an
explicit name regardless of which reading wins.

## verify
whichever is chosen, written into `FACTION_SPEC.md` beside the existing
`fixedName` line so the next reader is not left with the bare restraint.

## criteria
—

## notes
**Imported from `queue/DECIDE.md`. Its `state:` read, verbatim:**

ready — for DECIDE

## ruling
🔴 **DECIDE, 2026-08-21 — (a). Add `fixedName` to all eleven.** The restraint at
`FACTION_SPEC.md:71` does not survive the evidence, and the reason (b) offered — *"the world
is generated ONCE and then frozen"* — is the strongest argument **for** (a), not against it.

**Why the freeze cuts the other way.** A repair-after-generation is a manual step performed
by hand on the one world we ship. If it is skipped, mistimed, or done before the last
regenerate, **eleven factions carry random names into a frozen savegame and there is no
regenerate behind it.** (b) buys nothing and stakes the whole roster on somebody remembering
an unwritten step at the one moment it cannot be redone. (a) makes the correct name a
property of the def, where it cannot be forgotten.

⭐ **And "only where the world must say a specific name" is now satisfied for all eleven.**
That clause was written before the content existed. The world must say these names: they
are in twelve cast rosters, 294 character briefs, the settlement CSV, and every faith text.
There is no longer a faction on this planet whose name is free to vary.

**It also fixes the `LabelCap` nuance for free** — with `fixedName` the string is used
verbatim, so **`the Junkers`** stays lower-case instead of presenting as *"The Junkers"*.
Under (b) that faction needed a special case anyway, which makes (b) *"costs nothing"*
false.

### The eleven, and the exact string — no ambiguity to resolve

⚠️ **It is eleven, not ten.** Measured 2026-08-21: only `Empire` already carries
`fixedName` (`GalacticEmpire.xml:102`).

✅ **`fixedName` is the faction's `<label>`, verbatim** — and this is not a judgement call:
the `faction` column of `world/ASHKARR_WORLDMAP_settlements.csv` is already authored with a
display name for every one of the twelve, and **it agrees with every `<label>` exactly.**

| def | `fixedName` |
|---|---|
| `Jawa_AscendantHelix` | `Ascendant Helix` |
| `Jawa_DeepwaterCompact` | `Deepwater Compact` |
| `Jawa_FreeDroidEnclaves` | `Free Droid Enclaves` |
| `Jawa_GeonosianFoundryHive` | `Geonosian Foundry Hive` |
| `Jawa_HuttCartel` | `Hutt Cartel` |
| `Jawa_IndigenousTribes` | `Jawa Trade Moot` |
| `Jawa_Junkers` | ⭐ `the Junkers` — lower-case article, deliberately |
| `Jawa_WildsteamClan` | `Wildsteam Clan` |
| `OutlanderCivil` | `Homestead Defense League` |
| `TribeCivil` | `Deep Desert Tribes` |
| `Pirate` | `Blackstar Company` |

⛔ **Do not patch `factionNameMaker` away** (`FACTION_SPEC.md:124`) — `fixedName` overrides
it for the faction, and the namer is still what names the faction's SETTLEMENTS.
⛔ **`Mechanoid` is not on this list.** It is `hidden`, holds no settlement and is never
named to the player.

⇒ Filed as `FACTION_FIXEDNAME_ELEVEN_1` for BUILD. The live-world repair
(`FACTION_NAMES_ARE_GENERATED_1`, CHECK's) is unaffected and still wanted — this stops it
being needed a second time.
