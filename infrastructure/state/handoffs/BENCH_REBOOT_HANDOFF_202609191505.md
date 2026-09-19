# BENCH_REBOOT_HANDOFF_202609191505 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609190938`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**This wave was infrastructure, not RimWorld — and its whole point is that the owner can
now reach this machine when Claude's own Remote Control fails.** The mechanism lives in a
new machine-wide skill, `claude-remote-control` (`D:\Luke\dev\claude-remote-control`,
symlinked into `~/.claude/skills/`, remote `Lmandrake/claude-remote-control`). Load it
before touching anything RC-, phone- or login-related; do not re-derive it from this file.

🔑 The finding that reframed everything: **every machine-wide "sudden disconnect from the
rc server" was a `/login` in ONE window** — MEASURED 4 of 4 events (2026-09-08, 09-10,
09-12, 09-17), each time one window printing `Login successful` and the others printing
`Remote Control disconnected — signed-in claude.ai account or organization changed`. It
is not the server flaking, so "fix the server" is the wrong instinct. `--remote-control`
on every profile (shipped) fixes the RESTART path, not the drop.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **His fleet changed shape, on his word.** Every Claude profile now launches with
  `--remote-control '<label>'`; a new white `Server` tile runs `claude remote-control`
  standalone; `EMERGENCY` was folded into the installer (it was hand-made and would
  otherwise have missed the flag). `051d3cc55`. Takes effect per window on next launch.
- **`remoteControlAtStartup: true`** is now set in `~/.claude/settings.json` on his yes —
  it turns RC on for windows he opens by hand too. ⚠️ Its interaction with `claude -p`
  consumers (the in-game Oracle) is UNMEASURED; if the phone list fills with junk
  sessions, that setting is the first thing to turn off.
- 🔴 **Two Claude accounts are now credential slots on this machine**: `luke`
  (lukas.mandrake@gmail.com) and `steve` (steven.james.lewis@gmail.com), under
  `~/.claude/accounts/`, mode 0600. `rc account steve` / `rc account luke` switches in
  about a second with **no browser** (MEASURED, switched and switched back). Anyone
  working here should check `rc account` before wondering why usage or limits look odd.
- **The mystery window that flashed on his desktop for eight days was NOT an agent** —
  it was the Windows scheduled task `Custos SpaLogger` (created 2026-09-11, every 10
  min) running `python.exe`, which opens a console. Switched to `pythonw.exe`; verified
  still logging. `Custos@87cd749`. Unrelated but visible: the spa reads UNREACHABLE in
  885 of 1162 samples, long predating the change — his call whether that matters.
- **Custos now has a private GitHub remote** (`Lmandrake/Custos`) — it had none, so its
  history lived on one disk. `secrets.yaml` is gitignored and was never committed.
- **The skill was benchmarked, not just written**: 3 evals × with/without, 71% vs 23%
  pass (`D:\Luke\dev\claude-remote-control-workspace\iteration-1\review.html`). The
  cleanest result: asked about `/login` before travel, the no-skill baseline said
  *"nothing risky about it"* and claimed one login re-authenticates every window — the
  exact opposite of what happens.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `REBOOT_BREAKGLASS_VERIFY_1` -- proposed (BENCH), filed this wave, full spec in the
  item. NEXT: at a moment when losing the fleet for ten minutes is fine, reboot Windows,
  and BEFORE logging in try `mandrake@archmagi-wsl` from the phone over **cellular**; if
  refused, convert the `WSL Keepalive` task from `-AtLogOn` to `-AtStartup` and repeat.
- The 13 pointers inherited from `BENCH_REBOOT_HANDOFF_202609190938` were NOT worked this
  wave — art/queue items waiting on the Codex weekly meter (resets Mon 2026-09-21 09:32)
  or owned by FOUNDRY. NEXT: read that handoff as well as this one and treat its pointer
  list as still live; nothing here supersedes it.

Every other thing this wave touched is closed, committed and pushed in all three repos
(Rimworld `d1b980bf9`, claude-remote-control `05a9939`, Custos `87cd749`).

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- The CLI's `claude auth login` prints an authorize URL and waits for a pasted code; the
  browser does **not** auto-open from WSL — open it with `powershell.exe Start-Process`
  and hand the URL over (see: `claude-remote-control/references/incident-log.md`).
- `claude remote-control --help` prints its help and then HANGS; two processes had to be
  killed by PID. Use `claude --help | grep -A2 remote` (see: that same incident log).
- An agent **cannot** turn Remote Control on — in itself or a peer. Relaying "please
  resume remote control" to three windows scored 0 of 3 on 2026-09-19 (see: the skill).
- `scripts.aggregate_benchmark` reads `grading.json` → `summary.pass_rate` and only finds
  runs under `<config>/run-N/`; a grader writing `pass_count` at top level yields a
  confident **0% vs 0%, delta +0.00** rather than an error (see: that workspace).
- A Windows scheduled task running `python.exe` under an Interactive logon flashes a
  console window every run; `pythonw.exe` is the fix (see: `Custos/deploy/spa_logger.py`).

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (1) — the next seat's queue

- `REBOOT_BREAKGLASS_VERIFY_1` — Verify the break-glass path survives a Windows reboot: WSL Keepalive must bring tailscaled back before login, and the fleet may need a hand

## Commits

