# GSS pre-release GPT consult — dossier (2026-10-15)

Owner, 2026-10-15: *"since we're getting near deployment, go ahead and do a full ConsultGPT on each mod individually
with all of its information, the design goals, the known behaviors, and information on how we debug rimworld so that
it can help grind out any strange hidden behaviors."*

Mod: Gimme Some Slack, `src/RimMandrake/GimmeSomeSlack` (hoses moved to FlowWorks; out of scope).
Tool: `src/RimMandrake/Utils/gpt_consult.py` (codex.exe, gpt-6.1-sol, effort high). Source files were sent with
line numbers prefixed (`NNNNN| `) so findings cite real lines; numbered copies were scratch, not committed.

## Files here

| file | what |
|---|---|
| `CONTEXT.md` | what GSS is, owner intent, known behaviours/history, the static-ID-table lesson, how we debug (written for GPT) |
| `QUESTION.md` | the question template; `{PART}`/`{SCOPE}` filled per consult |
| `answer_A.md`, `answer_B1.md`, `answer_B2.md`, `answer_C.md`, `answer_D.md` | GPT's answers, verbatim (B timed out at 585 s and was re-split: B1 = rendering files, B2 = mod shell, settings kit, probes, About) |
| `TRIAGE.md` | every finding checked against the code: CONFIRMED / PLAUSIBLE / REJECTED, with item IDs |

## Every consult received (inlined, in this order)

Common: `CONTEXT.md`, `design/validation_walks/RimMandrake/GimmeSomeSlack.md` (walk + `## north star`),
`design/RimMandrake/gss_gpt_source_read_2026-10-06.md` (previous read + fix status),
`design/RimMandrake/debug_process.md`, `skills/rimworld-modding/references/project-engine-facts.md`,
`infrastructure/state/facts/instrument_traps.md`.

| consult | design excerpt | source (under `src/RimMandrake/GimmeSomeSlack/` unless `_Shared/`) |
|---|---|---|
| A cord graph | `messy_conduit_design_2026-10-02.md` lines 338-1056 (§8) | `Source/Core/{CordGraph,CordBuilder,CordAudit,ConduitTargets,WallMount,LegacyName}.cs`, `Source/CordWorldAdapter.cs`, `Source/RM_MapComponent_CordGraph.cs`, `_Shared/SlackGeometry/{CordMath,CordWorld,CordPlanner,CordLayer,DrawOrder}.cs`, `Source/GimmeSomeSlackDefOf.cs` |
| B cord render + shell | same §8 | `Source/{SectionLayer_RM_MessyCords,CordMaterials,ConduitVisuals,GimmeSomeSlackMod,GimmeSomeSlackProbe,StyleProbe}.cs`, `Source/Core/CordMotion.cs`, `_Shared/HarmonyResilience/PatchApplier.cs`, `_Shared/SettingsKit/*.cs`, `_Shared/SlackGeometry/DrawOrder.cs`, `Defs/MapMeshFlagDefs.xml`, `About/About.xml` |
| C overhead lines | `messy_conduit_phase2_design_2026-10-02.md` lines 130-361 (§2) | `Source/Aerial/{RM_MapComponent_Aerial,CompAerialAnchor,AerialMath,CompPowerTap,TapLedger,PowerTheftConsequences,RM_FallenWireShock,Alert_WireDown,PlaceWorkers_Aerial,AerialPowerPatch,SectionLayer_RM_AerialGround,AerialMaterials,AerialDefOf,PoleGeometryTable,BracketGeometryTable,AerialSettings,AerialProbe}.cs`, `Defs/Aerial/{RM_AerialAnchors,RM_PowerTheft,RM_FallenWireShock}.xml` |
| D styles | `messyconduit_style_per_build_design.md` lines 97-175 and 249-end | `Source/Aerial/{ConduitStyles,ConduitStylePicker,RM_MapComponent_ConduitRuns,AerialStyles,StylePicker,ConduitStyleProbe,StyleProbeAerial,AerialSettings,AerialMaterials}.cs`, `_Shared/StylePicker/StylePickerCore.cs`, `Source/{CordMaterials,GimmeSomeSlackMod}.cs`, `Defs/Aerial/{RM_ConduitStyles,RM_AerialStyles}.xml`, `Patches/RM_ConduitStyleable.xml` |

Not sent: `Source/SelfTest/*` (offline selftests/fuzz), the Python harness, art.

## Results

See `TRIAGE.md`.
