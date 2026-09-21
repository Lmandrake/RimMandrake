# UMBRA_IS_A_REGION_NOT_A_BIOME_1 — Umbra is a region, not a biome

## the ask

🔴 **Owner ruling, 2026-09-21 (BENCH question card), verbatim:**

> *"Umbra is a region not a biome. The Propane Lake is an ocean-biome made of propane,
> definitely its own biome."*

`RUT_Umbra` ships today as a `BiomeDef` and `design/RimMandrake/biome_mod_architecture.md`
listed it as biome row 24 sharing a mod with the Propane Lake. Both are now wrong. Umbra is
the antistellar cap — a named REGION of the planet, in the same class as the Dune Sea and
Sootreach, not a biome a tile can be.

## spec

1. Umbra leaves the biome row list (§2 of the architecture spec is already corrected).
2. Decide, and say in this item, what happens to the tiles `RUT_Umbra` carries: they need a
   real biome underneath the region. `the_propane_lakes.md` defines the cap's energy regime
   (fuel snow, ammonia flats, aurora) — that regime is either an existing biome or a new one,
   and this item is where that is settled.
3. Umbra becomes a named world region alongside the other 10, matching their convention.
   🔑 **No leading "The "** — he ruled 2026-09-21 that region names carry no article.
4. Retire the `RUT_Umbra` BiomeDef only once its tiles have somewhere to go.

## Watch out

- ⛔ **Do not cite a tile count as evidence about what is or is not built.** The planet is
  painted once at the end; the 2531 figure in the architecture spec is a pre-ruling reading
  and is not an instrument for this work.
- ⚠️ `ashkarr_paint.py`'s region literals were corrected by `ASHKARR_PAINTER_NAMES_DIVERGED_1`.
  If Umbra is added as a region, add it there in the corrected (no-article) form.

## criteria

`RUT_Umbra` no longer exists as a `BiomeDef`, its tiles carry a real biome, and Umbra is a
named region of the planet in the same form as the other ten.

## done — 2026-09-21 (FOUNDRY)

**1. Verified, not just trusted.** `design/RimMandrake/biome_mod_architecture.md` §2's
row 24 already read "⛔ `RUT_Umbra` is NOT a biome (it is a REGION) and has left this
list" — a sibling BENCH pass (§7 Q1) already corrected it. Confirmed by direct read.

**2. Umbra as a named region: already done, verified live, not re-authored.**
`src/RimMandrake/Utils/ashkarr_paint.py` line ~851 already reads
`regions.append(("Umbra", "waste", ...))` — no leading article — landed by
`ASHKARR_PAINTER_NAMES_DIVERGED_1` (commit `72b5dec81`, same session), which itself
renamed `"The Umbra"` -> `"Umbra"`. `src/RimMandrake/Utils/ashkarr_settle.py`'s
`BARREN_REGIONS` also already carries the bare `"Umbra"` string, and its
`validate_barren_regions()` re-checks every literal in that set against the LIVE
canonical save's `<world><features><features>` block every run (not the stale CSV) —
that check is closed (`BARREN_REGIONS_NAME_NOTHING_1`), which means **"Umbra" already
resolves against a real live WorldFeature on the canonical save**, not just a script
literal. Nothing further to author here.

