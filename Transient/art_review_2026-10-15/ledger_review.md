# Art ledger: design review, 2026-10-15

Read-only review of the art ledger, measured against the problem it was built for. Scope:
- Code in `/home/mandrake/rm/foundry/src/RimMandrake/Utils/art/`: `art.py`, `artledger.py`, `art_guard.py`, `enact.py`, `sheet_freshness.py`.
- The design doc `/home/mandrake/rm/foundry/design/RimMandrake/art_ledger_design_2026-10-04.md`.
- The `ART_VERSION_WRANGLING_1` ledger notes. The item has **no prose file**: no `items/**/ART_VERSION_WRANGLING_1.md` exists, closed or live.
- The event shards, lessons, `git log`, and the store at `D:\Luke\dev\_artstore`.

Every number below comes from a query run today against the folded events (`artledger.read_events()`, archives included) or against disk and git. Zero results were cross-checked against a query that is able to see non-zero (noted inline).

## Verdict: PARTLY serving

**The core promise holds.**
- No mechanical writer displaced an owner-kept picture: 0 events. The same query sees 171 displacements that his rulings authorised, so it is able to see.
- Every live or protected picture whose bytes still exist is in the store.
- The repo's texture bytes match the ledger exactly: 0 DISK_DRIFT across 9,611 hashed PNGs.
- The one "you changed my art again" complaint after go-live was recovered from the store in about one minute.

**Three things are wrong.** The ledger has gaps of its own, it costs real friction, and the pain has moved downstream into the review sheets.
- **Gaps:** a ledger event and its PNG can be committed apart. Bookkeeping reasons are free passes. Protection drifts.
- **Friction:** the `mod` argument path trap, no CLI verb to put a file in the store, and moves of kept art that need his words.
- **Sheets:** 33 of 41 sheets are stale right now.
- **Not built:** the design's §2.4 deploy check, the §2.5 store mirror, and phase 5.

## 1. The original failure classes (design §0, measured 2026-10-04)

| Class | Measured before the ledger | Source |
|---|---|---|
| **A. Overwritten in place / lost** | 774 PNGs overwritten in 71 commits. About 327 art changes cited no ruling. About 50 uncoordinated writers. | design §0 |
| **B. Owner-kept art clobbered** | 20 overwritten after a keep. The 10-03 sheet's "keep render" would have replaced already-kept art on 14 creatures. | design §0 |
| **C. Better older art replaced / shadowed** | Owner, 2026-10-04: *"Please don't replace older art that's actually better"*. 45 texPaths shipped by two mods. | design §0, ledger note 10-04 14:21Z |
| **D. Unknown provenance** | Nine places claimed "current". 0 of 1,322 keeps joined to a render. `registry.jsonl` held 0 verdict events. | design §0 |
| **E. Wrong or stale review sheets** | The "current" column showed corpse art on 65 of 109 rows. 21 of 45 decisions files sat in `Transient/`. | design §0 |
| **F. Facings incoherent** | 0 of 269 jobs used `derive_from`. | design §0 |

## 2. What happened after go-live (2026-10-04 16:00 → 2026-10-15)

### 2.1 Ledger volume
- **66,021 events** in three shards. The live `BENCH.jsonl` is 2.9 MB and `FOUNDRY.jsonl` is 1.3 MB. The archive `BENCH.0001` (10-04 to 10-09) is 31 MB.
  - By type: 33,273 variant, 13,906 live, 11,931 ruling, 4,730 binding, 1,056 purge, 925 rejected, 178 enact_done, 16 job, 6 owner.
  - Most of the bulk is the 10-04 backfill: 26,826 variants and 9,575 imported rulings.
- **`live` events by reason:**

| Reason | Count | Notes |
|---|---|---|
| backfill-observed | 10,426 | 8,266 on 10-04, plus **2,160 re-observed on 10-14** (see §3.1) |
| install under an owner ruling | 1,222 | |
| `script:*` | 1,507 | 60+ free-text tags, see §3.4 |
| artpipe-collect | 452 | |
| retire-duplicate | 216 | |
| retire | 80 | |
| conflict-sheet | 3 | |

  669 of the live events are retires.
