# FOUNDRY_HANDOFF_202610161835 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610161216`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The art pipeline is only safe at ONE shared Codex home per guard: any worker home whose sandbox state predates the latest elevated setup raises a full-screen UAC dialog on the owner's screen. Guard `3b184ada3` (`artpiped.py --check-sandbox`, `--sync-sandbox`) now syncs state before every launch; the daemon runs at -N 5 from the FOUNDRY clone via drop-in `zz-foundry-workdir.conf`. If ANY "sandbox setup required" line appears in `C:\Users\Mandrake\.codex_workers\artpipe\w*\.sandbox\sandbox.*.log` newer than 10:22 PDT 2026-10-16, drop `workers5.conf` to -N 1 at once. Also: every helper brief must forbid background timers/child agents (the owner killed stalled agents by hand).

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Review sheets for Zisska FireSpit, Braskeen v3 and swollen Dhoggur are ENACTED on his word; kit art designs (15 guessed pieces) are in `design/RimMandrake/kit_art_designs_2026-10-16.md` for his veto; 63 dessicated-corpse jobs use a look I wrote (no prose file existed).
- Decisions only he can make: the other ~129 AB_ names for Alpha Biomes retirement (`ALPHA_BIOMES_CENSUS_THE_REST_OF_IT`); retire `src/RimUtinni/PlantGrowth`; which RimPulse 'to rule' rows he wants as cards (I found most 'decision' items already ruled/triaged).
- His mod list lost 3 dead/redundant entries (551 -> 548, backups in deployed/config).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `ART_QUEUE_DRAIN_AND_SHEETS` — daemon rendering ~108 pending jobs at 5 workers (corpses, kit art, wave 2, overlays B/C/D, Braskeen v4/v5); NEXT: when the queue drains, build review sheets (art_sheet.py, true scale) and serve via serve_gated.py; install nothing unreviewed.
- `PACK_OVERLAYS_BUILD_SHARED_SADDLEBAGS` — overlay A rendered, B/C/D queued, none installed or on a sheet; NEXT: build a sheet of A-D over Bantha/Dewback/Reek bodies.
- `ALPHA_BIOMES_CENSUS_THE_REST_OF_IT` — plan written, 14 plants need RM_ twins; NEXT: put the 129-name census to the owner as a card, then start ALPHA_BIOMES_MIGRATE_PLANTS_TO_RM_TWINS.
- `SUCCULENT_PLANTS_REDRAW_BORROWED_WARDROBE` — 14 plants lack own art, 3 queued; NEXT: queue the rest after the owner reviews the first three.
- `DONOR_PHASE0_FINISH_AWAITING_HIS_RULINGS` — L1 249/11/6; NEXT: fix Bileworm (Cauldron, Miasma) and Zrrik (Greentide) rosters at his sitting, run the ikee swap on the FULL list, owner-present flight rows, then P7 and the section 0.5.5 gate.
- `DONOR_PHASE0_P6_SAVE_REWRITE` — 11 donor def refs in the canonical save unconfirmed; NEXT: grep the save offline and rewrite a copy per the rimworld-savegame skill.
- `ZISSKA_FIRESPIT_PROVE_LIVE` — FireSpit wired to RM_Zisska, never run live; NEXT: with the bridge, spawn a herd of 3-6 in the Cauldron and check fire spread and combat power 40.
- `ARTPIPED_BENCH_CLONE_PULL` — bench clone predates the sandbox guard; NEXT: have BENCH pull 3b184ada3, then delete ~/.config/systemd/user/rm-artpiped.service.d/zz-foundry-workdir.conf and `systemctl --user daemon-reload`.
- `DHOGGUR_STATUS_REPORT_SWOLLENART` — status report reads False when Dhoggur is off camera; NEXT: make the report check the swollen texture directly (TheForge rebuild with game down).

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- Codex worker homes with a stale sandbox state raise one UAC dialog per home; one approved setup breaks every other home (filed: LESSONS, 20261016T173052Z-FOUNDRY-codex-uac-sandbox-dialogs-from-artpipe).
- Mass-queueing artpipe jobs wakes all workers and was the trigger of the owner's popups (filed: LESSONS, 20261016T172335Z-FOUNDRY-queueing-many-artpipe-jobs-wakes-5).
- I killed `telemetryd` by PID guess; always read the command line first (filed: LESSONS, same file).
- Helpers that leave wait timers or child agents show as stalled agents (filed: LESSONS, 20261016T183351Z-FOUNDRY-subagents-left-background-wait-timers-child).
- My loose ledger filter listed 90 'owner' items; most were already ruled (see: rimflow show <ID>; BENCH triage 2026-10-12).

## Commits

