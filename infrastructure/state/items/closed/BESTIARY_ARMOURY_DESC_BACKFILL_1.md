# BESTIARY_ARMOURY_DESC_BACKFILL_1

Description backfill for RSW Armoury + RSW SWBestiary. Authority:
`design/Jawa/text_lore_load_report.md` §3 + §6; owner authorized wave 1
2026-09-11 ("Let's do it").

## wave 1 report (2026-09-11)

### 🔴 The scope in the census was wrong — the debt is ~55 entries, not ~1,830

§3 of the report put the debt at "Armoury 740 + SWBestiary 856 missing, plus
233 placeholder". Re-measured here by XML parse of all 303 def files in the two
mods (3,216 def elements, 3,064 concrete), **resolving description inheritance
through `ParentName`**, which the original census did not do:

| the report said | actually |
|---|---|
| SWBestiary 856 missing | **3** missing ThingDefs (2 filth, 1 projectile). 264 of 267 concrete SWBestiary ThingDefs already carry their own description, and the text is good. The 856 was 634 SoundDefs + 122 PawnKindDefs + BodyPartDefs/BodyDefs/LifeStageDefs — **none of which carry a description in vanilla either.** |
| Armoury 740 missing | **93** missing ThingDefs, of which 88 are projectiles, motes and filth — no inspect description in vanilla either. **5** were genuinely player-facing. |
| "An inconspicuous floor panel." ×211 | **×4.** There are four smuggling-compartment variants in the file, not 211. |
| a literal "TBD" | ✅ confirmed, ×2 (the NeedDef *and* the HediffDef of the same name). |
| — (missed) | **a literal `.` as the description on 42 defs**, inherited by **69 concrete defs**. This was the real placeholder debt and the census did not see it. |

`design/Jawa/text/armoury_bestiary_desc_remainder.csv` enumerates all 1,458
remaining description-less concrete defs with a classification column.
**1,447 are STRUCTURAL** (SoundDef, DamageDef, BodyPartDef, PawnKindDef,
projectiles/motes/filth — vanilla parity, not debt). The 11 marked
TEXT-BEARING are 8 projectiles, 1 filth and 2 TerrainDefs; the two terrain
defs were the only real ones and are written in this wave.

**There is no wave 2 for these two mods on missing descriptions.** The
description debt named in §6 is closed. What remains is a different kind of
work, listed under "not this item" below.

### What was written — 57 descriptions

55 in Armoury (all registered in the generator hook) + 2 in SWBestiary (a
hand-ported file with no generator). They resolve **84 concrete defs**, because
27 more inherit a corrected line from an abstract parent.

