# CANONICAL_SAVE_MODLIST_DIVERGENCE_1 — scrub 5 retired packageIds from the save's `<meta>` mod list

Item: `CANONICAL_SAVE_MODLIST_DIVERGENCE_1`. Date: 2026-09-19 (FOUNDRY, offline, no bridge).
Owner authorization: **"Yes, scrub it now"**.
Target: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\CANONICAL_ASHKARR_START_2026-09-12.rws`

## Backup

`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\CANONICAL_ASHKARR_START_2026-09-12.rws.bak-pre-modlist-scrub-20260919`

| file | bytes | sha256 |
|---|---|---|
| original (pre-edit) | 17,590,355 | `220703b4f454023d904bc48ab183d77cce9a5177185502c5839933ae6ec4e735` |
| backup | 17,590,355 | `220703b4f454023d904bc48ab183d77cce9a5177185502c5839933ae6ec4e735` |
| installed (post-edit) | 17,589,878 | `e750f98b6b81ddac52a8453860a7c1ba764faaf9b0c707fd90fe61819f59662e` |

Byte-identical backup (`cp -p`). Naming follows the existing `.rws.bak-pre-<what>-<date>`
convention already in that folder.

⛔ **The save itself is NOT in this repo and must not be committed** —
`.gitignore:157` ignores `*.rws` globally, with only two `world/` exceptions.
That is a standing decision, not an oversight. The edited file lives at the
Windows path above; the backup beside it is the undo.

## Format (MEASURED, not assumed)

`<meta>` holds exactly three parallel lists, **635 `<li>` each**, one `<li>` per
line, CRLF throughout:

| list | line range (0-based) | entries |
|---|---|---|
| `<modIds>` | 5–639 | 635 |
| `<modSteamIds>` | 642–1276 | 635 |
| `<modNames>` | 1279–1913 | 635 |

`modSteamIds` is `0` for 628 of 635 entries (7 real Steam ids), so it carries
almost no distinguishing information — index alignment is therefore verified
positionally, never by value matching. No duplicate packageId in `modIds`.

## What was removed

Indices resolved **once**, from `modIds`, and the same indices applied to all
three lists — that is what keeps them aligned.

| index | packageId | steamId | name |
|---|---|---|---|
| 429 | `als.gravtech` | 0 | GravTech |
| 450 | `petetimessix.researchreinvented.steppingstones` | 0 | Research Reinvented: Stepping Stones |
| 478 | `biomesteam.biomespollutedlands` | 0 | Biomes! Polluted Lands |
| 484 | `als.gravtech.bc` | 0 | GravTech - Big cannons |
| 501 | `halituisamaricanous.gravtechbigcannons` | 0 | GravTech - Big cannons Retextured |

15 whole lines removed (5 × 3 lists), 477 bytes. Raw byte edit, CRLF preserved,
no XML re-serialisation. Script:
`Transient/canonical_save_modlist_scrub_2026-09-19_scrub.py` (refuses to write in
place; asserts list lengths before and after, one-line `<li>` shape on every
entry, exactly one match per target, and per-survivor triple alignment).

**`diff` original vs edited: 15 deletions, 0 additions, 0 modifications.** All 15
inside the three `<meta>` lists.

Post-edit: all three lists = **630**; positional element-wise comparison against
`source minus {429,450,478,484,501}` matches for all three lists; whole-file
`ElementTree` parse succeeds.

## Verification (offline)

Reference dumps:
- **current list** — `DefDump/captures/2026-09-19T04-19-13Z`, `modCount` 622, all 5 packageIds absent. Has `defs/`.
- **donor reference** — `DefDump/captures/2026-08-29T13-30-02Z`, `modCount` 584, all 5 packageIds present.
- (`2026-09-19T02-35-03Z`, 621 mods, is unusable — it has no `defs/` directory.)

### 1. The scrub introduced nothing. This is the load-bearing result.

The 5 retired mods owned **678** defs in the 584-mod dump (630 distinct
defNames); **583** of those names are absent from the current 622-mod dump.
Scanning for all 583 as element values (`>NAME<`), before and after the edit:

| | names occurring | element-value hits | as `<def>NAME</def>` Thing refs | `<def>` hits |
|---|---|---|---|---|
| before scrub | 388 | 1,500 | 3 | 5 |
| after scrub | 388 | 1,500 | 3 | 5 |

**Identical.** The edit removes no data and changes no def's availability, so it
cannot create a cross-reference error — measured, not assumed.

Controls in the same run: `>Steel<` 916, `>Human<` 860, `>ZZZ_NoSuchDefName_ZZZ<` 0.

### 2. Map grids resolve clean against the current 622-mod dump

`rimbench/savemap.py`, identical before and after:

| grid | distinct | cells | unresolved |
|---|---|---|---|
| terrain (`topGridDeflate`) | 11 | 62,500 | **0** |
| under | 4 | 62,500 | 1 — `hash:0` × 51,929 = "nothing buried" |
| roof | 4 | 62,500 | 1 — `hash:0` × 55,158 = "no roof" |

`roundtrip_check`: `lossless: True`, 62,500/62,500 cells. `fogGrid` untouched by
construction.

### 3. Pre-existing residue — NOT introduced here, and a meta edit cannot fix it

Of the 1,500 element-value hits, only **5** are actual `<def>` Thing instance
references, to 3 donor defNames, and **every one is on a world pawn** (off-map —
no live colonist, no map thing, no caravan):

| defName | owner | count | where |
|---|---|---|---|
| `RR_Weapon_Torch` | Stepping Stones | 3 | 1 × `worldPawns/pawnsDead/li/inventory`, 2 × `worldPawns/pawnsDead/li/equipment` |
| `BMT_BufoBile` | Polluted Lands | 1 | `worldPawns/pawnsAlive/li/inventory` |
| `BMT_Toxwood` | Polluted Lands | 1 | `worldPawns/pawnsDead/li/inventory` |

The remaining ~1,495 hits are registry / dictionary / filter entries — VTE
`priceHistoryRecorders` keys and values, ThingFilter `allowedDefs`, tale and
battle-log def refs — the same classes `CANONICAL_SAVE_CAVERNS_SCRUB_1`
enumerated for Caverns. They will produce Scribe `Could not load reference to`
lines on load and the Thing is dropped; none is on anything alive on a map.
**This is route-2's data half and is owed separately; it is not part of this
scrub and it existed identically before it.**

⚠️ **Limit of this measurement**: donor ownership comes from the 584-mod dump of
**2026-08-29**, which predates the save (2026-09-12). A def one of the 5 mods
gained between those dates is invisible to this comparison. There is no dump of
the save's own 635-mod set.

## 🔴 The save still will not pass the compat gate

The 5 scrubbed entries were never the whole divergence. Re-measured against the
live `ModsConfig.xml` (620 active at time of writing) **after** the scrub:
**14 `modIds` entries remain that the live list lacks.**

| packageId | class | on disk? |
|---|---|---|
| `biomesteam.biomescaverns` | deliberately cut 2026-09-18 | yes (workshop `2969748433`) |
| `mandrake.rut.puffmiteartoverride` | deliberately retired 2026-09-18 | — |
| `mandrake.rut.kroffaartoverride` | same | — |
| `mandrake.rut.aaroxisdendoriaartoverride` | same | — |
| `mandrake.rut.bloodletterpetrelartoverride` | same | — |
| `mandrake.rut.bovinebeetleartoverride` | same | — |
| `mandrake.rut.cresteddragonartoverride` | same | — |
| `mandrake.rut.foundrybeetleartoverride` | same | — |
| `mandrake.rut.fungalmantisartoverride` | same | — |
| `mandrake.rut.jamelartoverride` | same | — |
| `mandrake.rut.screecherartoverride` | same | — |
| `badoaks.meatonastick` | 🔴 **untraced** — not in the item's 16 | yes (workshop `3435027361`, `3577333297`) |
| `badoaks.meatonastick.expansion` | 🔴 **untraced** | **NOT on disk** |
| `guy762.mm.kotorcore` | 🔴 **untraced** (Star Wars KotOR Resources and Materials) | yes (workshop `3254370945`) |

The item recorded 16 absences; the real set is **19** (16 + these 3). The three
new ones have no recorded retirement and are not the class the owner ruled on —
they need tracing, and `badoaks.meatonastick.expansion` is not installed at all,
so restoring it is a Steam action, not a ModsConfig edit.

## Owed to whoever next has the bridge

**Not done, deliberately** — another FOUNDRY agent holds the bridge this wave:
load `CANONICAL_ASHKARR_START_2026-09-12.rws` and confirm RimWorld itself
accepts it. Expect it **still to be refused** on the 14 above unless the
Caverns/ArtOverride route is settled first. When it does load, harvest
`Player.log` for `Could not load reference to` and expect the 5 world-pawn
Things above to be dropped.

⛔ Do not force-load to "just check" — and if a load happens, back up the Saves
folder keepers first; an autosave over this file is the one irreversible move.
