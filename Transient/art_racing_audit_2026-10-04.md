# Art racing audit — ART_VERSION_WRANGLING_1 (2026-10-04)

Owner, verbatim: *"different versions of art are now racing. I even saw some older art I liked being
replaced for reasons I don't understand."* This audit covers every route that writes or picks art,
project-wide. It is read-only and changes no art.

## 0. Headline

1. **A live race, proven on disk and in the load order (the worst case).** 45 texPaths are shipped by
   two of our mods with **different art**. RimWorld resolves a texture from the **last-loaded** mod
   (`ContentFinder<T>.Get` walks `RunningModsList` from the end; read from the decompiled 1.6 source
   via RimSage). In the live `ModsConfig.xml` (638 active), `mandrake.rsw.swbestiary` sits at index
   **605**. That is after `iriazartoverride` (307), `nunaartoverride` (308), `rsw.patches` (552) and
   `dalgoartoverride` (574). **SWBestiary's older absorption-port copies (2026-09-09/12) therefore
   shadow the painterly override art wired on owner rulings 2026-09-13→17.** The deployed folders hold
   both copies. Subjects affected: Nuna (6 paths), Iriaz (3), Dalgo (3), Bantha (12, where
   StarWarsPatches has a 512px redraw), and Eopie (21, same pattern). The perceptual distance between
   the copies is 10–73 of 256 bits, so this is genuinely different art, not halo noise. The Nuna and
   Iriaz overrides *declare* `loadAfter swbestiary`, but the live list order wins anyway.
   ⚠️ No one has yet looked in game; the evidence is source plus deployed files plus load order.
2. **No code path consults an owner ruling before overwriting a texture**, except
   `LanternDeeps/wire_art.py`, which copies only `keep` rows. Every other writer overwrites in place
   silently and keeps no prior version (the table in §1).
3. **The artpipe registry has never recorded one verdict, commit or deploy.** `registry.jsonl` holds
   3,576 generated, 2,815 queued, 79 withdrawn and **0** accepted, committed or deployed events.
   `art_status.json` reports 2,018 targets `awaiting_verdict` and 0 accepted. Owner rulings live only
   in review-sheet JSONs, and wiring happens by hand-commit. So the pipeline cannot know what the owner
   kept.
4. **Rulings and renders don't share a key.** Review-sheet keys (`A_AA_BoulderMit`, `arpeau_a_v1`,
   `RSW_Anooba`) and artpipe job ids (`desert_swaca_gizka_east`) are different keyspaces. A fuzzy join
   links only 0–26 of each sheet's keeps to any render. "Which render did he keep?" is answered by a
   per-script hand map (`JOB_MAP`, `SET_DIR`), or not at all.

## 1. Write paths: who writes art, and what they trust

| Writer | Writes | Authority for "which art" | Checks owner ruling? | Keeps prior? |
|---|---|---|---|---|
| `src/RimMandrake/Utils/artpipe/artpiped.py` (daemon) | `_artsrc/<id>/` only, never `Textures/` | the job JSON | no | keeps raw + pre-downscale source |
| `artpipe/fill_queue.py` | queue only | CSV rows; **no check that art already exists** | no | n/a |
| `artpipe/apply_verdicts.py` → `artreg.py verdict` | registry events | sheet decisions | yes, but **never run**: 0 verdict events | append-only |
| `artpipe/artreg.py` committed/deployed | registry events | caller's say-so, **never checked against disk** | n/a | append-only |
| **`artpipe/artpipe_state.py collect`** (l.160-186) | **copies `_artsrc` → `src/**/Textures`** | done/ manifest (`--allow-failed` skips even that) | **no** | **no**: `copy2` l.183; sha logged to `collected.jsonl` only *after* the overwrite |
| `src/RimMandrake/LanternDeeps/wire_art.py` | Textures | deeps decisions.json + `JOB_MAP` | **yes (`keep` only, l.180)**; `--all-pass` bypasses it | no |
| `src/RimMandrake/TheRot/port_fauna.py` | Textures | hard-coded `CREATURES`/`SET_DIR` | no | no, re-runnable overwrite |
| `src/RimMandrake/Utils/gen_races_mod.py` | Textures | donor textures | no | no (overwrites on size change) |
| `outline_faction_icons.py`, ~48 per-mod `Source/*.py` (vehicle reskins, north fixes, absorption gens, placeholder makers) | Textures | hard-coded paths | no | no |
| mechanical sweeps (e.g. `1135036ce` halo zeroing, 241 files; `cf3aee40b` %4 padding, 87) | Textures in place | none needed | no | git only |
| hand-commits by agents ("wire landed regens", 53 of 71 commits) | Textures | the agent's judgement | **sometimes**: 18 of 71 commit subjects cite a ruling | git only |
| `src/RimMandrake/Utils/deploy_custom_mods.py --apply` | game `Mods/` | **repo always wins** (`filecmp`, l.269) | no; only brake is `src/DEPLOY_HOLD.txt` | no; `--prune` deletes game-only files |
| **the game's load order** | (picks at runtime) | last-loaded mod with the texPath | no | n/a. This is the racing writer in §0.1 |

