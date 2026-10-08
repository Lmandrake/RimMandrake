# Art pipeline latency: from a ruling to seeing it in the game (2026-10-08)

Owner, 2026-10-08 ~08:25: *"Man it takes a long time just to write graphics into the game, cut it out, etc. Seems like maybe something is very inefficient."*

All figures were measured at about 08:30 PDT on 2026-10-08. They come from `D:\Luke\dev\_artpipe\throughput.jsonl` and `registry.jsonl`, the `pending/` and `active/` job files, the daemon log `D:\Luke\dev\_artpipe\logs\artpiped_20261007_232756_984256.log`, the codex worker-home `auth.json` files, git history, sheet `.decisions.json` timestamps, a dry-run `deploy_custom_mods.py` plan, the art-ledger events and the rimflow game-state stamps. This was a read-only investigation: no code was changed.

## 1. Timeline (measured)

| # | step | measured time | source |
|---|---|---|---|
| 1 | Owner saves sheet decisions → agent installs the "keep" picks and commits | **4–8 min** when an agent is attending (Miasma 21:02→21:06, Feverwood 21:26→21:34, Greentide 21:56→22:01, Webwork 07:33→07:39, Pyrelands 07:44→07:52) | `.decisions.json` last-save times vs `git log -- src/**/Textures` |
| 2 | "Redraw" ruling → artpipe job file written | about 0–5 min (Iriaz H/I created 14:02Z, enactment commit `5cb5cc22e` at 07:07 PDT) | job `created` field |
| 3 | **Job waits in the queue** | **median 3.3 h, p75 7.1 h, p90 10.8 h, max 184 h** (2,736 jobs, last 7 days) | registry `queued`→`generated` |
| 3a | …today's Iriaz redraw | position **174 of 283** pending. At today's rate that is about 5.8 h before it starts | pending sorted the daemon's way |
| 3b | …an owner "deploy it ASAP" job (`chill_item_hydrocarbonflesh_v1`, priority 10) | **still pending 32.6 h after it was filed** | job file `created` 2026-10-07T06:52Z |
| 4 | Generation, worker time | median **97 s**, p90 128 s per facing | throughput `elapsed_s` |
| 4a | Generation, wall time in `active/` | **up to 900–990 s** per job, while its own run is about 126 s | daemon log: e.g. `mott_f_swim_v1_south` 988 s in the slot, 126 s elapsed |
| 4b | Daemon throughput | **about 30 ok jobs/h** (24–33/h every hour 10-08 00–07). Mean busy workers **0.86** over 12 h and 0.48 over 7 d, against **5 configured** | throughput rows, worker-seconds ÷ wall time |
| 4c | Failures | **21%** (711 of 3,331 in 7 d). 311 job ids took 2–6 attempts. 6.4 worker-h were spent on failures. 671 jobs sit in `failed/` (`longshade_rsw_frilledgorg` failed 22 times) | throughput `status`, `failed/` |
| 5 | Finished render → visible on the owner's sheet | waits for an agent to run `refresh_ruled_sheets.sh` (MORNING_SHEETS: *"rerun it at dawn"*) | `Transient\biome_art_refresh_2026-10-07\refresh_ruled_sheets.sh` |
| 6 | Owner re-judges the new render | **30% of subjects needed 2 or more sittings** since 10-04 (167 of 549); 57 needed 3 or more; one needed 7 | art-ledger `ruling` events by=owner, distinct (day, sheet) |
| 7 | Install commit → deployed to the game's Mods folder | varies widely. RimMandrake.Biomes (Vaalok) was deployed **3 min** after commit. SWBestiary (Scurrier, same commit) is **not deployed**: the game copy still has the 2026-09-18 8,402-byte file. **276 files (239 PNGs) committed 10-07/10-08 are undeployed** in 3 enabled mods (SWBestiary 222, UtinniPatches 77-line diff, FlowWorks 31) | `deploy_custom_mods.py` dry plan (took **140 s** just to compute) |
| 8 | Deployed → the running game shows it | **needs a restart. There is no texture hot reload.** Recent down→up gaps: 24 min (10-07 08:18→08:42Z) and 35 min (10-08 04:05→04:40Z). The documented full-list cold load is about 15 min | rimflow `game` stamps; CLAUDE.md |
| 9 | Roster cut → defs actually gone from the game | **about 2–3 days**: sheets ruled 10-05/10-06; cuts audit `588cfd395` 10-08 00:23; deletion `d074b131a` 10-08 06:44 after a second question card, touching about 20 files plus 26 ledger retirements | git |

