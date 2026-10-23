# FOUNDRY_HANDOFF_202610230308 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610221110`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

Owner order 2026-10-22: FlowWorks first (done offline: all 38 selftests pass, 830+/830 SelfTest, ~all DIRTY reviewed, live scripts written, DLL stamp matches), then the mods closest to release, and he answers question cards on his phone (cannot review sheets). EVERYTHING is offline: game up, BENCH held the bridge all day, nothing was deployed. The next unit of value is ONE bridge sitting: read `design/RimMandrake/next_bridge_runbook_2026-10-22.md` (3 loads) with `design/RimMandrake/deploy_plan_2026-10-22.md` (needs `--prune` for Biomes composite + UtinniPatches; DLL mods need the game DOWN; hand-remove `Mods\Ninefold`, `Mods\IshkoDarkLandmarks`, `Mods\ShokkweaveEconomy`, `Mods\RustCathedralRoaches` from the game install or hooks run twice). Review replies from GPT for 8 mods are in `D:\ClaudeWork\gpt_review_2026-10-22\<Mod>\GPT_REPLY.md`; 7 triaged in `design/RimMandrake/gpt_review_findings_2026-10-22.md`. (filed: lessons)

## What the owner should see

- All of today's owner card answers are recorded in `webworks_open_questions_*`, `rot_open_questions_*`, `biome_owner_cards_*`, `gpt_review_findings_*` (look for ANSWERED lines). Surprises he may want to veto: Webwork front creep DELETED (spiders make webs); Ninefold folded into Salvation Rites and Ishko landmarks moved there (his words: the Nine Gods are not a general reuse mod); portable living mat (quest reward at ship-log entry 8, buds, cap 3/map); spider siege built (shaded neighbours only; cocoon death after a day).
- Pending his look: Graffiti offset drawing (south walls kept upright), navy deep-water tint + wall shadow band (blind pick), dustveil flight frames (15 queued, never live-test flight without him), RM_Webwork vs RUT_Webwork at the end paint.
- RimPulse fix is pushed but BENCH must pull and run `systemctl --user restart rm-pulse.service` (it runs from the BENCH clone).
- Unasked: biome cards 3, 6, 10, 11 need pictures (juvenile Igitz/Mudhorn, Kybuck, moss beetle, Nysyllin delete); 8 other Inhabited cast files differ from their generator; `cast_assignment.csv` still lists AnimaColossus; siege Q6 (night as shade) left as built.

## What is half-done, and where it stops

- `GPT_REVIEW_BIOMESCOMPOSITE_UNTRIAGED_1` — reply is back, not verified; NEXT: spawn an Opus helper to verify `D:\ClaudeWork\gpt_review_2026-10-22\BiomesComposite\GPT_REPLY.md` against the code and append to `design/RimMandrake/gpt_review_findings_2026-10-22.md`.
- `NEXT_BRIDGE_SITTING_ALL_LIVE_CRITERIA_OWED` — ~25 items built with live criteria owed (FlowWorks water looks A1-A4, pipe/hose/levelling, overflow Stage 4, GSS fresh proof + record, siege rows, thrixweave resale, mat, dustveil state read, ponds, Rot core, Pyrelands opening_front, Graffiti L4, Ninefold/Rites minimal-list sitting, Greentide ants, egg market); NEXT: when BENCH releases the bridge run the runbook cheapest-first and `rimflow verify` each criterion.
- `BIOME_MECHANICS_JUDGE_FLUFF_ON_TRIAL` — inventory done (~420 rows), owner has not ruled; NEXT: ask him the top-10 fluff candidates by card from `design/RimMandrake/special_mechanics_review_2026-10-22.md`.
- `DIRTY_CODE_REVIEW_STANDING_LOOP_1` — Pyrelands.xml DIRTY on purpose (per-biome SunHeatExtension vs Direct Sun ruling); NEXT: re-review after the Direct Sun migration.
- `TheRot mock run` — same harness defect as Webwork's (2 PASS / 9 FAIL / 84 UNMEASURED); NEXT: route the TheRot driver mock to per-chain models like northstar_plan.py did for Webwork.
- `WORLD_REMAKE_TILE_PICKS` — ship-core tiles wait for the remake by his ruling; NEXT: nothing until the remake.
- `GREENTIDE_ANTS_NAME_ART_SOUNDS` — ants moved to the free Greentide mod; name, art, two raid sounds still owed; NEXT: queue only after he rules the name.

## Traps learned

- RimPulse's 22 reds were stale session files + its own OOM, not real breakage. (see: commit 8f6167818)
- `./publish` is refused by ANY other agent's uncommitted file in the shared clone (ledger OWNER.jsonl, validation_walks); wait/retry, never stash. (filed: LESSONS)
- Helper builds of a staged `src/` race with peers saving files (rsync 'vanished', rc=24): winbuild retries now. (see: commit 37f064ef7)
- Mock harness that does not know a bridge call turns a whole run into FAIL/UNMEASURED: check the mock before blaming the mod. (see: commit b93cf9984)
- A card option 'Recommended' can contradict a standing ruling (stop evictions): re-read rulings before recommending. (filed: LESSONS)

## Commits

