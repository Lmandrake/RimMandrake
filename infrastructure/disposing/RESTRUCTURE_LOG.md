# RESTRUCTURE_LOG.md — execution record for `output/RESTRUCTURE_PLAN.md`

Appended one block per stage as it lands. Written by the agent executing P5.
**Stage 9 (`skills/`) is owner-gated and was not run.**

## Baseline, re-measured immediately before stage 0

`python3 Utils/check_refs.py`

```
check_refs: 31 BROKEN, 169 UNVERIFIED across 201 docs (63 commit, 89 line, 2547 path, 290 rule, 85 skill)
```

`python3 Utils/doc_budget.py` → `repo total: 298 markdown files, 56,463 lines`

⚠️ **The 31 is not a regression against the plan's stated 21.** Ten of the 31 are
**forward references written by the stage-0 tier READMEs themselves** —
`design/README.md` cites `design/Jawa/`, `design/RimMandrake/`, `vendor/wisdom/`,
`MODLIST.md`; `vendor/README.md` cites `vendor/wisdom/` and
`design/RimMandrake/`; `src/README.md` cites `src/Jawa/` and `MODLIST.md`;
`observed/README.md` cites `deployed/config/`; `research/README.md` cites
`MODLIST.md`. `check_refs.py` indexes untracked files too
(`git ls-files --others --exclude-standard`), so the seven new READMEs also
explain the doc count of 201 vs the plan's 194.

**These ten resolve themselves as the stages create the directories they name.**
The pre-existing debt is 21 and that is the number a stage must not raise.

## Stage 1 — `research/`

Moved: `hand_authored_maps/` `samuel_streamer_study/` `reference/` →
`research/RimMandrake/`; `mods/inspiration/` → `research/RimMandrake/inspiration/`;
`worldbuilding/star_wars_species_scale_reference_atlas.pdf`,
`Utils/Jawa_Visual_Research_Dossier_v2_Image_Dense.pdf`,
`mods/sw_ingredients_inventory.md` → `research/Jawa/`.

| check | result |
|---|---|
| a `git status --porcelain` | 118 `R` + 10 named `M`; no bare `D` |
| b `ls hand_authored_maps reference samuel_streamer_study` | all three ERROR ✔ |
| c `check_refs.py` | 35 → **31** after the sweep = baseline ✔ |
| d `doc_budget.py` | 299 markdown files, exit as before ✔ |
| e stage check "old dirs gone, not drained" | ✔ (b) |

**Plan inaccuracies found.** §2 names the dossier
`Utils/Jawa_Visual_Research_Dossier_v2.pdf`; the file is actually
`Utils/Jawa_Visual_Research_Dossier_v2_Image_Dense.pdf`. And
`mods/sw_ingredients_inventory.md` is listed in the §2 `research/Jawa/` row but
not in the §5 stage-1 scope cell — moved here, since its destination is
`research/`.

**Windfall:** `research/RimMandrake/hand_authored_maps/README.md:8`'s relative
link `../reference/rimworld_handcrafted_map_atlas.md` was BROKEN before the move
and is correct after it — `reference/` is now its sibling.


---

## Stages 3–8 — ONE PASS, one commit

Executed by `infrastructure/output/do_restructure.sh` (moves) and
`infrastructure/output/fix_refs.py` (references), both committed beside this
log. `git mv` for every tracked path; plain `mv` only where git refuses because
the payload is gitignored (`runtime/logs/`, art `_raw`/`_cut`, `_review/`).
**Stage 9 (`skills/`) did not run — owner gate.**

### What moved

