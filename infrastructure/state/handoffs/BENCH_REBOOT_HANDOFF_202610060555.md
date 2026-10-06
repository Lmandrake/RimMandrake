# BENCH_REBOOT_HANDOFF_202610060555 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610051409`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**Many agents in one seat clone deadlock git.** Tonight ~15 helpers shared /home/mandrake/rm/bench; any one agent's dirty files block every other's `git rebase`, so finished work sat unpushed for hours and agents improvised (in-memory replays, one /usr/bin/git hook bypass). What worked: push from a `git clone --shared` scratch copy in ~/.cache (cherry-pick, union-merge *.jsonl), then `git reset --keep origin/main` in the seat clone after proving every local commit's content is on origin. Brief every writing helper with that recipe up front.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Ikee shows lilac in game** even though his liked picture (the single-eye RSW_Ikee A) is now live: the def carries a `<color>` tint (190,170,202). Strip it? It is one of 57 rows on `TINT_ON_COLOUR_ART_1` — his ruling per def (tints multiply full-colour art; that is what the "strange tints" in the scale panel were).
- **Nothing tonight is in the game yet.** Deploy + restart wait for the art queue (his card: "Wait for more art"); last deploy was Blue Desert/Abyss at ~08:15 2026-10-05.
- **Sheets he has NOT sat yet** (gate must PASS and placeholder rows must have landed renders before reopening): Cauldron, Feverwood, Flooded Canyon, Greentide, Grey Sea, Miasma, The Chill, The Forge, The Rot, Twilight Sea, Wasteland, Webwork, Weeping Stones, Long Shade (2nd sitting), Leaning Scrub re-sit. Grey Sea is half-ruled.
- **Fire Hawk / Fire Wasp flight review sheet does not exist** — the sheet tool can't build a frames strip (Pyrelands agent). 48 flip-book frames queued; he asked "Please advise and assist" — the advice is in `Transient/biome_ffar/pyrelands_close_progress_2026-10-05.md`.
- Owner-said rules from tonight, all filed: no donor art kept (vanilla too, by card) but kept as past art; one sheet per biome; cuts apply to RUT_ twins; Abyss dark family = smooth names, pitch-black, four glowing yellow eyes; scale panel on every row (skill `scaled-game-image-review`).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `BIOME_FLORAFAUNA_ART_REVIEW_1` — 10 sheets sat tonight and ingested; ~340+ renders queued; NEXT: after the queue drains, run `scaled_review_gate.py all --urls`, reopen only PASS sheets with zero placeholder-only rows, and list them for him.
- `rm-sheet-refresh-night` (systemd) — refreshes sheets + requeues flakes every 30 min until the art queue drains; NEXT: when it exits, commit the dirty Transient/biome_ffar + infrastructure/state/art files and push.
- `rm-artpiped-back-to-5` (systemd timer 2026-10-06 08:00) — drops artpipe to 5 workers per his card; NEXT: confirm `systemctl --user status rm-artpiped` shows `-N 5` after 08:00.
- `FLYER_FLIPBOOK_ART_1` — 48 FireHawk/FireWasp frames queued, no review sheet tool for frame strips; NEXT: extend art_sheet.py to render a flight-frames strip section, then build the two-flyer sheet.
- `ABYSS_SHEET_DONOR_PORT_1` / `WARSCAR_SHEET_DONOR_PORT_1` — his picks on donor rows wait for owned RM_ defs; NEXT: FOUNDRY ports the defs, then `art install` the ruled picks.
- `ART_RULING_RENAME_CARRY_1` — rulings stay on the old defName across renames (Ikee overwritten 3x); NEXT: make the art guard follow keeps/rejects across renames and copies.
- `TINT_ON_COLOUR_ART_1` — 57 tinted full-colour defs; NEXT: put them on one card/sheet for his per-def ruling, Ikee first.
- Deploy — tonight's installs are repo-only; NEXT: when the queue drains and he says go, `deploy_custom_mods.py --compose biomes --apply` + `--mod UtinniPatches --apply` (+ SWBestiary, TerminalBiomes, etc.), then restart.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Gap-fill counted script-drawn stand-ins and vanilla textures under our defNames as "our art" — Grey Sea was 43/46 placeholders (see: src/RimMandrake/Utils/art/placeholder_detect.py, gate req 3).
- Def `<color>` tints are multiplied into full-colour art in game; the sheet's raw columns hide it, only the scale panel shows it (see: TINT_ON_COLOUR_ART_1).
- SCALE_BIOMES whitelist silently left 21 sheets with no scale panel; one null drawSize blanked whole sheets (see: skills/scaled-game-image-review/SKILL.md req 2, gate req 13).
- An owner's open tab goes stale when a sheet rebuilds; he reviewed old HTML (see: reload banner in art_sheet.py).
- /tmp (18 GB tmpfs) filled from old sessions' scratchpads and broke every agent's commands; put clones/scratch in ~/.cache (filed: LESSONS).
- `art install` + a pathspec commit of defs left the new PNGs untracked — defs on main pointed at missing textures until ac532dccf (filed: LESSONS).

## Closed since the last handoff (1)