- **Owner rulings:**
  - 1,884 `keep` (ruled), 267 `redo`, 179 `release`, 64 `hold`.
  - The noise is larger than the signal: about 7,300 agent `prefill` rulings and about 1,870 `legacy-unresolved` ones.
  - **223 keeps came from `--owner-said`, using only 20 distinct phrases.** 120 rest on one sentence: *"Accept every one you showed me. Good job."* 19 rest on *"Yes, do as you said."* and 9 on *"go! and anything else you can do too!"*.

### 2.2 Recurrence by class

| Class | After go-live | Evidence |
|---|---|---|
| **A** | **0 losses of committed bytes**: every non-purged, non-canon variant is in the store, and DISK_DRIFT is 0. **But 18 intended installs silently never shipped** (§3.1). | queries below |
| **B** | **0 mechanical displacements of a then-kept picture.** Of the 351 displacements of a kept picture, 171 were authorised by his ruling, 59 were retires on his words, and **121 were `retire-duplicate`** (a free pass). 118 of those 121 pictures are still live elsewhere; 7 are live nowhere now, but their bytes are in the store. Friction: Venomvine collects were refused (`8fc50d8bf`), and `CRACKEDLANDS_FULL_RENAME_1` sat unpushed waiting for his words to move 13 kept PNGs (ledger note 10-11). | displacement query; subagent sweep |
| **C** | **1 recurrence, 10-05** (about 30 h after go-live). Owner: *"Not again! Where's the ikee art I had before? I liked it! Why do you keep changing the ikee art?"* A new def (`RM_ContagionIkee`) shipped a different picture from `RM_Ikee`. Protection is keyed by path and sha, so a new def for the same creature is unprotected. The old picture (`0a52fabd`) was in the ledger and was reinstalled within 1 minute (live event 10-05 22:26). `subject_aliases.json` was added afterwards and is still tiny (196 B). | ruling events 10-05 22:25–22:26 |
| **D** | Largely solved. 15,056 distinct pictures, each with provenance (git 12,144 · repo 10,426 · artpipe 6,448 · donor 3,140 · canon 784 · install 281 · derived 47). About 329 renders were still unbound per the 10-09 status. | type counts |
| **E** | **The dominant class now.** The subagent sweep found 8 incidents from 10-04 to 10-14: the wrong "current" column, donor-vs-ours mislabels, a rename losing its renders, notes riding across sittings, a stale def dump on the GSS sheet, and 16 stale sheets rebuilt on 10-14 (with 2 OOM kills at 5.1 GB). Owner, 10-11: *"I have no idea what you want me to click on."* **Today, 33 of 41 sheets under `Transient/` fail `sheet_freshness scan`** (§3.6). | lessons and commits; scan today |
| **F** | Not measured in this review: there is no SET_MIXED flag in the projection. | UNMEASURED |

**The guard over history.** `art_guard.py range art-snapshot-2026-10-04..origin/main` covers 3,798 commits, 187 of them touching textures. It reports **78 unledgered**:
- 77 are pre-guard MessyConduit commits from 10-04, 13:14–14:25 local time. They predate the ledger and are expected.
- 1 is `adf9fc7be` (10-09): an artpipe-collect "displaced owner-kept a25f92f1". The keep was ingested at 22:57, **after** the 18:06 collect. This is a **retroactive false positive**: `range` judges history with today's protections. That keep's note reads *"Nope. I want you to take the Thrumbo art and then 'star wars ify' it…"*, so a keep verdict on a "Nope" note deserves a look.

## 3. Failure modes the ledger introduced or still misses

### 3.1 A live event and its PNG are committed separately (highest value)
The guard checks one direction only: PNG → event. It never checks event → PNG.
- **18 lost installs.** On 10-07 at 07:45, 18 FlowWorks machinery collects recorded `live` 910eba… over f17ea7…. The PNGs never reached git. For 7 days the ledger claimed bytes the repo did not hold, and no check noticed. On 10-14 a re-backfill wrote `backfill-observed` with the old sha, which silently relabelled the slot as the old picture. The newer renders' bytes are in the store; none was owner-kept.
- **9 ghost slots.** 9 FlowWorks/WreckedMachines PNGs exist only uncommitted in the BENCH clone (for example `RM_Sluice_Mover.png`). The shared ledger nevertheless says they are live, from the same 10-14 re-observation.
- **The reverse case already has a lesson.** `20261006T055636Z-BENCH-art-install-writes-new-pngs-that.md`: a pathspec commit of the defs left the PNGs untracked.

