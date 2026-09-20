# CANONICAL_SAVE_MODLIST_DIVERGENCE_1

The canonical campaign save cannot be loaded on the live mod list. This is not a
"one retired mod disarms some pawns" regression — the save's recorded mod list and
the live list have diverged, so RimWorld's own compatibility check refuses the
load before any def resolution happens.

🔴 **5 of the divergences are SCRUBBED as of 2026-09-19** on the owner's
*"Yes, scrub it now"* — see **"Scrub applied"** below. **14 remain, so the save is
still refused.** Every count in "Measured" below is the PRE-scrub state.

## Measured

RE-MEASURED 2026-09-20 by BENCH, superseding the 2026-09-19 pass. Both lists parsed
with `ElementTree` — the save by streaming `iterparse` and stopping at `</meta>`, so
the 17.6 MB body is never loaded. ⛔ Never `grep -c '<li>'` either file.

- `CANONICAL_ASHKARR_START_2026-09-12.rws` — `<meta><modIds>`: **630** entries.
- Live `activeMods`: **617** entries. ⚠️ This file describes the NEXT load and other
  windows rewrite it, so the count is a moment; the absence **set** is the durable
  finding.
- **18 mods the save needs and the live list lacks** — not the 14 this item
  previously recorded. Four more `*ArtOverride` retirements landed after that pass:
  `barbslinger`, `boomsnake`, `firewasp`, `razorjack`.
- 5 mods live but not in the save (harmless — a save loads fine with extras).

### 🔴 14 of the 18 CANNOT be restored, because they are not on disk

This is the finding that changes his decision, and the previous pass did not have it.

| group | count | on disk? | restorable by a ModsConfig edit? |
|---|---|---|---|
| `mandrake.rut.*artoverride` (the retirement wave) | **14** | 🔴 **no folder exists** | ⛔ **no — nothing to activate** |
| `biomesteam.biomescaverns` | 1 | yes, workshop `2969748433` | ✅ yes |
| `badoaks.meatonastick` | 1 | yes, workshop `3435027361` | ✅ yes |
| `badoaks.meatonastick.expansion` | 1 | yes, workshop `3577333297` | ✅ yes |
| `guy762.mm.kotorcore` | 1 | yes, workshop `3254370945` | ✅ yes |

The 14 are: `puffmite`, `kroffa`, `aaroxisdendoria`, `barbslinger`,
`bloodletterpetrel`, `boomsnake`, `bovinebeetle`, `cresteddragon`, `firewasp`,
`foundrybeetle`, `fungalmantis`, `jamel`, `razorjack`, `screecher`. They were
**rehomed into SWBestiary and their folders deleted** (`3f891c5c7`,
`CAVERNS_ARTOVERRIDE_REHOME_1`) — the art survives, the mods do not. 47 other
`*ArtOverride` folders are still on disk, so this is a targeted retirement, not a
wholesale one.

⇒ **Route 1 (restore) does not exist for 14 of the 18.** For those, only scrub-and-
re-mint or force-load are available. Route 1 is a live option only for Caverns, the
two Meat on a Stick mods and KotOR Resources.

### Corrections to the previous pass

- ⛔ **"`badoaks.meatonastick.expansion` is NOT on disk — restoring it is a Steam
  action" is FALSE.** It is installed at workshop `3577333297`. All four non-
  ArtOverride absences are ordinary ModsConfig edits; none needs Steam.
- The ArtOverride count was 10; it is **14**.
- The live count was 621; it is **617**.
- The live-but-not-in-save count was 2; it is **5**.

## Why this needs the owner, not a seat