| from | to |
|---|---|
| `worldbuilding/` | `design/Jawa/worldbuilding/`; `Custom_World`, `faction_authoring_mechanism`, `balance_paradigm` → `design/RimMandrake/` |
| `runtime/*.md` | 8 generic → `design/RimMandrake/`, 6 scenario → `design/Jawa/` |
| `runtime/{logs,latency_*.json}` | `observed/2026-08-13/` |
| `runtime/backups/*` | `deployed/config/` (ModsConfig, `Mod_*.xml`, RimSort userRules, `xenotypes/`) |
| `runtime/art/` | `src/Jawa/art_bench/` |
| `mods/*.md` (8 decisions) | `design/Jawa/mods/` |
| `mods/{live_mod_inventory.md,inventory,dumps}` | `observed/2026-08-13/` |
| `mods/dev/RimDefDump` | `src/RimMandrake/RimDefDump/` |
| `custom_patches/` | six `Jawa*`/`DesertVehicleReskin` → `src/Jawa/`; `MissingArtFixes`, `WreckedMachines` → `src/RimMandrake/`; `DEPLOY_HOLD.txt` → `src/` |
| `bridgetools/`, `Utils/` | `src/RimMandrake/` — `Utils/` as **one unit** (§4 dep 6) |
| `player_maps/` | `src/RimMandrake/mapsynth/` (`.py`, `authored/`), run outputs → `mapsynth/runs/` |
| `savegame/`, `image_request/`, `agents/`, `queue/`, `output/`, `disposing/`, 16 root files | per §2 |

⚠️ **The `observed/` stamp above was originally created as
`observed/2026-08-13_pre-restructure/`** — a name this script invented, which read
as an archive snapshot when the directory is in fact the *live* home for observed
game state. Renamed to `observed/2026-08-13/` on 2026-08-13 (the stamp is the
axis, per `observed/README.md`); the paths in this log and in
`do_restructure.sh` / `fix_refs.py` were rewritten to match.

`runtime/`, `mods/`, `custom_patches/`, `player_maps/`, `savegame/`,
`image_request/`, `worldbuilding/`, `agents/`, `queue/`, `output/`,
`disposing/` **all cease to exist.** Root now holds `CLAUDE.md`, `.gitignore`,
the seven tier dirs, and `skills/`.

### The dependency the plan missed

**§4 has no entry for repo-root derivation, and it was the sharpest hazard.**
Nine scripts in `Utils/` compute the repo root by counting `..` upwards
(`ROOT = os.path.dirname(HERE)`), which was correct while `Utils/` sat one level
below the root. It now sits **three** levels below, so every one of them silently
resolved to `src/RimMandrake/` — a root that exists, so nothing raises; the
scripts just read and write the wrong tree. Same shape in `Utils/jawavoice/`
(two → four) and in each `src/<tier>/<mod>/Source/` generator (three → four).
All fixed in `fix_refs.py`'s targeted pass.

`bridgetools/` is the **counter-example worth keeping**: it resolves
`<up-two>/Utils`, and because `bridgetools/` and `Utils/` moved together they are
still siblings, so those two `sys.path` inserts needed no change at all. That is
dep 6 paying off.

### Checks

| check | result |
|---|---|
| `ls runtime` | **ERRORS** ✔ — the sharpest single check, §8.2 |
| `git status --porcelain` | 556 `R`, no bare `D` ✔ |
| `check_refs.py` | **18 BROKEN** vs 21 baseline ✔ (was 26 mid-pass; 5 stale backslash refs and 3 sweep artifacts fixed) |
| `doc_budget.py` | exit 0, **299** markdown files — no class stopped matching ✔ |
| `deploy_custom_mods.py` plan-only | lists all 8 mods from `src/`, holds read from `src/DEPLOY_HOLD.txt` ✔ |
| `selftest_deploy_hold.py` | **4/4** ✔ (its fake repo needed the tier level too) |
| `status.py`, `whats_new.py`, `harvest_log.py` | exit 0 ✔ |

### Deliberate calls

- **`custom_patches/README.md` → `src/Jawa/README.md`**, not `src/README.md`:
  the tier README from stage 0 already owns that name and the plan forbids
  renames (§2). No content changed.
- **Bare root filenames were NOT rewritten in prose.** `check_refs.py` resolves
  a bare basename anywhere in the tree, so `TODO.md` still resolves; rewriting
  every mention would have touched hundreds of prose lines for no gain. They
  *were* rewritten wherever they carry an absolute prefix, and in the three
  scripts that open them by name (`doc_budget.py`, `whats_new.py`, `status.py`).
- **`mods/dumps/capture_manifest.py` stayed with its dumps** in
  `observed/<stamp>/dumps/`. §2's note wants it in `src/RimMandrake/`; the
  execution brief said move `mods/dumps/` whole. Left as a `[?]` follow-up.
- **`observed/**` payload rules already covered `runtime/logs/`**, so that
  `.gitignore` stanza became `**/logs/Player*.log` — a log dropped anywhere is
  still refused.