- `LANTERNDEEPS_RSW_ORIGINALS_RETIRE_1` — 8c988d74b

## Filed and still open (17) — the next seat's queue

- `PROPANE_LAKE_HYDROCARBON_TENTACLER_1` — Propane Lake: new invented hydrocarbon tentacler from the kept bluedesert_Vapaad_v2 render (owner: keep Option B in the Propane Lakes)
- `ABYSS_SHEET_DONOR_PORT_1` — Abyss sheet 2026-10-05: port 17 donor rows to owned RM_ defs under new names, wire the ruled art
- `ARTPIPE_REQUEUE_AUTOMATION_1` — Auto-requeue codex schema-channel flakes and their master_failed siblings
- `ART_SHEET_DONOR_JOIN_GAPS_1` — Sheet art join misses donor-prefixed names and mislabels our own mandrake.* copies as donor
- `LEANINGSCRUB_SHEET_ART_REDO_1` — Leaning Scrub sheet: wiring, variants and design asks
- `NIGHTSIDEICE_SHEET_ART_REDO_1` — Nightside Ice sheet: redo art and Tauntaun canon wiring
- `NIGHTSIDE_ICE_NEW_LIFE_1` — Nightside Ice strange life: sheet sitting on the roster draft, then defs/C#
- `RUSTCATHEDRAL_SHEET_ART_REDO_1` — Rust Cathedral sheet: LivingBolt redo art, roach size, installs
- `RUSTCATHEDRAL_LIVINGBOLT_WALL_FLIT_1` — LivingBolt flits on walls and surfaces: no mechanism exists, design owed
- `LANTERNDEEPS_SHEET_ART_REDO_1` — Lantern Deeps art sheet 2026-10-05: eye repaints, blinker redo, plant variants to install on return
- `SCALD_SHEET_REDOS_1` — The Scald sheet 2026-10-05: collect and install the redo renders (shimmer eel, doss, crowncarpet x3, iridesce, sando aqua monster)
- `TWILIGHT_GIANT_CATCHES_1` — Twilight Sea owes fishTypes catches for its two new floor giants: RM_GrippingTerror and RSW_SandoAquaMonster (sea ruling: floor + catch)
- `TINT_ON_COLOUR_ART_1` — 57 defs multiply full-colour art by a <color> tint — owner ruling per def
- `ART_RULING_RENAME_CARRY_1` — Art guard: rejected bytes and keep rulings must follow a creature across def renames/copies (Ikee overwritten)
- `MYNOCK_FLIPBOOK_FRAMES_1` — RSW_Mynock flies with no wing-beat: its 8-frame flight flip-book is owed art
- `WARSCAR_SHEET_DONOR_PORT_1` — Warscar donor rows: ruled art picks wait for owned defs
- `FLYER_FLIPBOOK_ART_1` — Wing-beat flip-book frames for every flyer missing them (36 of 64)

## Commits

```
3e9ddbb4c Stillsand sheet sitting 2 ingested: 30 installs, Duumma swim slot, 47 regen jobs
aa4fb0acd Contagion close: validate on the full list (op-24 error was a 10-mod ModsConfig artifact); sheet state
4f8ba82b4 Contagion sheet closed: ikee art restored, 5 tints stripped, Shambles to the Rot, sizes, 39 variant jobs
f01425573 Pyrelands sheet closed: FireHawk walking art M, Orray F, Dalgo B; 48 flyer flip-book jobs
556b020e5 Sheet decisions and art events refresh
d67f9da43 Gate req 14: a purged picture still live in game shows as non-pickable IN GAME column
b7065dc1d Sheet state refreshed
7bcb69807 Sheet state refreshed
0d6e51a3a AA_Helixien is bileworm everywhere: drop the vulloth block from Contagion_Rename
653e02afb Warscar sheet closed: ruled, ingested, cuts, descriptions, jobs
ae134f067 Restore RSW_FacetMoth/RSW_MossBeetle egg-laying; eggs hatch the RM_ larvae
c7e1db396 Close LANTERNDEEPS_RSW_ORIGINALS_RETIRE_1; note the texture hook on ART_VERSION_WRANGLING_1
d50273fb0 Sheet snapshot refreshed
57077365b Sheet snapshots refreshed
8c988d74b Retire the five RSW_ Lantern Deeps originals; texture guard hook registered; 7 names recorded as ours
278ca9876 FOUNDRY helper notes: liquid-looks port + FlowWorks queue
6b5eefe90 FlowWorks DLL rebuilt from d6676a833
d6676a833 FlowWorks: port crash-backup liquid looks, pit outline, pit shadow onto main
50771beb2 FlowWorks machinery art: 23 artpipe jobs filed (stills, pump, cargo tank, adapters, water bottle, 5 machines x wrecked/kludged/repaired chain)
b48a7193c Sheet state and art events refresh
... 196 more: git log --oneline 8cec56723..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : DOWN  → corrected to UP, measured now
- Bridge: FREE    since 2026-10-06T03:43:05Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
(committed ac532dccf) contagion/deep_desert sheet state — BENCH
?? conversations/   session transcript exports written by a hook; deliberately untracked, not BENCH work
```

