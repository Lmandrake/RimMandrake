# BIOME_MOD_UNIFICATION_1 — merge the biome mods into one player-facing RimMandrake.Biomes mod

Ruled 2026-09-27, decision taken by question card on the owner's own framing (he
proposed "a single RimMandrake.Biomes mod that players can configure/select from
like AlphaBiomes does … It might be simpler"). He chose **"One mod, merge now"**
over merging at the repaint window. Authority: §7 Q17 of
`design/RimMandrake/biome_mod_architecture.md` (this item is its execution).

## The ruling, executable

- ONE shipped mod — working name `RimMandrake.Biomes`, packageId
  `mandrake.rm.biomes` (tier grammar; final name is a sub-decision below).
- Per-biome toggle screen in Mod Settings (AlphaBiomes shape), per the
  Mod Settings law: each biome's worldgen spawning and mechanics gateable,
  defaults = all on.
- What does NOT change: per-biome sittings/review, `RM_` def prefixes, the
  RimUtinni patch layer beneath (it now patches the one mod), Q13
  duplicate-then-diverge (same mod, still separate defs), and the frozen-world
  law — a workerClass remains inert on Ash'karr.
- Non-biome mods stay independent: FlowWorks, Graffiti, Oracle, TheBazaar,
  CreatureBehaviors (check: biome-kit vs framework), etc.
- Kills on landing: the cross-mod class-reference failure class
  (BLUEDESERT_JOIN_FULL_LIST_1 becomes moot once bluedesert's content is inside
  the one mod — keep the interim list-add only if the merge takes longer than
  the next cold-load cycle) and the double-authored liquid terrain
  (`LIQUID_TERRAIN_AUTHORED_TWICE_1` resolves by unification, one def survives).

## Sub-decisions the spec pass must put to the owner (card agenda)

1. Final mod name + whether the Workshop page is one mod or one mod + the
   campaign scenario mod.
2. Exact roster: which of the ~20+ biome mod folders under `src/RimMandrake/`
   are IN (biomes + their kits) vs OUT (frameworks, campaign wiring).
3. Source strategy: physically merge folders vs keep per-biome dev folders and
   compose the shipped mod in a packaging step (deploy_custom_mods.py grows a
   compose target). BENCH's stated lean at the card: keep dev folders, compose.
4. Assembly strategy: one merged DLL vs per-biome DLLs inside one mod (RimWorld
   loads all Assemblies/*.dll; per-biome DLLs keep the srchash guard granular).
5. Migration order: which mods fold in first (the ones already on the full list
   vs the bedazzle-fresh ones), and what happens to per-mod modcheck north stars
   (rename-key vs re-validate).

## spec

1. A backgrounded design/spec pass writes
   `design/RimMandrake/biome_mod_unification_spec.md`: roster table (every
   candidate folder, in/out, why), packaging mechanism, settings screen design,
   def/patch collision sweep (duplicate defNames, duplicated terrain), modcheck
   and deploy tooling changes, migration order, and the numbered card agenda
   above. BENCH cards the sub-decisions.
2. FOUNDRY executes per the ruled spec, in waves; each wave load-proven.

## Watch out

- ModsConfig.xml load-order entries for the folded-in mods must be removed in
  the SAME swap that adds the unified mod, or the game logs missing-mod noise.
- The shipped savegame references BiomeDefs by shortHash — defNames must not
  change during the merge, or the frozen world's tiles orphan
  (`biome-defname-deletion-must-check-live-tiles`).
- Per-mod `.srchash` sidecars and `block_dll_source_mismatch.py` assume mod
  folder = DLL home; the packaging step must keep that invariant or update the
  guard.
- `modcheck` north stars are keyed by mod folder name; folding a VALIDATED mod
  in without `rename-key` strands its checklist as ORPHANED.

## verify

- The unified mod loads clean on the full list with every folded-in biome's
  content present (def counts measured, not assumed) and the per-biome toggles
  actually gate spawning.
- No duplicate-defName collisions in the merged def set.
- The folded-in standalone mods are retired from the live list in the same
  swap.