## 2. Measured overwrites (git, 2026-08-20 → 2026-10-04)

`git log --diff-filter=M -- 'src/**/Textures/**'`:

- **71 commits modified 774 existing PNGs** (623 distinct paths). For comparison, 7,639 PNGs were
  added, 169 deleted and 2,959 renamed (renames are mostly mod moves and absorptions).
- **Only 18 commits (119 PNGs) name a ruling in the subject. 53 commits (655 PNGs) do not.** 328 of
  those 655 are the two mechanical sweeps (halo, padding), which change pixels without changing art.
  Netting those out leaves **~327 art-changing overwrites with no cited ruling.**
- **73 paths were overwritten more than once.** The churn is concentrated in the Pyrelands painterly
  fight of 2026-09-13→17. Gizka_east was rewritten 6×, and Gizka north/south, Iriaz_south, all six
  Nuna facings and Mantistanis_south 5× each. Anooba, Orray, Zeer, FireHawk and FurnaceBeast were
  rewritten 3–4× each. The sequence ran: canon-lawset install `dde341c12` → painterly revert
  `645b93f2e` → painterly regen `f209d892c` → **reverted the same day `7c9f2c7b7`** → re-applied
  `3a255e2bb` → approved wave `9e7e773a0` → owner locks `bd9a1b8ee`/`de46f98c1` → halo sweep. Each
  step was an in-place overwrite with no prior variant kept outside git.
- Earlier churn: the landmark icons (VEE_DustBowl and VEE_SaltPlains 3× each, 2026-08-25/26) and the
  desert vehicle reskins (CoveredCarriage_south 3×, 2026-08-21/22).
- **Overwritten after a keep ruling, on the same subject:** `arpeau_a`, `dulcisgrown_a` and `nuitae_a`
  were kept on the Deeps sheet 2026-09-18. `06966e55d` (2026-09-20, no ruling cited) then overwrote
  the **RotSporeKit** copies of the same plants with Rot-wave renders. Each mod's own copy is now
  different art for one species. Arpeau has live textures in three mods: LanternDeeps `VellokReed`,
  UtinniPatches `BMT_Caverns`, and TheRot `RotSporeKit`.
- **Basenames in more than one mod: 173, of which 55 differ.** Most are distinct subjects that share
  a name (e.g. the Armoury apparel). The 45 *same-texPath* collisions are the race in §0.1.

## 3. Kept-but-not-live, and live-without-ruling

Method: a perceptual 16×16 dHash of all 7,928 `src/**/Textures` PNGs and all 2,685 `_artsrc`
renders. A distance of 24/256 or less counts as "live". The sanity probe was Gizka: 6 renders were
found, and the matched ones were live.

- **1,525 of 2,530 `_artsrc` render stems match a live texture, and ~1,005 do not.** This is expected
  in bulk, because most are rejects or still awaiting a verdict. The registry cannot say which,
  because it has no verdicts.
- **Kept, but no render of that subject is live** (UNVERIFIED candidates; perceptual match only):
  - `desert_art_verdict_2026-09-20`: RSW_Corinathoth, RSW_Gutkurr, RSW_Hrumph, RSW_Mynock.
  - `longshade_fills_art`: maidenbloom, tazzok.
  - `deepfire_pigment_review`: deepfire_crowncarpet_b.
  - `desert_art_review_2026-10-03`: 6 of 26 joinable keeps. This is **correct for now**: the owner
    held wiring (`1ef6e06e7`).
- **Kept *and live* is not proof the kept variant is the one showing.** §0.1 shows an approved
  override can be live on disk and still lose at runtime.
- **Live art with no ruling: UNMEASURABLE mechanically.** Rulings carry no texPath and no job id, and
  0 of 1,081 `creature_register` keeps and 0 of 241 `creature_art_register` keeps join to a render.
  The proxy is §2: ~327 unruled art-changing overwrites plus 7,639 additions, almost none of which
  cite a ruling.
- **Rulings themselves decay.** 21 of the 45 `*.decisions.json` files ever committed live in
  `Transient/` (14-day shelf life), and 3 are already deleted
  (`ab_size_recheck_2026-09-19`, `forsaken_crags_fauna_sheet`, `pawn_flavor_register`). His
  rulings are stored in the bin directory.

## 4. Parallel registries, and where they disagree

