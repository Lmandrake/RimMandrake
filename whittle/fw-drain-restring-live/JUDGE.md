Fresh independent read-only Opus judgment. The complete raw envelope is preserved in evidence/judge_raw.json and the bounded fresh-call receipt in evidence/judge_call.json.

I would show this to the owner as completing the item. Every frozen bullet is backed by the raw records. I could only read files (no shell), so I could not re-hash anything or check for running processes myself; the current-hash and process checks below come from the maker's readback script, whose code I read and which does the hashing itself.

**Bullet 1: A1 L2, live style join on the deployed artifact.** Met, from `attempt3/a1-cf6t5111/receipt.json` and the raw `stdout.txt`.
- **Cut and split:** the probe cut the only joining span (24645↔24636). The census then shows two networks (915393082 / 140839248), two runs (24634 / 24636), one span up and one cut.
- **Different styles:** after the cut, the two sides read back as Modern / `RM_AerialMast_Modern` and Industrial / `RM_AerialMast_Industrial`. The lamp followed the Industrial run.
- **Real job, running then completed:** the colonists probe shows Ellison (478) undrafted with the current job `RM_RestringSpan`. Over ticks 2327→4080, the restring state moved from cut 1 / jobsDone 1 to cut 0 / jobsDone 2 / spansRestrung 2. The order succeeding was not treated as proof; the job had to run and finish.
- **Joined single style:** afterwards all three masts share one network (1480521728) and one run (24634), all Modern / `RM_AerialMast_Modern`. The lamp returned to Modern. The game logged "Joined a Industrial run to a larger Modern run".
- **Job assignment:** I read `AerialProbe.cs`. `restringjob` builds the job with the real `WorkGiver_RestringSpan` and hands it over with `TryTakeOrderedJob`. So the real job driver ran, but the normal work-scheduler pickup was skipped.

**Bullet 2: A2 L2 fresh row, A3 L0 mod_completion.** Met.
- **Fresh row:** the M15f row is MOD class and PASS. The launcher (`restring_style_proof.py`) checks that the output file was created inside the run's own time window and has schema 1 with `jobDef` `RM_RestringSpan`.
- **Full driver exit:** the full aerial driver exited 0 with 39/39 rows PASS, and the log-budget row found no errors and no lost polls.
- **Artifact:** the loaded GSS DLL hash is `c16983bc…`, its MVID matches the file, and the census shows GSS among the running mods. That proves it was loaded and active, not just deployed.
- **A3:** before the run, mod_completion listed `RM_RestringSpan` as unverified; after, it is "works" (2 passes, 0 fails, last pass 2026-11-11) and the Unverified list is empty.
- **No faked provenance:** `proof_runs` finds result files by searching the mod's own source folder. The copy placed there is checked to be byte-identical to the raw driver output, so nothing was marked by hand.

**Bullet 3: identity, preflight, restoration, shutdown.** Met.
- **Mod list:** 13 mods. That is the smallest tier the dependencies need, with all five DLCs, in an order that matches the intended list. A snapshot of the mod list was saved first.
- **Preflight:** the deep cold preflight and the live preflight are both GREEN, run with the unit's own seat.
- **Deploys:** they were scoped to just the GSS and HugeThings DLL+stamp pairs, both reported "VERIFIED in sync", and the deploy holds were respected.
- **Restoration (from `attempt3_guard.json`):**
  - The guarded begin save's hash was the same before the restore reload.
  - After reloading, the scene, pawns, jobs and tick (3) exactly equal the baseline.
  - Mod settings, debug flags and difficulty were restored and read back. The GSS config files are byte-equal.
  - No existing save changed; the only new save is the unit's own begin save.
  - After shutdown, the readback re-hashed every save and they still match.
- **Shutdown:** stopped via `live_session.stop_game`. The game measures NOT RUNNING / DOWN, the driver lock is FREE, and the BRIDGE file reads FREE since 20:23:02Z.

**Bullet 4: tests, builds, broaden, look.** Met.
- **Harness fixes were narrow and didn't loosen acceptance.** The attempt 1 and 2 failures were harness faults:
  - A local `tap` variable overwrote the log tap; it is now renamed `power_tap`.
  - The drip-loops-off check expected a stale 25-point curve. It now copies the shipping `SpanEndSamples` logic and expects 31, and its self-test still rejects the retired 25-point curve.
  - The journal reader now accepts the bridge's standard reply wrapper while still rejecting failed reads.
- **Tests:** they went from RED (raw output kept) to a final GREEN of 4/4.
- **Build:** no shipping C# or texture changed, and the DLL is the one already published last round. The single `.cs` edit is a comment on a file the normal build doesn't compile; executable text is checked equal to HEAD, and it is not in the DLL's source-hash list.
- **Failed attempts preserved:** attempts 1 and 2 are kept in full in the raw folder.
- **Broadener:** a fresh Opus broadener ran before the final proof, with Read/Glob/Grep only, no saved session and no MCP servers.
- **Look:** the approved cord look is unchanged.

**Limits to state honestly:**
- The cut, the restyles, the job hand-off, teleports and drafting were all done through dev probes, not player designations or a real explosion.
- The test used one disposable registered site. Loading that site logs a vanilla "CurKindLifeStage" error, before the proof's log cursor starts.
- The masts read colour as null on both sides, so the style comparison really checks look and raw style, not colour.
- Other rows in the full driver are still synthetic kinetic or gravship "owed" rows.
- The test runner marked its GREEN results "not recordable"; the readback's input-hash match covers this.
- My hash verification relies on `readback_final.json` and the scripts I read.
- The wrapper's automatic OWNER game events (logged as run by the unit's own seat) are preserved for the parent to note.
- Three GSS switches still show as broken in mod_completion; they belong to other items.

**Blocker:** none.

Would you show this to the owner as completing this item? **Yes.**

would show: yes
