import json
V="design/concepts/Pyrelands/version/in_game/visit_1/"
E=V+"evidence/"; ML=E+"modlist_pyrelands_tier.json"
SHA_A="090cd707f5"; SHA_B="db9b7d66fa"   # deployed source sha (mod folder unchanged by db9b7d66: validation.py only, hash-exempt)
D='python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains '
rows=[]
def r(test, verdict, cmd, ev, note=None, sha=SHA_A):
    d={"test":test,"verdict":verdict,"site_checked":True,"game":"archmagi","mod_sha":sha,"command":cmd,"evidence":ev,
       "modlist":ML,"game_build":"1.6.4871 rev590","site":"NS_Pyrelands_site_1_090cd707f5_visit1, gate B CLEAN (biome RM_Pyrelands, Clear, quiet, 3 colonists)"}
    if note: d["note"]=note
    rows.append(d)
r("sc_burn_line_walks","PASS",D+"burn_line",E+"pyre_v1_i.json","fresh reload; an earlier attempt on the used site read UNMEASURED (not fresh: my lightning experiment burned 2449 cells)")
r("sc_ash_ground","PASS",D+"ground_deep_ash",E+"pyre_v1_a.json")
r("sc_ash_watered","PASS",D+"ash_fertility_watered",E+"pyre_v1_b.json")
r("sc_burn_compounds","PASS",D+"fresh_burn_bonus",E+"pyre_v1_h.json","planted PF_PROBE_CALLER_NEVER_WET: WOULD have been seen [inferred from code ~90%, not mutation-run]: the fault makes ProbeLine's watered field False and the chain fails on 'Black Rain did not water the field'")
r("sc_grass_regreens","PASS","python.exe design/concepts/Pyrelands/version/in_game/visit_1/scripts/regrow_steps.py (the embergrass_regrow chain's own pad, cohort, burn and thresholds, real clock, resumable)",E+"regrow_state.json","day 3 33.6% (>=25%, <=55%), day 7 69.5% (>=60%); 0 of 256 originals survived the burn. Run as a resumable replica because the chain's 420k ticks exceed the 540 s per-command bound")
r("sc_scorchfruit","PASS",D+"plant_census,scorchfruit_fire_born",E+"pyre_v1_i.json","first run UNMEASURED (plant_census must run in the same driver run)")
r("sc_populations","PASS",D+"plant_census,animal_census",E+"pyre_v1_a.json")
r("sc_ruins","FAIL",D+"ruins",E+"pyre_v1_a.json","83% deep ash vs 90%; ash on the ground 10 of 10")
r("sc_ruins","UNMEASURED",D+"ruins",E+"pyre_v1_i.json","check judged wrong (note to the Conductor): CharFloor keeps ruin floors, charred, by design; the check counts them as misses. Item RIMMANDRAKE_FIX_RUINS_CHECK_COUNTS_CHARRED_FLOORS_AS_MISSES. Ash half held 10/10")
r("sc_firehawk","PASS",D+"firehawk",E+"pyre_v1_d.json","state reads only; flight never watched")
r("sc_furnace","PASS",D+"furnace_warmth",E+"pyre_v1_c.json")
r("sc_ashwallow","PASS",D+"burrowers",E+"pyre_v1_c.json")
r("sc_ullai","FAIL",D+"ullai_and_giant",E+"pyre_v1_b.json","herd closed 20% on A in 2500 ticks (<30%); decision right 10/10, anchor = A")
r("sc_ullai","UNMEASURED","python.exe design/concepts/Pyrelands/version/in_game/visit_1/scripts/herd_exp.py",E+"pyre_v1_b.json","check judged wrong (note to the Conductor): window premise ~100 cells/2500 ticks; measured ~19 cells/1000 on deep-ash sand, RM_ShadeDash at noon. Watched 12,500 ticks: 149 -> 48 cells to A, never towards B. Item RIMMANDRAKE_FIX_HERD_CHECK_WINDOW_ASSUMES_PRE_SAND_PACE. Planted PF_HERD_CALLER_ANCHOR_ALWAYS: would NOT have been seen [inferred from code]: with the anchor invalid the faulted code picks the same nearest-ash target; only the probe's goAnchor/goAsh label changes, and sc_ullai only runs with a valid anchor")
r("sc_three_skies","FAIL","python.exe design/concepts/Pyrelands/version/in_game/visit_1/scripts/rain_fire.py + three_skies.py (+ "+D+"cinderfall,blackrain)",E+"rain_fire.json","the chains only compare defs (PASS, pyre_v1_g.json); read by hand: lightning under cinderfall 40 fires in 5/10 windows, ash fall 3 in its first window only then 0; patch depthSum 283 -> 161 under black rain; FIRES DO NOT GO OUT under black rain (both pads out at 2250 ticks; vanilla rain -0.10 vs ember-grass fire +0.132 per 150). Items RIMMANDRAKE_FIX_BLACK_RAIN_LOSES_TO_EMBER_GRASS_FIRE, RIMMANDRAKE_EXTEND_SKY_CHAINS_TO_READ_THE_SCENE_CLAUSES. Captures: black rain distinct; cinderfall close to vanilla Rain at that zoom; the ash-fall frame was mid-blend (screenshots/three_skies_and_rain.jpg)")
r("sc_no_rain","PASS",D+"no_ordinary_rain + python.exe design/concepts/Pyrelands/version/in_game/visit_1/scripts/rain_postfix.py",E+"rain_postfix.json","owed RIMMANDRAKE_FIX_FORCED_WEATHER_SKIPS_THE_RAIN_LIST shown live: forced RainyThunderstorm, Rain, FoggyRain each rolled through WeatherDecider -> RM_FE_BlackRain (storyteller swapped off Tutor for the read: TutorialMode returns Clear first)")
r("sc_firefoam_sprayer","PASS",D+"firefoam_sprayer",E+"pyre_v1_d.json")
r("sc_sand_shovel","PASS",D+"sand_shovel",E+"pyre_v1_c.json")
r("sc_furnace_bed","PASS",D+"furnace_sleep",E+"pyre_v1_g.json")
r("sc_heat_dome","PASS",D+"heat_dome",E+"pyre_v1_c.json")
r("sc_fire_dusts_ash","PASS",D+"fire_tick_effects",E+"pyre_v1_b.json")
r("sc_flamefang_venom","FAIL",D+"flamefang_venom",E+"pyre_v1_c.json","HARNESS: the victim fled unbitten (no injury at all)")
r("sc_flamefang_venom","PASS",D+"flamefang_venom",E+"pyre_v1_f.json","after HARNESS fix db9b7d66 (victim drafted; latch stops on all but hurt/downed): venom 0.317 -> 0.405 over 6 h, fennec control no venom",sha=SHA_B)
r("sc_furnace_giant","PASS",D+"ullai_and_giant",E+"pyre_v1_b.json","components ullai_wired + giant_furnace_beast PASS; the chain's herd row is sc_ullai")
for t,c,f in (("P_startup_and_def_wiring","startup_and_def_wiring","a"),("P_mapgen_log","mapgen_log","a"),("P_grass_cover","grass_cover","a"),
              ("P_animal_census","animal_census","a"),("P_ambient_ash_drift","ambient_ash_drift","g"),("P_scorchfruit_produces","scorchfruit_produces","j"),
              ("P_scorchfruit_spoils","scorchfruit_spoils","j"),("P_furnace_room","furnace_room","d"),("P_ashfall_weather_accumulation","ashfall_weather_accumulation","g"),
              ("P_ashfall_drifts","ashfall_drifts","g"),("P_blackrain","blackrain","g"),
              ("firehawk_first_sighting_letter","firehawk_first_sighting_letter","h"),("firehawk_crestfeather_yield","firehawk_crestfeather_yield","h")):
    r(t,"PASS",D+c,E+"pyre_v1_%s.json"%f, "run through the northstar driver (same suite chain) instead of modcheck run, which lands on a list without the biome" if t.startswith("firehawk") else None)