### 3.2 `mod` and `rel` spelling is not normalised
- `install()` takes `mod` verbatim. Only `install_bytes` goes through `locate()`.
- 58 live events are keyed under **17 non-canonical mod spellings**: `SWBestiary`, `RimMandrake/FlowWorks`, `FlowWorks`, an absolute `/home/mandrake/rm/bench/src/RimMandrake/Abyss` (15 events) and others. All 49 events that have a canonical twin carry the same sha, so they are duplicates, not conflicts.
- Effects:
  - The pre-push guard refuses them. This produced two lessons today: `20261015T040732Z-…absolute-mod…` and `20261015T192329Z-…keys-events-by…`.
  - `art status` prints false `FLAG SHADOWED`.
  - With an unknown mod, the write lands at `<repo>/<mod>/Textures/…`, outside `src/`.
- 262 rulings record `via` as `../../../../Transient/…`. They are deduped by content, but they are the same class of trap.

### 3.3 No CLI way to put bytes into the store
`install` refuses a sha that is not already in the store ("put it there first"). There is no `art.py put` or `install --file` verb, so agents call `artledger.store_put_file` from inline Python.

### 3.4 Bookkeeping and `script:` reasons are free passes
- **`BOOKKEEPING` reasons** (`backfill-observed`, `retire-duplicate`) pass the guard unconditionally.
  - No code outside the selftests writes `retire-duplicate`. It is hand-typed, and it displaced 121 kept pictures.
  - A `backfill-observed` event with `prev: null` legalises **any new file** with no provenance.
  - The 10-14 re-observation shows the laundering in practice: it overwrote 18 recorded live shas with the disk state, and nothing was flagged.
- **`script:` accepts any text**: `script:decision taken by question card 2026-10-11`, `script:owner-card-2026-10-09-rot-cartoon-variants`, `script:Transient/…/fish_texpaths.md`. Owner authority hides inside mechanical tags, where protection does not apply.

### 3.5 Protection drift
- **2,384 shas are protected; 555 of them are not live.** The projection has no KEEP_NOT_LIVE flag to show which ones are deliberately kept alternatives.
- **79 purged shas still carry an active keep**, and **77 of them no longer have their bytes** in the store.
  - 51 were kept before the purge: ingest's sheet route, or the same-row ✕/keep ordering.
  - 28 were kept after the purge: a later sheet ruling kept a picture whose bytes were already gone.
  - Either way, the projection claims a protected picture that cannot be installed.
- **Keeps from `--owner-said` carry `subject_key: ""`.** All 223 are invisible in `art status <subject>`'s rulings list, though protection by sha still works.
- **Blanket words mint permanent protections.** For example, "Yes, do as you said." protects 19 pictures with no record of what was shown.

### 3.6 The sheet layer is now where the failures are
- `sheet_freshness scan`: **33 of 41 stale**.
  - **25 are stale only because thumbnails are missing.** Sheet images under `Transient/biome_ffar/img/` are clone-local: 580 are untracked in FOUNDRY, and the missing ones exist only in BENCH. The same sheet is fresh in one clone and stale in the other.
  - 6 are really stale: 151 "installed now but not shown as installed" and 143 "shown as installed but no file holds those bytes".
- The subagent counts roughly 22 of the 109 commits under `Utils/art/` since 10-04 as sheet join or freshness fixes, against roughly 5 fixes to the ledger core.

### 3.7 Designed but not built
Status as of today:
- §2.4 **deploy DISK_DRIFT check**: absent. `deploy_custom_mods.py` has no reference to the ledger.
- §2.5 **store mirror**: absent. `_artstore` holds 13,414 files (1.55 GB) on one disk, with no second copy found.
- §2.1 transforms: absent.
- §1.2 `art recover` and the transaction journal: absent.
- §2.3 `collisions_held.json`: absent.
- `Art-override` trailer: absent.
- Phase 5:
  - `artpipe/artreg.py` is still present.
  - `_artpipe/art_status.json` was last written 10-02, so it is stale and still present.
  - `collected.jsonl` has been effectively frozen since 10-08 (288 lines; 19 post-ledger rows have no matching live event).