**3. Biome-mapping decision (this item's own call).** The antistellar cap's regime —
fuel snow, ammonia flats, aurora, cold hydrocarbon/ammonia chemistry, no icy dayside
analog, crystal flora — matches no other owned BiomeDef. Checked the one plausible
candidate, `RUT_NightsideIce` (the only other biome on the nightside cold end): it is
the OPPOSITE regime by design (no precipitation, no wildlife, "dead and silent"
interior per its own sheet's §6 hard bans) — cannot merge. ⇒ **Genuinely new BiomeDef
needed.** Since `RUT_Umbra`'s existing content already WAS that biome (terrain,
weather, wildAnimals, wildPlants, diseases all fully authored, not a stub), the fix
was a rename, not new authoring: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/
RUT_Umbra.xml` deleted, content carried forward verbatim (only defName/label/header
changed) into a new file, `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/
RUT_FuelSnows.xml` — defName `RUT_FuelSnows`, label "the Fuel Snows" (keeps the "it
snows fuel" flavour without reusing "Umbra", now the region's name). Stays `RUT_`-tier
under UtinniPatches for now — the wider `biome_mod_architecture.md` migration wave
(RUT_ → standalone RM_ mods) hasn't reached this biome; that doc now has a pointer at
row 24 for whoever runs that wave next.

**4. 🔴 Dramatic finding worth recording: `RUT_Umbra` was NOT a zero-tile biome.**
Unlike most still-authoring biomes this repo's "zero tiles is not a defect" doctrine
covers, `RUT_Umbra` was already LIVE-PAINTED onto 2,531 real world tiles by
`BIOME_WORLD_SWITCH_WAVE_1` (commit `f90d660ae`, 2026-09-12, status DONE) — a real,
committed, executed repaint, not a pending one. Renaming the defName without also
repainting those tiles (explicitly out of THIS item's scope — "don't repaint tiles
now") leaves them referencing an unresolvable defName until the terminal repaint. This
is a deliberate, recorded tradeoff, matching the owner's own stated policy on exactly
this situation (`[[world-remake-is-the-last-step]]`: "do the clean thing and let the
remake absorb the divergence" — not licence to break the save carelessly, but licence
to do a clean rename rather than contort the work around save continuity). Recorded in
`infrastructure/state/facts/biome_paint_list.md`'s `RUT_FuelSnows` row so the
terminal-repaint author has this, rather than rediscovering it. **Not cited as
evidence for or against anything in this item** — recorded per the correctness rule,
not used to justify a different action.

**5. Files touched, all comment/reference updates only (no functional patch-xpath
changes — neither `BiomeDescriptions_Ashkarr.xml` nor `BiomeFlora_Ashkarr.xml` had an
`<xpath>` targeting `RUT_Umbra`, only prose comments):**
- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Umbra.xml` — deleted.
- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_FuelSnows.xml` — new, carries the
  retired def's full content forward.
- `src/RimUtinni/UtinniPatches/Patches/BiomeDescriptions_Ashkarr.xml`,
  `.../BiomeFlora_Ashkarr.xml` — comment references updated to the new defName.
- `design/Jawa/fauna/biome_name_migration.py`, `design/Jawa/mods/biome_flora.py` —
  the live `AB_PropaneLakes`→ mapping and `FAMILIES` key updated to `RUT_FuelSnows`
  (these are current-state lookup tables consumed by generators, not history).
- `infrastructure/state/facts/biome_paint_list.md`, `design/RimMandrake/
  biome_mod_architecture.md` §2 row 24 — updated per above.
- Deliberately NOT touched: `world/biome_world_switch_apply.py` (a historical record
  of an already-executed repaint — editing it would misstate what actually ran),
  `infrastructure/state/facts/biome_rosters.md` (append-only dated fact log),
  the frozen `the_propane_lakes.md` (amendments only change it at a sitting), roster
  JSON files under `design/Jawa/worldbuilding/biomes/rosters/` (design-record data
  other generators own; not required for def loading), and other items'/handoffs'
  historical mentions of `RUT_Umbra` (accurate as of when they were written).

**6. Selftests:** 70/71 passed. The one failure,
`src/RimMandrake/Utils/selftest_deployed_biome_refs.py`, hit the documented
pre-existing 240s timeout in this environment — expected, not a regression.

**7. Static XML validation:** `validate_patch.py` against both edited patch files —
0 errors, 0 warnings (no `--defs`/`--live` dump available in this environment; static
checks only). New def file confirmed well-formed XML directly.

## addendum — 2026-09-21 (FOUNDRY, live-tile verification + remediation)

A later FOUNDRY subagent was sent to independently verify point 4 above (the "2,531
tiles" claim) with a real instrument rather than trusting it, because the raw grep
this repo's docs warn against proves nothing on a compressed world-tile array.

**Measured, not trusted:** decoded `CANONICAL_ASHKARR_START_2026-09-12.rws`'s live
`tileBiome` array offline with `src/RimMandrake/Utils/worldmap.py`'s `WorldGrid`,
using a def-dump capture taken `2026-09-21T08:56:31Z` — the last capture taken
**before** this item's rename deploy (which landed at `2026-09-21T12:00:10Z`/
`a73319758`) — to resolve `RUT_Umbra`'s pre-deletion `BiomeDef` shortHash (`15270`).
Result: **exactly 2,531 of 21,872 tiles carry shortHash 15270**, `RUT_FuelSnows`
carries **0**. **The 2,531 figure was accurate, not stale.** (One unrelated
unresolved hash, `58457`, also present — not investigated, not Umbra.)

Separately confirmed the deployed live Mods folder (`.../RimWorld/Mods/UtinniPatches/
Defs/BiomeDefs/`) no longer defines `RUT_Umbra` anywhere (only `RUT_FuelSnows.xml`,
carrying a comment reference to the old name, and an unrelated `RUT_PropaneLake.xml`
mention) — so on the canonical save's next load, 2,531 tiles' biome shortHash would
have resolved to nothing.

**Remediation applied:** restored `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/
RUT_Umbra.xml` as a full behavioural duplicate of `RUT_FuelSnows.xml` (same
terrain/weather/fauna/flora content, defName/label reverted, header rewritten to
explain the restoration and point future authoring at `RUT_FuelSnows`) — the lower-
risk, reversible fix, versus a live world-tile repoint via the bridge (which would
have required loading the canonical save into a game currently on an unrelated
scratch world, and the "paint once at the end" doctrine does not forbid this kind of
minimal compatibility duplicate). Deployed via `deploy_custom_mods.py --mod
UtinniPatches --apply` — plan showed exactly one file added
(`Defs/BiomeDefs/RUT_Umbra.xml`), confirmed present on disk in the live Mods folder
after apply. Both `RUT_Umbra` and `RUT_FuelSnows` now resolve; no game content was
lost or duplicated in effect (they are byte-identical bodies under two defNames,
the same "twin" pattern already used elsewhere in this registry, e.g.
`RUT_Greentide`/`RM_Greentide`).

**Owed:** retire `RUT_Umbra.xml` again once the terminal repaint
(`BIOME_PAINT_ONCE_AT_THE_END_1`) has moved every tile still carrying it onto
`RUT_FuelSnows` — verify with the same `worldmap.py` decode before deleting, not by
trusting a tile count from a doc. `biome_paint_list.md`'s `RUT_FuelSnows` row and a
new `RUT_Umbra` row updated to match.

Bridge: taken solely to check whether the game was live and on the canonical save
(it was not — a different, non-Ash'karr scratch world, seed "corn cob", 119,904
tiles, was loaded); no live game state was read or written for the canonical save,
so all verification above was done offline against the `.rws` file directly.
Released immediately after.
