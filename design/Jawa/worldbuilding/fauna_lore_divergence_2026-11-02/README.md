# Fauna lore divergence round — decision record (FAUNA_LORE_DIVERSIFICATION_1, 2026-11-02)

The owner, 2026-09-11: *"We need to look at the art and eventual description to deduce whether a beast is
particularly scary or harmless. Diversity is good. I am less interested in forcing everyone to a scaling and more
that we allow huge things to terrify and tiny things to be harmless."* 2026-09-19: this round runs after biomes +
creature art + body sizes and **before** `FAUNA_TOLERANCE_NORMALIZATION_1`, which applies the numbers.

**The decision record is `design/Jawa/worldbuilding/data/fauna_lore_divergence_manifest.csv`**: 28 deliberate
divergences from the Law 3 band (12–15 × bodySize), 17 terror (above), 11 harmless (below). Columns: defName ·
direction · bodySize · band_lo/band_hi · current_best (pre-normalization) · K_ruled · ruled_best (= K × bodySize,
floor 1) · reason (what the player sees in the art and reads in the description) · ruling.

## Who decided

The item's verify line asked for an owner card per divergence. That line predates the owner's 2026-10-22 delegation
(*"Nearly everything including art"*; taste calls go to a judge agent that is not the maker,
`design/RimMandrake/delegation_policy.md`); damage tuning is not on its §2 short list. So: the builder proposed, an
independent judge (GPT via `gpt_consult.py`, given the art sheet and the descriptions) ruled each row accept / adjust /
reject. Every manifest row is a judge accept or adjust, at the judge's K. The calls are delegated, class
`fauna lore divergence`, and reach the owner in the daily digest; nothing here is recorded as his approval.

Files: `judge_prompt.md` (the brief), `judge_input.csv` (36 proposals with descriptions), `art_sheet.jpg`
(the art judged: red = proposed terror, green = proposed harmless; the last tiles include seven the builder dropped),
`judge_verdict.md` (20 accept, 8 adjust, 8 reject).

- **Dropped by the builder before judging** (art contradicts the description): RM_Vekka and RSW_Hssiss (art reads as
  mild lizards), RSW_ShadeWhale, RM_Ulgga, RSW_Corinathoth (art looks fearsome, described as grazers/peaceful),
  RM_Radyak (ambiguous); GR_Chickenrabbit has no art. The judge kept them dropped.
- **Rejected by the judge** (stay in band): RSW_Dragonsnake, RM_Cindermare, RM_Flamefang, RSW_Klorslug,
  RM_Meltgut, RM_Starmaw, RSW_Starmaw (a *"vanished crews"* line undercuts harmless), RM_Vaalok.

## Roster snapshot

`design/Jawa/worldbuilding/data/fauna_roster_damage_2026-11-02.csv`: 666 animals = every animal on an `RM_`/`RUT_`
biome roster (BiomeDef `wildAnimals` and patch-added rows) plus every `RM_`/`RSW_`/`RUT_` race def, measured by
`src/RimMandrake/Utils/animal_inventory.py` over the 316-mod ModsConfig load set of 2026-11-02 (mod XML,
inheritance-resolved, PRE-patch: `current_best` is the best tool power before any normalization). Three roster
names are absent: RSW_SandLion (retired twin of RM_Vekka, aliased in `RM_SWBRehome_Aliases.xml`) has no def;
RM_Drommath and RM_Ollareth (FeverWood birds) DO have defs but inherit their whole `<race>` block from
`RM_SapSuckerBase`, which `animal_inventory.py`'s own-`<race>` selection drops (found by
FAUNA_TOLERANCE_NORMALIZATION_1, whose `data/fauna_norm_input.csv` carries both).

## Graph

`python3 src/RimMandrake/Utils/fauna_divergence_graph.py` checks the manifest and draws
`Transient/fauna_lore_divergence/damage_vs_bodysize.png`: band shaded, roster grey, divergences labeled at their
ruled values. `selftest_fauna_lore_diversification.py` proves the manifest, the judge trace and the redraw.

## For FAUNA_TOLERANCE_NORMALIZATION_1

When it rescales the full roster into the band, the 28 manifest rows take `ruled_best` instead (best tool power;
the other tools scale with it, and the sublinear-DPS cooldown rule still applies). Re-measure bodySize at that time:
if a row's bodySize has changed, keep its K, not its absolute power.