```
de4b8ffe0 lesson: helpers must leave no background timers or child agents running
2d8aff2bb BENCH handoff 2026-10-16 midday: ExplosiveGrowth consensus landed, self-matching wait guard shipped fleet-wide
a061cba92 Queue 63 dessicated-corpse artpipe jobs; Alpha Biomes retirement plan (14 plants + 3 diseases already have our art); file 7 items
f5b83b4ec Sprint kit art: 15 guessed designs for veto, 21 artpipe jobs queued (SPRINT_KIT_ART_SKETCH_BEFORE_THE_VETO)
c940fe347 lesson: pgrep -f wait loops match their own shell and never end
3b184ada3 artpipe: never launch codex into a stale Windows sandbox state (no UAC setup dialog)
43e130724 Repoint unfertilized BedBug/Dustveil egg defs to installed fertilized art (shared graphic, vanilla convention); de-stale texture_gap_lint selftest probe
0fb6105a5 Sprint art commissions: 65 artpipe jobs (overlays B/C/D, Braskeen v4/v5, 4 gap fills, 50 donor-byte item/icon/pose jobs); 207 SWAC-byte slots found still live
932b338c3 Mod list: remove 1 dead (tormentmaster) and 2 folded-into-Biomes entries (explosivegrowth, plantgrowth)
ae93c2fab File SUCCULENT_PLANTS_REDRAW_BORROWED_WARDROBE: 14 defs on donor succulent paths owe own art
0aba1c303 Fix 17 file-vs-folder texPath/graphicClass mismatches (donor-off L1 L04_TEX_OURS)
71447e741 Dhoggur swell live 16/16 PASS with the attack-only filter; close DHOGGUR_SWELL_PROVE_LIVE_POKE_THE_BEAR
64cba2bdb dhoggur_swell chain: env arms retry past the hide; fresh unhurt dhoggur for the attack arms
a5fe575ba Explosive growth consensus: ground moisture taxonomy, density vs growth, watering model
66f11b6b5 Dhoggur swell: only attacks provoke it (card 2026-10-16); jawa/damage gains instigatorId
d34ead293 Explosive growth consensus model (draft; ground taxonomy section pending)
b3a4e27fc BENCH handoff 2026-10-16 morning: FW walk fixes built offline, sprint S0 ruled, ExplosiveGrowth consensus running
197f977b0 Install swollen Dhoggur art (3 facings) and Braskeen v3 variant on owner's word; enact Braskeen/Firespit-Zisska sheets; close BRASKEEN_REDRAW_VARIATIONS_ON_E
c4068a896 Ledger: owner's ExplosiveGrowth intent (verbatim)
fa04d1f55 Venomvine design: islands, tree height, own creep outside Explosive Growth, 15 forms as rooms; 4 card questions
... 182 more: git log --oneline 2738d7ec1..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/biome_ffar/abyss_sheet_2026-10-04.html   generated/other (sheet tooling, not mine)
 M Transient/biome_ffar/aiwha_wingfirst_sheet_2026-10-15.html   generated/other (sheet tooling, not mine)
 M Transient/biome_ffar/phase0_remaining_art_sheet_2026-10-16.decisions.json   generated/other (sheet tooling, not mine)
 M Transient/biome_ffar/scale_ground_measured.json   generated/other (sheet tooling, not mine)
 M Transient/phase0_p6_save_renames.md   generated/other (sheet tooling, not mine)
 M conversations/2026-10-16-0549-c453ca3a.md   generated/other (sheet tooling, not mine)
?? Transient/biome_ffar/img/00063bfc98bbf60c00c9.webp   generated/other (sheet tooling, not mine)
?? Transient/biome_ffar/img/004678d5bc522129f222.webp   generated/other (sheet tooling, not mine)
?? Transient/biome_ffar/img/0052887ea95ee55cb4ce_full.png   generated/other (sheet tooling, not mine)
?? Transient/biome_ffar/img/0099e32f18695cf71e35.webp   generated/other (sheet tooling, not mine)
?? Transient/biome_ffar/img/012b0e9de80257c66cba.webp   generated/other (sheet tooling, not mine)
?? Transient/biome_ffar/img/012c446f56fabd4bd893_full.png   generated/other (sheet tooling, not mine)
?? Transient/biome_ffar/img/0139244f2dcf4a25b9e9.webp   generated/other (sheet tooling, not mine)
?? Transient/biome_ffar/img/0172b49133d12ef1a9d8.webp   generated/other (sheet tooling, not mine)
?? Transient/biome_ffar/img/01b25e0103f7c8b21a1e_full.png   generated/other (sheet tooling, not mine)
?? Transient/biome_ffar/img/01c24ff299b19e05ebf3_full.png   generated/other (sheet tooling, not mine)
?? Transient/biome_ffar/img/01fbc3e8db36f63ab5e8.webp   generated/other (sheet tooling, not mine)
?? Transient/biome_ffar/img/022a46d1fe26ef2d1b71_full.png   generated/other (sheet tooling, not mine)
?? Transient/biome_ffar/img/0246ec2415ecfd9034c5.webp   generated/other (sheet tooling, not mine)
?? Transient/biome_ffar/img/0365aef56ed78f6d87d8.webp   generated/other (sheet tooling, not mine)
... 1373 more uncommitted paths (by top-level dir: Transient 1367, deployed 2, infrastructure 2, (root) 1, src 1): git status --short
```