| group | n | note |
|---|---|---|
| `.` placeholder owners | 42 | resolves **69** concrete defs (27 inherit) |
| — of those, ModularWeapons2 armour/melee/helmet parts | 35 | written from each part's own `statOffsets`/`equippedStatOffsets`/`tools` |
| — loose ThingDefs (ysalamir, flight-suit compressor, worker's helmet, 2 Sith neck guards) | 5 | |
| — abstract family bases (gravship hull overlay, decorative terminal) | 2 | one line each, inherited by the whole family |
| `An inconspicuous floor panel.` variants | 4 | one shared body + a varied finish clause, per the family pattern |
| literal `TBD` (`RSW_ToxinDependence` NeedDef + HediffDef) | 2 | |
| no `<description>` at all, player-facing | 7 | 3 Imperial banners, Imperial outdoor lamp, water tank, 2 named freighter hull patterns |
| TerrainDef (junkyard soil, trash sediment) | 2 | |

Every line was written against the def's **own fields** — nothing describes a
mechanic the def does not have. RSW tier discipline held: no Ash'karr, no
Utinni, no "Jawa clan", no `millennia`/`ten thousand years`.

### 🔑 The fixes live in the generator hook, not in the XML

**16 of the 17 edited files are GENERATED** by `gen_additionalmods_absorption.py`,
`gen_kotorcore_absorption.py` or `gen_kotorweapons_absorption.py` — a regen would
have silently restored every placeholder. All 55 Armoury descriptions are
therefore registered in
`src/RimStarWars/Armoury/Source/absorption_content_fixes.py` as
`DESCRIPTION_BACKFILL`, folded into `FIXES`, which is exactly what that module
exists for. Two extensions were needed and made:

- `apply_content_fixes` now falls back to the **`Name=` attribute** when a def
  has no `<defName>`, so a placeholder on an abstract parent can be fixed once
  for the whole variant family. (`MAYREQUIRE_FIXES` deliberately stays
  defName-only.)
- a **`MISSING` sentinel** for `expected_broken_text`, meaning "the donor has no
  such field": the fix then creates it (after `<label>`), and skips — as every
  other fix does — if the donor later grows a field of its own.

**Proved, not assumed:** `gen_additionalmods_absorption.py` was re-run and its
output is byte-identical to the hand-written text for all registered entries
(`CONTENT FIX APPLIED` in the log); the two SWBestiary TBD lines are in a
hand-ported file with no generator. `selftest_absorption_generators.py` 4/4
pass. Every edited file re-parses under ElementTree. Placeholder census after
the change: **NONE**.

### ⚠️ Found in passing, NOT fixed here — 4 content fixes are silently dead

Re-running the generator revealed that four pre-existing `FIXES` entries never
apply: their `expected_broken_text` is written in Python with backslash-n
escapes (real newlines) but the donor XML ships the two literal characters
backslash and n, so the equality check fails and `apply_content_fixes` skips
with "donor text no longer matches expected". The good text currently in the
committed XML for these is hand-edited and **any regen reverts it** — which is
exactly what happened to `guy762_SWForceLightsabers_CrystalPart_heart` during
this wave's verification run (reverted, not committed).

Affected: `guy762_SWForceLightsabers_CrystalPart_heart`, `guy762_MalgusArmor`,
`guy762_VisasRobes`, `guy762_brifle_jurgan`. The fix is to escape the
backslashes in those four `expected_old` strings. Worth its own small item —
it is a live regression risk, not a text nit.

Also surfaced by that run and **left in the working tree uncommitted**, because
it is another item's output and not mine to judge: a `MayRequire` addition to
`Absorbed_Kotorcore_ModularWeapons2_Building_KotORGunsmithWorkbench.xml`
(reverted), and two untracked artifacts the current generator now emits —
`Armoury/Patches/Absorbed_AdditionalMods/kotorweapons/TheForceLightsabers/Absorbed_Kotorweapons_TheForceLightsabers_Patch_KotORLightsaberRecipes.xml`
and `Armoury/Textures/Things/Item/Resource/Crystal/`. Both look like owed
CRYSTAL_INGEST_EXECUTION_1 output that the committed tree predates.

### Samples for the owner

- **ysalamir** — "A slow, claw-footed tree lizard whose living body nullifies psychic sensitivity in everything near it. It eats almost nothing, lays eggs and takes training well; keeping one close is a dependable way to make a psychic problem stop being a problem."
- **Beskar plating** — "Plates of beskar, the Mandalorian iron that turns blaster bolts and holds against a lightsaber. Priceless, absurdly heavy, and worth every kilogram."
- **floor panel (family line)** — "An inconspicuous floor panel with a smuggler's void cut in beneath it. It swallows a startling amount of cargo and runs cold enough to keep it, and anyone crossing it sees nothing but deck. Finished in blue dreadnaught cabin tile."
- **toxin dependence (hediff)** — "A body rebuilt around toxic intake. While the creature can keep feeding on polluted matter it is perfectly well; cut off from it, the withdrawal is slow, painful and eventually fatal."
- **regal adornments** — "Inlay, filigree and a great deal of expensive trim added to an otherwise sensible helmet. It does nothing for the wearer's safety and a great deal for how seriously anyone takes them."
- **Armorply plating** — "Light armorply panels, matted and contoured to break up the wearer's outline. It adds nothing to the suit's protection; what it buys is free movement and a silhouette that game and sentries both miss." *(the label says plating; the def's stats are pure stealth and mobility — described as it behaves)*
- **water tank** — "A pressed-metal water tank of the sort bolted beside every moisture farm and dust-side outpost. This one is a prop: nothing can be drawn from it."

### Not this item

- `RSW_Karrask` ("Jawa clan") and `RSW_GlassPearl` (names Ash'karr) —
  TIER_GRAMMAR_TEXT_FIXES_1, still open, still carrying the owner's card.
- Donor text quality across the absorbed pools — DONOR_PROPER_NOUN_SCAN_1.
- The 4 dead `FIXES` entries above — needs its own item.
- Not deployed. `deploy_custom_mods.py` has not been run for this change.