```
d1b980bf9 REBOOT_BREAKGLASS_VERIFY_1: file the one open follow-up from the Layer 3 build
4d2652878 Remote Control protocol: point at the new claude-remote-control skill; lesson filed
051d3cc55 Fleet: --remote-control on every Claude window; new white Server tile runs `claude remote-control`
9929af465 FOUNDRY_REBOOT_HANDOFF_202609191332: overnight BELT wave handoff
6e515e79b rimflow: sync ledger (game-state DOWN stamp) + derived health/queue artifacts
133a19658 rimflow: sync ledger — KCSG_PAWNKIND_COLONIST_FALLBACK_1, PYRELANDS_FLORA_LEAK_1, BRIDGE_MAPGEN_STALE_FINALIZE_1 closed
960d911db FOUNDRY overnight batch: live-verify 10 items on the full 621-mod load
7d1cd16f0 SWBestiary: fix Juv PawnKindDef lifeStages append bug (live regression from FULL_LOAD_RESIDUE_TRIAGE_1)
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-19T13:30:27Z

Uncommitted — NONE of these are this wave's; every file BENCH touched is committed and pushed (
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   <<< health publisher (auto), not mine >>>
 M Transient/codebase_health.json   <<< health publisher (auto), not mine >>>
 M Transient/codebase_health_artifact.html   <<< health publisher (auto), not mine >>>
A  infrastructure/artpipe/daemon_run_20260916_bench_restart.log   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kinrath_v1_east.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kinrath_v1_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kinrath_v1_north.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kinrath_v1_north.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kinrath_v1_south.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kinrath_v1_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kreetle_v1_east.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kreetle_v1_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kreetle_v1_north.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kreetle_v1_north.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kreetle_v1_south.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kreetle_v1_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json   <<< artpipe daemon + other waves — not mine >>>
R  infrastructure/artpipe/pending/nuitae_a_v1.json -> infrastructure/artpipe/done/nuitae_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/nuitae_a_v1.manifest.json   <<< artpipe daemon + other waves — not mine >>>
R  infrastructure/artpipe/pending/nuitae_b_v1.json -> infrastructure/artpipe/done/nuitae_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/nuitae_b_v1.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/rut_agelesscap_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/rut_agelesscap_v1.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.manifest.json   <<< artpipe daemon + other waves — not mine >>>
R  infrastructure/artpipe/pending/yumbulbs_a_v1.json -> infrastructure/artpipe/done/yumbulbs_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/yumbulbs_a_v1.manifest.json   <<< artpipe daemon + other waves — not mine >>>
R  infrastructure/artpipe/pending/yumbulbs_b_v1.json -> infrastructure/artpipe/done/yumbulbs_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/yumbulbs_b_v1.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/failed/nysyllin_v1_r2.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/failed/nysyllin_v1_r2.manifest.json   <<< artpipe daemon + other waves — not mine >>>
 D infrastructure/artpipe/failed/orray_v3_south.json   <<< artpipe daemon + other waves — not mine >>>
 D infrastructure/artpipe/failed/orray_v3_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/crystalcap_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/crystaltipbrambles_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/crystaltipbrambles_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/dulciscropitem_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/dulcisgrown_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/dulcisharvested_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/dulcisimmature_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/fungusfern_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/fungusfern_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/fungusfern_c_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/fungusfern_d_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/gleamtip_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/gleamtip_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/greyladygrown_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/greyladygrown_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/greyladygrown_c_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/greyladyimmature_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonechunk_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonechunk_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonechunk_c_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonechunk_d_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonehuge_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonehuge_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstoneitem_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstoneitem_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstoneitem_c_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonelarge_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonelarge_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonemedium_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonemedium_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonemedium_c_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonesmall_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonesmall_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonesmall_c_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonesowableimmature_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstoneterrain_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonewallicon_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/luminousspout_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/luminousspout_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/mycelium_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/mycelium_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/mycelium_c_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_falsefruit_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_furnacecap_plant_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_gene_furnaceblood_icon_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_grownfurnace_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_liveingredient_agelesscap_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_liveingredient_euphoriccrown_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_liveingredient_regenerantveil_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_liveprep_toxicinjection_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_livingfurnacecap_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_palemoss_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_paletree_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_regenerantveil_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_symbiont_mycoid_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_symbiont_nightwake_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_symbiont_quickflesh_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_symbiont_sheenblood_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_tea_agereversal_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_tea_bioregeneration_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_tea_pleasure_v1.json   <<< artpipe daemon + other waves — not mine >>>
MM infrastructure/artpipe/registry.jsonl   <<< artpipe daemon + other waves — not mine >>>
M  infrastructure/artpipe/throughput.jsonl   <<< artpipe daemon + other waves — not mine >>>
 M infrastructure/dashboards/hub/data/health.json   <<< health publisher (auto), not mine >>>
 M infrastructure/state/codebase_health_last.json   <<< health publisher (auto), not mine >>>
 M infrastructure/state/queue/FOUNDRY.md   <<< rimflow/queue churn from peers — not mine >>>
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\tools_dump.txt"   <<< peer scratch output — not mine >>>
?? deployed/config/ModsConfig.before-tier-oracle.xml   <<< FOUNDRY's modlist snapshots — not mine >>>
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   <<< FOUNDRY's modlist snapshots — not mine >>>
?? deployed/config/ModsConfig.before-tier-warlab.xml   <<< FOUNDRY's modlist snapshots — not mine >>>
?? infrastructure/artpipe/pending/orray_v3_south.json   <<< artpipe daemon + other waves — not mine >>>
?? infrastructure/state/.rimflow_conc_97j8px_9/   <<< rimflow/queue churn from peers — not mine >>>
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   <<< rimflow/queue churn from peers — not mine >>>
```

