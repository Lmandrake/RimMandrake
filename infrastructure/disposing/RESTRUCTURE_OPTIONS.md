# RESTRUCTURE_OPTIONS.md — four layouts for the top level

Proposal only. Nothing was moved. The owner picks; execution is a separate job.

---

## 1. Measured facts

`du` / `git ls-files`, taken fresh. **Tracked** is what git carries; **total** is disk.

| dir | total | tracked | files (tracked) | what is actually in it |
|---|---|---|---|---|
| `hand_authored_maps\` | 467M | 0M | 49 | 49 downloaded `.rws` worlds; payloads gitignored, only per-world `README.md` tracked |
| `mods\` | 419M | 17M | 46 | **430M is `mod_sources\` (61 third-party mods, gitignored)**. Tracked = 12 loose `.md`, `inventory\` (17M generated CSV), `dumps\`, `dev\RimDefDump`, `inspiration\` |
| `Utils\` | 49M | 48M | 95 | **47M is one research PDF.** Real content: 64 flat `.py`, 3 `.sh`, 4 sub-benches (`rimbench`, `jawavoice`, `ilprobe`, `_speakup_src_1p6`) |
| `savegame\` | 33M | 31M | 2 | 2 binary `.rws` (13.6M + 17.7M) tracked; the 6 report files beside them are gitignored |
| `runtime\` | 28M | 27M | 97 | **Four unrelated classes**: 17 design `.md`, `backups\` (25M salvaged game DLLs), `art\` (the art bench), `logs\` (ignored), latency JSON |
| `custom_patches\` | 28M | 27M | 165 | 7 authored mod folders + `README.md` + `DEPLOY_HOLD.txt`. Only one (`Jawa_Patches`) is patches |
| `worldbuilding\` | 23M | 23M | 34 | Campaign fiction + design, 5 PNG/PDF (16M atlas), 2 rendered `.html` |
| `samuel_streamer_study\` | 20M | 20M | 62 | Downloaded mod-lists + config zips. Research |
| `promo\` | 12M | 12M | 3 | 5.6M HTML pitch + 2 PNG. Zero inbound refs |
| `player_maps\` | 6M | 5M | 127 | Generator scripts + plans + outputs + before/after PNGs, all in one flat folder |
| `image_request\` `skills\` `bridgetools\` `disposing\` `queue\` `agents\` `reference\` | <1M each | | 38/7/5/5/2 | |

Root: **22 `.md`** files.  `.git\` is **274M**.

Largest tracked blobs: `Utils\Jawa_Visual_Research_Dossier_v2_Image_Dense.pdf` 46.7M ·
`savegame\24_Bounty_Hunter__starting_save.rws` 17.7M ·
`worldbuilding\star_wars_species_scale_reference_atlas.pdf` 16.0M ·
`runtime\backups\TribalFurniture-strayAssemblies\Assembly-CSharp.dll` 15.0M ·
`savegame\03_Gravtasm__starting_save.rws` 13.6M · `promo\Kolyska_pitch.html` 5.6M.

**Regenerable / third-party / research / authored is not the same cut as subject
matter.** By tracked bytes: research ≈ 36M, third-party salvage ≈ 20M, generated
≈ 17M, binary saves ≈ 31M — roughly half the tracked repo is not authored work.

## 2. Structural defects the facts expose

| # | defect | evidence |
|---|---|---|
| 1 | `runtime\` is a drawer, not a subject | 17 design `.md` sit beside 25M of salvaged DLLs, an art bench and ignored logs. Already ratified as such: *"`runtime/` was the case that forced the rule — it is a decision-doc drawer, not one subject"* (`STRUCTURE.md`) |
| 2 | `Utils\` is 97% not-tooling by bytes | one 47M research PDF in a folder `STRUCTURE.md` §7 calls **"Tooling only."** `STALE_FILE_AUDIT.md` A:39 already votes DELETE |
| 3 | `custom_patches\` is misnamed | it holds 7 complete **mods**, not patches. Its own deploy script's docstring calls it *"the SOURCE of our authored mods"* |
| 4 | `agents\` and `queue\` share all five basenames | the five per-seat `.md` basenames exist twice. A bare-basename reference is ambiguous |
| 5 | `agents\`, `queue\`, `disposing\` are absent from the manifest | zero mentions of `queue/` and `agents/` in `STRUCTURE.md`; `disposing/RimMaster.md` is filed under the **`runtime/`** heading |
| 6 | binaries live in git | 274M `.git` for a repo whose text is a few MB. `savegame\*.rws`, the two PDFs and `promo\` are 100M+ of tracked, never-diffed blobs |
| 7 | `player_maps\` is an unswept bench at root | scripts, plans, outputs and 8 already-convicted orphan reports in one flat folder |

## 3. Hard dependencies — must survive every option

| dependency | breaks if… | fix cost |
|---|---|---|
| `.claude\skills\*` are **relative symlinks** to `..\..\skills\<name>` (5 of them) | `skills\` moves | 5 symlinks, but a silent harness failure if missed. **Pin `skills\` at root.** |
| `Utils\deploy_custom_mods.py` `SRC_ROOT = ROOT/"custom_patches"` | `custom_patches\` moves or renames | 1 line |
| Steam deploy targets, hardcoded in `Utils\deploy_custom_mods.py`, `Utils\game_paths.py`, `Utils\ilprobe\meta*.py`, `bridgetools\build.py` | never — they point **out** of the repo | none |
| `.claude\settings.json` hooks → `${CLAUDE_PROJECT_DIR}/.claude/hooks/*.py` | `.claude\` moves | n/a, `.claude\` is fixed |
| Docs and skills invoke `Utils\*.py` **by path**: `refresh.py` ×26, `deploy_custom_mods.py` ×24, `whats_new.py` ×18, `doc_budget.py` ×10 | `Utils\` moves | large, see §4 |

**Not a hard dependency, contrary to a note on record:** `Utils\Savegame_*.py`
reference `../save_authoring_pipeline.md` and `../rimworld_file_lore.md` in
**docstrings only** — no code reads them. Those two root files are movable.

## 4. Reference cost baseline

Occurrences of `<dir>/` across all tracked `.md .py .sh .json .xml .txt`.
`python3 Utils\check_refs.py` reports **25 BROKEN / 160 UNVERIFIED across 194 docs
(2595 path refs)** *before* any move — the checker exists and works, so post-move
repair is mechanical, but it is not free.

| dir | refs | files | | dir | refs | files |
|---|---:|---:|---|---|---:|---:|
| `Utils\` | **322** | 110 | | `player_maps\` | 54 | 17 |
| `skills\` | **149** | 63 | | `bridgetools\` | 39 | 16 |
| `mods\` | **139** | 49 | | `agents\` | 36 | 18 |
| `runtime\` | **104** | 37 | | `savegame\` | 25 | 13 |
| `worldbuilding\` | **101** | 44 | | `disposing\` `image_request\` | 12 · 12 | 3 · 8 |
| `queue\` | **100** | 29 | | `samuel_…\` `reference\` | 11 · 9 | 5 · 5 |
| `custom_patches\` | **92** | 50 | | `hand_authored_maps\` `promo\` | 6 · 4 | 4 · 4 |

**Total 1215.** Renaming `Utils\` alone costs more than every option in §5 D.

---

## 5. The options

### A — By seat ownership

> One top-level directory per seat; a thing lives where its owner sits.

```
bridge\      bridgetools\, latency\, bridge probes, rimbridge design
ops\         mods\, savegame\, logs\, backups\
create\      custom_patches\, image_request\, art\
vision\      worldbuilding\, hand_authored_maps\, samuel_streamer_study\, player_maps\
project\     agents\, queue\, disposing\, the root spine
shared\      Utils\, skills\
```

| | |
|---|---|
| **Obvious** | Where new work goes *if you already know your seat*. Review scope. Which seat to ping. |
| **Hides** | That anything is third-party, generated or research — every trust class appears in every seat dir, so gitignore and backup rules can no longer be stated per-directory. Also hides shared artifacts: `custom_patches\` is authored by one seat, validated by another, deployed by a third. |
| **Helps** | A new seat on day one. |
| **Cost** | **~930 refs.** `Utils\` (322) cannot be assigned — it lands in `shared\`, which is the axis conceding defeat on its largest directory. |

### B — By artifact lifecycle

> Directories are pipeline stages: intent → source → deployed → observed.

```
design\      worldbuilding\, the 17 runtime\*.md, mods\*.md decisions
src\         custom_patches\ (mods), bridgetools\, Utils\, skills\, mods\dev\
deployed\    (empty by design — the Steam Mods folder is this tier; documented, not stored)
observed\    logs\, backups\, mods\dumps\, mods\inventory\, savegame\, player_maps outputs, latency
vendor\      mods\mod_sources\
research\    hand_authored_maps\, samuel_streamer_study\, reference\, the two PDFs
coord\       agents\, queue\, disposing\, root spine
```

| | |
|---|---|
| **Obvious** | What is regenerable — `observed\` is disposable wholesale, which makes gitignore, backup and `.git` weight one rule per top dir. Also makes the **"writing a file is not deploying it"** trap structural rather than a warning in `CLAUDE.md`: `src\` and `deployed\` are visibly different tiers. |
| **Hides** | Subject. The gravship is spread across `design\`, `src\` and `observed\`; so is the armoury. Seat ownership becomes invisible. |
| **Helps** | the docs seat (staleness, `.git` weight) and a retired seat (what can be thrown away and rebuilt). |
| **Cost** | **~1066 refs** — everything except `skills\`, which must stay pinned by the `.claude\skills\` symlinks and therefore breaks the scheme's own tidiness. |

### C — By trust class

> Directories answer "may I trust and edit this?", not "what is it about?".

```
authored\    custom_patches\, Utils\, bridgetools\, worldbuilding\, agents\, queue\, root spine
generated\   mods\inventory\, mods\dumps\, logs\, art\, player_maps\, savegame reports, latency
thirdparty\  mods\mod_sources\, runtime\backups\ (salvaged game assemblies)
research\    hand_authored_maps\, samuel_streamer_study\, reference\, the two PDFs
skills\      (pinned)
```

| | |
|---|---|
| **Obvious** | Editability. *"Never hand-edit a `generated\` file"* and *"never commit `thirdparty\`"* become enforceable by path, not by memory. Directly answers §1's finding that half the tracked repo is not authored. |
| **Hides** | Everything else. `authored\` absorbs ~60% of the tree, so the axis stops discriminating exactly where the most work happens. Regenerating `generated\x` means finding its producer in `authored\Utils\` — the script and its output are never adjacent. |
| **Helps** | A cold agent asked to clean, back up or gitignore. Nobody doing daily work. |
| **Cost** | **~1066 refs**, same as B, for a shallower payoff. |

### D — Minimal change: fix the seven defects, rename nothing large

> Keep every high-reference name; correct only what §2 proves is wrong.

```
runtime\             SPLIT: keep observed only (logs\, backups\, art\, latency_*.json)
  → design .md       move the 17 to worldbuilding\ or mods\ by subject
custom_patches\      → custom_mods\        (optional; honest name, 92 refs)
Utils\*.pdf          → reference\          (or delete — already convicted)
worldbuilding\*.pdf  → reference\
savegame\*.rws       untrack (keep on disk); git-lfs or GDrive
promo\               → disposing\promo\    pending owner
queue\<SEAT>.md      → queue\<SEAT>_queue.md   (kills the basename collision)
STRUCTURE.md         add agents\, queue\, disposing\ to §7; refile disposing\RimMaster.md
```
Then tag every top dir in `STRUCTURE.md` with B/C's vocabulary —
`authored · generated · third-party · research · observed` — as **metadata, not
directories**. `STRUCTURE.md` already uses 📜 📚 ⚙️ 🗑️ glyphs; this formalises them.

| | |
|---|---|
| **Obvious** | Nothing new by itself — the *tags* carry what B and C buy structurally, at zero path cost. |
| **Hides** | Nothing it does not already hide. It does not force anyone to relearn the tree. |
| **Helps** | Everyone, immediately; costs nobody a relearn. |
| **Cost** | **~50 refs** without the `custom_patches\` rename, **~145 with** (92 refs + 1 line in `deploy_custom_mods.py`). The `runtime\` design-doc moves are ~45 of `runtime\`'s 104. |

---

## 6. Recommendation

**Take D, plus B's tagging vocabulary applied to `STRUCTURE.md` §7.**

1. The single test — *can a seat tell where a thing lives and where new work
   goes?* — fails today at seven specific points, not globally. Six of the seven
   are one directory or one file. A 1000-reference rewrite to fix seven defects
   is not proportionate.
2. **Ownership is already defined in `agents\*.md` and works.** The tree does not
   need to restate it; §5 A's own `shared\` bucket admits the largest directory
   will not fit the axis.
3. **The trust distinction is real and worth having — as a column, not a
   folder.** B and C both correctly identify that provenance decides backup,
   gitignore and trust. Neither needs a directory to deliver it. Tagging costs
   one table edit; the directories cost 1066 references.
4. Do the `runtime\` split **first and alone**. It is the only defect that is a
   genuine structural wrong, its verdict is already ratified, and it is the one a
   new seat actually trips over.
5. **Untracking the binaries is independent of all four options and should
   happen regardless** — 100M+ of `.rws`, PDFs and `promo\` in a 274M `.git` for
   a text repo. Zero reference cost.

**Reject A (seat ownership).** It scores worst on cost among the three
restructures (~930) while being the only one that *increases* ambiguity for the
artifacts that matter most: every authored mod passes through three seats, so
each one needs an arbitrary home and a cross-reference back. It also fights three
hard dependencies at once — the `.claude\skills\` symlinks, `SRC_ROOT` in
`deploy_custom_mods.py`, and 322 `Utils\` references that no single seat owns.

**If the owner wants a real restructure anyway, take B, not C.** B's stages are
adjacent to how work actually moves; C's `authored\` swallows most of the tree.
Pin `skills\` and `Utils\` at root in either case — together they are 471 of the
1215 references, and pinning them converts a ~1066-reference move into ~590.

## 7. Contradictions to resolve before executing anything

| item | on record | this doc says |
|---|---|---|
| `Utils\...Dossier_v2.pdf` | `STALE_FILE_AUDIT.md` A:39 — **DELETE** | move to `reference\` instead; it is 47M of primary research and the `Utils\`→`reference\` move already has precedent |
| `Utils\Savegame_*.py` root deps | recorded as *"hard-code `../<file>.md`"* | **docstrings only**; those two root files are movable |
| root file count | `STRUCTURE.md` §7 — *"Fourteen files… nothing else"* | 22 exist. Not addressed by any option here; it is a doc-budget job, not a layout job |
| `disposing\RimMaster.md` | filed under `STRUCTURE.md`'s `runtime\` heading; `STALE:125` calls it `runtime\`'s | it is in `disposing\`; defect #5 |
