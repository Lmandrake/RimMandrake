using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // LONGSHADE_BEDAZZLE_MECHANICS_1 part 2 — the mirrak, "the shadow that
    // points the wrong way" (longshade_shade_ideation_2026-09-29.md §6.2,
    // owner: IN). Item spec: "The dash job giver treats it as shade and the
    // grid does not."
    //
    // So false shade is a SEPARATE layer from RM_MapComponent_ShadeGrid, not a
    // write into it: the grid stays the physical truth (a mirrak's body never
    // cools anyone), and PerceivedShadeAt is what a shade-SEEKING animal's eyes
    // see — the grid's value, or a lying false-shade pawn's, whichever is
    // higher. Shade-seekers read PerceivedShadeAt to CHOOSE a destination;
    // anything that computes heat reads ShadeAt. The shipped shade-seeking
    // wander (RM_JobGiver_WanderInShadeGrid) reads it now; the rest-dash-rest
    // job givers of SOLAR_HEAT_EXPOSURE_1 spec 5 are meant to read the same
    // call when they land ("otherwise it never eats", §6.2 ⚠️).
    // ════════════════════════════════════════════════════════════════════

    /// <summary>On a race ThingDef: while this pawn lies still, the cells
    /// within <see cref="radius"/> read as shade of <see cref="perceivedShade"/>
    /// to shade-seekers (never to the shade grid itself).</summary>
    public class RM_FalseShadeExtension : DefModExtension
    {
        public float perceivedShade = 0.9f;

        /// <summary>Cells from the pawn's own cell that read as its "shadow".
        /// 1.5 = its own cell plus the 8 around it — a boulder's worth.</summary>
        public float radius = 1.5f;
    }

    /// <summary>
    /// Per-map registry of lying false-shade pawns, refreshed on a coarse
    /// interval (a mirrak that is lying in wait does not move, so a few
    /// seconds' staleness is invisible). Usually holds 0–3 entries, so the
    /// per-cell lookup is a short loop.
    /// </summary>
    public class RM_MapComponent_FalseShade : MapComponent
    {
        private const int RefreshIntervalTicks = 120;

        private readonly List<Pawn> lures = new List<Pawn>();
        private readonly List<Thing> decoys = new List<Thing>();

        public RM_MapComponent_FalseShade(Map map) : base(map)
        {
        }

        public IReadOnlyList<Pawn> Lures => lures;

        /// <summary>DECOY_SHADE_TARP_1: buildings (RM_CompDecoyShade) that read as shade to seekers and give none.</summary>
        public IReadOnlyList<Thing> Decoys => decoys;
        public void RegisterDecoy(Thing t) { if (!decoys.Contains(t)) decoys.Add(t); }
        public void UnregisterDecoy(Thing t) { decoys.Remove(t); }

        /// <summary>What a decoy reads as: its extension's perceivedShade plus the stuff's shade bonus (mirrak hide
        /// is the most convincing), clamped to 1. 0 when the decoy toggle is off.</summary>
        public static float DecoyShadeOf(Thing t)
        {
            RM_FalseShadeExtension ext = t.def.GetModExtension<RM_FalseShadeExtension>();
            if (ext == null || !RM_CreatureBehaviorsSettings.decoyShadeEnabled)
            {
                return 0f;
            }
            return Mathf.Min(1f, ext.perceivedShade + RM_ShadeGear.StuffBonus(t));
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            Refresh();
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (Find.TickManager.TicksGame % RefreshIntervalTicks == 0)
            {
                Refresh();
            }
        }

        public void Refresh()
        {
            lures.Clear();
            if (!RM_CreatureBehaviorsSettings.falseShadeAmbushEnabled)
            {
                return;
            }
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.Dead || p.Downed || p.def.GetModExtension<RM_FalseShadeExtension>() == null)
                {
                    continue;
                }
                if (p.pather != null && p.pather.Moving)
                {
                    continue; // a moving body is an animal, not a shadow
                }
                lures.Add(p);
            }
        }

        public float FalseShadeAt(IntVec3 cell)
        {
            float best = 0f;
            for (int i = 0; i < decoys.Count; i++)
            {
                Thing d = decoys[i];
                if (!d.Spawned || d.Map != map)
                {
                    continue;
                }
                RM_FalseShadeExtension dext = d.def.GetModExtension<RM_FalseShadeExtension>();
                float shade = DecoyShadeOf(d);
                if (dext != null && shade > best && (cell - d.Position).LengthHorizontalSquared <= dext.radius * dext.radius)
                {
                    best = shade;
                }
            }
            for (int i = 0; RM_CreatureBehaviorsSettings.falseShadeAmbushEnabled && i < lures.Count; i++)
            {
                Pawn p = lures[i];
                if (!p.Spawned || p.Map != map || p.Dead || p.Downed || (p.pather != null && p.pather.Moving))
                {
                    continue; // re-check the cheap eligibility: the cached list can be up to one refresh stale
                }
                RM_FalseShadeExtension ext = p.def.GetModExtension<RM_FalseShadeExtension>();
                if (ext == null)
                {
                    continue;
                }
                if ((cell - p.Position).LengthHorizontalSquared <= ext.radius * ext.radius && ext.perceivedShade > best)
                {
                    best = ext.perceivedShade;
                }
            }
            return best;
        }
    }

    public static class RM_ShadePerception
    {
        /// <summary>What a shade-SEEKER sees at a cell: the real grid shade or
        /// a lying false-shade pawn's, whichever is higher. 0 = full sun.
        /// Never use this for heat — use RM_MapComponent_ShadeGrid.ShadeAt.</summary>
        public static float PerceivedShadeAt(Map map, IntVec3 cell)
        {
            if (map == null)
            {
                return 0f;
            }
            float real = map.GetComponent<RM_MapComponent_ShadeGrid>()?.ShadeAt(cell) ?? 0f;
            if (!RM_CreatureBehaviorsSettings.falseShadeAmbushEnabled && !RM_CreatureBehaviorsSettings.decoyShadeEnabled)
            {
                return real;
            }
            float lie = map.GetComponent<RM_MapComponent_FalseShade>()?.FalseShadeAt(cell) ?? 0f;
            return Mathf.Max(real, lie);
        }
    }

    /// <summary>DECOY_SHADE_TARP_1: a cheap painted awning. Registers with RM_MapComponent_FalseShade so shade-SEEKING
    /// animals read it as shade (RM_ShadePerception); it is never written to the shade grid, so it cools nobody.</summary>
    public class RM_CompDecoyShade : ThingComp
    {
        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            parent.Map.GetComponent<RM_MapComponent_FalseShade>()?.RegisterDecoy(parent);
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            map.GetComponent<RM_MapComponent_FalseShade>()?.UnregisterDecoy(parent);
        }
    }
}
