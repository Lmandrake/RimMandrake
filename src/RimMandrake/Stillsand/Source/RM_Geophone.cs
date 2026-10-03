using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.CreatureBehaviors;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_GEOPHONE_1 — a staked biosilica resonator. Every ReadIntervalTicks it asks the
    // sand-swim kit's own query (RM_CompSandSwim.Submerged, CreatureBehaviors) which swimmers
    // under the sand lie within the radius, and keeps ONE coarse marker per rumble: a compass
    // bearing in eighths and a size class. No distance, no species.
    // It also hears a drum lure's drumming (RM_CompDrumLure) by the same rule: it cannot tell a
    // drazzik's lie from a real drum. A sand gale (drownsRumble) silences every reading.
    // Settings: RM_GlassChainSettings.geophoneEnabled / geophoneRadius.
    // ════════════════════════════════════════════════════════════════════
    public enum RM_RumbleSize { small, medium, large }

    public struct RM_RumbleMarker
    {
        public int compass;          // 0 = N, clockwise in eighths
        public RM_RumbleSize size;
        public IntVec3 cell;         // for the drawn line only; never shown as a position
    }

    public static class RM_GeophoneUtil
    {
        public static readonly string[] Names = { "north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest" };

        public static int CompassOf(Vector3 from, Vector3 to)
        {
            float ang = Mathf.Atan2(to.x - from.x, to.z - from.z) * Mathf.Rad2Deg; // 0 = north, clockwise
            if (ang < 0f) ang += 360f;
            return Mathf.RoundToInt(ang / 45f) % 8;
        }

        public static RM_RumbleSize SizeOf(float bodySize)
        {
            return bodySize < 1f ? RM_RumbleSize.small : (bodySize < 2.5f ? RM_RumbleSize.medium : RM_RumbleSize.large);
        }

        // True when this pawn makes a rumble the geophone can hear: a submerged swimmer, or a drum lure.
        public static bool Rumbles(Pawn p)
        {
            if (p == null || !p.Spawned || p.Dead) return false;
            RM_CompSandSwim swim = p.GetComp<RM_CompSandSwim>();
            if (swim != null && swim.Submerged) return true;
            return RM_CreatureBehaviorsSettings.drumLureEnabled && !p.Downed && p.GetComp<RM_CompDrumLure>() != null;
        }

        public static void Read(Map map, IntVec3 at, float radius, List<RM_RumbleMarker> into)
        {
            into.Clear();
            if (map == null || (RM_WeatherSenseExtension.On(map)?.drownsRumble ?? false)) return;
            Vector3 from = at.ToVector3Shifted();
            float r2 = radius * radius;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if ((p.Position - at).LengthHorizontalSquared > r2 || p.Position == at || !Rumbles(p)) continue;
                into.Add(new RM_RumbleMarker
                {
                    compass = CompassOf(from, p.DrawPos),
                    size = SizeOf(p.BodySize),
                    cell = p.Position
                });
            }
        }
    }

    public class RM_CompProperties_Geophone : CompProperties
    {
        public int readIntervalTicks = 60;

        public RM_CompProperties_Geophone() { compClass = typeof(RM_CompGeophone); }
    }

    public class RM_CompGeophone : ThingComp
    {
        private readonly List<RM_RumbleMarker> markers = new List<RM_RumbleMarker>();
        private int lastMessageTick = -99999;

        public RM_CompProperties_Geophone Props { get { return (RM_CompProperties_Geophone)props; } }
        public IList<RM_RumbleMarker> Markers { get { return markers; } }

        public override void CompTick()
        {
            if (!parent.Spawned || !parent.IsHashIntervalTick(Mathf.Max(1, Props.readIntervalTicks))) return;
            if (!RM_GlassChainSettings.geophoneEnabled) { markers.Clear(); return; }
            int before = markers.Count;
            RM_GeophoneUtil.Read(parent.Map, parent.Position, RM_GlassChainSettings.geophoneRadius, markers);
            if (markers.Count > before && parent.Faction == Faction.OfPlayer
                && Find.TickManager.TicksGame - lastMessageTick > 1800)
            {
                lastMessageTick = Find.TickManager.TicksGame;
                Messages.Message("The geophone hums: a rumble to the " + RM_GeophoneUtil.Names[markers[markers.Count - 1].compass] + ".",
                    parent, MessageTypeDefOf.NeutralEvent, historical: false);
            }
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_GlassChainSettings.geophoneEnabled) return "Geophone switched off in Mod Settings.";
            if (markers.Count == 0) return "The sand is quiet.";
            var sb = new StringBuilder();
            for (int i = 0; i < markers.Count; i++)
            {
                if (i > 0) sb.Append('\n');
                sb.Append("Rumble, ").Append(markers[i].size.ToString()).Append(", to the ").Append(RM_GeophoneUtil.Names[markers[i].compass]);
            }
            return sb.ToString();
        }

        public override void PostDrawExtraSelectionOverlays()
        {
            if (!parent.Spawned) return;
            GenDraw.DrawRadiusRing(parent.Position, RM_GlassChainSettings.geophoneRadius);
            Vector3 o = parent.DrawPos; o.y = AltitudeLayer.MetaOverlays.AltitudeFor();
            for (int i = 0; i < markers.Count; i++)
            {
                float ang = markers[i].compass * 45f * Mathf.Deg2Rad;
                float len = 3f + 2f * (int)markers[i].size;
                Vector3 tip = o + new Vector3(Mathf.Sin(ang), 0f, Mathf.Cos(ang)) * len;
                GenDraw.DrawLineBetween(o, tip, SimpleColor.White);
            }
        }
    }
}