### 3.8 Smaller items
- The pre-push guard skips merge commits (`--no-merges`). A conflict resolution that changes bytes is never checked.
- The live fold orders by the `ts` string. All 66,021 events are `-0700` today, so this is safe until a machine in another timezone writes.
- There are 42 orphan store files with no variant event, which is harmless.
- `art status` takes 0.9 s, so speed is fine.

## 4. Improvements, ranked by value ÷ cost

| # | Change | Value | Cost |
|---|---|---|---|
| **1** | **Check both directions at push.** Every `live` event added in the pushed range must have its sha at that path in the pushed tree, or be superseded inside the range. Add `art.py doctor`: ledger-live vs the **HEAD tree** (not the worktree), with uncommitted installs listed. Make backfill **never overwrite a differing live sha**: emit a `drift` event and stop. | Kills §3.1 (18 lost, 9 ghosts, the laundering) | ½ day |
| **2** | **Normalise `mod`/`rel` inside `install()`**: route through `locate()` and accept `SWBestiary`, absolute paths and `RimMandrake/X`. Refuse a mod that is not under `src/`. Alias the 58 phantom keys in the projection. Add `art.py put <png>` and `install --file <png>`. | Removes the most-repeated lesson (twice today) and the false SHADOWED flags | ¼ day |
| **3** | **Remove the free passes.** `retire-duplicate` must prove the sha is live at another path. `backfill-observed` is allowed only where no prior live exists. `script:` must name an existing repo file. Owner authority goes through `--owner-said`, `--by-card` or `--per-ruling`, as the rimflow convention already does. The guard judges protection **as of the event's time**. | Closes §3.4 and the retroactive false positive | ½ day |
| **4** | **Mirror `_artstore`** to a second disk or Drive with a nightly `rsync` timer, plus a committed sha manifest. Add the §2.4 deploy DISK_DRIFT refusal. | The store is the only copy of history-only renders and purged/displaced bytes: about 13.4k files on one disk | ¼ day plus a timer |
| **5** | **Sheets from the store, by sha.** Serve thumbnails content-addressed from `_artstore` (or a shared cache keyed by sha), not from clone-local `img/`. Then freshness checks only the real installed-vs-shown mismatches. | 25 of 33 stale sheets become fresh. Cross-clone sheets stop lying. | ½–1 day |
| 6 | **Protection hygiene.** Purge refuses (or releases) a sha that has an active keep. A keep on purged bytes is refused at ingest. `--owner-said` keeps record `subject_key` and the shown sheet or row. Add `KEEP_NOT_LIVE` and `KEPT_BUT_PURGED` flags to `art status` and the index. | Makes the 555 kept-not-live and the 79 kept-but-purged pictures visible and correct | ½ day |
| 7 | **Subject identity across defs.** When a new def's texPath shares a subject alias with a protected picture, `install` warns and the sheet shows the old keep. Grow `subject_aliases.json` from `def_history.json`. | The ikee class (C) | ½ day |
| 8 | **Finish phase 5.** Delete `artreg.py` verdicts and `art_status.json` with inbound references fixed. Hide prefill and legacy-unresolved rulings from `status` by default. Write the `ART_VERSION_WRANGLING_1` item prose, or close it and re-file the leftovers as named items. | Removes rival "current" sources and noise | ¼ day |

## 5. Instrument notes
- **DISK_DRIFT = 0** is a real zero. The same pass hashed 9,611 files and did find 2 files that are on disk while the ledger says they are retired (Etchcap/Wickwood singles; `c7c7b6a59`: *"the guard has no legal move-retire"*) and 59 ghost keys.
- **"0 mechanical over kept"** is a real zero. The query counted 351 displacements of kept pictures under other authorities.
- **The incident list** in §2.2 classes B, C and E combines my event queries with a Sonnet subagent's sweep of lessons, commits and notes. That sweep **missed the ikee recurrence**, which the event data shows, so treat its "0 incidents" for A, B and C as a floor, not a proof.
- Scratch queries: `/home/mandrake/.seat-tmp/FOUNDRY/claude-1000/-home-mandrake-rm-foundry/cccc4587-0aa9-40fc-bb99-c5f6d4c592c9/scratchpad/` (`ev.py`, `m2.py`, `guard_range.out`, `fresh.json`).
