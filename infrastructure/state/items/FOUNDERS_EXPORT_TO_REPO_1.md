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
