# LANTERNDEEPS_TIER_COLLISION_1 — the live Lantern Deeps has no repo copy, and its successor would delete it

Found 2026-09-26 by BENCH while preparing `BIOME_LOAD_PROOF_WAVE_1`. Nothing has been
deployed for this mod; the hazard was caught before `--apply`.

## what is true (MEASURED 2026-09-26)

| | |
|---|---|
| Live mod list | **628 active** (parsed from `activeMods`, not grepped) and it contains `mandrake.rut.lanterndeeps` |
| That mod's files | exist **only** at `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\LanternDeeps` |
| Its repo copy | **THERE IS NONE.** `grep -rl mandrake.rut.lanterndeeps --include=About.xml src/` returns nothing |
| The successor | `mandrake.rm.lanterndeeps`, in the repo at `src/RimMandrake/LanternDeeps` — 96 tracked files, its own 51 textures under `Textures/RM_LanternDeeps/` |
| Its deploy target | `Mods\LanternDeeps` — **the same folder name** |
| Is the successor active? | No. `mandrake.rm.lanterndeeps` is absent from `ModsConfig.xml` |

## the hazard, concretely

`deploy_custom_mods.py --mod LanternDeeps --apply` writes the repo's
`About/About.xml` over the game's. That single file carries the packageId. The moment
it lands:

1. `mandrake.rut.lanterndeeps` **no longer exists anywhere on the machine** — not in
   the game folder (overwritten), not in the repo (never there).
2. It is still listed in `ModsConfig.xml`, so it becomes a listed-but-missing mod.
3. The canonical campaign save references `RUT_LanternDeeps` defs — the biome, the
   two entrance buildings, the lanternstone terrain and walls, the cave flora. Those
   resolve through that mod and nothing else.
4. ⚠️ **This is the `Could not load reference to` class, which no mod change fixes** —
   the save itself holds the dead names. See the `rimworld-savegame` skill on the
   difference between that and a def-loader cross-reference error.

⛔ **So this is not a deploy that merely needs care. It is a deploy that must not
happen until the migration is done properly.**

🔑 Two standing lessons this is an instance of: *"Deploy tool needs unique mod names —
collides silently"*, and *"a BiomeDef deletion needs a live-tile check; a grep of the
`.rws` for the old defName lies because `tileBiome` is shortHash-encoded."*

## a second finding, same root

`deploy_custom_mods.py --pull LanternDeeps` **pulled the old tier's content into the new
tier's folder** — 28 paths including `About/About.xml` (reverting the packageId to
`mandrake.rut.lanterndeeps`), a parallel `Textures/RUT_LanternDeeps/` tree, the old DLL
and 27 `RUT_*` defs and patches sitting beside their `RM_*` successors.

`--pull` is documented as the rescue for `-` lines and is correct for a hand-edited
deployed copy — but it is **wrong whenever the deployed folder is a different mod that
happens to share the folder name**, and it gives no warning. BENCH reverted it the same
minute: `About.xml` restored from git, the 28 untracked paths moved aside (not deleted)
to the session scratchpad. `git status src/RimMandrake/LanternDeeps` is clean.

⚠️ **Whoever takes this item: do not re-run `--pull` on this mod.**

## what is owed

- [ ] Decide the migration route. The likely shape, not yet ruled: give the RM mod its
      own folder name so the two can coexist through one cold load, enable it, confirm
      the save resolves, then retire the RUT folder — rather than an in-place swap that
      has no rollback.
- [ ] Establish what the canonical save actually holds. A grep of the `.rws` for
      `RUT_LanternDeeps` is **not** the instrument for the biome — `tileBiome` is
      shortHash-encoded. Placed Things (the two entrance buildings, lanternstone walls,
      cave plants) grep normally as `<def>NAME</def>` and are the reachable half.
- [ ] Get `mandrake.rut.lanterndeeps` into the repo, or prove it is fully superseded
      file-for-file by the RM version. Right now a disk failure loses a live mod
      outright, which is true of nothing else we ship.
- [ ] Only then: `LanternDeeps` joins `BIOME_LOAD_PROOF_WAVE_1`.

## what is NOT owed
- No worldmap repaint. A biome of ours on zero tiles is the expected mid-migration
  state (`BIOME_PAINT_ONCE_AT_THE_END_1`).
- No fix to `deploy_custom_mods.py` is assumed. Whether `--pull`/`--apply` should refuse
  on a packageId mismatch between repo and game copy is a real question, but it is a
  separate call and not a prerequisite for the migration.