**Typical end to end for a picture that needs one redraw:** about 5 min + 3–11 h queue + about 2 min generation + an unknown wait for a sheet refresh + one more owner sitting (30% of subjects need more than one) + 5 min install + an unknown wait for deploy + a 15–35 min restart. The machine time is about 2 minutes. Nearly all the rest is waiting.

## 2. Bottlenecks, ranked by time lost

### B1. The artpipe daemon has quietly been running one job at a time (largest single loss)
`artpiped.py`'s `_StaleRefreshGuard` makes every codex job take one global `_stale_refresh_lock` whenever its worker home's `auth.json` `last_refresh` is more than 12 h old (`STALE_REFRESH_THRESHOLD_S = 12*3600`, `skills\generating-images\scripts\codex_image.py:394`). **All 32 worker homes carry the same `last_refresh` of 2026-10-06T18:39:21Z, which is 45 h old.** Codex refreshes only when it needs to, so the timestamp never moves and the guard never lets go. In effect every job holds the lock, and 5 slots behave like 1.
- Evidence: jobs finish one at a time about every 100–130 s, which matches the 97 s median worker time. Jobs sit in the slot for 15+ min while their own run is about 2 min. Throughput is 24–33/h every hour since 10-07 00:00 PDT. The last hour at 62/h was 10-06 23:00 PDT, just inside 12 h of the 18:39Z resync.
- Capacity being left unused: 1.62 ok/min (97/h) at N=3, and requests scaling to 12.4/min at N=32 (`Transient\artpipe_concurrency_measurement_2026-09-26.md`).
- **Time lost:** today's 283-job backlog clears in about 9.4 h at 30/h, versus about 2.9 h at the measured N=3 rate. Every queued ruling is held up about 3× longer than the hardware needs.

### B2. Priority does not let ruled work jump the queue
Pending jobs are sorted by `(priority, filename)` (`artpiped.py:1017`). **267 of the 283 pending jobs are priority 0.** The tie is then broken alphabetically, so the owner's Iriaz redraw (`regen_ls3_…`) waits behind 123 bulk `regen_gt_canon_*` jobs. The one job the owner wrote "ASAP" on sits at priority 10, which places it 265th. Saying "queued at priority 0", as the morning enactment does, buys nothing while the bulk regen is also at 0.
- **Time lost:** about 4–6 h per ruled redraw at today's rate, and up to 30+ h for anything marked anything other than 0.

### B3. Installed is not deployed, and deployed is not visible
- No step runs deploy after `art install`. Today's Scurrier install is still the September file in the game, and 276 files from last night's installs are undeployed in mods that are enabled. The dry-run plan alone takes 140 s because it scans all 149 mods over `/mnt/c`.
- The engine has no texture swap. RimSage, `Verse/ModContentHolder.cs` `ReloadAll(hotReload)`, shows that hot reload **skips any path already loaded** (`if (contentList.ContainsKey(first))`). It picks up new files only and never changed ones. `jawa/hot_reload_defs` is retired anyway.
- So every art change waits for a full restart: 15–35 min of game time, plus the bridge hand-off, and usually several hours until someone decides a restart is worth spending.

### B4. The re-review loop: the sheet does not refresh itself, and 21% of jobs fail
A redraw comes back to the owner only after an agent re-runs `refresh_ruled_sheets.sh`. 30% of subjects take 2 or more sittings. Failures are retried with no cap: a 22-attempt subject is in `failed/`. Each extra sitting adds the whole of B1 + B2 again.