The two precedents in this exact class were both resolved by **restoring** the
retired mod: `DOORSEXPANDED_SAVE_COMPAT_REGRESSION_1` and
`DROID_DONOR_SAVE_COMPAT_REGRESSION_1` (both closed, both "mod restored, real fix
still owed"). That remedy **contradicts** the two deliberate cuts here — Caverns
was retired on purpose, and the 10 ArtOverride mods were retired on purpose the
same day. A seat restoring them would silently revert two decisions.

He picked **route 2 for the 5 ported-then-cut mods** (*"Yes, scrub it now"*,
2026-09-19) and that is applied. The route for the remaining **14** — Caverns, the
10 ArtOverrides, and the 3 untraced — is still his:

1. **Restore** — available for only **4** of the 18: Caverns, the two Meat on a
   Stick mods and KotOR Resources. All four are on disk, so all four are ordinary
   ModsConfig writes (expensive list, his call). ⛔ **Not available for the 14
   ArtOverrides at all** — their folders were deleted when they were rehomed into
   SWBestiary, so there is nothing to activate. Whatever he picks, the 14 need
   route 2 or route 3.
2. **Scrub and re-mint** the canonical save against the current list. The `<meta>`
   half is cheap (the 5-mod scrub took 15 lines and 477 bytes). The DATA half is
   much larger: `CANONICAL_SAVE_CAVERNS_SCRUB_1`'s own finding MEASURED **3,279
   refs to 575 Caverns defNames still in the save** after the `BMT_CaveSpiderHead`
   scrub, of which 2 are the NRE-risk class (`<stuff>` on worn apparel of two
   mothballed colonists). ✅ **The grids are no longer UNMEASURED** — see
   "Scrub applied": terrain resolves 62,500/62,500 cells with 0 unresolved against
   the current 622-mod dump, so no grid scrub is owed.
3. **Accept a force-load** with compatibility ignored, once, and see what breaks.
   Nobody has ever loaded this save without Caverns, so the blast radius is
   genuinely unknown — which is why no seat has done it unasked.

## Watch out

- ⛔ **Do not force-load to "just check"** — the save is the frozen world and the
  ship-claim campaign; a load that half-resolves and then autosaves over itself is
  the one irreversible move here. Back the Saves folder's keepers up first
  (`rimworld-savegame`).
- 🔴 **`ModsConfig.xml` describes the next load, never the running process.** A
  live game can be running a mod set that no longer matches this file, so
  "the live list has 621" is not a claim about what is loaded right now.
- This gates **every** live verify that needs the real Ash'karr campaign, not just
  one item: `VAULT_THAW_QUEST_FAMILY_1` (V1/V6's fixed siteTiles are Ash'karr tile
  ids and are meaningless on any other world) and `RIVER_STEAM_ANIMATION_1` (needs
  a real Pyrelands river tile). Both are blocked on this.
- The 3 GravTech mods, SteppingStones and PollutedLands were once flagged
  "unexplained" here and on `CANONICAL_SAVE_CAVERNS_SCRUB_1`. **They are traced and
  scrubbed** — see the two sections below. The open untraced absences are the three
  *new* rows in the table: `badoaks.meatonastick`,
  `badoaks.meatonastick.expansion`, `guy762.mm.kotorcore`.

## The 5 once-unexplained absences, traced (FOUNDRY, offline forensics, 2026-09-19)

All 5 are **deliberate, owner-authorized, and recorded** — the "unexplained"
framing above was itself stale, written before (or without checking) the
commits that explain them. None looks accidental or like a side-effect of an
unrelated edit.

**`als.gravtech`, `als.gravtech.bc`, `petetimessix.researchreinvented.steppingstones`
— DELIBERATE.** Owner card 2026-09-18T20:05Z on `RESEARCH_TRIO_RETIRE_1`:
*"Port all 17, then cut"* (superseding an earlier same-day "port the 4 ruled"
card). Executed same day, commit `59944939f` (hash back-filled in
`7d94e1219`), backed up first to
`infrastructure/state/modlists/ModsConfig.PRESWAP.20260918_204447_pre_research_trio_retirement.xml`.
All 18 owned `ResearchProjectDef`s (17 ruled + `GravEngineBuild`, a gap found
mid-pass) ported natively with **identical defNames**
(`RUT_Ported_ResearchTrio.xml`, `RUT_Ported_GravForge.xml`) so every existing
cross-reference keeps resolving with zero repointing. All 3 recorded in
`infrastructure/state/facts/retired_mods.json` with full rationale.
`RESEARCH_TRIO_RETIRE_1` is deliberately left `status=doing`, not because the
cut is undecided but because one closure criterion
(`research_manifest_validate.py --inventory` recost re-check) needs a fresh
def dump from a live restart, per its own 2026-09-18T20:54Z note.

**`halituisamaricanous.gravtechbigcannons` — DELIBERATE**, same commit
`59944939f`, as a derived consequence: a pure retexture with a hard
`modDependencies` on `als.gravtech.bc` and zero own content
(`stat_normalization_audit_2026-09-09.md` §2D). Retiring `gravtech.bc` alone
would have left a load-breaking hard dependency, so this rode along in the
same change — a real finding from the item's original 2026-09-11 diligence
sweep, unactioned until the 09-18 execution. Recorded in `retired_mods.json`.

**`biomesteam.biomespollutedlands` — DELIBERATE**, separate item
`POLLUTED_LANDS_FLORA_PORT_1` (owner-authored spec 2026-09-18T20:33Z, closed
by FOUNDRY at `e4ab343f3`, 2026-09-19T02:21Z). The spec named removing this
mod as step 2's explicit endpoint: *"...and biomesteam.biomespollutedlands
leaves ModsConfig."* 18 of its 21 unmapped `BMT_` flora rows were confirmed
true donor-owned plants (via live def dump `packageId`, not the
`plant_pool.csv` label); 5 were ported natively as `RUT_` `ThingDef`s with
real donor art carried over (`RUT_TwistingThornwood`, `RUT_TreeMartyr`,
`RUT_TwistingThorngrass`, `RUT_TwistingThornweed`, `RUT_ScorchedStars`), the
other 13 toxic-filler rows cut at the `biome_flora.py` source as accepted
loss (redundant with non-donor plants already in those rosters). Confirmed
via `git show e4ab343f3 -- infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`:
the diff removes exactly the `<li>biomesteam.biomespollutedlands</li>` entry.
Live-verified via bridge on a 29-mod list before the cut landed.
⚠️ **Gap**: unlike the trio, this packageId was never added to
`infrastructure/state/facts/retired_mods.json` (checked — absent). The
removal is fully documented in the commit and the closed item, so it isn't
actually unexplained, but the cross-ref exclusion list is incomplete and
worth a one-line fix.

**Timeline correction**: the claim above that "there is no snapshot named for
their retirement, unlike Caverns and the ArtOverrides" is wrong for the
research trio —
`ModsConfig.PRESWAP.20260918_204447_pre_research_trio_retirement.xml` is
exactly that snapshot, same naming convention as
`ModsConfig_before_caverns_cut_2026-09-18.xml`. UTC-normalized snapshot
diffing places the trio+retexture's departure between that 20:44 UTC
snapshot (still has all 4) and the 22:16 UTC `before_caverns_cut` snapshot
(already lacks all 4, still has PollutedLands); PollutedLands itself departs
between `before_caverns_cut` (22:16 UTC Sep 18) and `before_artoverride_retire`
(01:04 UTC Sep 19).

Live-checked 2026-09-19 (offline file read of the Windows `ModsConfig.xml`,
not a bridge call): all 5 packageIds confirmed absent, 620 active mods.

**Bearing on the 3-route decision above**: 4 of these 5 were deliberately
*ported-then-cut* — their content already lives on natively under new/same
defNames. "Restore" (route 1) would re-import mods whose content is now
duplicated, risking defName collisions with the ported defs (the exact "Port
trap" `RESEARCH_TRIO_RETIRE_1`'s own ruling warned about, run in reverse).
These 5 are **not** the same class as the Caverns/ArtOverride restore
question — for these 5, "scrub and re-mint the canonical save" (route 2) is
the fit, not "restore."

## Scrub applied — the 5 ported-then-cut mods (FOUNDRY, offline, 2026-09-19)

Owner authorization: **"Yes, scrub it now"**. Full report:
`Transient/canonical_save_modlist_scrub_2026-09-19.md`; script
`Transient/canonical_save_modlist_scrub_2026-09-19_scrub.py`; commit `32f1d34c2`.

**Backup** (byte-identical, `cp -p`):
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\CANONICAL_ASHKARR_START_2026-09-12.rws.bak-pre-modlist-scrub-20260919`
— 17,590,355 bytes, sha256 `220703b4f454023d904bc48ab183d77cce9a5177185502c5839933ae6ec4e735`.
Edited file: 17,589,878 bytes, sha256 `e750f98b6b81ddac52a8453860a7c1ba764faaf9b0c707fd90fe61819f59662e`.

⛔ **The `.rws` is not in this repo and must not be committed** — `.gitignore:157`
ignores `*.rws` globally, with only two `world/` exceptions. That is a standing
decision. The backup beside the save is the undo.

**What changed.** `<meta>` holds exactly three parallel lists, one `<li>` per line,
CRLF: `modIds` (lines 5–639), `modSteamIds` (642–1276), `modNames` (1279–1913),
635 each. Removed 15 whole lines — one from each list at indices **429**
`als.gravtech`, **450** `petetimessix.researchreinvented.steppingstones`, **478**
`biomesteam.biomespollutedlands`, **484** `als.gravtech.bc`, **501**
`halituisamaricanous.gravtechbigcannons`. All three lists 635 → **630**. Raw byte
edit, no XML re-serialisation; `diff` = **15 deletions, 0 additions, 0
modifications**.

🔑 **Alignment was verified POSITIONALLY, not by value.** `modSteamIds` is `0` for
628 of 635 entries, so matching values proves nothing; the indices were resolved
once from `modIds` and applied to all three lists, then the written file's three
lists were compared element-wise against `source minus {429,450,478,484,501}`.
All 630 survivors match in all three lists. Whole-file `ElementTree` parse OK.

**Verification — the edit introduced nothing.** Reference: dump
`DefDump/captures/2026-09-19T04-19-13Z`, `modCount` **622**, all 5 packageIds
absent (the 621-mod `2026-09-19T02-35-03Z` capture is unusable — no `defs/`).
The 5 mods owned 678 defs / 630 distinct defNames in the 584-mod
`2026-08-29T13-30-02Z` dump; 583 of those names are absent from the 622-mod dump.
Scanning for all 583, **before and after the edit: 388 names occur, 1,500
element-value hits, 3 as `<def>NAME</def>` Thing refs, 5 hits — identical.**
Controls in the same run: `>Steel<` 916, `>Human<` 860, `>ZZZ_NoSuchDefName_ZZZ<` 0.
A `<meta>` edit removes no data and changes no def's availability, so it cannot
create a cross-reference error — now measured, not assumed.

**Grids** (`rimbench/savemap.py`, identical before and after; `fogGrid` untouched
by construction): terrain 11 distinct defs / 62,500 cells / **0 unresolved**;
`under` and `roof` each carry one pseudo-entry `hash:0` (51,929 and 55,158 cells)
which means "nothing buried" / "no roof". `roundtrip_check`: `lossless: True`.

**Pre-existing residue, NOT introduced here and not fixable by a `<meta>` edit.**
Of the 1,500 hits only **5** are real `<def>` Thing instance references, to 3
donor defNames, and **every one is on a world pawn** — no live colonist, no map
thing, no caravan:

| defName | owner | count | where |
|---|---|---|---|
| `RR_Weapon_Torch` | Stepping Stones | 3 | 1 × `worldPawns/pawnsDead/li/inventory`, 2 × `worldPawns/pawnsDead/li/equipment` |
| `BMT_BufoBile` | Polluted Lands | 1 | `worldPawns/pawnsAlive/li/inventory` |
| `BMT_Toxwood` | Polluted Lands | 1 | `worldPawns/pawnsDead/li/inventory` |

The other ~1,495 are registry / dictionary / filter entries — VTE
`priceHistoryRecorders` keys and values, ThingFilter `allowedDefs`, tale and
battle-log def refs — the same classes `CANONICAL_SAVE_CAVERNS_SCRUB_1`
enumerated. They yield Scribe `Could not load reference to` lines and the Thing is
dropped. **That is route 2's DATA half, owed separately.**

⚠️ **Limit.** Donor ownership comes from the 584-mod dump of **2026-08-29**, which
predates the save (2026-09-12). A def one of the 5 mods gained between those dates
is invisible to this comparison; no dump of the save's own 635-mod set exists.

## Still open after the scrub

1. 🔴 **The save is still refused.** 14 `modIds` entries have no live counterpart —
   Caverns, the 10 ArtOverrides, and the 3 untraced rows in the table above. The
   route for those is the owner's (see "Why this needs the owner").
2. 🔴 **Trace `badoaks.meatonastick`, `badoaks.meatonastick.expansion` and
   `guy762.mm.kotorcore`.** No recorded retirement; not the class he ruled on.
   `badoaks.meatonastick` resolves to **two** workshop folders
   (`3435027361`, `3577333297`) — worth knowing which is which before restoring.
3. **Owed to bridge, not taken** (another FOUNDRY agent held it this wave): load
   the save and confirm RimWorld itself accepts it. Expect it still refused on the
   14 above. When it does load, harvest `Player.log` for
   `Could not load reference to` and expect the 5 world-pawn Things to be dropped.
4. **Ledger gap, one line**: `biomesteam.biomespollutedlands` is still absent from
   `infrastructure/state/facts/retired_mods.json` (the other 4 are recorded).

## ruling — owner, 2026-09-20

Verbatim: **"Scrub all 18"**.

Restore nothing. Every reference to all 18 absent mods is scrubbed out of
`CANONICAL_ASHKARR_START_2026-09-12.rws`, **including the four that are still on
disk** — `biomesteam.biomescaverns`, `badoaks.meatonastick`,
`badoaks.meatonastick.expansion`, `guy762.mm.kotorcore`. The cave biome and
whatever those four placed in the world go with them.

- Route 1 (restore by ModsConfig edit) is **dead**, not deferred.
- Route 3 (force-load with compatibility checks ignored) was **not** chosen.
- Ruled alongside `CANONICAL_SAVE_SCENARIO_MISMATCH_1` ("Hand-edit the founders
  in"), which is what makes a loadable save necessary in the first place.
