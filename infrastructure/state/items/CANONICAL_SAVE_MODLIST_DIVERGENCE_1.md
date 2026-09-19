# CANONICAL_SAVE_MODLIST_DIVERGENCE_1

The canonical campaign save cannot be loaded on the live mod list. This is not a
"one retired mod disarms some pawns" regression — the save's recorded mod list and
the live list have diverged by 16 mods, so RimWorld's own compatibility check
refuses the load before any def resolution happens.

## Measured

MEASURED 2026-09-19 (FOUNDRY, offline). Both lists parsed with `ElementTree`,
never grepped — `ModsConfig.xml` puts many `<li>` on one line and a
`grep -c '<li>'` returns a plausible wrong number.

- `CANONICAL_ASHKARR_START_2026-09-12.rws` — `<meta><modIds>`: **635** entries.
  `/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves/CANONICAL_ASHKARR_START_2026-09-12.rws`
- Live `activeMods`: **621** entries.
  `/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/ModsConfig.xml`
  ⚠️ This file describes the NEXT load, and it was being rewritten by the other
  window during this measurement (it read 632 an hour earlier) — so the count is a
  moment, not a constant. The 16-mod **set** below is the durable finding.
- **16 mods the save needs and the live list lacks:**

| packageId | name | why absent |
|---|---|---|
| `biomesteam.biomescaverns` | Biomes! Caverns | **deliberately cut** 2026-09-18 (`ModsConfig_before_caverns_cut_2026-09-18.xml`) |
| `mandrake.rut.puffmiteartoverride` | Puffmite Art Override | **deliberately retired** 2026-09-18 (`ModsConfig_before_artoverride_retire_2026-09-18.xml`) |
| `mandrake.rut.kroffaartoverride` | Kroffa Art Override | same retirement |
| `mandrake.rut.aaroxisdendoriaartoverride` | AaroxisDendoria Art Override | same retirement |
| `mandrake.rut.bloodletterpetrelartoverride` | BloodletterPetrel Art Override | same retirement |
| `mandrake.rut.bovinebeetleartoverride` | BovineBeetle Art Override | same retirement |
| `mandrake.rut.cresteddragonartoverride` | CrestedDragon Art Override | same retirement |
| `mandrake.rut.foundrybeetleartoverride` | FoundryBeetle Art Override | same retirement |
| `mandrake.rut.fungalmantisartoverride` | FungalMantis Art Override | same retirement |
| `mandrake.rut.jamelartoverride` | Jamel Art Override | same retirement |
| `mandrake.rut.screecherartoverride` | Screecher Art Override | same retirement |
| `als.gravtech` | GravTech | **unexplained** |
| `als.gravtech.bc` | GravTech - Big cannons | **unexplained** |
| `halituisamaricanous.gravtechbigcannons` | GravTech - Big cannons Retextured | **unexplained** |
| `petetimessix.researchreinvented.steppingstones` | Research Reinvented: Stepping Stones | **unexplained** |
| `biomesteam.biomespollutedlands` | Biomes! Polluted Lands | **unexplained** |

- 2 mods live but not in the save (harmless — a save loads fine with extra mods):
  `mandrake.rm.weathersuite`, `mandrake.rut.lanterndeeps`.

## Why this needs the owner, not a seat

The two precedents in this exact class were both resolved by **restoring** the
retired mod: `DOORSEXPANDED_SAVE_COMPAT_REGRESSION_1` and
`DROID_DONOR_SAVE_COMPAT_REGRESSION_1` (both closed, both "mod restored, real fix
still owed"). That remedy **contradicts** the two deliberate cuts here — Caverns
was retired on purpose, and the 10 ArtOverride mods were retired on purpose the
same day. A seat restoring them would silently revert two decisions.

Three routes, and picking one is his:

1. **Restore** the 16 mods to the live list (reverts the Caverns and ArtOverride
   cuts for the campaign's sake). ModsConfig write — expensive list.
2. **Scrub and re-mint** the canonical save against the current list. The scrub is
   much larger than the one already done: `CANONICAL_SAVE_CAVERNS_SCRUB_1`'s own
   finding MEASURED **3,279 refs to 575 Caverns defNames still in the save** after
   the `BMT_CaveSpiderHead` scrub, and map terrain/biome grids are still
   UNMEASURED (needs `savemap.py` and a shortHash table from a matching dump).
2 of those refs are the NRE-risk class (`<stuff>` on worn apparel of two
   mothballed colonists).
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
- The 5 **unexplained** absences (3 GravTech, SteppingStones, PollutedLands) were
  already flagged as unexplained on `CANONICAL_SAVE_CAVERNS_SCRUB_1` at
  2026-09-19T01:07Z and still are. Nobody has traced when or why they left the
  list; there is no snapshot named for their retirement, unlike Caverns and the
  ArtOverrides. Worth answering before choosing route 1 — they may simply be
  uninstalled from disk, in which case restoring them is a Steam action, not a
  ModsConfig edit.
  🔴 **TRACED — see "The 5 unexplained absences, traced" below. All 5 are
  deliberate and recorded; the claim above is stale.**

## The 5 unexplained absences, traced (FOUNDRY, offline forensics, 2026-09-19)

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
