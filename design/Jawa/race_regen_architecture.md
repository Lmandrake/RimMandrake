<!-- status: architecture spec — RACE_REGEN_ARCHITECTURE_1, BENCH 2026-08-31, green-lit (tier 2).
     Executes V2_DREAMS "Regenerate the races from scratch" as an ARCHITECTURE, not yet a content
     pass. Generator anatomy MEASURED 2026-08-31 (pipeline map in the item's commit); mod lives at
     src/RimStarWars/StarWarsRaces (mandrake.rsw.starwarsraces, renamed Phase 2a aa759446 —
     naming_inventory.md's src/Jawa path is stale on this point). -->
# Race regeneration — from migration to authorship

## 0. The one-sentence architecture

**Invert the generator: today the donors are the source and our mod is
output; after this, per-species AUTHORED FILES are the source, our mod is
output, and the donors are history.** The art is already ours — 876 PNGs sit
copied and namespaced under `Textures/RimMandrakeSW` — only
`gen_races_mod.py` still re-reads donor XML every run (`index_donors:283`,
`pick_species:494`, `copy_textures:752`). Severing that is a data-flow
change, not a content rewrite.

## 1. The species file — the implicit schema made explicit

The generator's `built` dict IS the schema (measured): species · src ·
genes[] · headless · label · description · iconPath · inheritable ·
canGenerateAsCombatant · combatPowerFactor · nameMaker/nameMakerFemale/
chanceToUseNameMaker · factionlessGenerationWeight, plus the hand-owned
PawnKindDef fields (apparelTags, apparelMoney, initialResistanceRange,
xenotypeChances). One YAML per species under
`src/RimStarWars/StarWarsRaces/species/<Name>.yml`, holding exactly those
fields plus provenance (`authored_from: <donor tag>` on day one, edited
freely after). **The hand-owned `RimMandrakePawnKinds.xml` folds INTO the
species files** — ending the measured drift risk where the generator skips a
file it can no longer model.

## 2. The migration — one export run, then byte parity

1. **The export run** (the LAST donor-reading run ever): serialize `built` +
   the pawnkind hand-edits into the 69 species files. Donors mounted once,
   for this.
2. **The generator rewrite**: `index_donors`/`pick_species`/`copy_textures`
   replaced by a species-file loader; emit paths unchanged.
3. 🔴 **The acceptance test is BYTE PARITY**: with donors unmounted, the
   rewritten generator must reproduce the currently shipped 14 XML files
   identically (allowing only a provenance-banner diff). Byte-equal output
   from authored input is the proof of independence with zero content risk —
   nothing changes in game until parity is banked and committed.
4. Only THEN does authorship begin: edits land in species files, never in
   donor XML, never by hand in Defs/.

## 3. What the guards become

All three survive, re-pointed at the new source (they are the mod's memory
of past disasters — keep them):
- `_guard_species_regression`: species-file count vs shipped count — a
  deleted YAML must be an explicit act, not a glob accident.
- the gene-count guard: per-species gene list vs shipped — silent gene loss
  stays impossible.
- the hand-owned-file guard retires WITH its file (its job moves into the
  schema).

## 4. The content passes this unlocks (each its own sitting, not this spec)

1. **The four stripped genes** return as per-species deliberate calls in the
   YAML: the three Force genes stay OUT pending the owner's
   Force-in-the-setting ruling (a setting call, not a gene fix); the Defel
   cloak needs its measured 4-def set taken together (and the donor's own
   `<hediffDef>` case typo checked before assuming it ever worked).
2. **The six deferred species** (Herglic, Anzati, Muun, SithZ, Togorian —
   Ortolan already shipped) come back as authored files; Herglic's "source
   carries no genes" mystery dies with the donors.
3. **The text pass**: 69 labels/descriptions + 48 RulePacks rewritten in
   campaign voice — Fable-shaped writing work, gated only on parity.
4. **The art pass**: the magenta three (Gand/Selkath/Chagrian) and every
   later fix become ordinary sprite-skill work against OUR texture tree.
5. Glued defNames (`RimMandrakeTwilek` style) stay AS-IS — renames remain
   governed by the namespace item and the no-savegame window; this
   architecture neither needs nor performs them.

## verify
Phase gate is §2.3's byte parity, run offline: donors unmounted (or the
loader path proven never to touch them via an fs-audit wrapper), regenerate,
`diff -r` against HEAD's mod folder = banner-only. LIES: parity against a
STALE checkout — diff against the deployed game copy too, since the repo and
game copies are never synced by writing alone.

## criteria
Generator runs with donor mods deleted from the machine and produces the
shipped mod; the species YAML dir is the only place a species is defined;
the owner edits one field in one YAML and sees it in game after a deploy.
