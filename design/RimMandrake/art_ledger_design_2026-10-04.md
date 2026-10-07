# Art ledger — one source of truth for every texture (design, 2026-10-04)

Item: `ART_VERSION_WRANGLING_1`. Status: DESIGN — reviewed by GPT (gpt-6.1-sol, high), revisions applied (§5). Nothing built.

## 0. Problem, measured

Owner, 2026-10-04: *"We clearly need some kind of art wrangling to bring this all together. Likely
different versions of art are now racing... Please don't replace older art that's actually better...
I would want to make sure we compare them with the other variants FOR THE SAME CREATURE we already
have."*

Inputs (all three read in full): `Transient/art_racing_audit_2026-10-04.md`,
`Transient/art_census_desert_2026-10-04.md` + `.csv`, `Transient/desertport_art_diagnosis_2026-10-04.md`.
What they measured, and what each section below answers:

| Defect (measured) | Size | Answered by |
|---|---|---|
| Nine places claim "current"; none authoritative (`registry.jsonl`, `art_status.json`, `collected.jsonl`, ~43 `*.decisions.json`, `decisions_propagated.json`, canon `## ruling`, per-script `JOB_MAP`/`SET_DIR`/`CREATURES`, git, load order) | 9 | §1 ledger |
| Rulings and renders share no key (sheet keys vs job ids); fuzzy join links 0–26 keeps per sheet | 0 of 1,322 register keeps join to a render | §1 variant = sha256 |
| `registry.jsonl` holds 0 verdict/commit/deploy events | 3,576 generated, 0 accepted | §1, §4 |
| Writers overwrite `Textures/` in place, no ruling check, no prior kept | 774 PNGs overwritten in 71 commits; ~327 art-changing with no cited ruling; ~50 writers | §2 installer + guard |
| Same texPath shipped by two of our mods, different art; last-loaded (SWBestiary, idx 605) shadows the approved overrides | 45 paths (Nuna 6, Iriaz 3, Dalgo 3, Bantha 12, Eopie 21) | §2 path ownership |
| Review sheet showed `dessicatedBodyGraphicData` as "current" | 65 of 109 rows | §3 roles |
| Facings generated independently, so S/E/N are different animals | 0 of 269 jobs use `derive_from` | §3 per-facing set view, §1 `set` |
| 10-03 "keep render" would replace art already kept | 14 creatures; 20 overwritten after a keep | §3, §4 phase 3 |
| Rulings stored in the 14-day bin | 21 of 45 decisions files in `Transient/`, 3 already deleted | §4 phase 0 (being moved to `infrastructure/state/art_rulings/` by another agent) |

**Not in scope here, owned elsewhere today:** moving ruling files into
`infrastructure/state/art_rulings/` (another agent, in flight — this design *reads* that folder);
re-briefing the stale desert jobs (another agent). The 45 doubles are **held for this plan** (owner).
## 1. The art ledger

### 1.1 Identity: what a "slot" and a "variant" are

- **Slot** = the thing exactly one image fills in game:
  `slot = (subject, role, facing, frame)` where
  - `subject` = the def that draws it (ThingDef/PawnKindDef defName, plus lifeStage/gender suffix when
    the def has more than one body graphic, e.g. `RSW_Nuna#f`, `RSW_Nuna#juvenile`). Plants, buildings,
    apparel, icons use the ThingDef/terrain/icon defName.
  - `role` ∈ `body`, `dessicated`, `mask` (`*m.png`), `flying` (frame N), `swimming`, `icon`,
    `apparel_worn`, `plant_leafless`, `plant_immature`, `other:<tag>`. **Role is resolved from the def
    field the texPath came from** (`bodyGraphicData` vs `dessicatedBodyGraphicData` vs
    `flyingAnimationFramePathPrefix`), never from the filename — that is the 65-of-109 bug.
  - `facing` ∈ `north|east|south|west|single`; `frame` = 1..N for flight frames, else 0.
