# Audit — `research/` and `vendor/`, plus stray archives — 2026-08-20

**Scope:** `research/` (566 MB) · `vendor/` (455 MB) · every `*.zip` / `*.7z` /
`*.tar*` / `*.rar` and every extracted third-party tree anywhere in the repo.
**AUDIT ONLY.** Nothing was deleted, moved or `git mv`'d.

---

## Headline

| | |
|---|---|
| **Total reclaimable** | **789 MB** — 311 MB DELETE, 478 MB QUARANTINE |
| **Of that, TRACKED** | **20 MB** (one group: `samuel_streamer_study/configs/`) |
| **Of that, UNTRACKED** | **769 MB** — free to remove, costs nothing in clone size |
| **Tracked files over 50 MB** | **NONE.** See §3 |
| **`.gitignore` coverage** | Complete. `git status --untracked-files=all` returns **0** untracked-and-unignored files under either tree |

🔑 **The bulk is already off git.** `vendor/` is 455 MB with **8 tracked files**;
`research/` is 566 MB with **149 tracked files** totalling ~52 MB. The repo rule
("commit provenance, not bulk") is being honoured almost everywhere. The finding is
about **disk**, not history — with two exceptions, both flagged below.

---

## 1. Ranked by bytes reclaimed

| # | path | size | tracked? | copy of / re-fetchable from | referenced by | verdict | why |
|---|---|---|---|---|---|---|---|
| 1 | `D:\Luke\dev\Rimworld\research\RimMandrake\hand_authored_maps\` | **453 MB** | payload **NO** (29 `README.md` = 31 KB tracked) | 40 GitHub map repos, pulled via `https://api.github.com/repos/OWNER/REPO/zipball`; census in `research\RimMandrake\reference\rimworld_handcrafted_map_atlas.md`, per-world source URL in each tracked `README.md`, plus `Download Instructions.txt` | **Only** `design\RimMandrake\beautiful_tilemap.md` — a doc whose own first line is *"Status: `[v2]` concept. Nothing built."* No script reads it (`grep hand_authored_maps src/ skills/` → 0 hits) | **QUARANTINE** | 44 `.rws` (186 MB) + repo cruft supporting a v2 concept with no code behind it. Fully re-fetchable and the provenance is committed — but it is the only copy, so dwell rather than delete |
| 2 | `D:\Luke\dev\Rimworld\vendor\mod_sources\**\{bin,obj,packages,.vs}\` | **201 MB** | NO | MSBuild/NuGet output of *third-party* mods. 65 MB of it is 10 `Lib.Harmony.*.nupkg`; 116 MB is `.dll`, 18 MB `.pdb` | nothing | **DELETE** | Build intermediates of somebody else's mod. We never build these; the repo already ignores `obj/` for our own code for exactly this reason |
| 3 | `D:\Luke\dev\Rimworld\vendor\mod_sources\Outer-Rim-*-main\` (9 dirs, 197 MB gross — **36 MB net of row 2**) | 36 MB net | NO | GitHub `*-main` branch zips (Zeta/Outer Rim) | `design\Jawa\mods\outer_rim_cherrypick_list.md`, `required_mods.md` — but by defName, not by file | **DELETE** | `design\V2_DREAMS.md:539` rules on these by name: *"All nine `vendor/mod_sources/Outer-Rim-*-main` extracts are **stale-branch pulls** — delete or clearly mark them, or a third pass reaches the same wrong answer."* They have already caused two wrong `supportedVersions` reads over six days. The Workshop copy on disk is the authority |
| 4 | nested archives inside `vendor\mod_sources\` (6 files, **56 MB**) | 56 MB | NO | zips of the tree that sits beside them | none | **DELETE** | `ReinforcedMechanoid2-main\Source\original_mod.zip` **34 MB** · `CustomQuestFramework-Old-src\QuestEditor_Library.zip` **15 MB** · `NWNRealFogOfWar-main\Source\original_mod.zip` 5.7 MB · `CaveworldFlora` 908 KB · `CaveBiome` 504 KB · `BiomesCore 1.5/1.6.zip` 512 KB. Each is the packaged form of the extracted source next to it |
| 5 | `D:\Luke\dev\Rimworld\vendor\salvage\TribalFurniture-strayAssemblies-2026-08-11\` | **19 MB** | payload NO (`MANIFEST.json` tracked) | `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\` | `infrastructure\STRUCTURE.md:151` (tier description only) | **DELETE** | Its own `MANIFEST.json` marks **every** moved DLL `"byte_identical_to_game": true` — 15.8 MB `Assembly-CSharp.dll` included. A byte-exact duplicate of files the game ships. The manifest is the artifact; the bytes are not |
| 6 | `D:\Luke\dev\Rimworld\research\RimMandrake\samuel_streamer_study\configs\` | **20 MB** | 🔴 **YES — 31 tracked `.zip`** | Google Drive links recorded verbatim in the tracked `00_MASTER_INDEX.md` | `design\RimMandrake\Custom_World.md` and `required_mods.md` cite `02_TECHNIQUE_ANALYSIS.md` and `lists/*.rml` — **never `configs/`** | **QUARANTINE** | The one place third-party bulk is *committed*. ⚠️ **Untracking reclaims 20 MB of checkout and 0 bytes of history** — git already has them (landed in `7e98004`, the re-init). Worth doing to stop the next one, not to shrink `.git` |
| 7 | `D:\Luke\dev\Rimworld\vendor\salvage\StrayBaseGameAssemblies-2026-08-11\` | **6 MB** | payload NO (`MANIFEST.json` tracked) | two Workshop mods' `Assemblies\` folders | `infrastructure\STRUCTURE.md:151` | **QUARANTINE** | Unlike row 5, its manifest flags `tickleyourpawn.core\mscorlib.dll` (5.4 MB) as **`"byte_identical_to_game": false`** — not a duplicate of anything, and it is the rollback net for two mods we stripped. Cheap to hold |
| — | `D:\Luke\dev\Rimworld\vendor\mod_sources\` (residual after rows 2–4, ~139 MB) | 139 MB | NO | GitHub branch zips | **live code references:** `src\RimMandrake\Utils\build_jawavoice.py:6` reads `_speakup_src_1p6\`; `skills\rimbridge\references\extending.md:16-17` and `skills\rimbridge\SKILL.md:416` read `RimBridgeServer-main\`; `src\RimMandrake\Utils\check_refs.py:54` excludes the path | **KEEP** | Real third-party XML/C# we read to answer def questions. See §4 for the one thing wrong with it |
| — | `D:\Luke\dev\Rimworld\research\Jawa\*.pdf` (2 files, 64 MB) | 64 MB | NO (gitignored by `research/**/*.pdf`) | owner-supplied dossiers | `design\Jawa\art\graphic.md:239` and `design\Jawa\mods\cherry_picker_killlist.md:211` — the latter calls the scale atlas *"already load-bearing"* and uses it to contradict a shipped gene | **KEEP** | `infrastructure\disposing\RESTRUCTURE_PLAN.md:68` already ruled: *"47 MB; do **not** delete for size"* |
| — | `D:\Luke\dev\Rimworld\research\Jawa\spinning_inspirational_generic_desert_planet.gif` | 22.5 MB | **YES** | owner-supplied | `design\Jawa\worldbuilding\the_one_map.md:50` — motion reference for the one map | **KEEP** | Largest tracked file in the repo but under the 50 MB line, and it is live input to the one thing the project is building. See §3 |
| — | `D:\Luke\dev\Rimworld\vendor\wisdom\` (132 KB, 5 files, all tracked) | — | YES | **ours** | `infrastructure\REFRESH.md:55`, `src\RimMandrake\Utils\def_diff.py:32,971`, `skills\rimworld-ideoligion\references\validation.md:287`, `src\RimMandrake\WreckedMachines\README.md:135` | **KEEP** | Not vendored at all — our writing about their mods, exactly as `vendor\README.md` intends |
| — | `research\RimMandrake\{reference,inspiration}\`, `installed_packageids.json` | 236 KB | YES | ours | `installed_packageids.json` is read by `build_packageid_index.py:47`, `preload_check.py:56`, `cherrypick_build.py:304` | **KEEP** | Live tooling input |

### Totals

| verdict | rows | bytes |
|---|---|---|
| **DELETE** | 2, 3, 4, 5 | **311 MB** (all untracked) |
| **QUARANTINE** → `infrastructure\disposing\`, 7-day dwell | 1, 6, 7 | **478 MB** (20 MB of it tracked) |
| **KEEP** | the rest | 712 MB |

---

## 2. Stray archives and extracted trees — full sweep

`find` across the whole repo (excluding `.git`) for `*.zip *.7z *.tar* *.rar *.gz *.bz2 *.xz`:

- **37 archives, ~76 MB total.** Every one falls in row 4 (56 MB, inside `vendor/mod_sources/`) or row 6 (20 MB, the tracked `samuel_streamer_study/configs/`).
- **No archives anywhere else in the repo.**
- **No decompiled-source trees** — `find` for `*decompil*`, `*ilspy*`, `*dnspy*` returns nothing. `research\RimMandrake\reference\rimworld_decompiled_source.md` is a *document about* decompiled source, not a copy of it.
- **No stray extracted mod folders outside `vendor/` and `research/`.** All 21 `About.xml` outside those trees are our own mods under `src\Jawa\` and `src\RimMandrake\`.
- `research\RimMandrake\hand_authored_maps\SickBoyWi_RimWorldMaps\` (240 KB) is a third-party C# project, explicitly named in `.gitignore` and correctly ignored.

---

## 3. Tracked files over 50 MB

**None.** Full scan of `git ls-files` by on-disk size:

| bytes | path | landed |
|---|---|---|
| 22,503,344 | `D:\Luke\dev\Rimworld\research\Jawa\spinning_inspirational_generic_desert_planet.gif` | `824d747` — *Owner's desert-world visual research and Star Wars cuisine/xenohusbandry design docs* |
| 14,207,047 | `D:\Luke\dev\Rimworld\world\WORLDMAP_source.rws` | (out of audit scope) |
| 14,178,821 | `D:\Luke\dev\Rimworld\world\WORLDMAP_gen.rws` | (out of audit scope) |
| 11,124,314 | `D:\Luke\dev\Rimworld\world\WORLDMAP_sub7b_source.rws` | (out of audit scope) |

Nothing else tracked exceeds 10 MB. The 50 MB rule and the 100 MB host limit are
both clear, with 2.2× headroom.

⚠️ **Note for the WORLD seat, out of scope but adjacent:** the three `world\*.rws`
files are tracked *despite* `.gitignore` line `*.rws`, because they were committed
before the rule. They are the hand-authored planet, so that is almost certainly
deliberate — but every future save of them writes a fresh 14 MB blob into history
permanently. Worth an explicit decision by whoever owns `world/`.

---

## 4. The one governance gap

🔴 **`vendor/mod_sources/` has 62 third-party trees, 431 MB, and ZERO committed
provenance.** No `MANIFEST`, no `SOURCE.txt`, no index doc — `find` for any of them
returns nothing, and no tracked file lists the 62 repos and the commits they came
from. The absence of `.git` directories in all 62 confirms they are flattened branch
zips, so the branch and commit they represent is **unrecoverable from the tree itself**.

That is the exact inverse of the project's own rule: the bulk is (correctly) ignored,
but the provenance that is supposed to replace it was never written. Combined with
row 3, it is *why* two independent passes read a stale `supportedVersions` — a
`*-main` folder on disk looks authoritative and carries no evidence of its own age.

**Recommended (one small tracked file, not a deletion):** `vendor\mod_sources\SOURCES.md`
— repo URL, branch, and fetch date per directory. It costs a few KB and makes rows 2–4
safe to delete, because everything removed becomes re-fetchable by command.

Second, smaller: `research\README.md` still describes a `MODLIST.md` that **does not
exist** — the file itself flags this at the bottom. Unrelated to size, but it is the
same shape of stale pointer.

---

## 5. Method

```
git ls-files <path> | wc -l          vs   find <path> -type f | wc -l
git ls-files -z | xargs -0 stat -c%s      → tracked files by size
git status --porcelain -uall <tree>       → gitignore coverage gaps (0 found)
grep -rn '<name>' --include='*.md' --include='*.py' --include='*.sh' \
     design/ src/ skills/ infrastructure/ vendor/wisdom/ CLAUDE.md
```

Reference counting for `vendor/mod_sources/` was done per-directory across all 62:
**34 of 62 (210 MB) are named in no tracked doc or script at all.** That set overlaps
rows 2–4 heavily, so it is not scored separately — but it is the pool to look at next
if more space is needed.