```
97715d9fb ROT_WARM_MAT_BUILD_WORKS_FOR_FOOD: owner card answers noted, re-implemented at 346405c30 (7 live criteria owed); clean marks
346405c30 Living mat root: won from the dead ship's last camp, buds when well fed (capped per map), keeps its floor-tile art
80f9c706d Art selftests: reopen fixture rows c87bbf460 now drops as all-ruled; guard selftest covers the reverse shadow
6c7d8af76 Sheet decisions, conversation log, modcheck fixture tick and ModsConfig backup left uncommitted by earlier helpers
24d69185f Art guard selftest: latest retire wins
b3f19d366 Art guard: a deletion is judged by the latest explaining ledger event, not an older restored one
d235b9c1c Greentide ants: retire the four kept RUT_ stub pictures (copies live in src/RimMandrake/Greentide, byte-identical)
ec8f4d3ee Graffiti: a mark on a south wall stays upright (still offset onto the wall); other sides unchanged
5aa3154dd Ledger: file ART_INSTALL_WIRE_BY_CARD_FLAG_MISSING
628201bd2 Modern hose reel: fire-hose-reel research (12 sources) + 3 drafted options, all facings; phone set rebuilt
1b15c4435 walk_tonight: joint check as a hard rebuild step; fittings note
18b4852f1 Ledger: release hose joint leases
1c79980b7 Ledger: hose joints + scenario reels built; three findings filed
48a27caed Rebuild RimMandrakeFlowWorks.dll from committed source at landing
7870b3b59 Hose joints: lesson (why the GSS connector test did not come over), review marks; comments cite the real reel-port test selftest_reel_ports.py never existed; the table-vs-art check is FlowWorks/selftest_hose_ports.py.
3330c60f9 Hose walls: items built (HW1 live row owed on save b), lesson on self-measuring selftests, ledger
95554978c Ledger: note redraw 8 installed
41c06f6a2 Portable ladder: install redraw 8 (Graphic_Multi, drawSize 1.5, RM_Ladder offsets); legibility pass
cf6d33f7b Rebuild RimMandrakeFlowWorks.dll from committed source at landing
849b1674e Rebuild RimMandrakeFlowWorks.dll from committed source at landing
... 384 more: git log --oneline 45c4ade22..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
?? Transient/fw_scenes/live/S1_20261017T084726.txt   pre-crash FlowWorks scene captures from 2026-10-17 (Transient, unpinned, ~14-day shelf; not mine, left untracked by design)
?? Transient/fw_scenes/live/S1_20261017T084802.txt   pre-crash FlowWorks scene captures from 2026-10-17 (Transient, unpinned, ~14-day shelf; not mine, left untracked by design)
?? Transient/fw_scenes/live/S1_20261017T092155.txt   pre-crash FlowWorks scene captures from 2026-10-17 (Transient, unpinned, ~14-day shelf; not mine, left untracked by design)
?? Transient/fw_scenes/live/S1_20261017T110253.txt   pre-crash FlowWorks scene captures from 2026-10-17 (Transient, unpinned, ~14-day shelf; not mine, left untracked by design)
?? Transient/fw_scenes/live/S1_p00.png   pre-crash FlowWorks scene captures from 2026-10-17 (Transient, unpinned, ~14-day shelf; not mine, left untracked by design)
?? Transient/fw_scenes/live/S1_p03.png   pre-crash FlowWorks scene captures from 2026-10-17 (Transient, unpinned, ~14-day shelf; not mine, left untracked by design)
?? Transient/fw_scenes/live/S1_p10.png   pre-crash FlowWorks scene captures from 2026-10-17 (Transient, unpinned, ~14-day shelf; not mine, left untracked by design)
?? Transient/fw_scenes/live/S1_p14.png   pre-crash FlowWorks scene captures from 2026-10-17 (Transient, unpinned, ~14-day shelf; not mine, left untracked by design)
?? Transient/fw_scenes/live/S2_20261017T084824.txt   pre-crash FlowWorks scene captures from 2026-10-17 (Transient, unpinned, ~14-day shelf; not mine, left untracked by design)
?? Transient/fw_scenes/live/S2_20261017T092355.txt   pre-crash FlowWorks scene captures from 2026-10-17 (Transient, unpinned, ~14-day shelf; not mine, left untracked by design)
?? Transient/fw_scenes/live/S2_20261017T110404.txt   pre-crash FlowWorks scene captures from 2026-10-17 (Transient, unpinned, ~14-day shelf; not mine, left untracked by design)
?? Transient/fw_scenes/live/S2_p00.png   pre-crash FlowWorks scene captures from 2026-10-17 (Transient, unpinned, ~14-day shelf; not mine, left untracked by design)
?? Transient/fw_scenes/live/S2_p10.png   pre-crash FlowWorks scene captures from 2026-10-17 (Transient, unpinned, ~14-day shelf; not mine, left untracked by design)
?? Transient/fw_scenes/live/S2_p30.png   pre-crash FlowWorks scene captures from 2026-10-17 (Transient, unpinned, ~14-day shelf; not mine, left untracked by design)
?? Transient/fw_scenes/live/S2_p60.png   pre-crash FlowWorks scene captures from 2026-10-17 (Transient, unpinned, ~14-day shelf; not mine, left untracked by design)
?? Transient/fw_scenes/live/S3A_p20.png   pre-crash FlowWorks scene captures from 2026-10-17 (Transient, unpinned, ~14-day shelf; not mine, left untracked by design)
?? Transient/fw_scenes/live/S3B_p06.png   pre-crash FlowWorks scene captures from 2026-10-17 (Transient, unpinned, ~14-day shelf; not mine, left untracked by design)
?? Transient/fw_scenes/live/S3B_p16.png   pre-crash FlowWorks scene captures from 2026-10-17 (Transient, unpinned, ~14-day shelf; not mine, left untracked by design)
?? Transient/fw_scenes/live/S3_20261017T084854.txt   pre-crash FlowWorks scene captures from 2026-10-17 (Transient, unpinned, ~14-day shelf; not mine, left untracked by design)
?? Transient/fw_scenes/live/S3_20261017T084938.txt   pre-crash FlowWorks scene captures from 2026-10-17 (Transient, unpinned, ~14-day shelf; not mine, left untracked by design)
... 171 more uncommitted paths (by top-level dir: Transient 167, deployed 3, src 1): git status --short
```

