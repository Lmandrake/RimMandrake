# BENCH live round 5 — ratchet pilot at ONE HEAD, 2026-10-15

ROUND HEAD **38d3744bc9** (2b913cc892 + the tier fix). git archive -> `/home/mandrake/.seat-tmp/BENCH/r5_export`, copied
(minus Transient) to `D:\Luke\dev\_rmscratch\bench_live_20261015_r5`. No mod fix landed mid-round.

## 0. Tier fix (r4 recorder refusal)
SWBestiary dropped the Star Wars Animal Collection dependency at 3898fe6212; no pilot mod hard-depends on it (rm.patches and
rut.patches reach it only through guarded patches). Round 4 applied its list before that commit, so it loaded SWAC and
`modcheck record` refused. The tier was right; it now FORBIDS `mlie.starwarsanimalcollection` (38d3744bc9) and resolves to 22
mods. Cost seen live: 8 'Failed to find any textures' lines at startup (7 donor `swanimals/` pack paths + Orray pack) vs 1 in
r4 -> DONOR_PACK_TEX_REPAIR_SEVEN_LEFT_BEHIND (FOUNDRY).

## 1. Deploy
modset_builder --tier ratchet_pilot --apply run FROM THE BENCH CLONE (marker in bench, r4 trap avoided); owner backup md5
ee01dae9. Deployed GSS 2, FlowWorks 2, LuminousPigment 1, SWBestiary 6, UtinniPatches 5, composed biomes 36; WeatherSuite,
MandrakePatches, PyrelandsMechanics in sync. All re-plans 0 drift; dll_source_stamp FlowWorks/GSS/FireEcologyHook/
PyrelandsMechanics MATCH. Companion build --gm: identical to deployed; selftest_tool_metadata 1/1. Tank-looks art not installed.
Launch via Steam READY 89 s (pid 3220), 22 mods. Test profile until 12:00Z. health armed 240 min, telemetry tier test.
health_observer did NOT run: another collector holds `JawaBench\health\collector.lock` (not ours).

## 2. Suites at 38d3744bc9
| suite | result |
|---|---|
| C1 GSS proof_all --live | run 4 **110/110 PASS**, wall 364.8 s, aerial 43.2 s, log budget PASS; `modcheck record` ACCEPTED. Run 1 + 3 aerial disturbed by hostile MECHS after the noon pin (Militor; Lancer + 2 RM_HullBolt) -> TESTENV_FOGGED_MECH_HARDEN_WOKE_ON_REVEAL; run 2 preflight stopped on dormant hives (noted on TESTENV_QUICKTEST_HIVES_HARDEN_EMPTY_NEST) |
| C2 FlowWorks v2 --live --fresh-map | **61/61 GREEN** (P4/P4f/P4b/P5n PASS: ladder fix live) -> V2_LADDER_ROWS_DIAGNOSE_STAGE_FRIGHT closed; recorded (REFUSED verdict only for step 4 UNMEASURED). River extension 19 PASS / 0 FAIL / 1 UNMEASURED (flood_refill, by design); swept restarted after a new dormant Hive -> PASS |
| C3 Pyrelands, FRESH site r6 (tile 5) | 36 rows: 33 PASS / 0 FAIL; embergrass_regrows INFERRED (256->1->35->70); furnacebeast_warmth tool gap; **scorchfruit_spoils_fast restarted twice, never scored**: site at 56.7 C, vanilla Heatstroke downs colonists in its long advance -> TESTENV_SITE_HEAT_HARDEN_COOKS_BY_ROW3 (fresh site r7 read 58.3 C; r4's 52.7 C fixture no longer loads). floor Pyrelands VALIDATED 21/21 |

## 3. Section H at 38d3744bc9
1 **MET** · 2 **MET** (v2 0/0; river 0 FAIL, the UNMEASURED is by design) · 3 **NOT MET strictly**: 0 FAIL, but
scorchfruit_spoils_fast is a heat-disturbed restart, not INFERRED/tool-gap · 4 **NOT MET**: POND_BED closed (D4 + walk-out
PASS); PYRELANDS_GRASS_SATURATION_1 machine half done, needs owner look; WEIR_WASH A2 needs a no-room proof hook (mod code);
POND_ELEVATION owner-deferred · 5: code_review 86/87 changed files CLEAN (11 cleaned this round); modset_builder.py DIRTY with 2
findings (MODSET_MARKER_REPAIR_RESTORES_YESTERDAY); selftests targeted only · 6 owner-only. **Pilot NOT closed.**

## Worklist
- PASS/closed: TESTENV_WILD_DOWNED_REPAIR_STOPS_CLOCK (wild downed stop resumed, 2000/2000), FACTION_LEADER_REPAIR_SIX_EMPTY_THRONES
  (Free Droid Enclaves leader non-null without Droid Depot, 0 'Faction leader for'), MAYREQUIRE_REPAIR_GUARDS_NAME_A_GHOST
  (DesalPlant + PumpingStation wrecks on a river map), PIT_REROUTE_FIX_TIME_TRAVEL_FORGIVEN (S1: v2 61/61 twice across a reload
  to an earlier tick), BURROW_TIMEOUT_FIX_DEJA_VU_CURED (S2 A1+A2), POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE.
- PASS, item open: RONTO_PACK_TEXTURE_REPAIR_SADDLEBAGS_MISSING (0 RontoPack lines; owner art approval owed).
- Arrival origins: 2 fresh quicktests with the noon pin + 8-12k governed ticks: 0 arrivals. Lead (unproven): fog reveal wakes an
  ancient-danger room ('Area revealed' letter 2 ticks after the pin in GSS run 1).
- UNMEASURED: settings Reset-all live checks (FlowWorks/GSS/Pyrelands; no Dialog_ModSettings driver, shading is an owner look),
  GSS spark settings (needs a fallen-wire staging + glow-draw read).

## Teardown
health 343.9 ms frame-hist hook total; disarmed; telemetry campaign; awareness off. Game killed by PID 3220.
`modset_builder --restore` (bench marker) -> md5 **ee01dae9**, 550 active, verified. Bridge released, game DOWN.