| Registry | Where | Keyed by | Says what is "current"? | Disagreement |
|---|---|---|---|---|
| `registry.jsonl` | `D:\Luke\dev\_artpipe` | job id / target | it would, but 0 verdict, commit or deploy events | believes all 2,018 renders are unjudged, though hundreds are wired |
| `art_status.json` | same | target (2,167) | projection of the above | same blindness; shows "accepted 0" |
| `collected.jsonl` | same | job id → dest + sha | only for `collect` copies | silent about hand-wired and port-script copies |
| `*.decisions.json` (21 in Transient, 22 in design/) | repo | per-sheet keys, 10+ verb vocabularies (keep, approve, right, ok, current, replace, regen, redo, revise, cut) | per sheet, at that date | a later sheet on the same subject silently outranks an earlier one; "replace" means *replace donor*, not "reject"; nothing records precedence |
| `decisions_propagated.json` (+ `flora_…`) | `design/Jawa/worldbuilding/review/round2/` | defName | cited by items as authority | **no script reads or writes it**; hand-edited |
| canon library `## ruling` | `design/RimStarWars/canon_references/` | species | canon target, not a variant pick | no link to renders |
| creature art register | retired 2026-09-11 | defName | (dead) | its decisions file is still in `design/` with 241 keeps |
| per-script maps (`JOB_MAP`, `SET_DIR`, `CREATURES`) | in code | job id → texPath | **the actual wiring authority** | one per mod, unaware of each other |
| game load order | `ModsConfig.xml` | texPath | **the final word at runtime** | overrides all of the above (§0.1) |

That makes **nine places that can claim "current", and none is authoritative.**

## 5. One source of truth: options

What every option needs:
- A **subject id**: one per creature or plant (defName-level), with facets for facing and variant.
- A **variant** record: render, port, hand, or donor, with sha256, provenance and date.
- **Owner rulings** attached to a variant, never to a sheet key.
- **Exactly one `live` variant per (subject, texPath)**, plus a guard.

### Option A: Guard-only (cheapest, ~1 day)
- A pre-commit hook that refuses modifying or deleting a PNG under `src/**/Textures` whose path
  appears in a small hand-seeded `art_locks.json` (path → ruling quote + date), unless the commit body
  carries `Art-ruling: <ruling ref>`.
- A selftest that fails when one texPath is shipped by two of our mods with different bytes.
- Fix the 45 collisions now: delete the losing copy, or make the override load last.
- **Cost:** small. **Gap:** it does not unify the registries or let him compare variants; locks must
  be seeded by hand.

### Option B: Art ledger (recommended, ~4–6 days)
- `infrastructure/state/art/ledger.jsonl`, append-only and sharded per seat like the rimflow ledger,
  plus a rendered `art_index.json` (subject → variants → ruling → `live`).
- **Writers must go through one CLI**, `art install <subject> <variant> --ruling <ref>`. It is the
  only code that copies into `Textures`; `collect`, `wire_art`, `port_fauna` and the hand-wires all
  call it. It refuses to replace a variant ruled `keep` unless given a newer ruling, and archives the
  displaced bytes to `D:\Luke\dev\_artpipe\_superseded\<subject>\` with sha.
- Review sheets write rulings into the ledger keyed by **variant sha**, not by sheet key, so a ruling
  survives Transient expiry and renames.
- **Compare-all-variants sheet generator:** for one subject, show every variant ever seen (git
  history blobs + `_artsrc` + `_superseded` + donor), the live one marked, and every past ruling with
  its quote. This answers "the older art I liked" directly. Git history alone recovers every
  overwritten blob for the 623 paths in §2.
- A pre-commit hook (Option A's) plus a collision selftest, both reading the ledger instead of a
  hand list.
- `registry.jsonl` keeps generation telemetry only, and the ledger owns verdict/live.
  `art_status.json` and `decisions_propagated.json` become projections, or are deleted.
- **Migration:**
  1. Backfill variants from git (`git log --all` blobs for every Textures path) plus `_artsrc` plus
     `collected.jsonl`.
  2. Backfill rulings from the 43 decisions files, matching on texPath where one exists and
     otherwise via a one-time `subject_alias.json` built from the per-script maps (`JOB_MAP` etc.).
  3. Mark the current on-disk bytes `live`, and **flag every subject where a ruled `keep` variant is
     not the live one**. That list goes to him as a compare-all sheet, one biome at a time, per his
     biome-by-biome ruling.
- **Cost:** the backfill is mechanical; the alias table is the only judgement step. **Gap:** it needs
  discipline that every wire goes through the CLI, which the hook enforces.

### Option C: Content-addressed art store (~2 weeks)
- All variants live in `_artstore/<sha>.png`. Mod `Textures/` become build outputs, materialised by
  `deploy_custom_mods.py` from the ledger's `live` pointers, so nothing hand-edits `Textures/`.
- **Cost:** large. It touches every mod's build and the 7.9k existing files, and changes the edit loop
  every seat uses. **Gain:** overwriting kept art becomes structurally impossible, and racing
  copies cannot exist.

### Recommendation
**Do Option A's collision fix and hook today, then build Option B.**
- The §0.1 race is a live defect regardless of design. Remove the SWBestiary copies of
  Nuna/Iriaz/Dalgo/Bantha/Eopie, or make the overrides load after it, but only after he confirms the
  override art is the one he likes, through a compare sheet.
- B fixes the actual failure: rulings stored where no writer looks, under keys no writer can join.
- C is B plus enforcement-by-construction. Revisit it only if the B hook is bypassed in practice.

Owed as filed work (not filed by this audit):
- `ART_TEXPATH_COLLISION_1` (the 45 paths).
- `ART_LEDGER_SOURCE_OF_TRUTH_1` (Option B).
- Move the 21 Transient rulings out of the 14-day bin before any expire.
