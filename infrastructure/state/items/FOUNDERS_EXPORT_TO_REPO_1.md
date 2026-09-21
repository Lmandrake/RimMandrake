# FOUNDERS_EXPORT_TO_REPO_1 — the founders are not in the repo

## what is wrong

`WORLD_REMAKE_FINAL_STEP_1` names exactly three things that survive the world
remake: the worldmap, the gravship, and the founders. Owner, verbatim: *"We have
the worldmap saved out and the gravship and the founders. Everything else can be
regenerated."*

MEASURED 2026-09-20 — two of the three are saved out. The founders are not.

| artifact | where it actually lives |
|---|---|
| worldmap | `world/ASHKARR_WORLDMAP_tiles.csv` (21,872 rows) + landmarks / links / settlements / mutators CSVs + `world/ASHKARR_DRAFT_2026-08-24.rws` — **in the repo** |
| gravship | `design/Jawa/worldbuilding/ship_build/exported/Gravship_v2_ring_2026-09-12.xml` — **in the repo** |
| **founders** | **only inside `CANONICAL_ASHKARR_START_2026-09-12.rws`** (17,500,721 bytes, modified 2026-09-20 07:28) in `…/RimWorld by Ludeon Studios/Saves/` |

Also measured: `…/RimWorld by Ludeon Studios/CharacterEditor/` contains only
`options.txt` and `pawnslots.txt` — **no founder presets have ever been exported.**

⚠️ The repo's `src/RimUtinni/UtinniPatches/Defs/PawnKindDefs/JawaColonistPawnKinds.xml`
and `Defs/ScenarioDefs/Scenario_Utinni.xml` are **not** this. They are pawnkind
templates and scenario wiring — the rules for making colonists, not the specific
hand-edited individuals.

## why it matters

🔴 **The Saves folder is not version control.** It is reconciled by Steam Cloud,
which has already demonstrated it can restore 26 deleted `.rws` files with their
original mtimes after a deletion was recorded as done. A folder that can silently
put files *back* can silently put an older version back.

The standing rule is that work products belong in the repo, and that a scratch
location is only for things you would not mind losing. The founders are the
opposite of that: they are hand-made, they are one of three things ruled to
survive the remake, and they cannot be regenerated.

⚠️ **They were being edited on the day this was filed** — a sibling backup
`CANONICAL_ASHKARR_START_2026-09-12.rws.bak-pre-founder-scrub-20260920T134157Z`
exists, so a founder scrub ran 2026-09-20. Active editing plus no repo copy is the
combination worth fixing now rather than at remake time.

## the work

1. **Export the founders out of the canonical save** into a durable, re-importable
   form, and commit it. Options, in order of preference — pick by what actually
   round-trips:
   - CharacterEditor presets, one per founder (its own folder is the natural home
     and is currently empty).
   - A hand-authored def or scenario block that reproduces them exactly.
   - As a last resort, a committed copy of the save itself. ⚠️ At ~17 MB that is
     under the ~50 MB ceiling, but it is a derived bulk artifact and the weakest
     answer — prefer a form a human can read and diff.
2. **Prove the round trip.** Export, re-import into a throwaway colony, and confirm
   every founder arrives with name, backstory, traits, genes, skills and apparel
   intact. 🔑 An export nobody has re-imported is not a backup.
3. Record in `WORLD_REMAKE_FINAL_STEP_1` that the third artifact is now safe.

## Watch out

- 🔴 **Back up the Saves folder's keepers before touching anything**, and stat it
  afterwards. `rimworld/save_game` has silently written the CURRENT slot instead of
  the named one; confirm a NEW file appeared and no existing one changed size, and
  never trust the path a tool hands back.
- ⚠️ **Deleting saves only sticks while the game is RUNNING** — Steam Cloud restores
  them otherwise. Irrelevant to exporting, but relevant to any cleanup done alongside.
- ⚠️ A `.rws` is plain XML plus base64 grids, and its def shortHashes are only
  meaningful against the SAME mod set. If the founders are extracted by parsing
  rather than by the game, the mod list at extraction time is part of the artifact —
  record it.
- 🔑 This does not block the remake and the remake is far off. It is cheap now and
  expensive the day the save is lost.

## verify

The founders exist in the repo in a form that has been re-imported successfully at
least once, and `WORLD_REMAKE_FINAL_STEP_1`'s three carried artifacts are all under
version control.

## criteria

Losing the Saves folder would cost time, not the campaign.

## round trip 2026-09-21

**Step 2 is discharged: the round trip WORKS, observed in game — but the export as
it stands is not yet a backup, because re-importing it correctly needs one remap
the README does not name.** Full evidence:
`Transient/founders_roundtrip_2026-09-21.md`.

Done on the live full-mod-list game (618 active, the mod set the fragments were
exported against). No cold load spent. `rimworld/save_game` was never called and
every keeper save is byte-unchanged — `CANONICAL_ASHKARR_START_2026-09-12.rws` is
still md5 `75be9ecd4764a397e9802d997bb9e0b9`.

**What passed.**

- **Def resolution: 0 unresolved.** All 169 def-bearing references across the 8
  fragments (134 of them `<def>`) resolve against the current mod set, checked
  with a negative control.
- **Reference closure: 0 dangling.** 62 `Thing_*` references, all 62 inside the 22
  ids the fragments themselves declare. Nothing else from the source save has to
  travel with them.
- **Live fidelity.** Spliced into a *foreign* save (different world, player faction
  `Faction_17`, ideo `Ideo_12`, 69 colonists of its own) and loaded: all 8 pawns
  arrived. Compared against a pre-switch snapshot of the same pawns in the
  canonical world over name, backstories, body/head/hair/beard, gender, ages,
  kindDef, apparel with hit points, equipment, hediffs, all 12 skills with passion,
  all traits, all genes and all relations — **5 of 8 identical in every field**, and
  the other 3 differ only by `ageChronologicalYears` +1 (different in-game date) or
  one hediff the receiving game *adds*. The five-way relation clique and both
  animal bonds resolved by name.

**🔴 What failed first, and must be written down.** The first attempt — doing only
the remaps the README names — **silently lost the `Wimp` trait from 5 of the 6
founders, with nothing in Player.log.** `Wimp` is the only trait carried with a
non-null `<sourceGene>`, and gene `loadID`s are save-local exactly like
`Faction_21`. The destination had already issued gene loadIDs 0–1633, so
`Gene_342/382/422/462/814` resolved *successfully* into the destination's own
genes. The one founder whose gene id was above that range (Sekki, `Gene_2009`) kept
the trait — 6 of 6 agree, including the negative case. Offsetting every `<loadID>`
in the fragments by +1,000,000, rewriting the `Gene_<n>` references with them, and
bumping `uniqueIDsManager` fixed it completely.

**Owed, so the next person does not rediscover it.** `founders/README.md` must gain
(a) `Ideo_20` beside `Faction_21` in the remap list, (b) the `uniqueIDsManager`
bump (`nextThingID`/`nextGeneID`/`nextHediffID`/`nextJobID`), and (c) the
`<loadID>` offset rule with its reason. Stronger still, and the thing that would
actually close "an export nobody has re-imported is not a backup": a committed
`import_founders.py` beside the fragments that performs all four remaps against a
named destination save. A script is a backup; a prose caveat is a note. Left as a
judgement for the item's owner rather than done in this pass.
