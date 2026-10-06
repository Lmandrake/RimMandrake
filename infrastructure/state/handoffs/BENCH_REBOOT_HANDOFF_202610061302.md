# BENCH_REBOOT_HANDOFF_202610061302 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610060904`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**The Grey Sea floor's first live run found a real defect, and the fix is committed but NOT DEPLOYED.** Map Designer (`zylle.mapdesigner`) snapshots biome densities at startup (ctor 835/1610) and writes them back at game start, undoing `RM_SeabedFloorLife`'s copy (ctor 1607): every sea floor reads plantDensity 0 / animalDensity 0 live, so floors grow no plants and spawn no animals. Fix (re-assert before floor generation + on `Game.FinalizeInit`) is in `d97142596`; the game copy of `RimMandrake.DivingInteraction.dll` still drifts. Any seat touching sea floors must deploy it first.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Morning card ruled (02:06, by card): tints stripped on all 56 (`e2bcad71d`, incl. the 3 reskins — RSW_VentStalker/WraidAlpha/ShadeWhale now look like the creatures whose art they borrow until they get their own); only fish-sized sea creatures get a catch (CLAUDE.md amended); deploy+restart done (full 610-mod list restored, biomes compose, Utinni, SWBestiary, GreentideRaidAnt, bridge tools DLL with layer=).
- Grey floor live (first ever, `src/RimMandrake/DivingInteraction/northstar/grey_floor_live_20261006T055557.json`): Grey generator runs on RM_SeabedLayer (no pocket map), pillars + crystals PASS, flora 0/16 RED → Map Designer cause above.
- Salt chimney: its sprite was the 09-26 script placeholder; render job `greysea_saltchimney_v1` filed with his words. Pillars/domes/jackets/crystals draw as rock walls (ParentName RockBase), not sprites.
- Keeper save `RM_gss_review_20261006_prerestart.rws` taken of FOUNDRY's GSS review map before BENCH's restart.
- Northstar review for him: `design/RimMandrake/northstar_review_2026-10-06.md`.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `GREYSEA_FLOOR_PASS_1` — density fix committed (d97142596), not deployed, game DOWN (BENCH closed it, then paused for FOUNDRY); NEXT: with the game closed run `deploy_custom_mods.py --compose biomes --apply`, launch, then `python.exe src/RimMandrake/DivingInteraction/northstar/run_grey_floor_live.py` and expect flora/cast GREEN plus the log line "densities were reset by another mod".
- `NORTHSTAR_RESULTS_JOIN_1` — report names unread mods, no join; NEXT: add a `checkout:` walk header and teach required_checks.py + the report to read proof_all rows.
- `SHEET_DONOR_COLUMN_FALSE_PASS_1` — req 4 false pass on our copies; NEXT: export `ours`, count an owner-purged donor original as shown-and-rejected, rebuild Abyss/TheRot/Feverwood/WeepingStones.
- `PROPANE_LAKE_HYDROCARBON_TENTACLER_1` — RM_Ulkhoss deployed with the 610 restart; NEXT: confirm name/stats with him at the Chill sheet, then close.
- `BIOME_FLORAFAUNA_ART_REVIEW_1` — ready to sit: Grey Sea, The Chill, Twilight Sea, Webwork, The Scald; NEXT: rerun `scaled_review_gate.py all` after the queue drains and list PASS sheets for him.
- `FLYER_FLIPBOOK_ART_1` — sheet shows flip-books; 48 Pyrelands frames pending; NEXT: when they land, rebuild the Pyrelands sheet and take his flight pick.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Map Designer re-applies a startup density snapshot at game start, silently undoing any runtime BiomeDef density write made after its ctor (see: design/validation_walks/RimMandrake/DivingInteraction.md anti-guessing notes).
- `jawa/get_defs fields=` takes a COMMA list; `;` reads as one unknown field "(no such field)" (see: DivingInteraction validation.py floor_biomes_carry_sea_life).
- `./publish -m A -m B` treats the second `-m` as a path and refuses; one -m only (see: this handoff).
- `rimflow bridge release` by one seat clears the BRIDGE file even when the other seat took it since (FOUNDRY's 12:31Z release freed BENCH's 12:23Z hold) (see: this handoff).

## Closed since the last handoff (1)

- `TINT_ON_COLOUR_ART_1` — e2bcad71dbd7

## Filed and still open (0) — the next seat's queue

Nothing filed in this window.

## Commits

```
970b6a32d Art job: Grey Sea salt chimney (owner: 'looks like crude blocks stacked'); its sprite was the 09-26 placeholder
d97142596 DivingInteraction DLL rebuilt from 61cf4800f (floor density re-assert)
32428ae6b Grey floor grew 0 plants: Map Designer writes back its startup density snapshot over the floor-life copy; re-assert before floor generation and on FinalizeInit
d07fd3b37 FlowWorks v2 aborts at preflight when the running DLL is not the repo's
e99f4f6b5 FOUNDRY handoff 2026-10-06 12:32
ab5cf1488 Biome kits live run 2026-10-06: Forge/Miasma/Scarlands/Sump results recorded, notes, bridge released
5d1ed6ed0 FeverWood lure_raid declares the swarm it waits for, so its arrival is not a surprise
e5f4f08c3 Close TINT_ON_COLOUR_ART_1, drop TWILIGHT_GIANT_CATCHES_1 (card 02:06); CLAUDE.md: only fish-sized sea creatures owe a catch
e2bcad71d Strip the <color> tint from all 56 full-colour defs (TINT_ON_COLOUR_ART_1, decision taken by question card 2026-10-06)
7c9a20104 modcheck status: write the status file in binary mode so python.exe does not emit CRLF
814597021 Scarlands loosened-panel proof takes two params, as jawa/static_call passes them
1a82be722 modcheck status: python.exe recording works over \\wsl.localhost (mkdir mutex where byte-range locks are unsupported)
cc741b6e4 TheForge gas wash bursts from real fuel; voices chain runs with hazard scald off
24e19306b FOUNDRY biome-kits overnight notes 2026-10-06
b5785abdf BIOME_KITS_PUSH_TO_TEST_1: 2026-10-06 offline pass logged
f983aca2b Greentide mire escalation gets a seeded chain; RM_Mired is ambient terrain, not an injury surprise
6f08b61ae TheForge script drops other suites' permanent weather locks before starting the cycle
4b6127995 CreatureBehaviors script covers every Mod Settings field: defaults read back, all 64 bools round-trip
37c96a7dd TheForge script: every cycle chain declares its own letters and fires; wind-down puts the gas wash out
eb4b3e41f Miasma and Warscar get their validation walks; Miasma's script round-trips all 18 settings
... 13 more: git log --oneline 8aab315dd..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-10-06T13:02:51Z

Uncommitted: none of BENCH's. Untracked only: `conversations/` (hook transcripts), Transient serve logs, `Transient/modcheck/fixtures.json` (run_suite fixture cache from the live Grey run), BENCH's GPT-bundle extracts in `Transient/northstar_review_2026-10-06/` (derived, deliberately untracked).

