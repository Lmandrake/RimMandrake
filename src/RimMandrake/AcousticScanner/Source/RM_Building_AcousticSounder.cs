using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.AcousticScanner
{
    // GRAVSHIP_ACOUSTIC_SCANNER_1 — the ship-mounted acoustic scanner.
    //
    // Owner (question card + typed note, 2026-09-30): "I like the belly sounder
    // immensely and it should do something in every biome actually. Acoustic scanner."
    //
    // Ship-mounted: built only on gravship substructure (vanilla
    // PlaceWorker_OnSubstructure in the ThingDef). Fires only while grounded — the
    // map carries a GravEngine and this sounder still stands on substructure — and
    // powered. A pulse: dust jumps off nearby walls, a low thump and a camera shake
    // for the bass through the hull, then the biome's payload
    // (RM_AcousticPayloadExtension on map.Biome) is heard and drawn as coarse
    // probability bands (RM_AcousticBanding) on a temporary overlay
    // (RM_MapComponent_AcousticReading). A biome with no payload reads "nothing
    // unusual". Unlocked by research (RM_AcousticSounding), not given free.
    public class RM_Building_AcousticSounder : Building
    {
        private int lastPulseTick = -999999;

        private static RM_AcousticScannerSettings S => RM_AcousticScannerMod.settings;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref lastPulseTick, "lastPulseTick", -999999);
        }

        private int CooldownTicks => Mathf.RoundToInt(S.cooldownHours * GenDate.TicksPerHour);
        private int TicksUntilReady => lastPulseTick + CooldownTicks - Find.TickManager.TicksGame;

        public AcceptanceReport CanPulse()
        {
            if (!S.enabled) return "RM_Acoustic_Disabled".Translate();
            if (!Spawned) return false;
            CompPowerTrader power = GetComp<CompPowerTrader>();
            if (power != null && !power.PowerOn) return "RM_Acoustic_NoPower".Translate();
            if (S.requireLandedShip && !OnLandedShip())
                return "RM_Acoustic_NotOnShip".Translate();
            int left = TicksUntilReady;
            if (left > 0) return "RM_Acoustic_Cooldown".Translate(left.ToStringTicksToPeriod());
            return true;
        }

        private bool OnLandedShip()
        {
            ThingDef engine = DefDatabase<ThingDef>.GetNamedSilentFail("GravEngine");
            if (engine == null || Map.listerThings.ThingsOfDef(engine).Count == 0) return false;
            foreach (IntVec3 c in this.OccupiedRect())
            {
                TerrainDef f = Map.terrainGrid.FoundationAt(c);
                if (f == null || !f.IsSubstructure) return false;
            }
            return true;
        }

        public override IEnumerable<Gizmo> GetGizmos()
        {
            foreach (Gizmo g in base.GetGizmos()) yield return g;
            if (Faction != Faction.OfPlayer) yield break;

            var cmd = new Command_Action
            {
                defaultLabel = "RM_Acoustic_PulseLabel".Translate(),
                defaultDesc = "RM_Acoustic_PulseDesc".Translate(),
                icon = def.uiIcon,
                action = Pulse
            };
            AcceptanceReport can = CanPulse();
            if (!can.Accepted) cmd.Disable(can.Reason);
            yield return cmd;

            if (DebugSettings.ShowDevGizmos)
            {
                yield return new Command_Action
                {
                    defaultLabel = "DEV: reset sounder cooldown",
                    action = () => lastPulseTick = -999999
                };
            }
        }

        public override string GetInspectString()
        {
            var sb = new StringBuilder(base.GetInspectString());
            AcceptanceReport can = CanPulse();
            if (sb.Length > 0) sb.AppendLine();
            sb.Append(can.Accepted ? "RM_Acoustic_Ready".Translate().ToString() : can.Reason);
            return sb.ToString().TrimEndNewlines();
        }

        public void Pulse()
        {
            if (!CanPulse().Accepted) return;
            lastPulseTick = Find.TickManager.TicksGame;
            Map map = Map;

            if (S.pulseEffects) DoPulseEffects(map);

            RM_AcousticPayloadExtension payload = map.Biome?.GetModExtension<RM_AcousticPayloadExtension>();
            var hits = new List<List<IntVec3>>();
            var weights = new List<float>();
            var colors = new List<Color>();
            var labels = new List<string>();
            if (payload != null)
            {
                foreach (RM_AcousticTarget t in payload.targets)
                {
                    var cells = new List<IntVec3>();
                    if (t != null) t.CollectCells(map, Position, S.rangeCells, cells);
                    hits.Add(cells);
                    weights.Add(t?.weight ?? 1f);
                    colors.Add(t?.color ?? Color.white);
                    labels.Add(t?.label ?? "?");
                }
            }

            List<RM_AcousticBand> bands = RM_AcousticBanding.Build(map, hits, weights,
                S.BandSizeClamped, Gen.HashCombineInt(thingIDNumber, lastPulseTick));
            map.GetComponent<RM_MapComponent_AcousticReading>()?.SetReading(bands, colors, labels,
                Mathf.RoundToInt(S.overlayHours * GenDate.TicksPerHour));

            Find.LetterStack.ReceiveLetter("RM_Acoustic_LetterLabel".Translate(),
                BuildReport(payload, hits, bands, map), LetterDefOf.NeutralEvent, new LookTargets(this));
        }

        private string BuildReport(RM_AcousticPayloadExtension payload, List<List<IntVec3>> hits,
            List<RM_AcousticBand> bands, Map map)
        {
            var sb = new StringBuilder();
            sb.AppendLine("RM_Acoustic_LetterIntro".Translate(map.Biome.LabelCap));
            sb.AppendLine();
            bool any = false;
            if (payload != null)
            {
                for (int i = 0; i < payload.targets.Count; i++)
                {
                    if (hits[i].Count == 0) continue;
                    any = true;
                    RM_AcousticTier best = RM_AcousticTier.Faint;
                    foreach (RM_AcousticBand b in bands)
                        if (b.targetIndex == i && b.tier > best) best = b.tier;
                    RM_AcousticTarget t = payload.targets[i];
                    sb.Append("  - ").Append(t.label.CapitalizeFirst()).Append(": ")
                      .Append(("RM_Acoustic_Tier" + best).Translate().ToString());
                    if (!t.reading.NullOrEmpty()) sb.Append(" ").Append(t.reading);
                    sb.AppendLine();
                }
            }
            if (!any)
            {
                sb.AppendLine(payload != null && !payload.quietText.NullOrEmpty()
                    ? payload.quietText
                    : "RM_Acoustic_NothingUnusual".Translate().ToString());
            }
            else
            {
                sb.AppendLine();
                sb.AppendLine("RM_Acoustic_LetterBanded".Translate());
            }
            return sb.ToString().TrimEndNewlines();
        }

        private void DoPulseEffects(Map map)
        {
            // Bass through the hull: a low thump at the sounder and a short shake if watched.
            DefDatabase<SoundDef>.GetNamedSilentFail("Explosion_Thump")?.PlayOneShot(new TargetInfo(Position, map));
            if (Find.CurrentMap == map) Find.CameraDriver.shaker.DoShake(0.6f);

            // Dust jumps from nearby walls: puff on the open side of every wall/rock face in range.
            int puffs = 0;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(Position, 14f, true))
            {
                if (puffs >= 60) break;
                if (!c.InBounds(map)) continue;
                Building ed = c.GetEdifice(map);
                if (ed == null || ed.def.Fillage != FillCategory.Full) continue;
                for (int d = 0; d < 4; d++)
                {
                    IntVec3 open = c + GenAdj.CardinalDirections[d];
                    if (open.InBounds(map) && open.Standable(map) && Rand.Chance(0.35f))
                    {
                        FleckMaker.ThrowDustPuff(open, map, Rand.Range(0.8f, 1.4f));
                        puffs++;
                        break;
                    }
                }
            }
        }
    }
}
