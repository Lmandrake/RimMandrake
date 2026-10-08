# Failed art jobs — triage 2026-10-08 00:15 (BENCH helper)

Source: `D:\Luke\dev\_artpipe\failed` (25 manifests younger than 24 h; the "38" in the brief also counted jobs already requeued earlier) + `journalctl --user -u rm-artpiped`.
Script that did the moves (ran once): `D:\Luke\dev\RimMandrake\Transient\biome_art_refresh_2026-10-07\requeue_failed_2026-10-08.py`. Requeued jobs carry **priority -10**; artpiped sorts `(priority, name)` ascending and the 520 bulk jobs are at 0, so these claim first.

## Causes by count
| cause | n | action |
|---|---|---|
| codex worker flake: model invoked the final `--output-schema` response before the image tool ("final schema invoked prematurely", "routing error") | 11 requeued (+1 obsolete, withdrawn) | requeued same id (the sanctioned fix, same as `requeue_flakes.py`) |
| canon gate FAIL after the daemon's one corrected retry (derived north/south facings) | 6 | requeued as v2 with the failed Must-show points baked into the prompt up front |
| validator REJECT (size/centering) | 2 | tooke-trap: v4 with a consistent footprint line |
| worker REFUSED: owner note "No new art!" pasted into the prompt as an override | 1 + 5 derived (master_failed) | HELD, owner question below |

No quality gate touched. No pipeline code change was needed: the placeholder check did not misfire (no placeholder failure anywhere), validator and canon gate behaved correctly. The flake rate (about 1 in 6 jobs tonight, both attempts hit it) is a codex-side routing fault; retry is the only remedy.

## Per job
**Flake -> requeued same id, priority -10** (wreck_*/chill left at 0): miasma_canon_yobshrimpjuv_v1_north, miasma_nemreth_varb_v1, 0vv_desert_venomvine_v4 (SIGINT at the 23:27 daemon drain), 0vv_rearing_venomvine_v1, 0vv_shedding_venomvine_v2, wreck_nightsideexpeditionrig_a, wreck_canyonwreckspeeder_a, wreck_falllinewreckcarapace_a, chill_item_hydrocarbonflesh_v1 (the last four had already failed this way once before).
- miasma_canon_laajuv_v1_east, miasma_canon_laajuv_v2_north: flake. The v1 group is obsolete (v2 east and south are done), so v1_east was **withdrawn** to `_withdrawn/`; v2_north requeued (derives from the done v2_east).

**Canon gate -> v2, derive_from unchanged (done v1 east master)**, failed lines are spelled out in the v2 prompt:
- miasma_canon_opeejuv_v1_north -> `miasma_canon_opeejuv_v2_north`: antennae shorter than body.
- miasma_canon_opeejuv_v1_south -> `miasma_canon_opeejuv_v2_south`: antennae short, legs thick paddles not thin jointed, tongue a nub.
- miasma_canon_bogwing_flying_2_v1_north -> `miasma_canon_bogwing_flying_2_v2_north`: hind talons small, not splayed.
- miasma_canon_yobshrimpjuv_v1_south -> `miasma_canon_yobshrimpjuv_v2_south`: bulky claws not thin scissor blades; antennae curls not whips.
- twilightsea_mee_canon_redo_v1_north -> `twilightsea_mee_canon_redo_v2_north`: scales mottled not hexagonal.
- twilightsea_mee_canon_redo_v1_south -> `twilightsea_mee_canon_redo_v2_south`: needle sticking sideways (and doubled) instead of on the centreline.

Pattern: every canon failure is a derived facing losing a thin long feature (whips, needles, scissor blades) at 256 px, while the east master passed. A v2 can still miss; if so the fix is a hand-written per-facing description, never a looser gate. Note the facing set now mixes v1 east with v2 north/south ids; whoever installs must pick by facing, not by version prefix.

**Validator -> v4**
- webwork_tooketrap_redo_v2 / v3: both REJECT on subject width/height/origin. v3 came back 193x182 at (34,49) vs the reference 210x207 at (22,25). The v3 prompt contradicted itself ("no wider than 198x195, centred" and "fill 210x207 starting x=22,y=25"). `webwork_tooketrap_redo_v4` states one footprint (bbox exactly 210x207, top-left 22,25) and tells the worker to crop to the alpha bbox, scale uniformly and paste there.

**Held: owner question** (not requeued; files remain in `failed/`)
- miasma_canon_blixus_v1_east (+ north, south, swim_east/north/south, master_failed): the worker REFUSED because the prompt quoted the owner's note "No new art!" as an overriding instruction. On the Miasma sheet the row is `decision: redo`, `note: "No new art!"`, `picks: Blixus_Swimming = B`; those contradict, so I did not guess. Ask him: does "No new art!" mean keep the current Blixus art (cancel the redo), or redo without art direction? If redo, drop the owner-note line from the job prompt and refile `miasma_canon_blixus_v2` (builder: `build_miasma_regen_jobs.py`, row `miasma_canon_blixus_v1`).
