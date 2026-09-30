# CRACKEDLANDS_MECHANICS_BUILD_1: tranche 1 report

Mod: `src/RimMandrake/FloodedCanyon` (`mandrake.rm.floodedcanyon`). The work is built against the
current names; `CRACKEDLANDS_FULL_RENAME_1` has not landed yet. The item stays open because it is a
multi-tranche build.

## Built (offline; not deployed; no live test)

| Spec part | What | Commit |
|---|---|---|
| §3 Fossils in the walls | `RM_FossilStrata.cs`. A GenStep (order 250, registered on Core's abstract `MapCommonBase` via a Conditional patch) seeds the ruled seam defs into natural-rock wall **faces**. Placement is biased low using the generator's Elevation grid. Impressions go in 2–4 cell runs. Articulated seams are rarer. The deep-stratum tier only goes 3+ cells into the rock. On recede, the flood cuts fresh seams (setting `floodRecutSeamCount`, default 4) in natural rock that touches the wetted footprint. A seam only replaces non-resource natural rock. The GenStep is gated on the biome. | `db5a324fb` |
| §4 Muttavaq | `RM_CompPanSleeper`, the RM_-tier member of the CompWaterWakeTrigger family. It wakes the muttavaq when non-scalding water is within 2.9 cells (stock `WakeUp`) and drops wax (`RUT_CrackWax` by name, silent if absent, 10~30). After 12 dry hours with no flood it seals itself where it stands (stock `ToSleep`). The def gains `jobDormancy` (without it a "dormant" animal wanders) and `freezeNeeds` Food/Rest. | `71af82b7b` |
| §5 Peakstorm Light | `RM_PeakstormLight` WeatherDef. It has zero precipitation by construction: its only event is `RM_WeatherEvent_DistantFlicker`, a dimmed vanilla LightningFlash that plays Thunder_OffMap and never strikes. While it stands, the flood clock may pull the next flood forward once, but never within half a period of the last flood. It is added to both the RM_ table and the campaign's Op-4 replacement table. | `0967fa8d9` |
| §5 Chime staging | The chime rings three times across the lead time (full, half, last moments), each stage with its own message. | `c12cf4088` |

Every mechanic has a Mod Settings toggle. The defaults are the shipped behaviour, and the settings page now scrolls. Debug actions added: Recede flood NOW, Report fossil seams. The flood state report now also shows chime stage and weather.

## Remaining (and why)

- **§1 The Swale.** This needs a new FlowWorks canal variant plus a bounded fertility writer. That is a cross-mod FlowWorks change and needs design of the variant def and fill hook. The Utinni discovery lock (WorldComponent) depends on §2's survey. It is the next tranche.
- **§2 Survey and cistern loop.** This needs survey scoring, a survey item, a prospect job, and a cistern FlowWorks source. It is large, and the survey item needs art.
- **§4 Walking-weir trail.** FlowWorks exposes no driver "dig" API; only `TryFloodDriverCell` and `TrySetDriverFill` exist. This needs a FlowWorks API addition.
- **§4 Uttaqar cave-mouth spawns.** Not started.
- **§5 Bespoke chime tones, wind-in-the-slots ambient, ticking flats, tarruq call-stop.** These need audio. Every stage currently plays vanilla TinyBell.
- **§6 Salvage, visitor incident, ledges/toll gate, bloom market.** Later tranches; the spec says the bloom market goes last.
- **Calibration picks, not ruled numbers:** the wake-drop 10~30, Peakstorm commonality 3 (RM_) and 10 (campaign), and the seam densities.
- **Design question:** the RM_ biome's generic weather table still carries Rain, RainyThunderstorm and Snow. The campaign patch bans them for the campaign only. Q11a says the free mod should look the same as the campaign one. This is an owner/BENCH call, left untouched here.

## Verification

- XML parse clean for all FloodedCanyon Defs/Patches and the edited UtinniPatches patch.
- `dotnet build` produced 0 warnings and 0 errors after each piece. The DLL and its `.srchash` are committed together.
- `run_selftests.py`: 76/78 passed. The one failure is the known pre-existing `selftest_deployed_biome_refs`. 1 test is unmeasured and 2 were skipped.
- RimSage was connected. Seams read: CompCanBeDormant, CompProperties_CanBeDormant, Need.IsFrozen, ListerThings.EverListable, MapCommonBase genSteps, WeatherEvent_LightningFlash, WeatherDef fields.
- Owed quicktest, as state reads only: "Report fossil seams" on a new Cracked Lands map, then again after "Start flood NOW" and "Recede flood NOW". For the muttavaq, read the dev-mode inspect line (`sealed` / `awake`) before and after water reaches it.
