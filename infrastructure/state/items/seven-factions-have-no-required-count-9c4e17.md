## spec
🔴 **A scope call only DECIDE can make, and worldgen is the last chance to
make it.** Seven of the eight authored Jawa FactionDefs carry
`canMakeRandomly true` and **no `requiredCountAtGameStart`**, so they
arrive on the Configure Factions page at a default count of **0** and a
world generated without touching them contains none of them.
Measured, all 8 files in `src/Jawa/Jawa_Patches/Defs/FactionDefs/`:

| faction | defName | requiredCountAtGameStart | settlementGenerationWeight |
|---|---|---|---|
| Jawa Trade Moot | `Jawa_IndigenousTribes` | **1** (max 2) | 1.0 |
| Hutt Cartel | `Jawa_HuttCartel` | — (max 1) | 1.15 |
| the Junkers | `Jawa_Junkers` | — | 1.15 |
| Deepwater Compact | `Jawa_DeepwaterCompact` | — | 0.7 |
| Geonosian Foundry Hive | `Jawa_GeonosianFoundryHive` | — | 0.7 |
| Wildsteam Clan | `Jawa_WildsteamClan` | — | 0.6 |
| Ascendant Helix | `Jawa_AscendantHelix` | — | 0.45 |
| Free Droid Enclaves | `Jawa_FreeDroidEnclaves` | — | 0.45 |

🔴 **`EXPECTED_FAILURES` §2 S7 asserts the opposite** — "Seven are authored
defs with `requiredCountAtGameStart 1`, so they should be forced". That is
FALSE on disk and it is written into the file that gets read AT worldgen.
Corrected in place by BUILD 2026-08-15; recording it here because the
wrong belief may have travelled into other docs.
THE CHOICE: (a) add `requiredCountAtGameStart 1` to the seven, so the
campaign's own factions cannot be forgotten at the screen; or (b) leave
them optional and rely on the operator ticking each up by hand.
⚠️ **(b) is one distraction away from a world with no Hutts in it, and the
world is generated once — a faction absent at worldgen cannot be added
later.** BUILD recommends (a) and can implement it in minutes, offline.

## verify
—

## criteria
—

## notes
**from:** BUILD, 2026-08-15, measured on disk while the game was down

**Imported from `queue/DECIDE_ARCHIVE.md`. Its `state:` read, verbatim:**

✅ CLOSED 2026-08-19 — DECIDE's half is done twice over: ruled 2026-08-15, and on
2026-08-19 re-measured, found NEVER IMPLEMENTED, and filed to BUILD as
`seven-jawa-factions-still-default-to-zero-at-worldgen-4a71c8` with the exact seven
files. The measurement also found the Worldbuilder preset prefills the same page
from `factionCountsStrings` — recorded there. Nothing left here; BUILD holds it.