### B5. Every enactment is hand-built
25 `.py` files in `Transient\biome_art_refresh_2026-10-07\` alone, and 73 one-off Transient scripts added since 10-04 (`morning_rulings_install.py`, `retire_deleted_creature_textures.py`, …). Each enactment redoes the same discovery: which texPath, which mod owns it, whether it is owner-kept, which frozen rosters name it. Cuts are worst: a sheet cut edits the roster JSON but leaves the defs, eggs, products, frozen rosters and textures. A separate audit plus another card is needed later to finish the job (B9 above: 2–3 days).

## 3. Fixes

| # | fix | expected saving | cost |
|---|---|---|---|
| F1 | **Unstick the stale-refresh guard.** After a guarded job finishes and `last_refresh` has *not* moved, record "lineage checked at T" and treat homes as fresh until T+12 h. Better still, do one deliberate refresh plus `resync_stale_worker_homes` and release. The rule becomes "serialize only around an actual refresh", not "serialize forever once 12 h old". Add a status line: `lock-held fraction` | **about 3× throughput now** (30/h → about 97/h at N=5, with headroom to N=8). Queue wait p50 3.3 h → about 1 h | about 30 lines in `artpiped.py`, plus a selftest with fake auth files. **Tonight's no-code workaround:** re-run the resync / restart the daemon to refresh the homes, which buys 12 h of parallel running |
| F2 | **Make priority mean something.** Sort by `(priority, created)`, not by filename. Reserve 0–9 for redraws and ASAP notes the owner ruled on; `fill_queue.py` defaults bulk/canon regen to 50. One-off now: bump `chill_item_hydrocarbonflesh_v1` and `regen_ls3_iriaz_*` to 0 and re-prioritise the 123 `regen_gt_canon_*` jobs to 50 | ruled redraw wait drops from about 5–6 h to the next free slot (minutes, once F1 lands) | about 5 lines + a fill_queue default; editing pending job files is cheap |
| F3 | **Deploy as part of install.** `art install`/enactment ends with `deploy_custom_mods.py --apply --mod <owning mod>`, scoped to that mod only. That skips the 140 s whole-tree scan and stops repo≠game drift from building up (276 files today) | removes the hidden "installed but not in game" gap of hours to days | small; the per-mod deploy path exists |
| F4 | **A JawaBench `jawa/reload_textures` tool:** for each changed texPath, `Texture2D.LoadImage(bytes)` *into the existing* texture object held by `ModContentHolder<Texture2D>`, so cached Graphics and Materials keep pointing at it. Then `PortraitsCache.Clear()` / `GlobalTextureAtlasManager` rebake. This is **unproven:** prove it on the minimal list first. Do not revive def hot reload | if it works, art changes show in seconds with no 15–35 min restart; most art-only rulings never need a load | about 100 lines of C# + a proof session; risk is atlas-baked pawn textures, which need the rebake |
| F5 | **Close the loop automatically.** Run `refresh_ruled_sheets.sh` from the systemd loop whenever `done/` changes. Cap retries (for example 3 failures, then park and flag it on the sheet). One `art enact <decisions.json>` verb does ingest + install keeps + queue redraws + deploy, and for cuts also deletes defs, eggs, products, frozen-roster references and art in the same pass | removes the agent wait between render and sheet; cuts go from 2–3 days to the sitting; ends 1–2 bespoke scripts per sitting | medium. Most of the pieces exist (`ingest.py`, `art install`, `fill_queue.py`, the cut method from `7663b4e5c`/`d074b131a`) |

**Do first:** F1 + F2 together. They are about 35 lines and cut the largest measured wait, the queue, by roughly 3–5× for ruled work. F3 is next, because it is the cheapest way to make "installed" mean "in the game". F4 is the only fix that removes the restart.

## 4. Hand-offs and repeated discovery

A single redraw currently passes through these hands: **owner** (rules) → **agent** (ingest, queue, often a one-off script) → **daemon** (queue, serialized) → **agent** (`art backfill` + refresh sheets, "at dawn") → **owner** (re-rules; 30% of the time this goes round again) → **agent** (install, commit) → **agent or nobody** (deploy) → **bridge holder** (decides to spend a restart) → **game** (15–35 min load). That is 5–7 hand-offs. At least 3 of them have no trigger at all: sheet refresh, deploy, and restart all wait on someone noticing.

The repeated discovery happens in step 2 and in cuts. Every enactment re-derives texPath → owning mod → owner-kept protection → frozen-roster references by hand, which is why 73 Transient scripts appeared in 4 days. The ledger already holds most of that mapping (`art status <subject>`). An `art enact` verb that reads it would end the re-derivation.

## 5. Fix applied (2026-10-08 10:29–10:46 PDT, `17d313cbc`)

**F1, the lock.** It exists because ChatGPT refresh tokens are single-use and every worker home shares one lineage (`ARTPIPE_WORKER_AUTH_STALENESS_1`, closed): two homes refreshing at once means one wins and the rest die with *"refresh token was already used"*. That protection is kept. What changed is *when* the lock is taken. A stale home (`last_refresh` > 12 h) still takes it. When that job finishes cleanly **and its `last_refresh` did not move**, codex has shown it does not want to refresh this lineage, and the daemon records that probe. Later jobs on the same lineage then run in parallel for `STALE_PROBE_VALID_S` = 1 h. Three cases still take the lock every time: the first job after the probe window lapses, any home whose access token expires within 70 min (codex *will* refresh it), and any run that follows a probe whose output named a refresh-token failure (such a probe is never recorded). A real rotation still resyncs every sibling home before the lock is released. Cost: about one serialized job per hour.

**F2, the order.** `claim_next` and `--dry-run` sort by **(priority, has `owner_note`, oldest `created`, filename)**. Lower priority still claims first and 0 is still the top. Among equal priority, a job carrying the owner's verbatim sheet note runs ahead of bulk work that carries none. A job with no `created` falls back to file mtime. The filename only breaks exact ties. `chill_item_hydrocarbonflesh_v1` (the owner's "ASAP", filed at 10) was moved to 0 by hand. It was claimed second and passed at 10:40.

**Selftest.** `selftest_artpipe.py` has 3 new tests: a probe unit test, an end-to-end daemon run with `-N 3` on 45 h-stale homes, and an ordering test. The mock worker gained `sleep_s` and a timeline file. 519 checks, all pass. The new tests fail against the pre-fix `artpiped.py` (peak overlap 1, order alphabetical).

**Restart.** `systemctl --user kill --kill-whom=main -s SIGINT` signalled only the daemon, not its codex children. A plain `restart` signals the whole cgroup. The daemon drained its 5 in-flight jobs (3 PASS, 1 `worker_error` after 2 attempts, 1 `failed_canon`, which are ordinary verdicts), exited with status 1 ("work remains"), and `Restart=on-failure` brought it back at 10:37:09. Nothing was lost or run twice. The codex logins were not refreshed.

| | before (10-08 00–07 PDT) | after (10:37:09–10:45:46) |
|---|---|---|
| ok jobs | 24–33 per hour | **16 in 8.6 min ≈ 111 per hour**, 16/16 PASS, no auth errors |
| codex runs at the same time | ~1 (mean busy 0.86 of 5) | **5** `codex_image.py` processes live at 10:46. Completions land in pairs seconds apart after the 10:39:30 probe |
| time in slot for a ~100 s run | up to 900–990 s | 82–141 s |

**Re-prioritisation: proposed, not applied.** 228 of the 243 pending jobs are at priority 0. 174 of them carry `owner_note`, so most of the 0s are genuinely ruled work, and the ordering above now handles them. These are the jobs still wrongly placed:
- **`regen_ls3_iriaz_*` (6 jobs) is a ruled redraw with no `owner_note`**, so it now sorts behind every noted job at 0. The enactment that files a redraw should copy the ruling onto `owner_note`, or file the redraw at a lower number than the bulk work.
- **Bulk work with no note sits at 0**: 31 `regen_gt_hawkbat_flying_*` derive children, 9 `webwork_*`, 3 `wsart_*`, 5 `wsfix_*`. Proposal: `fill_queue.py` callers file backfill at 50, keep 0–9 for owner rulings, and leave the default at 100. Re-filing the existing 48 jobs is a judgment for BENCH. It has not been done.

## Follow-up 2

- `fill_queue.py` default priority is now 50 (was 100); 0-9 stays for owner-ruled redraws (`art/enact.py` already files 0).
- Pending re-prioritise: before {0: 202 (149 with owner note), 70: 2, 75: 1, 100: 12}; only the 3 `wsart_*` weather-stone jobs (no note, no ruled sheet) went 0 -> 50. After: {0: 199 + 5 re-filed below, 50: 3, 70: 2, 75: 1, 100: 12}. The `regen_gt_*`, `ls3_*`, `webwork_*`, `wsfix_*` note-less jobs are derived facings or rows of sheets the owner ruled `redo`, so they stay at 0.
- Re-filed at priority 0 with the owner note intact: `ls3_pufferpig_v1_east/north/south` (failure was a codex worker flake, "tool channel unavailable"; north/south derive from east) and `ls3_nysyllin_a_v1`, `ls3_nysyllin_b_v1` (failed the canon gate on "Grown in dense rows as a crop", which does not apply to a WILD single plant; added `canon_na` for that line with a reason). Failed manifests parked in `_requeued_manifests/`.
- Sketto: the 14 pending jobs already cover north+south (grounded north/south plus flying 1-4 each east/north/south, all priority 0); nothing to add.
