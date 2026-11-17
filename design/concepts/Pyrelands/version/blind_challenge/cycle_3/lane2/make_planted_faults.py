import json,os,sys
R='/home/mandrake/rm/relentless/clones/RIMMANDRAKE_JUDGE_PYRELANDS_BLIND_CYCLE_THREE_TESTS_FIRST.det/'
M='src/RimMandrake/Pyrelands/'
K=M+'Source/Kernel/'
F=[
# ash_fertility_probe kernel + caller
("probe_wet_ignores_switch",K+'RM_FireEcoKernel.cs',"bool wetNow = waterOn && watered;","bool wetNow = watered;",["ash_fertility_probe"]),
("probe_no_refusal_ash_off",K+'RM_FireEcoKernel.cs',': !waterOn ? "the ash field is off (ashWaterFertilityEnabled)" : null;',': null;',["ash_fertility_probe"]),
("probe_consistent_always_true",K+'RM_FireEcoKernel.cs','(Math.Abs(fertility - expected) < 0.001f ? "True" : "False")','"True"',["ash_fertility_probe"]),
("fertility_water_ignores_switch",K+'RM_FireEcoKernel.cs',"float v = (waterOn && isWatered ? watered : dry)","float v = (isWatered ? watered : dry)",["ash_fertility_probe","ash_fertile_when_watered"]),
("bonus_never_fades",K+'RM_FireEcoKernel.cs',"return bonus * (f > 1f ? 1f : f);","return bonus;",["ash_fertility_probe","fresh_burn_compounds_with_black_rain"]),
("probecell_reads_base_not_grid",M+'Source/PyrelandsAshField.cs',"return RM_FireEcoKernel.ProbeLine(m.fertilityGrid.FertilityAt(c), t?.defName,","return RM_FireEcoKernel.ProbeLine(t?.fertility ?? 0f, t?.defName,",["ash_fertility_probe"]),
("probecell_bonus_dropped",M+'Source/PyrelandsAshField.cs',"comp?.BonusAt(c, now) ?? 0f, comp?.burnTick","0f, comp?.burnTick",["ash_fertility_probe"]),
("probecell_gate_ignored",M+'Source/PyrelandsAshField.cs',"                PyrelandsMechanicsGate.On, FertilityCap);\n        }\n\n        /// <summary>Bar ash_fertility_probe: ProbeCell","                true, FertilityCap);\n        }\n\n        /// <summary>Bar ash_fertility_probe: ProbeCell",["ash_fertility_probe","inv_settings_gate"]),
# biome_text_says_engineered
("desc_engineered_to_natural",M+'Defs/BiomeDefs/Pyrelands.xml',"savanna, genetically engineered in a forgotten age","savanna, grown wild in a forgotten age",["biome_text_says_engineered"]),
("desc_millennia_dropped",M+'Defs/BiomeDefs/Pyrelands.xml',"for millennia. Coarse","for a season. Coarse",["biome_text_says_engineered"]),
("heat_immunity_gate_ignored",M+'Source/Patch_FurnaceBeastHeatImmunity.cs',"if (!PyrelandsMechanicsGate.On || !RM_PyrelandsSettings.furnaceThermalEnabled)","if (false)",["inv_settings_gate","furnacebeast_warms"]),
("heat_immunity_absorbs_nothing",M+'Source/Patch_FurnaceBeastHeatImmunity.cs',"                absorbed = true;\n                return false;","                absorbed = false;\n                return true;",["biome_text_says_engineered","inv_art_and_text"]),
("dig_leaves_no_gravel",M+'Source/RM_TerrainDig.cs',"if (ext.leaves != null) map.terrainGrid.SetTerrain(c, ext.leaves);","",["sand_shovel_yields_glass_sand","inv_art_and_text"]),
("dig_default_count_one",M+'Source/RM_TerrainDig.cs',"public int count = 5;","public int count = 1;",["sand_shovel_yields_glass_sand","inv_art_and_text"]),
# inv_firebreak_firefoam / inv_lightning_breaker
("firebreak_terrain_back",M+'Defs/TerrainDefs/AshField.xml',"</Defs>",'  <TerrainDef ParentName="FloorBase"><defName>RM_FirebreakLine</defName><label>firebreak line</label><description>Fire will not cross it.</description><texturePath>Terrain/Surfaces/Concrete</texturePath><costList><Chemfuel>2</Chemfuel></costList></TerrainDef>\n</Defs>',["inv_firebreak_firefoam"]),
("firebreak_keyed_back",M+'Languages/English/Keyed/Pyrelands.xml',"</LanguageData>","  <RM_FirebreakLabel>Firebreak line</RM_FirebreakLabel>\n</LanguageData>",["inv_firebreak_firefoam"]),
("breaker_def_back",M+'Defs/ThingDefs_Items/RM_FurnaceHide.xml','  <ThingDef ParentName="LeatherBase">\n    <defName>RM_FurnaceHide</defName>','  <ThingDef ParentName="ResourceBase"><defName>RM_LightningBreaker</defName><label>lightning breaker</label><description>Draws the strike.</description></ThingDef>\n  <ThingDef ParentName="LeatherBase">\n    <defName>RM_FurnaceHide</defName>',["inv_lightning_breaker"]),
("fulgurite_def_back",M+'Defs/ThingDefs_Items/RM_FurnaceHide.xml','  </ThingDef>\n\n</Defs>','  </ThingDef>\n  <ThingDef ParentName="ResourceBase"><defName>RM_Fulgurite</defName><label>fulgurite</label><description>Glass from a strike.</description></ThingDef>\n</Defs>',["inv_lightning_breaker"]),
# inv_settings_gate
("gate_ignores_shell",K+'RM_FireEcoKernel.cs',"return modMaster && (!shellPresent || shellOn);","return modMaster;",["inv_settings_gate"]),
("gate_shellon_always",M+'Source/PyrelandsMechanicsGate.cs',"public static bool ShellOn => shellEnabled == null || shellEnabled(RosterKey);","public static bool ShellOn => true;",["inv_settings_gate"]),
("wind_scribe_default_off",M+'Source/RM_PyrelandsMod.cs','"windCarriesFireEnabled", true);','"windCarriesFireEnabled", false);',["inv_settings_gate"]),
("worldgen_ships_on",M+'Source/RM_PyrelandsMod.cs',"public static bool biomeGenerationEnabled = false;","public static bool biomeGenerationEnabled = true;",["inv_settings_gate"]),
("wind_checkbox_wrong_field",M+'Source/RM_PyrelandsMod.cs','list.CheckboxLabeled("The wind carries the fire", ref windCarriesFireEnabled,','list.CheckboxLabeled("The wind carries the fire", ref burnLineEnabled,',["inv_settings_gate"]),
("wind_not_in_section_reset",M+'Source/RM_PyrelandsMod.cs','new[] { "burnLineEnabled", "windCarriesFireEnabled", "fireHawkSpreadEnabled"','new[] { "burnLineEnabled", "fireHawkSpreadEnabled"',["inv_settings_gate"]),
("wind_ignores_its_switch",M+'Source/MapComponent_BurnLine.cs',"&& RM_PyrelandsSettings.windCarriesFireEnabled;",";",["inv_settings_gate","burn_line_walks"]),
("wind_ignores_gate",M+'Source/MapComponent_BurnLine.cs',"public bool WindCarries => IsPyrelandsMap && PyrelandsMechanicsGate.On && RM_PyrelandsSettings.burnLineEnabled","public bool WindCarries => IsPyrelandsMap && RM_PyrelandsSettings.burnLineEnabled",["inv_settings_gate","burn_line_walks"]),
("preflight_wind_default_off",M+'preflight_pyrelands.py','"blackRainDousing": 40.0, "windCarriesFireEnabled": True,','"blackRainDousing": 40.0, "windCarriesFireEnabled": False,',["inv_settings_gate"]),
("preflight_worldgen_on",M+'preflight_pyrelands.py','"biomeGenerationEnabled": False','"biomeGenerationEnabled": True',["inv_settings_gate"]),
# inv_art_and_text
("texpath_broken",M+'Defs/ThingDefs_Plants/EmberGrass.xml',"<texPath>Things/Plant/RM_FE_EmberGrass</texPath>","<texPath>Things/Plant/RM_FE_EmberGrassMissing</texPath>",["inv_art_and_text"]),
("description_emptied",M+'Defs/ThingDefs_Items/RM_FurnaceHide.xml',"<description>The banded hide of a furnace-beast,","<description></description><x>The banded hide of a furnace-beast,",["inv_art_and_text"]),
("about_promises_worldgen_more",M+'About/About.xml',"Every mechanic has its own switch in Mod Settings","Pyrelands appears on new worlds by default. Every mechanic has its own switch in Mod Settings",["inv_art_and_text"]),
# burn_line_walks: kernel (changed) and callers (changed)
("probes_far_goes_back",K+'RM_BurnKernel.cs',"int lean = (n + side + 8) % 8, far = (n - side + 8) % 8;","int lean = (n + side + 8) % 8, far = (n + 4) % 8;",["burn_line_walks"]),
("carry_twice",K+'RM_BurnKernel.cs',"return enabled && freeStanding && onPyrelandsGround && !alreadyCarried && ticksSinceSpawn >= WindCarryTicks;","return enabled && freeStanding && onPyrelandsGround && ticksSinceSpawn >= WindCarryTicks;",["burn_line_walks"]),
("line_along_wind",K+'RM_BurnKernel.cs',"return (windBearingDeg + 90f) % 360f;","return windBearingDeg % 360f;",["burn_line_walks"]),
("downwind_cone_wide",K+'RM_BurnKernel.cs',"return along > 0f && across <= along * 2.4143f;","return along > -1f;",["burn_line_walks"]),
("vanilla_spread_still_runs",K+'RM_BurnKernel.cs',"return !(enabled && freeStanding && onPyrelandsGround);","return true;",["burn_line_walks"]),
("carry_lights_every_probe",M+'Source/FireEcologyHook.cs',"                    && FireUtility.TryStartFireIn(c, map, Fire.MinFireSize, fire.instigator))\n                {\n                    return;","                    && FireUtility.TryStartFireIn(c, map, Fire.MinFireSize, fire.instigator))\n                {\n                    continue;",["burn_line_walks"]),
("spread_prefix_always_vanilla",M+'Source/FireEcologyHook.cs',"return RM_BurnKernel.VanillaSpreadRuns(governed, true, true);","return true;",["burn_line_walks"]),
("carry_forgets_carried",M+'Source/FireEcologyHook.cs',"burn.WasCarried(__instance), __instance.TicksSinceSpawn","false, __instance.TicksSinceSpawn",["burn_line_walks"]),
("markcarried_noop",M+'Source/MapComponent_BurnLine.cs',"carriedFires.Add(fire.thingIDNumber);",";",["burn_line_walks"]),
("front_line_along_wind_caller",M+'Source/PyrelandsFireFront.cs',"? RM_BurnKernel.AcrossWind(burn.WindBearing) : Rand.Range(0f, 360f);","? burn.WindBearing : Rand.Range(0f, 360f);",["burn_line_walks"]),
("scar_wind_not_set",M+'Source/PyrelandsFireFront.cs',"MapComponent_BurnLine.For(map)?.SetWindFromScar(scarEdge);",";",["burn_line_walks"]),
("front_width_four",M+'Source/PyrelandsTuning.cs',"public const int FireFrontWidthCells = 24;","public const int FireFrontWidthCells = 4;",["burn_line_walks","inv_burn_line_fire_clock"]),
("fronts_rare",M+'Source/PyrelandsTuning.cs',"public const float FireFrontMaxDays = 4f;","public const float FireFrontMaxDays = 40f;",["inv_burn_line_fire_clock"]),
("keyed_wind_letter_lost",M+'Languages/English/Keyed/Pyrelands.xml',"<RM_FireFrontLetterTextWind>","<RM_FireFrontLetterTextWindX>",["inv_art_and_text","burn_line_walks"]),
("sim_carry_splits_two",M+'pyre_burn_sim.py',"carry_splits=1,","carry_splits=2,",["burn_line_walks"]),
]
out=[]
bad=0
for fid,f,old,new,bars in F:
    t=open(R+f,encoding='utf-8').read()
    n=t.count(old)
    if n!=1: print('NOT ONCE',n,fid); bad+=1
    out.append({"id":fid,"file":f,"old":old,"new":new,"bars":bars})
json.dump({"faults":out},open(R+'design/concepts/Pyrelands/version/blind_challenge/cycle_3/lane2/planted_faults.json','w'),indent=1)
print(len(out),'faults',bad,'bad')