- **Resource** = the physical file a slot resolves to: `(texPath + facing/frame suffix)`. Slot and
  resource are separate identities because **several slots can share one resource** (a PawnKindDef
  reusing a ThingDef's graphic, two life stages on one texPath, renamed defs). Gender and life stage
  are independent dimensions of the subject, not one suffix. The installer always computes **every
  slot affected by a resource change** and requires compatible authorization across all of them (§2.1).
  The installer (§2) knows which mod owns each resource. Neither stores pixels.
- **Variant** = one image, **identified by its sha256 of the PNG bytes**. Same bytes in two places =
  one variant with two locations. A **perceptual hash (dHash 16×16)** is stored alongside so the sheet
  can group near-identical variants (halo sweep, %4 padding) as *derivatives* of one parent — the
  mechanical sweeps (328 PNGs) must not look like 328 new art choices.
- **Set** = an **immutable manifest** of exact `slot → sha` assignments, with a version id (the sha of
  the manifest). Created explicitly: from an artpipe job family (`derive_from` master + derived
  facings), by the sheet when the owner picks a column, or by backfill as an `observed` set (one
  commit's S/E/N for one subject, or the currently deployed combination — labelled as observed, never
  presumed coherent). A ruling targets a set **version**; adding a facing later makes a new version,
  never grows an approved one. Incomplete sets show their gaps. A sha may belong to many sets and
  carry many provenance records (lists, not a single field). Facing incoherence is visible: a slot
  family whose live variants come from different sets is flagged.

### 1.2 Events (the append-only log)

Location: **`infrastructure/state/art/events/<SEAT>.jsonl`**, git-tracked, one shard per writer,
`merge=union` in `.gitattributes`, exactly like `infrastructure/state/ledger/events/`. Pixels are
**not** in git beyond what `src/**/Textures` already ships: archived bytes live in a
content-addressed store `D:\Luke\dev\_artstore\<sha[:2]>\<sha>.png` (outside git, beside
`_artpipe`), and every event names the sha so the bytes are re-findable from git history,
`_artsrc`, or the store. Each event has `id` (uuid), `ts`, `seat`, `type`:

| type | fields | written by |
|---|---|---|
| `variant` | `sha`, `phash`, `w`,`h`, `provenance` {`kind`: artpipe\|donor\|git\|canon\|hand\|derived, `job`, `donor_pkg`, `git_sha`, `canon_ref`, `parent_sha`, `transform`}, `locations[]`, `set` | backfill, artpipe on render, installer |
| `bind` | `sha`, `slot` | backfill, artpipe (job's target slot), sheet (re-assign misfiled) |
| `ruling` | `target` {`sha`\|`set`}, `slot`, `verdict` ∈ keep\|reject\|redo\|prefer-over:<sha>\|hold, `by` (owner\|agent), `said` (verbatim, typed text only), `via` (sheet path + `reviewStatus`), `source_file`, `trust` ∈ ruled\|flawed-sheet\|prefill\|legacy-unjoined | sheet sidecar, importer, `art rule` CLI |
| `live` | `slot`, `sha`, `install` {mod, path}, `ruling_id` or `reason` | **installer only** |
| `owner` | `texpath`, `mod` | installer (`art own`) — path ownership, §2.3 |
| `retire` | `sha` or `slot`, `reason` | installer (slot deleted from defs) |

**Three separate facts, never one "latest ruling" (GPT critique #2):**
- **Verdicts** on candidates (`keep`, `reject`, `redo`, `hold`) — opinions about a variant/set.
- **Protection** — a `keep` by the owner makes that set version **protected**. Protection persists
  until a later owner ruling *names that protected set* and supersedes it (`prefer-over:<set>` or
  `release:<set>`). Rejecting some other candidate, `hold`, or `redo` never removes protection.
  Two protected sets for one slot is legal (several kept alternatives); it is a **conflict to show**,
  never resolved by timestamp.
- **Selection** — which protected (or unprotected, if none exists) set is deployed: the `live` event.
  Replacing a protected live set requires the owner to have selected the incoming one.
A `flawed-sheet` ruling is shown but authorises nothing; `prefill`/agent rulings authorise nothing.

**Merge and concurrency (#8):** event ids for imports are deterministic (hash of source file + key +
target), so a re-run or a union merge of duplicates is idempotent; the projection orders by causal
`prev` (each `live` event names the `live` event it replaces), and two `live` events with the same
`prev` are a **conflict** the index surfaces and the guard refuses. Installs take a lock file and write
a transaction journal (`pending → archived → written → recorded`) so a crash at any step is recovered
by `art recover` to one consistent state.

### 1.3 The projection (what tools read)

`art index` folds the shards into `infrastructure/state/art/index.json` — gitignored, rendered on
read, like the rimflow queue views — `slot → {live_sha, live_path, owning_mod, variants[], rulings[],
effective_ruling, flags[]}`. Flags (each counted against real data before it ships, per the
review-sheets rule): `KEEP_NOT_LIVE` (a kept variant is not the live one), `LIVE_UNRULED`,
`SHADOWED` (texPath shipped by >1 of our mods), `SET_MIXED` (facings from different sets),
`DISK_DRIFT` (bytes on disk ≠ ledger `live`). One reader library (`artledger.py`) is the only parser.

### 1.4 Initial build (backfill) — mechanical, resumable, idempotent

1. **Slots** from the def dump + our mods' XML (post-patch): every texPath per def, with its role from
   the field it sits in. Sanity probe: Gizka, Nuna, Anooba must resolve all roles.
2. **Variants from disk:** every PNG under `src/**/Textures` (7,928) → `variant`+`bind`+location.
3. **Variants from git:** every blob ever at a `src/**/Textures/**` path (`git log --all
   --diff-filter=AMDR -M`, following renames; GPT #9 — an `MD`-only walk misses art added then
   renamed away) — 774 overwritten + 169 deleted + 2,959 renamed + adds → `variant` with `provenance.git_sha`, bytes copied
   to `_artstore`. This is what recovers "older art I liked".
4. **Variants from artpipe:** `_artsrc/*` (2,685) + `done/` manifests (job id, prompt, `derive_from`,
   `style_notes`, `reference`) + `collected.jsonl` (job → dest sha, the only exact job↔texture join).
5. **Donor and canon:** donor sprites (loose + bundle, as the census did) and canon-library images,
   bound to the slot as `kind: donor|canon` — canon images are *references*, bindable as variants for
   comparison but never installable.
6. **Rulings importer** (authority only where the shown bytes are proven, GPT #9): every decisions file in `infrastructure/state/art_rulings/` (+ any left in
   `design/`, + deleted ones from git history). A ruling becomes **protecting** only when the exact bytes
   the owner saw are recovered: the sheet embeds an image sha, or its image path is resolved **at the
   sheet's commit date** (git blob at that time, not today's file), or a `collected.jsonl` / job id
   pins it. Otherwise it is imported as `trust: legacy-unresolved` — joined to the subject through
   `JOB_MAP`/`SET_DIR`/`CREATURES` and the census map (committed as
   `infrastructure/state/art/subject_alias.json`), **shown on the sheet, protecting nothing** until the
   owner re-confirms it there. So no today's-alias join manufactures a protection. Verb vocabulary (10+) is
   normalised by one table in the importer; `replace` (= replace donor) is NOT `reject`. Files whose
   `reviewStatus` is not `ruled` import as `prefill`. **The 10-03 desert sheet imports as
   `trust: flawed-sheet`**, with the reason string "current column showed corpse textures for 65/109
   rows; facings not coherent".
7. **Live:** one `live` event per slot for the bytes currently on disk in the **winning** mod per
   live `ModsConfig.xml` order, `reason: backfill-observed`. Then compute flags. The output of the
   backfill is a count table, not a fix: no Textures file is touched.

### 1.5 How artpipe registers new renders

- `artpiped.py` on job completion calls `artledger.register(png, job)` → `variant` (+ `bind` to the
  job's target slot, which `fill_queue.py` must now require as `slot`, not a free-text target).
- `fill_queue.py` **prints** the existing variants and protections for the slot before queuing (the
  2026-09-20 "check before queuing" rule, mechanised). It does not refuse: generating over a protected
  slot is harmless because only installation is gated (GPT #14).
- `registry.jsonl` keeps generation telemetry only; its verdict/commit/deploy event types are retired.
## 2. The installer and its guard

### 2.1 `art install` — the only writer into `src/**/Textures`

`python3 src/RimMandrake/Utils/art/art.py install <slot|set> <sha> (--ruling <ruling_id> | --reason
<mechanical-tag>)`:

1. Resolve slot → texPath → **owning mod** (§2.3). Refuse if the slot has no owner.
2. Compute **every slot that shares this resource** (§1.1). For each, refuse if its live set is
   protected and the owner has not selected the incoming set version for that slot. A `flawed-sheet`,
   `legacy-unresolved` or `prefill` ruling never satisfies this. The ruling must carry plumbing
   provenance (sheet sidecar `savedBy`/`writeCount` + `reviewStatus.state=ruled`, or a
   `block_forged_owner_said.py`-accepted typed quote) — **an agent-typed `--ruling` string is not
   evidence** (GPT #4).
3. Refuse a set install that would leave the slot's facings mixed across sets, unless `--mixed-ok
   "<owner words>"`.
4. Archive the displaced bytes to `_artstore/<sha>` **before** writing (copy, verify sha, then write
   the new file atomically: temp + rename). Append `live` (and `variant` if new).
5. Never deploy. Deployment stays `deploy_custom_mods.py`, which gains one check (§2.4).

**Mechanical transforms** (halo zeroing, %4 padding, downscale): only **allowlisted deterministic
operations** in `art/transforms.py`, each a pure function `(parent bytes, params) → bytes`.
`art transform <op> <slot...>` writes a `variant` with `provenance.kind=derived, parent_sha, op,
params`; the installer and the guard **re-run the op on the parent and require byte equality**. That,
not a perceptual threshold, is what lets protection follow the parent to the child (GPT #3: dHash
both passes small recolours and fails legitimate downscales). The parent stays archived. Perceptual
hash is a comparison aid on the sheet only.

**Every existing writer is rewired to call it** (list in §4): `artpipe_state.py collect`,
`LanternDeeps/wire_art.py`, `TheRot/port_fauna.py`, `gen_races_mod.py`, the ~48 per-mod `Source/*.py`
texture writers, and agents' hand-wires (which become `art install`).

### 2.2 The guard (two layers, same check)

- **`.claude/hooks/block_unledgered_texture.py`** (PreToolUse, Bash, on `git commit`/`./publish`):
  checks **authorization, not agreement** (GPT #4). For every PNG under `src/**/Textures` in the
  commit, rebuild the ledger state *including the commit's own staged ledger lines* and require: the
  bytes' sha equals the `live` sha; that `live` event's `prev` equals the previously committed live
  sha (no skipped transition); and the transition is authorized by the rules of §2.1 (protection,
  plumbing-provenanced ruling, or a re-verified allowlisted transform). Appending a matching `live`
  line by hand therefore does not pass. Deletions require a `retire` event. Refusal prints the
  `art install` command that would make it legal.
- **`infrastructure/githooks/pre-push`** gains the same check (`art guard --range <old>..<new>`),
  per commit in the range, so timers, scripts and plain shells are covered. This is the
  authoritative gate (the repo has no CI; GPT asked for one — see §5).
- Both **fail closed on a ledger parse error** for PNG commits only (and print it); every other commit
  is untouched. Repo convention: a crash elsewhere fails open; here a crash means the guard can't see,
  and a PNG commit then waits — said out loud in the refusal.
- Escape hatch for the owner only: `Art-override: "<his words>"` trailer, checked by the existing
  `block_forged_owner_said.py` rules (typed text only).
- Selftest: `selftest_block_unledgered_texture.py`, proving it bites on a raw `cp` + commit and
  passes an `art install` commit (re-introduce the bug, watch it go red).

### 2.3 One owning mod per texPath (the 45 doubles)

- An `owner` event assigns each texPath to exactly one of our mods. Backfill: unique paths get their
  only shipper. **Collisions get no owner** and are listed for decision.
- Selftest `selftest_texpath_unique.py` (in `run_selftests.py`): fails when two of our mods ship the
  same texPath, unless a ledger `owner` event names one and the other copy is absent. This also
  catches the RotSporeKit/LanternDeeps/BMT_Caverns Arpeau triple (same species, different paths, so
  it is flagged as `SUBJECT_MULTI_MOD` advisory, not a failure — they are different texPaths).
- **The 45 stay explicit grandfathered exceptions** in `infrastructure/state/art/collisions_held.json`
  until ruled, so the selftest is green on day one without touching them (GPT #10). Before retiring a
  copy, the installer checks the losing mod does not need the file when the owning mod is inactive
  (override mods depend on SWBestiary, so retiring the SWBestiary copy is safe only where the def
  still resolves; otherwise the override's copy *moves into* SWBestiary instead).
- **Resolution of the 45** (Nuna 6, Iriaz 3, Dalgo 3, Bantha 12, Eopie 21) runs through the §3 sheet,
  one creature at a time: both copies are variants of the same slot; he picks; the installer writes
  the winner **into the owning mod** (the override mod where it exists — they exist precisely to own
  that art) and `art retire`s the other copy, archived. No load-order editing: ownership, not order,
  decides. Until he rules, the 45 stay exactly as they are (his hold).

### 2.4 Deploy check

`deploy_custom_mods.py --apply` refuses to deploy a Textures file whose sha ≠ ledger `live`
(`DISK_DRIFT`), naming the slot, and **archives any game-side file it is about to overwrite or
`--prune`** into `_artstore` first. The ledger keeps three things apart (GPT #10): repo contents, the
approved selection, and the **observed** runtime resolution (from a given `ModsConfig.xml`, stamped
with that list's fingerprint) — the observation is evidence about one mod list, never truth.

### 2.5 The archive is a guarantee only if it is verified

`_artstore` writes are copy → fsync → re-hash → then record; an event naming a sha whose bytes are not
in the store (or git) is a **blocking** `BYTES_MISSING` flag. **Every candidate shown on a review
sheet is archived**, not only displaced live files (renders in `_artsrc` can be cleaned up). The store
is mirrored to a second location (the Drive-synced backup root, or a periodic commit of its sha
manifest plus a copy on the Mac) — GPT #6.
## 3. The review sheet generator

`python3 src/RimMandrake/Utils/art/art.py sheet <subject...|--biome <name>>` — built on
`skills/review-sheets` `assets/sheet_template.html`, served by `serve_sheet.py` (the tokened URL is
the delivery), gated by `check_sheet.py`.

**One row = one creature (subject).** Inside the row:
- **Grid: columns = sets (variants grouped by set/job family/commit), rows = facings S/E/N(+W if
  shipped).** So "different faces being different creatures" is visible as a broken column, and
  he picks a *column*. Every variant ever made for that subject is a column: live (marked), git
  history (dated, commit subject), artpipe renders (job id, prompt excerpt, `derive_from` yes/no,
  style register), donor original, and the canon reference image (marked REFERENCE, not pickable).
- **Roles are filtered by the ledger, not by filename:** the main grid shows `role=body` only;
  `dessicated`, `mask`, `flying` frames sit in a collapsed strip labelled with their role. A corpse or
  mask can never be the "current" column — `check_sheet` gains a FAIL for any body-grid cell whose
  slot role ≠ body.
- Shown on the row: canon library `## Visual brief` + `## Must show` (when an entry exists), biome
  doc creature entry, **every prior ruling** on any of these variants with date, sheet, verbatim note
  and its trust (a `flawed-sheet` ruling shows struck-through with the reason), and the flags
  (`KEEP_NOT_LIVE`, `SHADOWED`, `SET_MIXED`).
- **Columns are collapsed by default to: live (the actual deployed S/E/N, even when mixed),
  protected sets, distinct candidates, unresolved history.** Exact duplicates and verified mechanical
  derivatives fold into their parent with expandable lineage; perceptual grouping never hides a
  candidate (GPT #13). Plants get their own layout (growth stages, leafless) rather than S/E/N.
- Prefill (§1 of the skill): the agent pre-selects the column carrying the most recent `ruled` keep;
  if none, the live column; it never prefills a never-ruled render over a ruled keep. `CONFIG.criterion`
  says so; `CONFIG.invented` lists anything assumed (e.g. alias joins).
- Options per row: `keep column X` · `keep X, regenerate from it as master` · `none — redo` (note
  says what's wrong) · `hold`. Discouraged options are greyed, never hidden.
- **Snapshots and explicit intent (GPT #12):** every sheet build writes a snapshot manifest (sheet id
  → for each row, the exact set versions and shas per column). A saved decision names the snapshot id
  and set version, so a stale tab cannot approve a regenerated column under the same label (ingest
  refuses a decision whose snapshot is not the newest for that row, and says so). **Only rows the
  owner actually touched become rulings**; an untouched prefill is never a ruling, even on a sheet whose
  `reviewStatus` is `ruled`. An empty note still records a selection.
- **Decisions write straight into the ledger:** the sidecar's decisions file is the transport; on
  save, `art ingest <decisions.json>` appends `ruling` events (`by=owner`, `said`=his typed note,
  `via` the sheet, `reviewStatus` checked by `review_status.get_review_status()` — refuses prefill).
  It **does not install**; installing is a separate `art apply --from-rulings` step he can see the
  plan of first (dry run default).
- **Closing a biome sheet, in order** (as run on the Grey Sea, Chill and Twilight Sea closes,
  2026-10-06/07): stamp `reviewStatus` ruled with his typed words → blank any row he did not decide
  (no `decidedAt`) that he asked us to infer, recording `agentInference` on it, so ingest cannot turn
  a prefill into his ruling → file redo jobs carrying his note verbatim (`fill_queue.py`) → `art.py
  ingest --redo-jobs` → `art.py install` per pick → re-run `art.py purge` for purges ingest refused
  as live once their replacement is in → wire every texPath / graphicClass → `placeholder_detect.py`
  over every PNG the biome's defs draw (collect finished renders for borrowed texPaths, queue the
  rest) → **re-fit creature shadows: `python3 src/RimMandrake/Utils/art/sea_shadows.py apply <Defs
  xml> <PawnKind>...`** for every creature whose art changed (owner, 2026-10-07: shadows must follow
  the new art, not the placeholder shape; a creature with no `shadowData` draws no shadow at all) and
  look at its `contact` sheet → commit, deploy (`--compose biomes`).

**Desert family re-review:** 109 rows (92 creatures, 17 plants), split by biome per his
biome-by-biome rule (desert / deep desert / blue desert). Import order: all earlier rulings as
`ruled`, then the 10-03 sheet as `flawed-sheet`, shown on each row ("10-03: keep render — made against
a corpse comparison"). The 14 rows where the 10-03 keep would replace already-kept art and the 20
overwritten-after-keep rows sort first. The re-briefed renders (other agent's work) arrive as new
columns via artpipe registration — no extra wiring. Plants and the 7 droids join once their slots
resolve (droid art is bundled under unresolved names: census gap, a backfill step, not a sheet one).
## 4. Migration plan

Sizes are estimates for one agent; each phase ends committed and pushed, and touches **no Textures
file** until phase 3.

| Phase | What | Size | Done when |
|---|---|---|---|
| **0. Stop the loss** (today, ½–1 day) | **Snapshot** every `src/**/Textures` PNG, every `_artsrc` render, every decisions file and the `done/` manifests into `_artstore` + a committed sha manifest; tag the git ref. Make the two bulk destroyers **archive-before-write**: `artpipe_state.py collect` and `deploy_custom_mods.py --apply/--prune`. Guard in **warn** mode. (Ruling-file move: other agent.) | ½–1 day | a test overwrite via `collect` leaves the old bytes recoverable by sha (GPT #1: the exit proves bytes survive, not that a warning prints) |
| **1. Ledger + minimal sheet** | `artledger.py` (shards, deterministic ids, causal `prev`), `art index`, backfill steps 1–7, `subject_alias.json`, verb table. **A minimal one-creature compare sheet early** on Gizka, Nuna and Anooba, so the owner checks identity and historical joins before the backfill is trusted (GPT #11). | 2–3 days (git blob walk is the long pole; resumable) | he confirms the three probe creatures' history reads right |
| **2. Installer + rewire the busy writers** | `art install/transform/retire/own/recover/guard`, transforms allowlist, journal, archive verification. Rewire `collect`, `deploy_custom_mods.py`, `wire_art.py`, `port_fauna.py`, `gen_races_mod.py` and the hand-wire path **before** enforcement. Round-trip proven on a **disposable fixture mod**, not real Textures. | 2 days | selftests red-then-green on the fixture |
| **3. Enforce** | Guard → **block** for paths whose writers are migrated; the ~48 per-mod `Source/*.py` writers are disabled (exit with a pointer to `art install`) until each is adapted on next touch. | ½ day | guard blocks a raw `cp`+commit; passes an `art install` commit |
| **4. Desert re-review + the 45** | Full `art sheet`/`art ingest`/`art apply` (dry run first). The 45 doubles as their own 5-row sheet; desert family by biome sittings. | 2 days build; sittings at his pace | every displacement in the desert family is authorized and recoverable |
| **5. Retire registries, roll out per biome** | Below table. Remaining biomes get compare sheets as each comes up for its sitting (never a planet sweep). | 1–2 days, mechanical | guard has blocked nothing legitimate for a week |

**Completion criterion** (GPT #14): *every displacement is authorized and every displaced byte is
recoverable* — not `KEEP_NOT_LIVE = 0`; several protected alternatives can legitimately stay undeployed.

**Retired / rewired:**

| Tool | Fate |
|---|---|
| `artpipe/artpipe_state.py collect` | rewired → `art install` per slot (keeps `done/` manifest check) |
| `artpipe/apply_verdicts.py`, `artreg.py verdict/committed/deployed` | **retired** (never ran: 0 events); `art ingest` replaces it |
| `artpipe/make_verdict_sheet.py`, per-sheet builders (e.g. `Transient/desert_art_review_build_2026-10-03.py`) | **retired** for creature/plant art → `art sheet` |
| `art_status.json` | becomes a projection of the ledger or is deleted |
| `registry.jsonl` | telemetry only (generated/queued/withdrawn) |
| `collected.jsonl` | read once by backfill, then frozen |
| `decisions_propagated.json` (+ flora) | imported once, then deleted with inbound refs fixed (nothing reads it) |
| `LanternDeeps/wire_art.py`, `TheRot/port_fauna.py`, `gen_races_mod.py`, ~48 `Source/*.py` writers | rewired → `art install`; per-script `JOB_MAP`/`SET_DIR`/`CREATURES` folded into `subject_alias.json` |
| `artpipe/fill_queue.py` | requires `slot`; refuses over a keep; `--derive-facings` stays default |
| `deploy_custom_mods.py` | gains the `DISK_DRIFT` refusal |
| Canon library `## ruling` | unchanged (canon target, not a variant pick); the sheet displays it |
## 5. GPT review — taken / rejected

One consult, `gpt_consult.py -m gpt-6.1-sol --effort high`, the full design inlined, asked for failure
modes, over-engineering, gaps and phase order. It returned 14 ranked points; **13 taken, 1 partly**:

| # | GPT said | Taken? | Where |
|---|---|---|---|
| 1 | Phase 0 warn-mode freezes nothing; snapshot and make destroyers archive-before-write first | **taken** | §4 phase 0 |
| 2 | "Latest ruling per slot" lets a later reject/hold erase a keep | **taken** — verdict / protection / selection split | §1.2 |
| 3 | Perceptual hash cannot authorize mechanical changes (passes recolours, fails downscales) | **taken** — allowlisted deterministic ops, re-run and byte-compared | §2.1 |
| 4 | Guard checks agreement not authorization; agent-typed owner words aren't evidence | **taken** — guard validates the transition incl. staged ledger lines; plumbing provenance required | §2.1, §2.2 |
| 4b | Add an authoritative CI gate | **rejected** — the repo has no CI; the git-native `pre-push` (which already runs for timers and plain shells) is that gate | §2.2 |
| 5 | Slots ≠ resources; shared texPaths change several slots | **taken** — resource identity, affected-slot check | §1.1, §2.1 |
| 6 | Archive on one machine is not a guarantee; archive every shown candidate | **taken** | §2.5 |
| 7 | Sets must be immutable manifests, not commit/job membership | **taken**; backfilled commit sets kept but labelled `observed` | §1.1 |
| 8 | Union merge needs deterministic ids, causal order, conflicts, transaction journal | **taken** | §1.2 |
| 9 | Backfill can manufacture authority; `MD` walk misses variants | **taken** — protection only when shown bytes are recovered; `AMDR -M` walk | §1.4 |
| 10 | Load order is one machine's observation; retiring a copy can break a mod | **taken** — observed vs approved; dependency check; 45 grandfathered | §2.3, §2.4 |
| 11 | Phase 2 blocks writers before they're adapted; round-trip on real Textures | **taken** — rewire before enforce; fixture mod; early minimal sheet | §4 |
| 12 | Snapshots for sheets; untouched prefill is not a ruling | **taken** | §3 |
| 13 | Exhaustive columns bury the favourite | **taken** — collapsed default, expandable lineage | §3 |
| 14 | Cut queue refusal, perceptual inheritance, commit-sets; completion ≠ `KEEP_NOT_LIVE=0` | **taken** except commit-sets, kept as `observed` (they are the only record of what showed in game on a date) | §1.5, §4 |
## 6. Open questions for the owner

Six questions on two cards: `Transient/art_ledger_cards_2026-10-04.json` — guard strength (block / warn /
build-from-ledger), where replaced art is stored, whether exact mechanical operations may pass over a
keep, how the 45 doubles are settled, how the 109 desert rows are split into sittings, and which
variant is prefilled. The design above assumes each card's recommended answer; a different answer
changes only the named subsection.

## 7. Built so far (2026-10-04) and where it departs from §1–§4

Code: `src/RimMandrake/Utils/art/` — `artledger.py` (library), `art.py` (CLI), `backfill.py`, `ingest.py`,
`art_sheet.py`, `selftest_art.py`. Store: `D:\Luke\dev\_artstore\<sha[:2]>\<sha>.png`. Events:
`infrastructure/state/art/events/<SEAT>.jsonl`. Phase-0 manifest: `infrastructure/state/art/snapshots/`;
git tag `art-snapshot-2026-10-04`. Sheet snapshots: `infrastructure/state/art/sheets/`.

- **Purge (owner ruling 2026-10-04, new verb):** `art.py purge <sha> --owner-said "…"`, or ✕ on a picture in
  a compare sheet then `art.py ingest`. Deletes the bytes from the store, appends a `purge` event; every later
  sheet and every backfill skips the sha. Refused for a picture live in a mod; an owner keep on it is released
  in the same act (sheet route) or needs `--release-keep` (CLI). Renders stay in `_artsrc` (artpipe's state).
- **Slots are resolved from our defs on read** (`scan_def_slots`), not stored as `bind` events.
- **Prefill inference:** with no byte-exact owner keep anywhere yet, the doubles sheet prefills a shipped column
  whose installing commit (or a look-alike parent before the halo sweep) cites an owner approval, marked ⚠ inferred.
- **Writers rewired (2026-10-04):** `art install` takes `--reason artpipe-collect|script:<path>` for mechanical
  writers (refused over an owner-kept picture); scripts call `artwrite.TextureWriter` (`copy`/`save`/`put`/`sync`,
  sync = ledger-safe rmtree). Rewired: `artpipe_state.py collect`, both `port_fauna.py`, `wire_art.py`,
  `gen_races_mod.py`, and 28 per-mod `Source/*.py` writers. Not rewired: the `Utils/mockups/messy_conduit/*`
  writers (FOUNDRY mid-round), `MessyConduit/validation.py` + `northstar_matrix/run_live.py` (fixtures/game dir),
  `extract_bundle*.py` (generic, caller picks dest), `BlastDoorFrameAsyncFix/build_frameasync_east.py` (writes a
  stale path in the old repo).
- **Guard (2026-10-04, blocking):** `art_guard.py` (rule) + `.claude/hooks/block_unledgered_texture.py`, run by
  `infrastructure/githooks/pre-push` for every push. A texture PNG change must end an authorized `live` chain
  starting at the committed bytes. Its PreToolUse registration in `.claude/settings.json` is not made yet.
- **Not built yet:** `art transform`, the deploy check, `art recover`/journal, and the per-biome desert sheets.
