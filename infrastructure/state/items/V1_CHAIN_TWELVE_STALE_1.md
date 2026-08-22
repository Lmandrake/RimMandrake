## spec
REP swept `infrastructure/state/V1_CHAIN.md` on 2026-08-22 with a subagent: **57 assertions
verified true, 12 wrong.** The file argues the v1 dependency chain, so a wrong link in it
routes work that does not need doing.

⚠️ **Subagent findings, not REP measurements — verify each before editing.**

**Arguing from work that is finished**
| line | says | actually |
|---|---|---|
| 121-123 | `B53`'s 48 pawn kinds blocked, tags cannot be invented | `B53` is **done**, `6b454a6` |
| 102, 216-218 | "48 proposed, 0 literal defNames. 19 ship, none matching" | `JawaFactionRoster.xml` ships **49 literal** PawnKindDef defNames — that is what B53 closed on |
| 226 | "not one faction has a defName" | **8 FactionDefs ship with defNames** (AscendantHelix, DeepwaterCompact, FreeDroidEnclaves, GeonosianFoundryHive, HuttCartel, IndigenousTribes, Junkers, WildsteamClan) |
| 322 (R12) | "The Junkers still lose theirs — BUILD `B9` stands" | `B9` was never filed; it lives at `design/V2_DREAMS.md:92`, parked to v2 |

**Counts that do not reproduce**
| line | says | actually |
|---|---|---|
| 11 | "(`refmatch.py` stays cancelled)" | **v2, deferred not cancelled** — `436bf693`, later than this banner |
| 95 | "578 live vs 575 freeze (8 added, 5 removed)" | both totals right, the delta is **11 added / 8 removed** |
| 104 vs 273, 348 | row 9 "5 reskins", R7/R14 "6 reskins" | disk has **5** reskin patches. R7's sixth — the Unbound Hive / `Insect` — has **no patch file at all** |
| 210-211 | "All eleven carry `ideoName` and are deployed" | **12** files carry it (8 FactionDefs + 4 patches); `ForgottenArsenal.xml` carries none. 11 is neither count |
| 96, 161 | "1,308 keys live" in Cherry Picker | **1,342** `<li>`, and the freeze copy is identical |
| 45-46, 51 | "`V1.md` is the eight-row scoreboard / v1 = the 8 rows" | `V1.md` carries **14 rows (0-13)** — the same set this file's own chain table lists |

**IDs that point at nothing**
`B25a` (line 190, "load order not pinned, still open") was never filed and appears in no queue.
`C24` (243-244, gating R1) was never filed — it is `design/V2_DREAMS.md:283`, and `:778` reuses
the same ID for something unrelated.

**UNMEASURED**, do not round to a number: line 186's "624 installed-but-inactive mods" matches
nothing — the workshop tree holds 1,254 content dirs against 578 active, and `ls`-counting dirs
is not a mod census.

**In flux, flag don't fix:** line 105's 21,872 authored tiles agrees with
`ASHKARR_WORLD_DEFINITION.md`, but the owner is remaking the planet by hand, so every
tile-derived number here will move.

## verify
Each row re-checked against the ledger (`rimflow show <ID>`) or disk before editing. Numbers off
a large artifact come from `measure` or stay UNMEASURED.

## criteria
No link in the chain rests on a closed item, a never-filed ID, or a count that does not reproduce.

## Watch out
🪤 Four of the twelve are IDs from the retired `B*`/`C*` scheme that were **never filed at all**.
Do not "close" them — there is nothing to close. Say in the file that they were never items.