r("P_opening_front","FAIL",D+"opening_front",E+"pyre_v1_i.json","old-save row: lit 5 at litTick = map birth")
r("P_opening_front","UNMEASURED","python.exe design/concepts/Pyrelands/version/in_game/visit_1/scripts/rearm.py",E+"pyre_v1_i.json","check judged wrong for a post-change fixture (item RIMMANDRAKE_FIX_OLD_SAVE_ROW_MISREADS_A_NEW_FIXTURE); re-arm half by hand: done, lit 27, 27 free-standing fires, scar 2877 cells")
r("P_firefoam_aim","PASS","python.exe src/RimMandrake/Pyrelands/firefoam_aim_live_proof.py","design/concepts/Pyrelands/version/in_game/visit_1/evidence/firefoam_aim.log (exit 0: FIREFOAM fire True | cell True ... control fire False cell False)")
r("P_gate","PASS","python.exe src/RimMandrake/Pyrelands/gate_live_proof.py A1; ... A2","design/concepts/Pyrelands/version/in_game/visit_1/evidence/gate_A1.log + gate_A2.log, exit 0 both: A1 ShellPresent=True On=True; A2 ShellOn=True Enabled(Pyrelands)=True")
open(V+"rows.jsonl","w").write("".join(json.dumps(x)+"\n" for x in rows))
S=[{"what":"a freshly spawned wild ullai carries a 'Gunshot' (neck, severity 6) with no hostile, turret or colonist in range","status":"explained","why":"generated pawns carry old scars (the control colonist spawned with a 'stab scar'); presumed a birth injury [guess ~80%]","where":"scripts/anchorless.py hediffs"},
   {"what":"black X marks and dark rectangles in the grass west of the live burn front (station 4)","status":"explained","why":"the cells hold only RM_FE_Ash_Deep and grass, no things, ash depth 0: the deep-ash ground texture showing through bare cells","where":"Transient/pv1/shots/st4_zoom.png"},
   {"what":"ullai facing north render as thin sticks beside a wide furnace-beast giant","status":"filed","item":"RIMMANDRAKE_JUDGE_ULLAI_NORTH_VIEW_READS_AS_A_STICK","where":"screenshots/walk_stations.jpg station 5"},
   {"what":"two wild ullai abandoned the herd's walk for RM_ShadeDash at noon","status":"explained","why":"Direct Sun shade-seeking (owner's one Direct Sun ruling) preempts a GotoWander on a 50 C noon site; ordinary play","where":"scripts/herd_exp2.py"},
   {"what":"40 unlocked weather rolls all read Clear on a biome whose table gives Clear weight 0","status":"explained","why":"the site's own stacked Clear weather lock (GameCondition_ForceWeather) still stands after one unlock; Tutor storyteller also returns Clear first","where":"evidence/rain_postfix.json"},
   {"what":"wild fire-hawk and ashwallow downed during the 7-day regrow advance","status":"explained","why":"wild predation on the map's own fauna (safe_advance latch 'downed' on wild subjects, not colonists)","where":"evidence/regrow_state.json stops"},
   {"what":"the opening-front scar laid at the re-arm had fully regrown by the walk save, ~11 days later","status":"explained","why":"the regrow mechanic doing its job (69.5% green by day 7 measured); the station label was corrected","where":"screenshots/walk_stations.jpg station 1"}]
open(V+"strange.jsonl","w").write("".join(json.dumps(x)+"\n" for x in S))
print(len(rows), "rows;", len(S), "strange")
